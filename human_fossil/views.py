from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import (
    AnimationAward,
    Character,
    Event,
    EventPhoto,
    Illustration,
    Image,
    MangaPreviewPage,
)


def home(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    events = Event.objects.filter(is_published=True)
    return render(
        request,
        "home.html",
        {
            "upcoming_events": events.filter(date__gte=today).order_by("date"),
            "past_events": events.filter(date__lt=today).order_by("-date"),
            "animation_awards": AnimationAward.objects.filter(is_published=True),
            "characters": Character.objects.filter(is_published=True),
            "event_photos": EventPhoto.objects.filter(is_published=True),
            "illustrations": Illustration.objects.filter(is_published=True),
            "manga_preview_pages": MangaPreviewPage.objects.filter(is_published=True),
            "images": Image.objects.all(),
        },
    )
