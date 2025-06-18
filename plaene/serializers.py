# plaene/serializers.py

from rest_framework import serializers
from .models import (
    Plan, Kultur, Behandlung, ProduktInBehandlung, 
    KulturMetadaten, Pflanzenschutzmittel, SchaderregerMetadaten, Landwirt, Zulassung
)

# Diese Serializer bleiben für einfache Listen oder zum Erstellen
class KulturMetadatenSerializer(serializers.ModelSerializer):
    class Meta:
        model = KulturMetadaten
        fields = ['id', 'blv_id', 'name']

class PflanzenschutzmittelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pflanzenschutzmittel
        fields = ['id', 'zulassungsnr', 'produktname', 'wirkstoff']

class SchaderregerMetadatenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchaderregerMetadaten
        fields = ['id', 'blv_id', 'name']

class LandwirtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landwirt
        fields = ['id', 'betriebsname', 'vorname', 'nachname']


# --- NEUE, VERSCHACHTELTE SERIALIZER FÜR DIE DETAILANSICHT ---

class ProduktInBehandlungDetailSerializer(serializers.ModelSerializer):
    # Zeigt die kompletten Produkt-Infos, nicht nur die ID
    produkt = PflanzenschutzmittelSerializer(read_only=True)
    class Meta:
        model = ProduktInBehandlung
        fields = ['id', 'produkt', 'aufwandmenge', 'einheit']

class BehandlungDetailSerializer(serializers.ModelSerializer):
    # Jede Behandlung hat eine Liste von Produkten im Mix
    produkte_im_mix = ProduktInBehandlungDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Behandlung
        fields = ['id', 'titel', 'anwendungszeitpunkt', 'eigene_notizen', 'produkte_im_mix']

class KulturDetailSerializer(serializers.ModelSerializer):
    # NEU: Wir fügen manuell die ID der Metadaten hinzu
    meta_id = serializers.SerializerMethodField()
    behandlungen = BehandlungDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Kultur
        # 'meta_id' zum fields-Array hinzufügen
        fields = ['id', 'meta_id', 'name', 'flaeche_ha', 'behandlungen']

    def get_meta_id(self, obj):
        # Diese Funktion wird für jedes Kultur-Objekt aufgerufen.
        # Sie findet das passende Metadaten-Objekt über den Namen und gibt dessen ID zurück.
        # Dies ist ein Workaround, da wir keine direkte ForeignKey-Beziehung im Modell haben.
        try:
            # Finde die Kultur in den Metadaten, die denselben Namen hat
            kultur_meta = KulturMetadaten.objects.get(name=obj.name)
            return kultur_meta.id
        except KulturMetadaten.DoesNotExist:
            return None

# --- Wir passen den bestehenden PlanSerializer an ---
class PlanListSerializer(serializers.ModelSerializer):
    landwirt_name = serializers.CharField(source='landwirt.__str__', read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'landwirt_name', 'jahr', 'status']
        
class PlanDetailSerializer(serializers.ModelSerializer):
    landwirt_name = serializers.CharField(source='landwirt.__str__', read_only=True)
    kulturen = KulturDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'landwirt', 'landwirt_name', 'jahr', 'status', 'kulturen']
        extra_kwargs = {
            'landwirt': {'write_only': True}
        }

class ZulassungDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zulassung
        fields = ['id', 'aufwandmenge', 'wartefrist', 'anzahl_anwendungen']



