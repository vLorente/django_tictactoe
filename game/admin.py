from django.contrib import admin
from .models import Player, Game, Move

# Register your models here.

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Move)
