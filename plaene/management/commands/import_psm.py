# plaene/management/commands/import_psm.py

import requests
import io
import zipfile
from lxml import etree
from django.core.management.base import BaseCommand
from django.db import transaction
from plaene.models import Pflanzenschutzmittel, KulturMetadaten, SchaderregerMetadaten, Zulassung

class Command(BaseCommand):
    help = 'Lädt das ZIP-Archiv vom BLV mit lxml und importiert die Produktdaten inkl. aller Zulassungen (finale XPath-Version).'

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
                xml_bytes = zip_ref.read(xml_filename)
            self.stdout.write(self.style.SUCCESS(f"Download und Entpacken von '{xml_filename}' erfolgreich."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler bei Download/Entpacken: {e}"))
            return
        
        root = etree.fromstring(xml_bytes)
        self.stdout.write("XML-Daten erfolgreich mit lxml geparst.")

        self.stdout.write("Lösche alte Zulassungs- und Metadaten...")
        KulturMetadaten.objects.all().delete()
        SchaderregerMetadaten.objects.all().delete()
        Zulassung.objects.all().delete()

        self.create_metadata_from_xml(root, 'Culture', KulturMetadaten)
        self.create_metadata_from_xml(root, 'Pest', SchaderregerMetadaten)
        
        alle_produkt_eintraege = root.xpath("//*[local-name()='Product' or local-name()='Parallelimport']")
        self.stdout.write(f"{len(alle_produkt_eintraege)} Produkte und Parallelimporte gefunden. Importiere jetzt...")

        for produkt_node in alle_produkt_eintraege:
            produktname = produkt_node.get('name')
            if produkt_node.tag.endswith('Parallelimport'):
                zulassungsnr = produkt_node.get('id', '')
            else:
                zulassungsnr = produkt_node.get('wNbr')
            
            if not zulassungsnr or not produktname: continue

            produkt_obj, created = Pflanzenschutzmittel.objects.update_or_create(
                zulassungsnr=zulassungsnr, defaults={'produktname': produktname}
            )
            
            product_info_nodes = produkt_node.xpath("./*[local-name()='ProductInformation']")
            if not product_info_nodes: continue
            product_info_node = product_info_nodes[0]

            indication_nodes = product_info_node.xpath("./*[local-name()='Indication']")

            for indication_node in indication_nodes:
                culture_nodes = indication_node.xpath("./*[local-name()='Culture']")
                if not culture_nodes: continue
                culture_node = culture_nodes[0]
                
                kultur_pk = culture_node.get('primaryKey')
                try:
                    kultur_obj = KulturMetadaten.objects.get(blv_id=kultur_pk)
                except KulturMetadaten.DoesNotExist: continue

                aufwandmenge = indication_node.get('expenditureForm', '')
                wartefrist = indication_node.get('waitingPeriod', '')

                for pest_node in indication_node.xpath("./*[local-name()='Pest']"):
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
        metadata_blocks = root.xpath(f".//*[local-name()='MetaData' and @name='{metadata_name}']")
        count = 0
        if metadata_blocks:
            metadata_block = metadata_blocks[0]
            for detail_node in metadata_block.xpath("./*[local-name()='Detail']"):
                key = detail_node.get('primaryKey')
                desc_nodes = detail_node.xpath("./*[local-name()='Description' and @language='de']")
                if desc_nodes:
                    name = desc_nodes[0].get('value')
                    if key and name and model_class:
                        model_class.objects.get_or_create(blv_id=key, defaults={'name': name})
                        count += 1
        self.stdout.write(f"{count} '{metadata_name}'-Metadaten in die Datenbank importiert.")
        return count