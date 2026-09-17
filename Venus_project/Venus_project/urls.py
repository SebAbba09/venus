from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('chat/', include('chat.urls')),
    path('', RedirectView.as_view(pattern_name='users:login', permanent=False)),
]
