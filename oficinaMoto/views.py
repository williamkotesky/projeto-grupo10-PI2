from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrdemServicoForm
from .models import Moto, OrdemServico
from .services.atendimento import (
    identificar_tipo_busca,
    buscar_por_celular,
    buscar_por_placa,
    buscar_motos_do_cliente,
)


def home(request):
    return render(request, "home.html")


@login_required
def atendimento(request):
    contexto = {}

    if request.method == "POST":

        acao = request.POST.get("acao")

        if acao == "selecionar_moto":
            #contexto["moto_id"] = request.POST.get("moto_id")
            #contexto["cliente_id"] = request.POST.get("cliente_id")
            moto_id = request.POST.get("moto_id")

            return redirect("criar_ordem", moto_id=moto_id)

        elif acao == "nova_moto":
            contexto["cliente_id"] = request.POST.get("cliente_id")

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