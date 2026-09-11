from django.db import models


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
        decimal_places=2
    )
    custo_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    data_abertura = models.DateTimeField()
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
        unique=True
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