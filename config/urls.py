# config/urls.py

from django.contrib import admin
from django.urls import path, include

# HIER IST DIE WICHTIGE ZEILE, DIE WAHRSCHEINLICH FEHLT:
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('plaene.urls')),

    # Diese Zeilen benötigen den Import von oben
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]