from django.contrib import admin
from .models import Rant

# Register your models here.
@admin.register(Rant)
class RantAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
