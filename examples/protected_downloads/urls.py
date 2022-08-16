from django.urls import include, re_path, path

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^', include('protected_downloads.download.urls')),
]
