# plaene/management/commands/import_psm.py (Finale Version mit expliziter Dekodierung)

import requests
import io
import zipfile
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from django.db import transaction
from plaene.models import Pflanzenschutzmittel, KulturMetadaten, SchaderregerMetadaten, Zulassung

class Command(BaseCommand):
    help = 'Lädt das ZIP-Archiv vom BLV, entpackt die XML und importiert die Produktdaten inkl. aller Zulassungen.'
    PSM_ZIP_URL = "https://www.blv.admin.ch/dam/blv/de/dokumente/zulassung-pflanzenschutzmittel/pflanzenschutzmittelverzeichnis/daten-pflanzenschutzmittelverzeichnis.zip.download.zip/Daten%20Pflanzenschutzmittelverzeichnis.zip"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Starte den Import des Pflanzenschutzmittelverzeichnisses...")

        try:
            self.stdout.write("Lade ZIP-Datei...")
            response = requests.get(self.PSM_ZIP_URL, timeout=60)
            response.raise_for_status()
            zip_in_memory = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                xml_filename = next((name for name in zip_ref.namelist() if name.lower().endswith('.xml')), None)
                if not xml_filename: raise ValueError("Keine XML-Datei im ZIP-Archiv gefunden.")
                # Lese die rohen Bytes aus der ZIP-Datei
                xml_bytes = zip_ref.read(xml_filename)
            self.stdout.write(self.style.SUCCESS(f"Download und Entpacken von '{xml_filename}' erfolgreich."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler bei Download/Entpacken: {e}"))
            return
        
        # --- HIER IST DIE ENTSCHEIDENDE ÄNDERUNG ---
        # Wir dekodieren die Bytes explizit mit der korrekten Kodierung aus der XML-Datei
        try:
            xml_content_decoded = xml_bytes.decode('iso-8859-1')
            root = ET.fromstring(xml_content_decoded)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler beim Parsen der XML mit ISO-8859-1: {e}"))
            return
        # --- ENDE DER ÄNDERUNG ---

        self.stdout.write("Verarbeite XML-Daten...")
        self.stdout.write("Lösche alte Zulassungs- und Metadaten für einen sauberen Import...")
        KulturMetadaten.objects.all().delete()
        SchaderregerMetadaten.objects.all().delete()
        Zulassung.objects.all().delete()

        kultur_count = self.create_metadata_from_xml(root, 'Culture', KulturMetadaten)
        self.stdout.write(f"{kultur_count} Kulturen in die Datenbank importiert.")
        pest_count = self.create_metadata_from_xml(root, 'Pest', SchaderregerMetadaten)
        self.stdout.write(f"{pest_count} Schaderreger in die Datenbank importiert.")
        
        alle_produkt_eintraege = root.findall('Products/Product') + root.findall('.//Parallelimport')
        self.stdout.write(f"{len(alle_produkt_eintraege)} Produkte und Parallelimporte gefunden. Importiere jetzt...")

        # ... (der Rest des Skripts, die Schleifen, etc. bleiben exakt gleich) ...
        for produkt_node in alle_produkt_eintraege:
            produktname = produkt_node.get('name')
            if produkt_node.tag == 'Parallelimport':
                zulassungsnr = produkt_node.get('id', '')
            else:
                zulassungsnr = produkt_node.get('wNbr')
            
            if not zulassungsnr or not produktname: continue

            produkt_obj, created = Pflanzenschutzmittel.objects.update_or_create(
                zulassungsnr=zulassungsnr, defaults={'produktname': produktname}
            )
            
            product_info_node = produkt_node.find('ProductInformation')
            if product_info_node is None: continue

            indication_nodes = product_info_node.findall('Indication')

            for indication_node in indication_nodes:
                culture_node = indication_node.find('Culture')
                if not culture_node: continue
                
                kultur_pk = culture_node.get('primaryKey')
                try:
                    kultur_obj = KulturMetadaten.objects.get(blv_id=kultur_pk)
                except KulturMetadaten.DoesNotExist: continue

                aufwandmenge = indication_node.get('expenditureForm', '')
                wartefrist = indication_node.get('waitingPeriod', '')

                for pest_node in indication_node.findall('Pest'):
                    pest_pk = pest_node.get('primaryKey')
                    try:
                        schaderreger_obj = SchaderregerMetadaten.objects.get(blv_id=pest_pk)
                        Zulassung.objects.get_or_create(
                            produkt=produkt_obj, kultur=kultur_obj, schaderreger=schaderreger_obj,
                            defaults={'aufwandmenge': aufwandmenge, 'wartefrist': wartefrist, 'anzahl_anwendungen': ''}
                        )
                    except SchaderregerMetadaten.DoesNotExist: continue
        
        zulassungen_count = Zulassung.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Import abgeschlossen! {zulassungen_count} gültige Zulassungen wurden erstellt."))

    def create_metadata_from_xml(self, root, metadata_name, model_class):
        metadata_block = root.find(f"./MetaData[@name='{metadata_name}']")
        count = 0
        if metadata_block is not None:
            for detail_node in metadata_block.findall('Detail'):
                key = detail_node.get('primaryKey')
                desc_node = detail_node.find("./Description[@language='de']")
                if desc_node is not None:
                    name = desc_node.get('value')
                    if key and name and model_class:
                        model_class.objects.get_or_create(blv_id=key, defaults={'name': name})
                        count += 1
        return count