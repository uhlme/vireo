import requests
import io
import zipfile
from lxml import etree
from django.core.management.base import BaseCommand
from django.db import transaction
from plaene.models import Pflanzenschutzmittel, KulturMetadaten, SchaderregerMetadaten, Zulassung, AuflageMetadaten

class Command(BaseCommand):
    help = 'Finaler Import-Skript, der auch die Einheiten und Auflagen korrekt verknüpft (mit korrekten Variablennamen).'
    PSM_ZIP_URL = "https://www.blv.admin.ch/dam/blv/de/dokumente/zulassung-pflanzenschutzmittel/pflanzenschutzmittelverzeichnis/daten-pflanzenschutzmittelverzeichnis.zip.download.zip/Daten%20Pflanzenschutzmittelverzeichnis.zip"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Starte den Import des Pflanzenschutzmittelverzeichnisses...")
        
        try:
            response = requests.get(self.PSM_ZIP_URL, timeout=60)
            response.raise_for_status()
            zip_in_memory = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                xml_filename = next((n for n in zip_ref.namelist() if n.lower().endswith('.xml')), None)
                xml_bytes = zip_ref.read(xml_filename)
            root = etree.fromstring(xml_bytes)
            self.stdout.write(self.style.SUCCESS("XML-Daten erfolgreich geladen und geparst."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler bei Download/Entpacken: {e}"))
            return

        self.stdout.write("Lösche alte Daten für sauberen Import...")
        AuflageMetadaten.objects.all().delete()
        KulturMetadaten.objects.all().delete()
        SchaderregerMetadaten.objects.all().delete()
        Zulassung.objects.all().delete()

        self.create_metadata_from_xml(root, 'Culture', KulturMetadaten)
        self.create_metadata_from_xml(root, 'Pest', SchaderregerMetadaten)
        self.create_metadata_from_xml(root, 'Obligation', AuflageMetadaten)
        
        # Die Variable heisst hier konsistent 'unit_lookup'
        unit_lookup = self.create_lookup_dict_from_xml(root, 'Measure')
        self.stdout.write(f"{len(unit_lookup)} Einheiten (Measures) in Metadaten gefunden.")
        
        alle_produkt_eintraege = root.xpath("//*[local-name()='Product' or local-name()='Parallelimport']")
        self.stdout.write(f"{len(alle_produkt_eintraege)} Produkte gefunden. Importiere Zulassungen...")

        for produkt_node in alle_produkt_eintraege:
            produktname = produkt_node.get('name')
            zulassungsnr = produkt_node.get('id', '') if produkt_node.tag.endswith('Parallelimport') else produkt_node.get('wNbr')
            if not zulassungsnr or not produktname: continue

            produkt_obj, _ = Pflanzenschutzmittel.objects.update_or_create(
                zulassungsnr=zulassungsnr, defaults={'produktname': produktname}
            )
            
            product_info_nodes = produkt_node.xpath("./*[local-name()='ProductInformation']")
            if not product_info_nodes: continue
            product_info_node = product_info_nodes[0]

            for indication_node in product_info_node.xpath("./*[local-name()='Indication']"):
                culture_nodes = indication_node.xpath("./*[local-name()='Culture']")
                if not culture_nodes: continue
                culture_node = culture_nodes[0]
                
                try:
                    kultur_obj = KulturMetadaten.objects.get(blv_id=culture_node.get('primaryKey'))
                except KulturMetadaten.DoesNotExist: continue

                aufwandmenge_einheit_text = ''
                measure_nodes = indication_node.xpath("./*[local-name()='Measure']")
                if measure_nodes:
                    measure_pk = measure_nodes[0].get('primaryKey')
                    # Und hier wird auch 'unit_lookup' verwendet
                    aufwandmenge_einheit_text = unit_lookup.get(measure_pk, '')
                
                defaults = {
                    'aufwandmenge': indication_node.get('expenditureForm', ''), 'wartefrist': indication_node.get('waitingPeriod', ''),
                    'dosage_from': indication_node.get('dosageFrom', ''), 'dosage_to': indication_node.get('dosageTo', ''),
                    'aufwandmenge_einheit': aufwandmenge_einheit_text,
                }

                auflagen_in_db = []
                for obligation_node in indication_node.xpath("./*[local-name()='Obligation']"):
                    try:
                        auflage_obj = AuflageMetadaten.objects.get(blv_id=obligation_node.get('primaryKey'))
                        auflagen_in_db.append(auflage_obj)
                    except AuflageMetadaten.DoesNotExist: continue
                
                for pest_node in indication_node.xpath("./*[local-name()='Pest']"):
                    try:
                        schaderreger_obj = SchaderregerMetadaten.objects.get(blv_id=pest_node.get('primaryKey'))
                        zulassung_obj, created = Zulassung.objects.get_or_create(
                            produkt=produkt_obj, kultur=kultur_obj, schaderreger=schaderreger_obj,
                            defaults=defaults
                        )
                        if auflagen_in_db:
                            zulassung_obj.auflagen.set(auflagen_in_db)
                    except SchaderregerMetadaten.DoesNotExist: continue
        
        self.stdout.write(self.style.SUCCESS(f"Import abgeschlossen! {Zulassung.objects.count()} gültige Zulassungen wurden erstellt."))

    def create_lookup_dict_from_xml(self, root, metadata_name):
        lookup_dict = {}
        metadata_blocks = root.xpath(f".//*[local-name()='MetaData' and @name='{metadata_name}']")
        if metadata_blocks:
            for detail_node in metadata_blocks[0].xpath("./*[local-name()='Detail']"):
                key = detail_node.get('primaryKey')
                desc_nodes = detail_node.xpath("./*[local-name()='Description' and @language='de']")
                if desc_nodes and desc_nodes[0].get('value'):
                    lookup_dict[key] = desc_nodes[0].get('value')
        return lookup_dict

    def create_metadata_from_xml(self, root, metadata_name, model_class):
        lookup_dict = self.create_lookup_dict_from_xml(root, metadata_name)
        count = 0
        for blv_id, name in lookup_dict.items():
            defaults_data = {'text' if hasattr(model_class, 'text') else 'name': name}
            model_class.objects.get_or_create(blv_id=blv_id, defaults=defaults_data)
            count += 1
        self.stdout.write(f"{count} '{metadata_name}'-Metadaten in die Datenbank importiert.")
        return count