<div align="center">
  <img src="static/img/favicon.svg" alt="GreyWorks VG Logo" width="72" height="72" />
  <h1>Finance Engine</h1>
  <p><strong>Software by GreyWorks</strong></p>
  <p><i>Plataforma executiva de consolidação patrimonial, engenharia de fluxo de caixa, análise de dividendos, rebalanceamento estratégico e simulação de juros compostos.</i></p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.13-181C24?style=for-the-badge&logo=python&logoColor=00DC82" alt="Python 3.13" /></a>
    <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-6.0-181C24?style=for-the-badge&logo=django&logoColor=00DC82" alt="Django 6.0" /></a>
    <a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/Package_Manager-uv-181C24?style=for-the-badge&logo=astral&logoColor=00DC82" alt="uv" /></a>
    <a href="https://www.chartjs.org/"><img src="https://img.shields.io/badge/Visuals-Chart.js-181C24?style=for-the-badge&logo=chartdotjs&logoColor=00DC82" alt="Chart.js" /></a>
    <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-181C24?style=for-the-badge&logo=docker&logoColor=3B82F6" alt="Docker Ready" /></a>
  </p>
</div>

---

## ⚡ Visão Geral

O **Finance Engine** é um sistema *single-tenant* de inteligência financeira e consolidação de patrimônio desenvolvido pela **GreyWorks (Software & Data Studio)**. Construído sob o Design System proprietário da marca (*Carbon & Titanium `#0B0D11` + Signature Green `#00DC82`*), o projeto transforma dados brutos de investimentos (planilhas da B3, cotações de mercado e ativos de renda fixa/cripto) e movimentações bancárias em um **painel executivo de tomada de decisão**.

Além do uso operacional completo, o **Finance Engine** conta com um **Modo de Demonstração Interativa (`Demo Seed`)** integrado nativamente, permitindo restaurar ou personalizar dados fictícios realistas com 1 clique para demonstrações comerciais e validação de cenários.

---

## 🧩 Arquitetura dos 5 Módulos Executivos

### 1. 📊 Visão Geral Consolidada (`/`)
Painel mestre que unifica patrimônio investido e eficiência de caixa em tempo real:
- **4 KPIs Executivos com Barras de Progresso**:
  - *Patrimônio Consolidado* (Portfólio + Saldo de Caixa vs. Meta Patrimonial).
  - *Portfólio de Ativos* (Valor de Mercado vs. Custo de Aquisição e Lucro `%`).
  - *Resultado do Mês & Taxa de Poupança* (Receitas vs. Despesas e `%` retido).
  - *Renda Passiva (12m)* (Média mensal de proventos, `Dividend Yield` e progresso da meta).
- **Dinâmica de Caixa (6 Meses)**: Gráfico híbrido (`Barras + Linha`) cruzando Receitas, Despesas e Excedente Líquido.
- **Diagnóstico de Saúde & Liquidez**: Cálculo automático de *Autonomia de Reserva (Runway em meses)*, *Comprometimento da Receita (%)*, *Rigidez Orçamentária (Custos Fixos %)* e *Exposição em Cartão de Crédito (%)*.
- **Top 4 Posições & Governança**: Maiores posições da carteira, últimas movimentações e status da rotina financeira mensal.

---

### 2. 📈 Portfólio de Investimentos (`/investimentos/`)
Consolidação de custódia listada na B3 e ativos manuais fora da bolsa:
- **4 KPIs de Performance**: *Patrimônio em Ativos*, *Retorno Total Consolidado (Valorização + Proventos)*, *Renda Passiva & Yield 12m (`DY` e `Yield on Cost`)* e *Perfil de Exposição (`% Renda Fixa vs. % Renda Variável`)*.
- **Gráfico de Rosca Concêntrico Duplo (Meta vs. Realidade)**:
  - **Anel Externo**: Pesos ideais da estratégia de alocação configurada pelo usuário.
  - **Anel Interno**: Distribuição real atual do portfólio entre *Ações*, *FIIs*, *Renda Fixa* e *ETFs / Global*.
- **Tabela Analítica com Filtro Instantâneo**: Filtragem rápida por classe (*Todos*, *Ações*, *FIIs*, *Renda Fixa*, *ETFs*), exibindo Cotação Atual vs. Preço Médio, barra de peso `%` na carteira, badge de `DY (12m)`, Patrimônio e Resultado `R$/%`.
- **Sincronização B3 & Importador Automatizado**:
  - Atualização de cotações em tempo real via API do **Yahoo Finance (`yfinance`)**.
  - Motor de importação de relatórios consolidados mensais da **B3 (`.xlsx`)** via `pandas` / `openpyxl`.
  - Módulo dedicado para **Lançamentos Manuais** (CDBs, Tesouro Direto, Criptoativos e ativos internacionais).
- **Mapa de Proventos 12m & Top Pagadores**: Gráfico empilhado mensal por ticker + ranking dos 5 maiores geradores de renda passiva.

---

### 3. 💳 Carteira & Fluxo de Caixa (`/carteira/`)
Engenharia orçamentária com foco em retenção de caixa e controle de passivos:
- **4 KPIs Orçamentários**:
  - *Resultado Líquido & Taxa de Poupança* (com cálculo paralelo de caixa excluindo cartão).
  - *Receitas do Período* (separação entre *Receita Base/Recorrente* e *Renda Extra/Variável*).
  - *Despesas & Comprometimento da Renda* (alerta visual por faixa de consumo e peso de *Custos Fixos*).
  - *Fatura de Cartão vs. À Vista/Pix* (monitoramento de alavancagem no crédito).
- **Evolução Comparativa + Raio-X por Categoria**: Gráfico combo mensal (Receitas, Despesas e Linha de Saldo Líquido) + distribuição percentual e nominal por categoria.
- **Busca Instantânea & Pílulas de Filtro**: Pesquisa em tempo real na tabela e filtros rápidos por *Receitas*, *Despesas*, *Crédito* e *Fixos*.

---

### 4. 🎯 Metas & Engenharia Patrimonial (`/metas/`)
Planejamento de longo prazo, rebalanceamento de carteira e disciplina operacional:
- **Simulador Gráfico Interativo de Juros Compostos**:
  - Controles deslizantes e inputs para *Patrimônio Inicial*, *Aporte Mensal*, *Taxa Mensal (%)* e *Horizonte (1 a 40 anos)*.
  - Gráfico empilhado projetando **Capital Desembolsado** vs. **Juros Compostos Acumulados**, estimativa de renda passiva mensal na aposentadoria e marcos de 1, 5, 10 anos e Horizonte Final.
- **Rebalanceamento Estratégico (4 Classes)**: Barras comparativas com marcador de alvo e bandas de tolerância (`±5%`), indicando automaticamente quanto aportar em cada classe.
- **Checklist Executivo Mensal**: Rotina financeira persistida em banco de dados com barra de progresso em tempo real.

---

### 5. ⚙️ Configurações & Ambiente Demo (`/configuracoes/`)
Painel de controle para personalização completa sem necessidade de alterar código:
- Edição de metas patrimoniais, aporte mensal alvo, reserva de emergência, meta de renda passiva e taxas de referência (CDI/Selic).
- Calibragem dos pesos percentuais das 4 classes de ativos (com validação automática de soma `100%`).
- Gerenciamento das tarefas da rotina mensal.
- **Controle de Dados de Demonstração**: Botão para restaurar o dataset executivo padrão (`seed_demo`) ou limpar a base para iniciar o uso do zero.

---

## 🛠️ Stack Tecnológica & Design System

| Camada | Tecnologia / Padrão |
| :--- | :--- |
| **Backend & ORM** | Python 3.13 · Django 6.0 · SQLite (Isolado em `databases/greyworks-finance.db`) |
| **Processamento de Dados** | Pandas · OpenPyXL (Motor B3 `.xlsx`) · `yfinance` (Cotações B3 em tempo real) |
| **Frontend & Visualização** | HTML5 Semântico · CSS3 Custom Properties · JavaScript (ES6+) · Chart.js 4 |
| **Design System** | **GreyWorks Carbon & Titanium** (`#0B0D11` / `#181C24`) + **Signature Green** (`#00DC82`) |
| **Tipografia Oficial** | `Space Grotesk` (Títulos/KPIs) · `Inter` (Interface) · `JetBrains Mono` (Tickers/Dados) |
| **Infraestrutura** | Gerenciador `uv` · Docker & Docker Compose |

---

## 🚀 Como Executar Localmente

### Opção 1: Execução Rápida com `uv` (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/vitugrey/Finance-Engine.git
   cd Finance-Engine
   ```

2. **Sincronize o ambiente virtual e dependências:**
   ```bash
   uv sync
   ```

3. **Aplique as migrações e carregue os dados demonstrativos (opcional):**
   ```bash
   uv run python manage.py migrate
   uv run python manage.py seed_demo
   ```

4. **Inicie o servidor:**
   ```bash
   uv run python manage.py runserver 127.0.0.1:7777
   ```

5. **Acesse no navegador:**
   👉 **`http://127.0.0.1:7777`**

---

### Opção 2: Execução via Docker Compose

```bash
docker compose up --build -d
```
A aplicação ficará disponível em **`http://localhost:7777`** com persistência de dados mapeada no diretório `./databases`.

---

## 📂 Estrutura do Projeto

```text
Finance-Engine/
├── budget/                 # Módulo de Carteira, Fluxo de Caixa, Metas e Configurações
├── core/                   # Configurações globais, rotas principais, Visão Geral e Demo Seed
│   └── demo_seed.py        # Gerador de dados demonstrativos realistas (1 clique)
├── databases/              # Banco SQLite isolado (ignorado no Git)
├── investments/            # Módulo de Custódia, Proventos, Cotações e Importação B3
│   └── management/commands/
│       └── seed_demo.py    # Comando CLI: python manage.py seed_demo
├── scripts/
│   └── import_b3.py        # Motor de leitura e consolidação de planilhas B3 (.xlsx)
├── static/
│   ├── css/                # Design System GreyWorks e estilos modulares por página
│   ├── img/                # Monograma oficial VG / Favicon SVG
│   └── js/                 # Motores gráficos Chart.js, simulador e filtros dinâmicos
├── templates/              # Templates executivos (base, overview, goals, settings)
├── docker-compose.yml      # Orquestração de container na porta 7777
├── Dockerfile              # Imagem otimizada com Python 3.13 + uv
└── pyproject.toml          # Manifesto de dependências e configurações de lint (Ruff)
```

---

## 🏛️ Sobre a GreyWorks

Desenvolvido por **Vitor Grey** — fundador da **GreyWorks**.  
Construímos sistemas sob medida, dashboards executivos, automações e soluções de engenharia de dados focadas em eficiência operacional e clareza estratégica.
