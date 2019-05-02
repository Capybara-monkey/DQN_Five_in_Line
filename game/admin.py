from django.contrib import admin
from .models import Table, PlayNum, Memory, StateAction

# Register your models here.

admin.site.register(Table)
admin.site.register(PlayNum)
admin.site.register(Memory)
admin.site.register(StateAction)