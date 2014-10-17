from django.contrib import admin

from .models import Download


class DownloadAdmin(admin.ModelAdmin):
    list_display = ['title', 'file']

admin.site.register(Download, DownloadAdmin)
