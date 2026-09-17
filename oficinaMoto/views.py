from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests

from .forms import OrdemServicoForm, MotoForm
from .models import Moto, OrdemServico, Cliente

from .services.atendimento import (
    identificar_tipo_busca,
    buscar_por_celular,
    buscar_por_placa,
    buscar_motos_do_cliente,
)

from .services.fipe import (
    buscar_marcas,
    buscar_modelos,
    buscar_anos,
    buscar_preco,
)


def home(request):
    return render(request, "home.html")

@login_required
def fipe_marcas(request):
    try:
        marcas = buscar_marcas()
        return JsonResponse(marcas, safe=False)
    except requests.RequestException:
        return JsonResponse(
            {"erro": "Não foi possível consultar a FIPE."},
            status=503,
        )


@login_required
def fipe_modelos(request, brand_id):
    try:
        modelos = buscar_modelos(brand_id)
        return JsonResponse(modelos, safe=False)
    except requests.RequestException:
        return JsonResponse(
            {"erro": "Não foi possível consultar os modelos na FIPE."},
            status=503,
        )


@login_required
def fipe_anos(request, brand_id, model_id):
    try:
        anos = buscar_anos(brand_id, model_id)
        return JsonResponse(anos, safe=False)
    except requests.RequestException:
        return JsonResponse(
            {"erro": "Não foi possível consultar os anos na FIPE."},
            status=503,
        )


@login_required
def fipe_preco(request, brand_id, model_id, year_id):
    try:
        resultado = buscar_preco(
            brand_id,
            model_id,
            year_id,
        )
        return JsonResponse(resultado)
    except requests.RequestException:
        return JsonResponse(
            {"erro": "Não foi possível consultar o preço na FIPE."},
            status=503,
        )

@login_required
def atendimento(request):
    contexto = {}

    if request.method == "POST":

        acao = request.POST.get("acao")

        if acao == "selecionar_moto":
            
            moto_id = request.POST.get("moto_id")

            return redirect("criar_ordem", moto_id=moto_id)

        elif acao == "nova_moto":
            cliente_id = request.POST.get("cliente_id")
        
            return redirect(
                "criar_moto",
                cliente_id=cliente_id,
            )

        else:
            busca = request.POST.get("busca", "")

            tipo, valor = identificar_tipo_busca(busca)

            contexto["tipo_busca"] = tipo
            contexto["valor_busca"] = valor

            if tipo == "celular":
                cliente = buscar_por_celular(valor)
                contexto["cliente"] = cliente

                if cliente:
                    contexto["motos"] = buscar_motos_do_cliente(cliente)

            elif tipo == "placa":
                moto = buscar_por_placa(valor)
                contexto["moto"] = moto

    return render(request, "atendimento.html", contexto)

@login_required
def criar_ordem(request, moto_id):
    moto = get_object_or_404(
        Moto.objects.select_related("cliente"),
        id_moto=moto_id,
    )

    if request.method == "POST":
        form = OrdemServicoForm(request.POST)

        if form.is_valid():
            ordem = OrdemServico.objects.create(
                descricao=form.cleaned_data["descricao"],
                cliente=moto.cliente,
                moto=moto,
            )

            return redirect(
                "ordem_criada",
                ordem_id=ordem.id_ordem,
            )
    else:
        form = OrdemServicoForm()

    return render(
        request,
        "criar_ordem.html",
        {
            "form": form,
            "moto": moto,
        },
    )
@login_required
def ordem_criada(request, ordem_id):
    ordem = get_object_or_404(
        OrdemServico.objects.select_related("cliente", "moto"),
        id_ordem=ordem_id,
    )

    return render(
        request,
        "ordem_criada.html",
        {"ordem": ordem},
    )

@login_required
def criar_moto(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id_cliente=cliente_id,
    )

    if request.method == "POST":
        form = MotoForm(request.POST)

        if form.is_valid():
            moto = Moto.objects.create(
                placa=form.cleaned_data["placa"],
                marca=form.cleaned_data["marca"],
                modelo=form.cleaned_data["modelo"],
                cliente=cliente,
            )

            return redirect(
                "criar_ordem",
                moto_id=moto.id_moto,
            )
    else:
        form = MotoForm()

    return render(
        request,
        "criar_moto.html",
        {
            "form": form,
            "cliente": cliente,
        },
    )