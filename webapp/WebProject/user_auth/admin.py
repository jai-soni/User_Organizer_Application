from django.contrib import admin
from .models import *

class NotesModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'user', 'created_on', 'last_updated_on')
admin.site.register(NotesModel, NotesModelAdmin)