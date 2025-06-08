# plaene/admin.py

from django.contrib import admin
from .models import (
    Pflanzenschutzmittel,
    Landwirt,
    Plan,
    Kultur,
    Behandlung,
    ProduktInBehandlung,
)

# Diese Zeilen sagen Django: "Mache diese Modelle in der Admin-Oberfläche sichtbar und verwaltbar."
admin.site.register(Pflanzenschutzmittel)
admin.site.register(Landwirt)
admin.site.register(Plan)
admin.site.register(Kultur)
admin.site.register(Behandlung)
admin.site.register(ProduktInBehandlung)