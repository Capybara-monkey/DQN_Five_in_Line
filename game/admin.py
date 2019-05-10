from django.contrib import admin
from .models import Table, PlayNum, Memory, StateAction, Epsilon, C

# Register your models here.

admin.site.register(Table)
admin.site.register(PlayNum)
admin.site.register(Memory)
admin.site.register(StateAction)
admin.site.register(Epsilon)
admin.site.register(C)
