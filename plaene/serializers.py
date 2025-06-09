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
    # Jede Kultur in einem Plan hat eine Liste von Behandlungen
    behandlungen = BehandlungDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Kultur
        fields = ['id', 'name', 'flaeche_ha', 'behandlungen']

# --- Wir passen den bestehenden PlanSerializer an ---

class PlanSerializer(serializers.ModelSerializer):
    landwirt_name = serializers.CharField(source='landwirt.__str__', read_only=True)
    # NEU: Fügt die verschachtelten Kulturen zur API-Antwort hinzu
    kulturen = KulturDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        # Füge 'kulturen' zur Liste der Felder hinzu
        fields = ['id', 'landwirt', 'landwirt_name', 'jahr', 'status', 'kulturen']
        extra_kwargs = {
            'landwirt': {'write_only': True} # 'landwirt' wird nur zum Schreiben einer ID erwartet
        }

class ZulassungDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zulassung
        fields = ['id', 'aufwandmenge', 'wartefrist', 'anzahl_anwendungen']