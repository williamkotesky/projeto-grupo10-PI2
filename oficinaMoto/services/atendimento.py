import re
from django.db.models import QuerySet
from ..models import Cliente, Moto

def identificar_tipo_busca(valor):
    valor = valor.strip()

    valor_limpo = re.sub(r"[\s().-]", "", valor)

    if valor_limpo.isdigit() and len(valor_limpo) in (10, 11):
        return "celular", valor_limpo

    if re.fullmatch(r"[A-Za-z]{3}[0-9][A-Za-z0-9][0-9]{2}", valor_limpo):
        return "placa", valor_limpo.upper()

    return None, valor_limpo

def buscar_por_celular(celular):
    return Cliente.objects.filter(numero_celular=celular).first()


def buscar_por_placa(placa):
    return Moto.objects.select_related("cliente").filter(placa=placa).first()

def buscar_motos_do_cliente(cliente):
    return Moto.objects.filter(cliente=cliente)