# plaene/views.py

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Importiere alle Modelle nur einmal
from .models import (
    Plan, Kultur, Behandlung, ProduktInBehandlung, Landwirt, 
    KulturMetadaten, SchaderregerMetadaten, Pflanzenschutzmittel, Zulassung
)
# Importiere alle Serializer nur einmal
from .serializers import (
    PlanListSerializer, PlanDetailSerializer, KulturMetadatenSerializer, 
    PflanzenschutzmittelSerializer, SchaderregerMetadatenSerializer, 
    LandwirtSerializer, ZulassungDetailSerializer
)


class PlanViewSet(viewsets.ModelViewSet):
    """
    Ein ViewSet, das alle CRUD-Operationen für Pläne bereitstellt.
    Nutzt unterschiedliche Serializer für Listen- und Detailansichten.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Gibt nur die Pläne des eingeloggten Benutzers zurück
        user = self.request.user
        return Plan.objects.filter(landwirt__berater=user).prefetch_related(
            'kulturen__behandlungen__produkte_im_mix__produkt'
        )

    def get_serializer_class(self):
        # Wählt den passenden Serializer je nach Aktion
        if self.action == 'list':
            return PlanListSerializer
        # Für alle anderen Aktionen (Detail, Erstellen, Update) wird der detaillierte Serializer verwendet
        return PlanDetailSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        try:
            landwirt = Landwirt.objects.get(id=data['landwirtId'], berater=user)
        except Landwirt.DoesNotExist:
            return Response({'error': 'Landwirt nicht gefunden oder keine Berechtigung.'}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            neuer_plan = Plan.objects.create(landwirt=landwirt, jahr=data['jahr'], status='Entwurf')
            for kultur_data in data.get('kulturen', []):
                try:
                    kultur_meta = KulturMetadaten.objects.get(id=kultur_data['meta_id'])
                    neue_kultur = Kultur.objects.create(plan=neuer_plan, name=kultur_meta.name, flaeche_ha=kultur_data.get('flaeche_ha', 0))
                    for behandlung_data in kultur_data.get('behandlungen', []):
                        neue_behandlung = Behandlung.objects.create(kultur=neue_kultur, titel=behandlung_data.get('titel', 'Unbenannte Behandlung'))
                        for produkt_data in behandlung_data.get('produkte_im_mix', []):
                            produkt = Pflanzenschutzmittel.objects.get(id=produkt_data['produktId'])
                            ProduktInBehandlung.objects.create(
                                behandlung=neue_behandlung,
                                produkt=produkt,
                                aufwandmenge=str(produkt_data.get('aufwandmenge', '')).split(' ')[0],
                                einheit='N/A'
                            )
                except KulturMetadaten.DoesNotExist:
                    continue
        
        serializer = self.get_serializer(neuer_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        plan_obj = self.get_object()
        data = request.data
        
        with transaction.atomic():
            # 1. Update der Plan-Stammdaten
            plan_obj.status = data.get('status', plan_obj.status)
            plan_obj.jahr = data.get('jahr', plan_obj.jahr)
            plan_obj.save()

            # 2. Alle alten Kulturen löschen, was kaskadierend alle Behandlungen etc. mit löscht
            plan_obj.kulturen.all().delete()

            # 3. Die Struktur aus den neuen Frontend-Daten komplett neu aufbauen
            for kultur_data in data.get('kulturen', []):
                try:
                    # Hier verwenden wir meta_id, die vom Frontend geschickt wird
                    kultur_meta = KulturMetadaten.objects.get(id=kultur_data['meta_id'])
                    neue_kultur = Kultur.objects.create(
                        plan=plan_obj,
                        name=kultur_meta.name,
                        flaeche_ha=kultur_data.get('flaeche_ha', 0)
                    )

                    for behandlung_data in kultur_data.get('behandlungen', []):
                        neue_behandlung = Behandlung.objects.create(
                            kultur=neue_kultur,
                            titel=behandlung_data.get('titel', 'Unbenannte Behandlung')
                        )

                        for produkt_data in behandlung_data.get('produkte_im_mix', []):
                            produkt = Pflanzenschutzmittel.objects.get(id=produkt_data['produktId'])
                            ProduktInBehandlung.objects.create(
                                behandlung=neue_behandlung,
                                produkt=produkt,
                                aufwandmenge=str(produkt_data.get('aufwandmenge', '')).split(' ')[0],
                                einheit='N/A' # Platzhalter
                            )
                except KulturMetadaten.DoesNotExist:
                    continue
        
        serializer = self.get_serializer(plan_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LandwirtViewSet(viewsets.ModelViewSet):
    serializer_class = LandwirtSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Landwirt.objects.filter(berater=self.request.user)

    def perform_create(self, serializer):
        serializer.save(berater=self.request.user)


class KulturMetadatenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KulturMetadaten.objects.all().order_by('name')
    serializer_class = KulturMetadatenSerializer
    permission_classes = [IsAuthenticated]


class PflanzenschutzmittelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PflanzenschutzmittelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pflanzenschutzmittel.objects.all()
        kultur_id = self.request.query_params.get('kultur')
        if kultur_id is not None:
            queryset = queryset.filter(zulassung__kultur__id=kultur_id).distinct()
        return queryset


class SchaderregerMetadatenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchaderregerMetadaten.objects.all().order_by('name')
    serializer_class = SchaderregerMetadatenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SchaderregerMetadaten.objects.all()
        kultur_id = self.request.query_params.get('kultur')
        produkt_id = self.request.query_params.get('produkt')
        if kultur_id and produkt_id:
            queryset = queryset.filter(
                zulassung__kultur__id=kultur_id,
                zulassung__produkt__id=produkt_id
            ).distinct()
        return queryset.order_by('name')


class ZulassungViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ZulassungDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Zulassung.objects.all()
        kultur_id = self.request.query_params.get('kultur')
        produkt_id = self.request.query_params.get('produkt')
        schaderreger_id = self.request.query_params.get('schaderreger')
        if kultur_id and produkt_id and schaderreger_id:
            queryset = queryset.filter(
                kultur__id=kultur_id,
                produkt__id=produkt_id,
                schaderreger__id=schaderreger_id
            )
        else:
            return Zulassung.objects.none()
        return queryset