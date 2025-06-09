# plaene/management/commands/check_db_content.py

from django.core.management.base import BaseCommand
from plaene.models import Pflanzenschutzmittel, KulturMetadaten, SchaderregerMetadaten, Zulassung

class Command(BaseCommand):
    help = 'Gibt einen Überblick über den aktuellen Inhalt der wichtigsten Datenbank-Tabellen.'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Datenbank-Inspektion gestartet ---")

        # Zähle die Einträge in jeder Tabelle
        psm_count = Pflanzenschutzmittel.objects.count()
        kultur_count = KulturMetadaten.objects.count()
        schaderreger_count = SchaderregerMetadaten.objects.count()
        zulassung_count = Zulassung.objects.count()

        self.stdout.write(self.style.SUCCESS(f"\nAnzahl Produkte: {psm_count}"))
        self.stdout.write(self.style.SUCCESS(f"Anzahl Kulturen (Metadaten): {kultur_count}"))
        self.stdout.write(self.style.SUCCESS(f"Anzahl Schaderreger (Metadaten): {schaderreger_count}"))
        self.stdout.write(self.style.WARNING(f"Anzahl Zulassungen (Verknüpfungen): {zulassung_count}"))

        # Zeige die ersten 5 Einträge von jeder wichtigen Tabelle
        self.stdout.write("\n--- Beispiele: Erste 5 Kulturen ---")
        for kultur in KulturMetadaten.objects.all()[:5]:
            self.stdout.write(f"  ID: {kultur.id}, BLV_ID: {kultur.blv_id}, Name: {kultur.name}")

        self.stdout.write("\n--- Beispiele: Erste 5 Schaderreger ---")
        for erreger in SchaderregerMetadaten.objects.all()[:5]:
            self.stdout.write(f"  ID: {erreger.id}, BLV_ID: {erreger.blv_id}, Name: {erreger.name}")

        self.stdout.write("\n--- Beispiele: Erste 5 Produkte ---")
        for psm in Pflanzenschutzmittel.objects.all()[:5]:
            self.stdout.write(f"  ID: {psm.id}, Zulassungsnr: {psm.zulassungsnr}, Name: {psm.produktname}")

        self.stdout.write("\n--- Datenbank-Inspektion abgeschlossen ---")