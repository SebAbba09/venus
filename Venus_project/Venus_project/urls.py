from django.contrib import admin
from django.urls import path, include
from mfa.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Venus.urls')),
    path('mfa/', include('mfa.urls')),


]
