# Oficina MP Motos 🏍️

Sistema web para gerenciamento de ordens de serviço de uma oficina de motos, Projeto de Integração II, grupo 10 da UNIVESP. A aplicação permite organizar clientes, motos e serviços, facilitando o acompanhamento dos atendimentos e a consulta do andamento dos reparos.

## Funcionalidades

- **Autenticação:** acesso à área administrativa por meio de login.
- **Gerenciamento de clientes:** cadastro, consulta e edição dos dados dos clientes.
- **Gerenciamento de motos:** cadastro e edição das motos vinculadas aos respectivos clientes, incluindo placa, marca e modelo.
- **Ordens de serviço:** criação, consulta e edição de ordens de serviço vinculadas a clientes e motos.
- **Controle de status:** acompanhamento das ordens nos estados *Em andamento*, *Cancelada* e *Finalizada*.
- **Controle de custos:** registro dos custos de peças e serviços, com cálculo do valor total da ordem.
- **Histórico de atendimento:** visualização das ordens de serviço cadastradas, incluindo datas de abertura e fechamento.
- **Consulta por placa:** consulta da ordem de serviço segundo a placa informada.
- **Consulta por filtros:** consulta de ordens de serviço usando filtros diversos.
- **Consulta pública:** consulta do status e das informações da ordem de serviço por meio de um código de acesso, sem necessidade de login.
- **Integração com a API FIPE:** consulta de marcas e modelos de motos para auxiliar no preenchimento dos dados.
- **Interface responsiva e acessível:** utilização de componentes adaptáveis a diferentes tamanhos de tela, navegação por teclado, identificação de campos e recursos de acessibilidade.
- **Tamanho da fonte na pagina pública:** configuração do tamanho da fonte na Home do site, por razões de acessibilidade.

## Tecnologias utilizadas

- **Python 3.13** — linguagem de programação principal.
- **Django 6.1** — framework web responsável pela lógica de negócio, rotas, autenticação, modelos e integração com o banco de dados.
- **SQLite** — banco de dados relacional para armazenamento de clientes, motos, ordens de serviço e usuários.
- **HTML5** — estrutura das páginas.
- **CSS3** — estilização da interface.
- **Bootstrap 5.3** — componentes visuais e responsividade.
- **JavaScript** — funcionalidades e interações no lado do cliente.
- **Requests** — comunicação HTTP com a API FIPE.
- **Git e GitHub** — versionamento e gerenciamento do código-fonte.
- **PythonAnywhere** — hospedagem da aplicação web.

## Hospedagem

O sistema está publicado no PythonAnywhere. A disponibilidade da aplicação depende das condições do plano gratuito de hospedagem. A consulta da API FIPE depende da disponibilidade da API e das permissões de rede da hospedagem gratuíta.

## Projeto

O projeto aplica conceitos de desenvolvimento web com framework, persistência de dados, integração com API externa, versionamento de código, testes, acessibilidade e hospedagem em nuvem, reunindo esses recursos em uma aplicação voltada a uma necessidade real de gerenciamento de uma oficina de motos.
