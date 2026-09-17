from django import forms
import re


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


class MotoForm(forms.Form):
    placa = forms.CharField(
        label="Placa",
        max_length=10,
        required=True,
        error_messages={
            "required": "A placa é obrigatória.",
            "max_length": "A placa deve possuir no máximo 10 caracteres.",
        },
        widget=forms.TextInput(
            attrs={
                "placeholder": "ABC-1234 ou ABC-1D23",
                "required": True,
                "maxlength": 8,
                "pattern": r"^[A-Za-z]{3}-?[0-9][A-Za-z0-9][0-9]{2}$",
                "title": "Informe uma placa válida, como ABC-1234 ou ABC-1D23.",
            }
        ),
    )

    def clean_placa(self):
        placa = self.cleaned_data["placa"]
    
        placa = placa.strip().upper().replace("-", "").replace(" ", "")
    
        if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa):
            raise forms.ValidationError(
                "Informe uma placa válida no formato ABC1234 ou ABC1D23."
            )
    
        return placa

    marca = forms.CharField(
        label="Marca",
        max_length=50,
        required=True,
        error_messages={
            "required": "A marca é obrigatória.",
            "max_length": "A marca deve possuir no máximo 50 caracteres.",
        },
        widget=forms.TextInput(
            attrs={
                "placeholder": "Digite a marca da moto",
                "required": True,
                "maxlength": 50,
            }
        ),
    )

    modelo = forms.CharField(
        label="Modelo",
        max_length=100,
        required=True,
        error_messages={
            "required": "O modelo é obrigatório.",
            "max_length": "O modelo deve possuir no máximo 100 caracteres.",
        },
        widget=forms.TextInput(
            attrs={
                "placeholder": "Digite o modelo da moto",
                "required": True,
                "maxlength": 100,
            }
        ),
    )