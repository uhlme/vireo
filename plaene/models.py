# plaene/models.py

from django.db import models
from django.conf import settings

# ---------------------------------------------------------
# METADATEN-MODELLE (haben keine Abhängigkeiten)
# ---------------------------------------------------------

class KulturMetadaten(models.Model):
    """ Speichert eine Kultur aus dem BLV-Verzeichnis, z.B. "Weizen" oder "Apfel". """
    blv_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SchaderregerMetadaten(models.Model):
    """ Speichert einen Schaderreger (Indikation) aus dem BLV, z.B. "Echter Mehltau". """
    blv_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# NEUES MODELL für die Texte der Auflagen
class AuflageMetadaten(models.Model):
    """ Speichert eine Auflage/Bemerkung aus dem BLV, z.B. 'SPe 3: Gewässerschutz' """
    blv_id = models.CharField(max_length=50, unique=True)
    text = models.TextField()

    def __str__(self):
        return self.text

# ---------------------------------------------------------
# KERN-MODELL
# ---------------------------------------------------------

class Pflanzenschutzmittel(models.Model):
    zulassungsnr = models.CharField(max_length=50, unique=True)
    produktname = models.CharField(max_length=255)
    wirkstoff = models.CharField(max_length=255, blank=True)
    
    # Die Beziehung wird jetzt mit einem String 'Zulassung' definiert,
    # da das Modell 'Zulassung' erst weiter unten deklariert wird.
    zugelassene_anwendungen = models.ManyToManyField(
        KulturMetadaten,
        through='Zulassung',
        related_name='produkte'
    )

    def __str__(self):
        return self.produktname

# ---------------------------------------------------------
# VERKNÜPFUNGS- UND ANWENDUNGS-MODELLE
# ---------------------------------------------------------

class Zulassung(models.Model):
    produkt = models.ForeignKey('Pflanzenschutzmittel', on_delete=models.CASCADE)
    kultur = models.ForeignKey(KulturMetadaten, on_delete=models.CASCADE)
    schaderreger = models.ForeignKey(SchaderregerMetadaten, on_delete=models.CASCADE)
    
    aufwandmenge = models.CharField(max_length=100, blank=True)
    wartefrist = models.CharField(max_length=255, blank=True)
    anzahl_anwendungen = models.CharField(max_length=100, blank=True)
    aufwandmenge_einheit = models.CharField(max_length=50, blank=True)
    dosage_from = models.CharField(max_length=50, blank=True)
    dosage_to = models.CharField(max_length=50, blank=True)
    
    # ALT: auflagen_bemerkungen = models.TextField(blank=True) -> DIESE ZEILE LÖSCHEN
    
    # NEU: Many-to-Many-Beziehung zu den Auflagen
    auflagen = models.ManyToManyField(AuflageMetadaten, blank=True)

    class Meta:
        unique_together = ('produkt', 'kultur', 'schaderreger')

    def __str__(self):
        return f"{self.produkt.produktname} in {self.kultur.name} gegen {self.schaderreger.name}"

# Die restlichen Modelle, die ebenfalls von den oberen abhängen
class Landwirt(models.Model):
    berater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    betriebsname = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    telefon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.betriebsname} ({self.vorname} {self.nachname})"

class Plan(models.Model):
    landwirt = models.ForeignKey(Landwirt, on_delete=models.CASCADE, related_name="plaene")
    jahr = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('Entwurf', 'Entwurf'), ('Finalisiert', 'Finalisiert')], default='Entwurf')
    erstellt_am = models.DateTimeField(auto_now_add=True)
    zuletzt_bearbeitet = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan für {self.landwirt.betriebsname} - {self.jahr}"

class Kultur(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="kulturen")
    name = models.CharField(max_length=100)
    flaeche_ha = models.DecimalField(max_digits=7, decimal_places=2)
    parzellenname = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} auf {self.flaeche_ha}ha ({self.plan})"

class Behandlung(models.Model):
    kultur = models.ForeignKey(Kultur, on_delete=models.CASCADE, related_name="behandlungen")
    titel = models.CharField(max_length=200)
    anwendungszeitpunkt = models.CharField(max_length=100)
    eigene_notizen = models.TextField(blank=True)

    def __str__(self):
        return f"{self.titel} für {self.kultur.name}"

class ProduktInBehandlung(models.Model):
    behandlung = models.ForeignKey(Behandlung, on_delete=models.CASCADE, related_name="produkte_im_mix")
    produkt = models.ForeignKey(Pflanzenschutzmittel, on_delete=models.PROTECT)
    aufwandmenge = models.DecimalField(max_digits=7, decimal_places=3)
    einheit = models.CharField(max_length=10, default='l/ha')

    def __str__(self):
        return f"{self.produkt.produktname} in {self.behandlung.titel}"