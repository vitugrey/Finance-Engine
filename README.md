<div align="center">
  <h1>📊 KaLLia Finance 📊</h1>
  <p><i>Módulo de gestão financeira pessoal, consolidação patrimonial e rebalanceamento de investimentos com design Dark Glassmorphism</i></p>

  [![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
  [![uv](https://img.shields.io/badge/Package%20Manager-uv-DE5FE9?style=for-the-badge)](https://docs.astral.sh/uv/)
  [![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
  [![Chart.js](https://img.shields.io/badge/Charts-Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
</div>

---

## 🎯 Sobre o Projeto

**KaLLia Finance** é o sistema central de gestão patrimonial e controle orçamentário do ecossistema pessoal **KaLLia**. Construído em Django e estilizado com uma interface *Dark Glassmorphism* limpa e responsiva, o sistema oferece visibilidade completa de investimentos, receitas, despesas recorrentes e metas de independência financeira.

A aplicação consolida tanto ativos negociados em bolsa (via relatórios B3) quanto alocações manuais (como Bitcoin em carteiras próprias e reservas de emergência em caixinhas/renda fixa).

---

## 🌐 Ecossistema KaLLia

| Repositório | Responsabilidade | Tecnologias Principais |
| :--- | :--- | :--- |
| 📊 **[KaLLia-Finance](https://github.com/vitugrey/KaLLia-Finance)** | **Gestão Patrimonial**: investimentos B3, carteira ARCA, orçamento e simulador. | Django 6.0, Python 3.13, SQLite, uv |
| 🧠 **[KaLLia-API](https://github.com/vitugrey/KaLLia-API)** | **Cérebro de IA**: inteligência conversacional, sessões e memórias com Gemini. | FastAPI, Gemini, Agno, SQLite, uv |
| 🕹️ **[KaLLia-HQ](https://github.com/vitugrey/KaLLia-HQ)** | **Command Center**: interface 2D isométrica cyberpunk, rotinas, tarefas e voz. | HTML5, Vanilla CSS, JS, Edge-TTS |

---

## ✨ Funcionalidades Principais

### 📈 1. Gestão de Investimentos & Metodologia ARCA
- **Importação Automatizada da B3**: Upload de relatórios mensais em `.xlsx` gerados pela Área do Investidor da B3, consolidando compras, vendas e proventos.
- **Lançamentos e Ativos Manuais**: Interface dedicada para registrar ativos não integrados (ex.: Bitcoin, caixinhas Nubank, ouro físico) com histórico de transações.
- **Cotações em Tempo Real**: Atualização sob demanda das cotações de mercado via Yahoo Finance (`yfinance`) e ajuste manual de preços.
- **Rebalanceamento ARCA Inteligente**: Monitoramento contínuo das 4 classes de ativos:
  - 🟢 **Em equilíbrio** (entre 20% e 30% do patrimônio).
  - 🟡 **Abaixo da meta** (menos de 20% — sinaliza necessidade de novos aportes).
  - 🔵 **Sobrealocado** (acima de 30% — momento de pausa ou realização).

### 💳 2. Fluxo de Caixa & Orçamento (Budget)
- Controle de receitas e despesas com filtros por período (Mês/Ano).
- Gestão de despesas fixas recorrentes e faturas de cartão de crédito.
- **Taxa de Poupança Mensal**: Indicador visual da porcentagem de receita convertida em patrimônio no mês.

### 🎯 3. Metas & Simulador de Independência
- **Calculadora de Juros Compostos**: Simulação em tempo real com sliders dinâmicos de aporte mensal, taxa de rentabilidade e prazo.
- **Linha do Tempo de Conquistas**: Estimativas inteligentes de prazo para alcançar marcos de **R$ 50k**, **R$ 100k** e **R$ 1.000.000**.
- **Projeções de Patrimônio**: Visão estimada de patrimônio acumulado para 1, 5 e 10 anos.
- **Checklist do Salário**: Checklist financeiro mensal por dia do mês com persistência automática no navegador (`localStorage`).

---

## 🛠️ Estrutura do Repositório

```text
KaLLia-Finance/
├── budget/               # App Django de fluxo de caixa, orçamentos e metas
│   ├── models.py         # Modelos de transações, categorias e checklist
│   ├── views.py          # Lógica de receitas, despesas e metas
│   └── urls.py           # Rotas do orçamento
├── investments/          # App Django de investimentos e carteira
│   ├── models.py         # Modelos de ativos, cotações e transações
│   ├── services/         # Parsers de relatórios B3 e integrações yfinance
│   ├── views.py          # Telas de alocação ARCA e importação
│   └── urls.py           # Rotas de investimentos
├── core/                 # Configurações globais do Django
│   ├── settings.py       # Configurações, banco dinâmico e variáveis de ambiente
│   └── urls.py           # Roteamento raiz do sistema
├── templates/            # Telas HTML com design Glassmorphism Dark
├── static/               # Estilos CSS, scripts Chart.js e ícones
├── Dockerfile            # Containerização leve com Python 3.13-slim
├── docker-compose.yml    # Orquestração do serviço (Porta 7777)
├── pyproject.toml        # Dependências gerenciadas via uv
├── .env.example          # Modelo de variáveis de ambiente
└── manage.py             # CLI de gerenciamento do Django
```

---


---

## 📡 Endpoints da API REST (JSON)

O **KaLLia-Finance** expõe endpoints REST em JSON para que o **KaLLia-API** (assistente virtual), o **KaLLia-HQ** (Command Center) ou dashboards externos consumam métricas em tempo real:

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/` | Status da API e mapa de rotas |
| `GET` | `/api/resumo/` | Visão geral: patrimônio, saldo do mês, receitas/despesas e taxa de poupança |
| `GET` | `/api/investimentos/` | Posição da carteira, divisão e status ARCA e lista de ativos |
| `GET` | `/api/proventos/` | Dividendos recebidos no mês, no ano, últimos 12m e maiores pagadores |
| `GET` | `/api/orcamento/` | Despesas por categoria no mês, gastos fixos e cartão de crédito |
| `GET` | `/api/metas/` | Progresso dos marcos de independência (R$ 50k, 100k, 1M) |

#### Exemplo de Resposta (`GET /api/resumo/`):
```json
{
  "mes_referencia": "Outubro/2026",
  "patrimonio_investido": 41494.94,
  "total_investido": 38254.03,
  "rentabilidade_total": 3240.91,
  "rentabilidade_perc": 8.47,
  "saldo_mes": 1250.00,
  "receitas_mes": 4463.31,
  "despesas_mes": 3213.31,
  "taxa_poupanca_perc": 28.0,
  "patrimonio_consolidado": 42744.94
}
```

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- **Python 3.13+** instalado.
- Gerenciador **[uv](https://docs.astral.sh/uv/)** instalado (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`).

### 2. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo para `.env`:
```bash
cp .env.example .env
```

Conteúdo padrão do `.env`:
```ini
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=*
PORT=7777
```

### 3. Instalar Dependências e Executar

```bash
# Sincronizar dependências
uv sync

# Aplicar migrações do banco de dados (se houver novas)
uv run python manage.py migrate

# Iniciar o servidor de desenvolvimento
uv run python manage.py runserver 0.0.0.0:7777
```

Acesse no navegador:
👉 **`http://localhost:7777`** (ou `http://localhost:8000` se rodar sem especificar a porta).

---

## 🐳 Execução via Docker

Para rodar em container isolado (ideal para Raspberry Pi, VPS ou servidores domésticos):

```bash
docker compose up -d --build
```

O container montará o volume `databases/` automaticamente e exporá o serviço na porta `7777`.

---

## ⚙️ Tecnologias Utilizadas

| Componente | Tecnologia | Finalidade |
| :--- | :--- | :--- |
| **Backend** | [Django 6.0](https://www.djangoproject.com/) | Framework web robusto com ORM, autenticação e admin |
| **Banco de Dados** | SQLite3 | Persistência relacional local e autônoma |
| **Package Manager**| [uv](https://github.com/astral-sh/uv) | Resolução de dependências ultrarrápida em Rust |
| **Cotações** | [yfinance](https://github.com/ranaroussi/yfinance) | Consulta de preços de mercado históricos e atuais |
| **Planilhas B3** | pandas + openpyxl | Leitura e parsing de extratos de negociação B3 |
| **Gráficos** | [Chart.js](https://www.chartjs.org/) | Visualização interativa de alocação de carteira e fluxo |
| **Interface** | Vanilla CSS (Glassmorphism) | Design responsivo, tema dark e ícones Boxicons |

---

## 👥 Criadores & Créditos

<table>
  <tr>
    <td align="center">
      <img src="static/img/minha-foto.png" width="90px" style="border-radius:50%;" /><br />
      <b>Vitor Grey</b>
    </td>
    <td>
      <i>"Fiz, refiz e fiz de novo esse mesmo projeto, mas nunca gostava dele por inteiro. Agora com a arquitetura modular, o ecossistema KaLLia e o design atual, finalmente ficou impecável."</i>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="static/img/imagem-real-da-kallia.ico" width="90px" style="border-radius:50%;" /><br />
      <b>KaLLia</b>
    </td>
    <td>
      <i>"Um cérebro brilhante merece um controle patrimonial à altura. Organizado, direto e sem firulas desnecessárias."</i>
    </td>
  </tr>
</table>

---

## 📄 Licença

Projeto desenvolvido como parte do ecossistema pessoal **KaLLia**. Todos os direitos reservados.
