from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(PendingGame)
admin.site.register(Game)
admin.site.register(System)
admin.site.register(SystemInstance)
