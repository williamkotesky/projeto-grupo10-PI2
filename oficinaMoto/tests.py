from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch
import requests

from .forms import ClienteForm, MotoForm, OrdemServicoForm
from .models import Cliente, Moto, OrdemServico

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

        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

    def test_usuario_nao_autenticado_e_redirecionado_para_login(self):
        self.client.logout()
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

    def test_celular_inexistente_exibe_opcao_de_cadastrar_cliente(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )
    
        response = self.client.post(
            reverse("atendimento"),
            {
                "busca": "11988887777",
            }
        )
    
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cadastrar novo cliente"
        )

    def test_opcao_novo_cliente_redireciona_para_cadastro(self):
        self.client.login(
            username="funcionario",
            password="senha-teste",
        )
    
        response = self.client.post(
            reverse("atendimento"),
            {
                "acao": "novo_cliente",
                "celular": "11988887777",
            }
        )
    
        self.assertRedirects(
            response,
            reverse("criar_cliente")
        )

    def test_busca_por_placa_inexistente_exibe_formulario_de_cliente(self):
        response = self.client.post(
            reverse("atendimento"),
            {
                "busca": "ZZZ9Z99",
            }
        )
    
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Nenhuma moto encontrada para esta placa."
        )
        self.assertContains(
            response,
            "Informe o celular do cliente"
        )

    def test_placa_inexistente_cliente_existente_redireciona_para_nova_moto(self):
        cliente = Cliente.objects.create(
            nome="Maria da Silva",
            numero_celular="11988887777",
        )
    
        response = self.client.post(
            reverse("atendimento"),
            {
                "acao": "buscar_cliente_para_nova_moto",
                "celular": "11988887777",
            }
        )
    
        self.assertRedirects(
            response,
            reverse(
                "criar_moto",
                kwargs={"cliente_id": cliente.id_cliente},
            )
        )

    def test_placa_inexistente_cliente_nao_cadastrado_redireciona_para_novo_cliente(self):
        response = self.client.post(
            reverse("atendimento"),
            {
                "acao": "buscar_cliente_para_nova_moto",
                "celular": "11977776666",
            }
        )
    
        self.assertRedirects(
            response,
            "/clientes/novo/?celular=11977776666",
        )

    def test_novo_cliente_preenche_celular_recebido_por_parametro(self):
        response = self.client.get(
            reverse("criar_cliente"),
            {
                "celular": "11977776666",
            }
        )
    
        self.assertEqual(response.status_code, 200)
    
        self.assertContains(
            response,
            'value="11977776666"'
        )

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

class MotoFormTest(TestCase):

    def test_placa_valida_formato_antigo(self):
        form = MotoForm(data={
            "placa": "ABC-1234",
            "marca": "Honda",
            "modelo": "CG 160",
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["placa"], "ABC1234")

    def test_placa_valida_formato_mercosul(self):
        form = MotoForm(data={
            "placa": "ABC-1D23",
            "marca": "Honda",
            "modelo": "CG 160",
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["placa"], "ABC1D23")

    def test_placa_converte_para_maiusculas(self):
        form = MotoForm(data={
            "placa": "abc-1234",
            "marca": "Honda",
            "modelo": "CG 160",
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["placa"], "ABC1234")

    def test_placa_invalida(self):
        form = MotoForm(data={
            "placa": "ABC123",
            "marca": "Honda",
            "modelo": "CG 160",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("placa", form.errors)

    def test_placa_vazia(self):
        form = MotoForm(data={
            "placa": "",
            "marca": "Honda",
            "modelo": "CG 160",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("placa", form.errors)

class FipeServiceTest(TestCase):

    @patch("oficinaMoto.services.fipe.requests.get")
    def test_buscar_marcas(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"code": "1", "name": "Honda"},
            {"code": "2", "name": "Yamaha"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        resultado = buscar_marcas()

        self.assertEqual(
            resultado,
            [
                {"code": "1", "name": "Honda"},
                {"code": "2", "name": "Yamaha"},
            ],
        )

        mock_get.assert_called_once_with(
            "https://fipe.parallelum.com.br/api/v2/motorcycles/brands",
            timeout=10,
        )

    @patch("oficinaMoto.services.fipe.requests.get")
    def test_buscar_modelos(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"code": "123", "name": "CG 160"},
            {"code": "456", "name": "CB 500"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        resultado = buscar_modelos("1")

        self.assertEqual(
            resultado,
            [
                {"code": "123", "name": "CG 160"},
                {"code": "456", "name": "CB 500"},
            ],
        )

        mock_get.assert_called_once_with(
            "https://fipe.parallelum.com.br/api/v2/motorcycles/brands/1/models",
            timeout=10,
        )

    @patch("oficinaMoto.services.fipe.requests.get")
    def test_buscar_anos(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"code": "2025-1", "name": "2025"},
            {"code": "2024-1", "name": "2024"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        resultado = buscar_anos("1", "123")

        self.assertEqual(
            resultado,
            [
                {"code": "2025-1", "name": "2025"},
                {"code": "2024-1", "name": "2024"},
            ],
        )

        mock_get.assert_called_once_with(
            "https://fipe.parallelum.com.br/api/v2/motorcycles/brands/1/models/123/years",
            timeout=10,
        )

    @patch("oficinaMoto.services.fipe.requests.get")
    def test_buscar_preco(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "price": "R$ 18.500,00",
            "brand": "Honda",
            "model": "CG 160",
            "modelYear": 2025,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        resultado = buscar_preco("1", "123", "2025-1")

        self.assertEqual(
            resultado,
            {
                "price": "R$ 18.500,00",
                "brand": "Honda",
                "model": "CG 160",
                "modelYear": 2025,
            },
        )

        mock_get.assert_called_once_with(
            "https://fipe.parallelum.com.br/api/v2/motorcycles/brands/1/models/123/years/2025-1",
            timeout=10,
        )

class FipeViewTest(TestCase):
    def setUp(self):
            self.usuario = User.objects.create_user(
                username="teste",
                password="123456",
            )
            self.client.login(
                username="teste",
                password="123456",
            )
    
    @patch("oficinaMoto.views.buscar_marcas")
    def test_fipe_marcas_retorna_json(self, mock_buscar_marcas):
        mock_buscar_marcas.return_value = [
            {"code": "1", "name": "Honda"},
            {"code": "2", "name": "Yamaha"},
        ]

        response = self.client.get(
            reverse("fipe_marcas")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"code": "1", "name": "Honda"},
                {"code": "2", "name": "Yamaha"},
            ],
        )

    @patch("oficinaMoto.views.buscar_modelos")
    def test_fipe_modelos_retorna_json(self, mock_buscar_modelos):
        mock_buscar_modelos.return_value = [
            {"code": "123", "name": "CG 160"},
            {"code": "456", "name": "CB 500"},
        ]

        response = self.client.get(
            reverse(
                "fipe_modelos",
                kwargs={"brand_id": "1"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"code": "123", "name": "CG 160"},
                {"code": "456", "name": "CB 500"},
            ],
        )

        mock_buscar_modelos.assert_called_once_with("1")

    @patch("oficinaMoto.views.buscar_anos")
    def test_fipe_anos_retorna_json(self, mock_buscar_anos):
        mock_buscar_anos.return_value = [
            {"code": "2025-1", "name": "2025"},
            {"code": "2024-1", "name": "2024"},
        ]

        response = self.client.get(
            reverse(
                "fipe_anos",
                kwargs={
                    "brand_id": "1",
                    "model_id": "123",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"code": "2025-1", "name": "2025"},
                {"code": "2024-1", "name": "2024"},
            ],
        )

        mock_buscar_anos.assert_called_once_with("1", "123")

    @patch("oficinaMoto.views.buscar_preco")
    def test_fipe_preco_retorna_json(self, mock_buscar_preco):
        mock_buscar_preco.return_value = {
            "price": "R$ 18.500,00",
            "brand": "Honda",
            "model": "CG 160",
            "modelYear": 2025,
        }

        response = self.client.get(
            reverse(
                "fipe_preco",
                kwargs={
                    "brand_id": "1",
                    "model_id": "123",
                    "year_id": "2025-1",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "price": "R$ 18.500,00",
                "brand": "Honda",
                "model": "CG 160",
                "modelYear": 2025,
            },
        )

        mock_buscar_preco.assert_called_once_with(
            "1",
            "123",
            "2025-1",
        )

    @patch("oficinaMoto.views.buscar_marcas")
    def test_fipe_marcas_indisponivel_retorna_503(
        self,
        mock_buscar_marcas,
    ):
        mock_buscar_marcas.side_effect = requests.RequestException

        response = self.client.get(
            reverse("fipe_marcas")
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"erro": "Não foi possível consultar a FIPE."},
        )

    def test_fipe_marcas_exige_login(self):
        self.client.logout()
    
        response = self.client.get(reverse("fipe_marcas"))
    
        self.assertRedirects(
            response,
            "/login/?next=/fipe/marcas/",
        )

    @patch("oficinaMoto.views.buscar_marcas")
    def test_fipe_marcas_retorna_erro_quando_fipe_falha(self, mock_buscar_marcas):
        mock_buscar_marcas.side_effect = requests.RequestException
    
        response = self.client.get(
            reverse("fipe_marcas")
        )
    
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"erro": "Não foi possível consultar a FIPE."},
        )

    @patch("oficinaMoto.views.buscar_modelos")
    def test_fipe_modelos_retorna_erro_quando_fipe_falha(self, mock_buscar_modelos):
        mock_buscar_modelos.side_effect = requests.RequestException
    
        response = self.client.get(
            reverse("fipe_modelos", args=["1"])
        )
    
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"erro": "Não foi possível consultar os modelos na FIPE."},
        )

    @patch("oficinaMoto.views.buscar_anos")
    def test_fipe_anos_retorna_erro_quando_fipe_falha(self, mock_buscar_anos):
        mock_buscar_anos.side_effect = requests.RequestException
    
        response = self.client.get(
            reverse("fipe_anos", args=["1", "2"])
        )
    
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"erro": "Não foi possível consultar os anos na FIPE."},
        )

    @patch("oficinaMoto.views.buscar_preco")
    def test_fipe_preco_retorna_erro_quando_fipe_falha(self, mock_buscar_preco):
        mock_buscar_preco.side_effect = requests.RequestException
    
        response = self.client.get(
            reverse("fipe_preco", args=["1", "2", "3"])
        )
    
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"erro": "Não foi possível consultar o preço na FIPE."},
        )

class ClienteFormTest(TestCase):

    def test_cliente_form_valido(self):
        form = ClienteForm(data={
            "nome": "João da Silva",
            "numero_celular": "12999999999",
        })

        self.assertTrue(form.is_valid())

    def test_nome_obrigatorio(self):
        form = ClienteForm(data={
            "nome": "",
            "numero_celular": "12999999999",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_nome_muito_curto(self):
        form = ClienteForm(data={
            "nome": "A",
            "numero_celular": "12999999999",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_nome_muito_longo(self):
        form = ClienteForm(data={
            "nome": "A" * 101,
            "numero_celular": "12999999999",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_celular_obrigatorio(self):
        form = ClienteForm(data={
            "nome": "João da Silva",
            "numero_celular": "",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("numero_celular", form.errors)

class CriarClienteViewTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="funcionario",
            password="senha-teste",
        )

        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

    def test_usuario_nao_autenticado_e_redirecionado(self):
        self.client.logout()

        response = self.client.get(
            reverse("criar_cliente")
        )

        self.assertRedirects(
            response,
            "/login/?next=/clientes/novo/"
        )

    def test_tela_de_cadastro_exibe_formulario(self):
        response = self.client.get(
            reverse("criar_cliente")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cadastrar cliente")
        self.assertContains(response, "Nome")
        self.assertContains(response, "Celular")

    def test_cadastrar_cliente_com_dados_validos(self):
        response = self.client.post(
            reverse("criar_cliente"),
            {
                "nome": "João da Silva",
                "numero_celular": "12999999999",
            }
        )

        cliente = Cliente.objects.get()

        self.assertRedirects(
            response,
            reverse(
                "criar_moto",
                kwargs={"cliente_id": cliente.id_cliente},
            )
        )

        self.assertEqual(
            cliente.nome,
            "João da Silva"
        )

        self.assertEqual(
            cliente.numero_celular,
            "12999999999"
        )

    def test_cadastrar_cliente_com_nome_vazio(self):
        response = self.client.post(
            reverse("criar_cliente"),
            {
                "nome": "",
                "numero_celular": "12999999999",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Cliente.objects.count(),
            0
        )

        self.assertContains(
            response,
            "Este campo é obrigatório."
        )

    def test_cadastrar_cliente_com_celular_vazio(self):
        response = self.client.post(
            reverse("criar_cliente"),
            {
                "nome": "João da Silva",
                "numero_celular": "",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Cliente.objects.count(),
            0
        )

        self.assertContains(
            response,
            "Este campo é obrigatório."
        )

class EdicaoClienteMotoViewTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="funcionario",
            password="senha-teste",
        )

        self.cliente = Cliente.objects.create(
            nome="João da Silva",
            numero_celular="12999999999",
        )

        self.moto = Moto.objects.create(
            placa="ABC1D23",
            marca="Honda",
            modelo="CG 160",
            cliente=self.cliente,
        )

        self.client.login(
            username="funcionario",
            password="senha-teste",
        )

    def test_editar_cliente_carrega_dados(self):
        response = self.client.get(
            reverse(
                "editar_cliente",
                kwargs={"cliente_id": self.cliente.id_cliente},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial["nome"],
            "João da Silva",
        )
        self.assertEqual(
            response.context["form"].initial["numero_celular"],
            "12999999999",
        )

    def test_editar_cliente_atualiza_dados(self):
        response = self.client.post(
            reverse(
                "editar_cliente",
                kwargs={"cliente_id": self.cliente.id_cliente},
            ),
            {
                "nome": "João Atualizado",
                "numero_celular": "11988887777",
            },
        )

        self.assertRedirects(
            response,
            reverse("atendimento"),
        )

        self.cliente.refresh_from_db()

        self.assertEqual(
            self.cliente.nome,
            "João Atualizado",
        )
        self.assertEqual(
            self.cliente.numero_celular,
            "11988887777",
        )

    def test_editar_moto_carrega_dados(self):
        response = self.client.get(
            reverse(
                "editar_moto",
                kwargs={"moto_id": self.moto.id_moto},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial["placa"],
            "ABC1D23",
        )
        self.assertEqual(
            response.context["form"].initial["marca"],
            "Honda",
        )
        self.assertEqual(
            response.context["form"].initial["modelo"],
            "CG 160",
        )

    def test_editar_moto_atualiza_dados(self):
        response = self.client.post(
            reverse(
                "editar_moto",
                kwargs={"moto_id": self.moto.id_moto},
            ),
            {
                "placa": "DEF4G56",
                "marca": "Yamaha",
                "modelo": "Fazer 250",
            },
        )

        self.assertRedirects(
            response,
            reverse("atendimento"),
        )

        self.moto.refresh_from_db()

        self.assertEqual(
            self.moto.placa,
            "DEF4G56",
        )
        self.assertEqual(
            self.moto.marca,
            "Yamaha",
        )
        self.assertEqual(
            self.moto.modelo,
            "Fazer 250",
        )