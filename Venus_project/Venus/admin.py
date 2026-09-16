from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import UserContext, UserProfile, CustomUser, Password

# Enregistrement des modèles pour l'interface d'administration
admin.site.register(UserContext)
admin.site.register(UserProfile)
admin.site.register(CustomUser)

admin.site.register(Password)


