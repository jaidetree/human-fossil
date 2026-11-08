from django import template

from human_fossil.thumbnails import grid_thumbnail

register = template.Library()
register.simple_tag(grid_thumbnail, name="grid_thumbnail")
