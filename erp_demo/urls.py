 
# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin 
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('erp.urls')),
    path('i18n/', include('django.conf.urls.i18n')),   
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
