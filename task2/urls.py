from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include('blogging.urls')),
    path("blogging/",include('blogging.urls')),
    path(r'media/(?P<path>.*)', serve,{'document_root': settings.MEDIA_ROOT}),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)