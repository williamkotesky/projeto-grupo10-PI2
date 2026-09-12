from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Moto, OrdemServico
from .services.atendimento import (
    identificar_tipo_busca,
    buscar_por_celular,
    buscar_por_placa,
    buscar_motos_do_cliente,
)


class AtendimentoServiceTest(TestCase):

    def test_identificar_celular_com_11_digitos(self):
        tipo, valor = identificar_tipo_busca("12999999999")

        self.assertEqual(tipo, "celular")
        self.assertEqual(valor, "12999999999")

    def test_identificar_celular_formatado(self):
        tipo, valor = identificar_tipo_busca("(12) 99999-9999")

        self.assertEqual(tipo, "celular")
        self.assertEqual(valor, "12999999999")

    def test_identificar_placa(self):
        tipo, valor = identificar_tipo_busca("ABC1D23")

        self.assertEqual(tipo, "placa")
        self.assertEqual(valor, "ABC1D23")

    def test_identificar_placa_formatada(self):
        tipo, valor = identificar_tipo_busca("ABC-1234")

        self.assertEqual(tipo, "placa")
        self.assertEqual(valor, "ABC1234")

    def test_busca_invalida(self):
        tipo, valor = identificar_tipo_busca("123")

        self.assertIsNone(tipo)
        self.assertEqual(valor, "123")

    def test_busca_por_celular_encontra_cliente(self):
        cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        resultado = buscar_por_celular("12999999999")

        self.assertEqual(resultado, cliente)

    def test_busca_por_celular_nao_encontra_cliente(self):
        resultado = buscar_por_celular("12999999999")

        self.assertIsNone(resultado)

    def test_busca_por_placa_encontra_moto(self):
        cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        moto = Moto.objects.create(
            placa="ABC1D23",
            marca="Honda",
            modelo="CG 160",
            cliente=cliente,
        )

        resultado = buscar_por_placa("ABC1D23")

        self.assertEqual(resultado, moto)
        self.assertEqual(resultado.cliente, cliente)

    def test_busca_por_placa_nao_encontra_moto(self):
        resultado = buscar_por_placa("ABC1D23")

        self.assertIsNone(resultado)

    def test_busca_motos_do_cliente(self):
        cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        moto1 = Moto.objects.create(
            placa="ABC1D23",
            marca="Honda",
            modelo="CG 160",
            cliente=cliente,
        )

        moto2 = Moto.objects.create(
            placa="XYZ9A87",
            marca="Yamaha",
            modelo="Fazer",
            cliente=cliente,
        )

        motos = buscar_motos_do_cliente(cliente)

        self.assertEqual(motos.count(), 2)
        self.assertIn(moto1, motos)
        self.assertIn(moto2, motos)

    def test_busca_motos_de_cliente_sem_motos(self):
        cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        motos = buscar_motos_do_cliente(cliente)

        self.assertEqual(motos.count(), 0)


class AtendimentoViewTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="funcionario",
            password="senha-teste",
        )

        self.cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        self.moto1 = Moto.objects.create(
            placa="ABC1D23",
            marca="Honda",
            modelo="CG 160",
            cliente=self.cliente,
        )

        self.moto2 = Moto.objects.create(
            placa="XYZ9A87",
            marca="Yamaha",
            modelo="Fazer",
            cliente=self.cliente,
        )

    def test_usuario_nao_autenticado_e_redirecionado_para_login(self):
        response = self.client.get(
            reverse("atendimento")
        )

        self.assertRedirects(
            response,
            "/login/?next=/atendimento/"
        )

    def test_usuario_autenticado_pode_acessar_atendimento(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

        response = self.client.get(
            reverse("atendimento")
        )

        self.assertEqual(response.status_code, 200)

    def test_busca_por_celular_retorna_cliente_e_motos(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

        response = self.client.post(
            reverse("atendimento"),
            {"busca": "12999999999"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tipo_busca"], "celular")
        self.assertEqual(response.context["valor_busca"], "12999999999")
        self.assertEqual(response.context["cliente"], self.cliente)

        motos = response.context["motos"]

        self.assertEqual(motos.count(), 2)
        self.assertIn(self.moto1, motos)
        self.assertIn(self.moto2, motos)

    def test_busca_por_placa_retorna_moto(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

        response = self.client.post(
            reverse("atendimento"),
            {"busca": "ABC1D23"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tipo_busca"], "placa")
        self.assertEqual(response.context["valor_busca"], "ABC1D23")
        self.assertEqual(response.context["moto"], self.moto1)

    def test_busca_por_celular_inexistente(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

        response = self.client.post(
            reverse("atendimento"),
            {"busca": "11988887777"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["cliente"])

    def test_busca_por_placa_inexistente(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

        response = self.client.post(
            reverse("atendimento"),
            {"busca": "ZZZ9Z99"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["moto"])


class CriarOrdemViewTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="funcionario",
            password="senha-teste"
        )

        self.cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999"
        )

        self.moto = Moto.objects.create(
            placa="ABC1234",
            marca="Honda",
            modelo="CG 160",
            cliente=self.cliente
        )

        self.client.login(
            username="funcionario",
            password="senha-teste"
        )

    def test_usuario_nao_autenticado_e_redirecionado(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            )
        )

        self.assertRedirects(
            response,
            f"/login/?next=/ordem/nova/{self.moto.id_moto}/"
        )

    def test_tela_de_criacao_exibe_dados_da_moto(self):
        response = self.client.get(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "João da Silva")
        self.assertContains(response, "Honda")
        self.assertContains(response, "CG 160")
        self.assertContains(response, "ABC1234")

    def test_criar_ordem_com_descricao_valida(self):
        response = self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": "Moto apresenta dificuldade para dar partida."
            }
        )

        ordem = OrdemServico.objects.get()

        self.assertRedirects(
            response,
            reverse(
                "ordem_criada",
                kwargs={"ordem_id": ordem.id_ordem}
            )
        )

        self.assertEqual(
            ordem.descricao,
            "Moto apresenta dificuldade para dar partida."
        )

        self.assertEqual(
            ordem.cliente,
            self.cliente
        )

        self.assertEqual(
            ordem.moto,
            self.moto
        )

    def test_ordem_criada_inicia_em_andamento(self):
        self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": "Troca de óleo e revisão."
            }
        )

        ordem = OrdemServico.objects.get()

        self.assertEqual(
            ordem.status_ordem,
            OrdemServico.Status.EM_ANDAMENTO
        )

    def test_ordem_criada_recebe_data_de_abertura(self):
        self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": "Problema no sistema de freios."
            }
        )

        ordem = OrdemServico.objects.get()

        self.assertIsNotNone(
            ordem.data_abertura
        )

    def test_ordem_criada_recebe_codigo_de_acesso(self):
        self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": "Motor apresentando ruído."
            }
        )

        ordem = OrdemServico.objects.get()

        self.assertEqual(
            len(ordem.codigo_acesso),
            8
        )

        self.assertTrue(
            ordem.codigo_acesso.isalnum()
        )

        self.assertTrue(
            ordem.codigo_acesso.isupper()
        )

    def test_descricao_vazia_e_rejeitada(self):
        response = self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": ""
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            OrdemServico.objects.count(),
            0
        )
        self.assertContains(
            response,
            "Este campo é obrigatório."
        )

    def test_descricao_muito_curta_e_rejeitada(self):
        response = self.client.post(
            reverse(
                "criar_ordem",
                kwargs={"moto_id": self.moto.id_moto}
            ),
            {
                "descricao": "abc"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            OrdemServico.objects.count(),
            0
        )

    def test_ordem_criada_exibe_dados_da_ordem(self):
        ordem = OrdemServico.objects.create(
            descricao="Revisão completa da motocicleta.",
            cliente=self.cliente,
            moto=self.moto
        )

        response = self.client.get(
            reverse(
                "ordem_criada",
                kwargs={"ordem_id": ordem.id_ordem}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(ordem.id_ordem))
        self.assertContains(response, ordem.codigo_acesso)
        self.assertContains(response, "Em andamento")
        self.assertContains(
            response,
            "Revisão completa da motocicleta."
        )
        self.assertContains(response, "Honda")
        self.assertContains(response, "CG 160")
        self.assertContains(response, "ABC1234")
        self.assertContains(response, "João da Silva")