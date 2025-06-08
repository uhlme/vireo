# plaene/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, KulturMetadatenViewSet, PflanzenschutzmittelViewSet, SchaderregerMetadatenViewSet, LandwirtViewSet   # NEU

# 1. Einen Router erstellen
router = DefaultRouter()

router.register(r'plaene', PlanViewSet, basename='plan')
router.register(r'kulturen', KulturMetadatenViewSet, basename='kultur')
router.register(r'produkte', PflanzenschutzmittelViewSet, basename='produkt') # NEU
router.register(r'schaderreger', SchaderregerMetadatenViewSet, basename='schaderreger')
router.register(r'landwirte', LandwirtViewSet, basename='landwirt')
# 3. Die URL-Patterns der App sind jetzt die vom Router generierten URLs
urlpatterns = [
    path('', include(router.urls)),
]