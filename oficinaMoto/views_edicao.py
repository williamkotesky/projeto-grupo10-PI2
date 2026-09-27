from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from .forms import ClienteForm, MotoForm, EditarOrdemServicoForm
from .models import Cliente, Moto, OrdemServico


@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id_cliente=cliente_id,
    )

    if request.method == "POST":
        form = ClienteForm(request.POST)

        if form.is_valid():
            cliente.nome = form.cleaned_data["nome"]
            cliente.numero_celular = form.cleaned_data["numero_celular"]
            cliente.save()

            return redirect("atendimento")

    else:
        form = ClienteForm(
            initial={
                "nome": cliente.nome,
                "numero_celular": cliente.numero_celular,
            }
        )

    return render(
        request,
        "editar_cliente.html",
        {
            "form": form,
            "cliente": cliente,
        },
    )


@login_required
def editar_moto(request, moto_id):
    moto = get_object_or_404(
        Moto,
        id_moto=moto_id,
    )

    if request.method == "POST":
        form = MotoForm(request.POST)

        if form.is_valid():
            moto.placa = form.cleaned_data["placa"]
            moto.marca = form.cleaned_data["marca"]
            moto.modelo = form.cleaned_data["modelo"]
            moto.save()

            return redirect("atendimento")

    else:
        form = MotoForm(
            initial={
                "placa": moto.placa,
                "marca": moto.marca,
                "modelo": moto.modelo,
            }
        )

    return render(
        request,
        "editar_moto.html",
        {
            "form": form,
            "moto": moto,
        },
    )

@login_required
def editar_ordem(request, ordem_id):
    ordem = get_object_or_404(
        OrdemServico,
        id_ordem=ordem_id,
    )

    if request.method == "POST":
        form = EditarOrdemServicoForm(request.POST)

        if form.is_valid():
            custo_pecas = form.cleaned_data["custo_pecas"]
            custo_servico = form.cleaned_data["custo_servico"]
            status_novo = form.cleaned_data["status_ordem"]

            custos_nao_informados = (
                custo_pecas is None and custo_servico is None
            )

            if (
                status_novo in [
                    OrdemServico.Status.FINALIZADA,
                    OrdemServico.Status.CANCELADA,
                ]
                and custos_nao_informados
            ):
                form.add_error(
                    None,
                    "Não é possível encerrar ou cancelar a ordem "
                    "sem informar pelo menos um dos custos.",
                )
            else:
                if custo_pecas is not None and custo_servico is None:
                    custo_servico = 0

                elif custo_pecas is None and custo_servico is not None:
                    custo_pecas = 0

                status_anterior = ordem.status_ordem

                ordem.descricao = form.cleaned_data["descricao"]
                ordem.custo_pecas = custo_pecas
                ordem.custo_servico = custo_servico
                ordem.status_ordem = status_novo

                if status_novo == OrdemServico.Status.EM_ANDAMENTO:
                    ordem.data_fechamento = None

                elif status_novo in [
                    OrdemServico.Status.FINALIZADA,
                    OrdemServico.Status.CANCELADA,
                ]:
                    if (
                        status_anterior != status_novo
                        or ordem.data_fechamento is None
                    ):
                        ordem.data_fechamento = timezone.now()

                ordem.save()

                messages.success(
                    request,
                    "Ordem de serviço atualizada com sucesso."
                )
                
                return redirect("editar_ordem", ordem_id=ordem.id_ordem)
    else:
        form = EditarOrdemServicoForm(
            initial={
                "descricao": ordem.descricao,
                "custo_pecas": ordem.custo_pecas,
                "custo_servico": ordem.custo_servico,
                "status_ordem": ordem.status_ordem,
            }
        )

    return render(
        request,
        "editar_ordem.html",
        {
            "form": form,
            "ordem": ordem,
        },
    )