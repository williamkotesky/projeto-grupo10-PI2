from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AtendimentoViewTest(TestCase):

    def test_usuario_nao_autenticado_e_redirecionado_para_login(self):
        response = self.client.get(
            reverse("atendimento")
        )

        self.assertRedirects(
            response,
            "/login/?next=/atendimento/"
        )

    def test_usuario_autenticado_pode_acessar_atendimento(self):
        User.objects.create_user(
            username="funcionario",
            password="senha-teste"
        )

        self.client.login(
            username="funcionario",
            password="senha-teste"
        )

        response = self.client.get(
            reverse("atendimento")
        )

        self.assertEqual(response.status_code, 200)
