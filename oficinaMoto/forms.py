from django import forms


class OrdemServicoForm(forms.Form):
    descricao = forms.CharField(
        label="Descrição do problema",
        min_length=5,
        max_length=1000,
        required=True,
        error_messages={
            "required": "Este campo é obrigatório.",
            "min_length": "A descrição deve possuir pelo menos 5 caracteres.",
            "max_length": "A descrição deve possuir no máximo 1000 caracteres.",
        },
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Descreva o problema apresentado pela moto...",
                "required": True,
                "minlength": 5,
                "maxlength": 1000,
            }
        ),
    )