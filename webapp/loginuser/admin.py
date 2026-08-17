from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario,Empresa

admin.site.register(Usuario,UserAdmin)
admin.site.register(Empresa)