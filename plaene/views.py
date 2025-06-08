# plaene/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Plan, Kultur, Behandlung, ProduktInBehandlung, Landwirt, KulturMetadaten, SchaderregerMetadaten, Pflanzenschutzmittel
from django.db import transaction
from .serializers import PlanSerializer, KulturMetadatenSerializer, PflanzenschutzmittelSerializer, SchaderregerMetadatenSerializer, LandwirtSerializer

from rest_framework.response import Response
from rest_framework import status

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Plan.objects.filter(landwirt__berater=user)

    # WICHTIG: Die perform_create Methode entfernen oder auskommentieren,
    # da wir die Logik jetzt in der create-Methode selbst steuern.

    # NEU: Wir überschreiben die komplette create-Methode
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        try:
            # Prüfen, ob der angegebene Landwirt dem User gehört
            landwirt = Landwirt.objects.get(id=data['landwirt'], berater=user)
        except Landwirt.DoesNotExist:
            return Response({'error': 'Landwirt nicht gefunden oder keine Berechtigung.'}, status=status.HTTP_403_FORBIDDEN)

        # @transaction.atomic sorgt dafür, dass alle DB-Operationen nur dann gespeichert werden,
        # wenn ALLES erfolgreich ist. Bei einem Fehler wird alles zurückgerollt.
        with transaction.atomic():
            # 1. Haupt-Plan erstellen
            neuer_plan = Plan.objects.create(
                landwirt=landwirt,
                jahr=data['jahr'],
                status='Entwurf' # Wir setzen den Status standardmässig auf Entwurf
            )

            # Ein Dictionary, um Kulturen nicht doppelt anzulegen
            erstellte_kulturen = {}

            # 2. Durch die Behandlungen aus dem Frontend loopen
            for behandlung_data in data.get('behandlungen', []):
                kultur_id = behandlung_data['kulturId']
                
                # Prüfen, ob wir die Kultur für diesen Plan schon angelegt haben
                if kultur_id not in erstellte_kulturen:
                    kultur_meta = KulturMetadaten.objects.get(id=kultur_id)
                    neue_kultur = Kultur.objects.create(
                        plan=neuer_plan,
                        name=kultur_meta.name,
                        flaeche_ha=0 # Platzhalter, dieses Feld müssen wir noch im Frontend hinzufügen
                    )
                    erstellte_kulturen[kultur_id] = neue_kultur
                
                aktuelle_kultur_im_plan = erstellte_kulturen[kultur_id]

                # 3. Behandlung erstellen
                neue_behandlung = Behandlung.objects.create(
                    kultur=aktuelle_kultur_im_plan,
                    titel="Behandlung", # Platzhalter
                    anwendungszeitpunkt="", # Platzhalter
                    eigene_notizen=f"Produkt: {behandlung_data['produktName']}, Aufwand: {behandlung_data['aufwandmenge']}"
                )

                # 4. Produkt zur Behandlung hinzufügen
                produkt = Pflanzenschutzmittel.objects.get(id=behandlung_data['produktId'])
                ProduktInBehandlung.objects.create(
                    behandlung=neue_behandlung,
                    produkt=produkt,
                    aufwandmenge=behandlung_data['aufwandmenge'].split(' ')[0], # Nur die Zahl extrahieren
                    einheit='l/ha' # Annahme
                )

        # Gib die Daten des neu erstellten Plans zurück
        serializer = self.get_serializer(neuer_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class KulturMetadatenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ein schreibgeschütztes ViewSet, das alle Kulturen aus den Metadaten anzeigt.
    """
    queryset = KulturMetadaten.objects.all().order_by('name')
    serializer_class = KulturMetadatenSerializer
    permission_classes = [IsAuthenticated] # Nur eingeloggte User dürfen die Kulturen sehen

class PflanzenschutzmittelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PflanzenschutzmittelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pflanzenschutzmittel.objects.all()
        kultur_id = self.request.query_params.get('kultur')
        if kultur_id is not None:
            # ALT: queryset = queryset.filter(zugelassene_anwendungen__id=kultur_id).distinct()
            # NEU, expliziter und robuster:
            queryset = queryset.filter(zulassung__kultur__id=kultur_id).distinct()
        return queryset

class SchaderregerMetadatenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchaderregerMetadaten.objects.all().order_by('name')
    serializer_class = SchaderregerMetadatenSerializer
    permission_classes = [IsAuthenticated]

class LandwirtViewSet(viewsets.ModelViewSet): # von ReadOnlyModelViewSet zu ModelViewSet ändern
    """ Zeigt die Landwirte an UND erlaubt das Erstellen/Ändern/Löschen. """
    serializer_class = LandwirtSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Landwirt.objects.filter(berater=self.request.user)

    # NEU: Diese Methode hinzufügen
    def perform_create(self, serializer):
        """ Setzt den eingeloggten Benutzer automatisch als 'Berater'. """
        serializer.save(berater=self.request.user)