import secrets
import string

from django.db import models

def gerar_codigo_acesso():
    caracteres = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(caracteres)
        for _ in range(8)
    )

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    numero_celular = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Moto(models.Model):
    id_moto = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=100)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT
    )
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"


class OrdemServico(models.Model):

    class Status(models.TextChoices):
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CANCELADA = "cancelada", "Cancelada"
        FINALIZADA = "finalizada", "Finalizada"

    id_ordem = models.AutoField(primary_key=True)

    descricao = models.TextField()

    custo_pecas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    custo_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    data_abertura = models.DateTimeField(
        auto_now_add=True
    )

    data_fechamento = models.DateTimeField(
        null=True,
        blank=True
    )

    status_ordem = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EM_ANDAMENTO
    )

    codigo_acesso = models.CharField(
        max_length=8,
        unique=True,
        default=gerar_codigo_acesso
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT
    )

    moto = models.ForeignKey(
        Moto,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"OS #{self.id_ordem}"