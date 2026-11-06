from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Event, EventPhoto


def home(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    events = Event.objects.filter(is_published=True)
    return render(
        request,
        "home.html",
        {
            "upcoming_events": events.filter(date__gte=today).order_by("date"),
            "past_events": events.filter(date__lt=today).order_by("-date"),
            "event_photos": EventPhoto.objects.filter(is_published=True),
        },
    )
