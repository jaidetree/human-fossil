"""URL configuration for the Human Fossil project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from human_fossil import views as human_fossil_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", human_fossil_views.home, name="home"),
]

if settings.DEBUG:
    # Dev-only: serve MEDIA_ROOT directly (WhiteNoise only covers STATIC_ROOT).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
