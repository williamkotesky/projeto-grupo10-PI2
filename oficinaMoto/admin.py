from django.contrib import admin
from .models import Cliente, Moto, OrdemServico


admin.site.register(Cliente)
admin.site.register(Moto)
admin.site.register(OrdemServico)