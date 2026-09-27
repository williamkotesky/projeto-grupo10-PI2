from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, F, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render

from .models import OrdemServico

@login_required
def buscar_ordem_por_placa(request):
    ordens = None
    placa = ""

    if request.method == "GET":
        placa = request.GET.get("placa", "").strip().upper()
        placa = placa.replace("-", "").replace(" ", "")

        if placa:
            ordens = OrdemServico.objects.select_related(
                "cliente",
                "moto",
            ).filter(
                moto__placa=placa
            ).order_by("-data_abertura")

    return render(
        request,
        "buscar_ordem_placa.html",
        {
            "ordens": ordens,
            "placa": placa,
        },
    )

def ordens_com_total():
    return (
        OrdemServico.objects
        .select_related("cliente", "moto")
        .annotate(
            total_custo=(
                Coalesce(
                    F("custo_pecas"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
                +
                Coalesce(
                    F("custo_servico"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
        )
    )


@login_required
def ultimas_ordens(request):
    ordens = (
        ordens_com_total()
        .order_by("-data_abertura")[:10]
    )

    return render(
        request,
        "ultimas_ordens.html",
        {"ordens": ordens},
    )


@login_required
def buscar_ordem_por_placa(request):
    ordens = None
    placa_buscada = ""

    if request.method == "GET":
        placa_buscada = request.GET.get("placa", "").strip().upper()
        placa_buscada = placa_buscada.replace("-", "").replace(" ", "")

        if placa_buscada:
            ordens = (
                ordens_com_total()
                .filter(moto__placa=placa_buscada)
                .order_by("-data_abertura")
            )

    return render(
        request,
        "buscar_ordem_placa.html",
        {
            "ordens": ordens,
            "placa_buscada": placa_buscada,
        },
    )


@login_required
def buscar_ordens_filtros(request):
    ordens = None

    data_abertura = request.GET.get("data_abertura", "")
    status = request.GET.get("status", "")
    quantidade = request.GET.get("quantidade", "10")
    ordem = request.GET.get("ordem", "desc")

    quantidades_validas = [10, 20, 50, 100]

    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        quantidade = 10

    if quantidade not in quantidades_validas:
        quantidade = 10

    if request.GET:
        ordens = ordens_com_total()

        if data_abertura:
            ordens = ordens.filter(
                data_abertura__date=data_abertura
            )

        if status:
            ordens = ordens.filter(
                status_ordem=status
            )

        if ordem == "asc":
            ordens = ordens.order_by("data_abertura")
        else:
            ordens = ordens.order_by("-data_abertura")

        ordens = ordens[:quantidade]

    return render(
        request,
        "buscar_ordens_filtros.html",
        {
            "ordens": ordens,
            "data_abertura": data_abertura,
            "status": status,
            "quantidade": quantidade,
            "ordem": ordem,
            "status_choices": OrdemServico.Status.choices,
        },
    )