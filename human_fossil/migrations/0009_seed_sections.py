from decimal import Decimal

from django.db import migrations

HERO_CONTENT = (
    "A breath taking story about the remnants of civilization trying to survive as "
    "their planet runs out of breathable oxygen. Join characters Saesh and Yen on "
    "their perilous journey to salvage resources to make life underground better "
    "and fight for the future!"
)

SECTIONS = [
    {
        "key": "hero",
        "title": "Human Fossil Project",
        "subtitle": "Original story, manga, and animation by Reb",
        "content": HERO_CONTENT,
    },
    {"key": "characters", "title": "Characters"},
    {
        "key": "animation",
        "title": "Animation",
        "subtitle": "Watch Trailer",
        "content": "Watch the award winning full animated film now",
        "action": "Watch now",
    },
    {"key": "manga", "title": "Manga"},
    {
        "key": "manga_callout",
        "content": (
            "Enjoying the preview? Get your own digital copy to experience the full "
            "story and support this project"
        ),
        "action": "Buy the Manga",
        "price": Decimal("25.99"),
    },
    {"key": "illustrations", "title": "Illustrations"},
    {
        "key": "art_book_callout",
        "content": "Enjoy the art? Get the art book and explore the lore.",
        "action": "Buy the Art Book",
        "price": Decimal("32.00"),
    },
    {
        "key": "events",
        "title": "Events",
        "content": "Placeholder booth blurb for the owner to replace",
    },
]


def seed(apps, schema_editor):
    """Create missing Sections only; never overwrite owner edits."""
    Section = apps.get_model("human_fossil", "Section")
    for fields in SECTIONS:
        Section.objects.get_or_create(key=fields["key"], defaults=fields)


class Migration(migrations.Migration):
    dependencies = [("human_fossil", "0008_section_animationaward")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
