from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ClienteForm, MotoForm
from .models import Cliente, Moto


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ClienteForm, MotoForm
from .models import Cliente, Moto


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