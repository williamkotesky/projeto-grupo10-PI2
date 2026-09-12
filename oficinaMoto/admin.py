from django.contrib import admin
from .models import Cliente, Moto, OrdemServico


admin.site.register(Cliente)
admin.site.register(Moto)
#admin.site.register(OrdemServico)

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        "id_ordem",
        "cliente",
        "moto",
        "status_ordem",
        "data_abertura",
        "codigo_acesso",
    )