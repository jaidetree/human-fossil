"""URL configuration for the Human Fossil project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from human_fossil import views as human_fossil_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("works/", include("human_fossil.urls")),
    path("contact/", human_fossil_views.contact, name="contact"),
    path("training/", human_fossil_views.training, name="training"),
    path("", human_fossil_views.home, name="home"),
]

if settings.DEBUG:
    # Dev-only: serve MEDIA_ROOT directly (WhiteNoise only covers STATIC_ROOT).
    # Production media storage is Cloudflare R2 (ticket 16), which won't need this.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
