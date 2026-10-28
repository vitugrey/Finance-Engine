"""
Gerador de dados de demonstração para o GreyWorks Finance (Portfólio & Demo Interativa).
Popula ativos, histórico de aportes, dividendos, fluxo de caixa e checklist profissional,
sem qualquer dado pessoal.
"""

from datetime import date, timedelta
from decimal import Decimal

from budget.models import Category as BudgetCategory
from budget.models import ChecklistItem, FinancialSettings
from budget.models import Transaction as BudgetTransaction
from investments.models import Asset, Dividend
from investments.models import Category as InvestCategory
from investments.models import Transaction as InvestTransaction


def ensure_default_checklist():
    """Cria itens padrão profissionais do checklist caso não existam."""
    if ChecklistItem.objects.exists():
        return
    defaults = [
        (1, "Consolidar receitas do mês e revisar fluxo de caixa", ChecklistItem.TagType.REVISAO, True, 1),
        (2, "Executar aporte mensal seguindo o rebalanceamento de classes", ChecklistItem.TagType.APORTE, True, 2),
        (5, "Importar extrato mensal da B3 e conferir proventos creditados", ChecklistItem.TagType.REVISAO, True, 3),
        (7, "Liquidar despesas fixas essenciais (Moradia, Energia, Internet)", ChecklistItem.TagType.CONTAS, False, 4),
        (10, "Auditar e pagar fatura consolidada do cartão de crédito", ChecklistItem.TagType.CARTAO, False, 5),
        (15, "Reforçar reserva de liquidez / oportunidade em Renda Fixa", ChecklistItem.TagType.APORTE, False, 6),
        (25, "Avaliar eficiência de poupança mensal e desvios de orçamento", ChecklistItem.TagType.REVISAO, False, 7),
    ]
    for day, title, tag, done, order in defaults:
        ChecklistItem.objects.create(
            day_of_month=day,
            title=title,
            category_tag=tag,
            is_completed=done,
            order=order,
        )


def reset_and_seed_demo():
    """Limpa o banco local e popula um conjunto completo de dados de demonstração."""
    InvestTransaction.objects.all().delete()
    Dividend.objects.all().delete()
    Asset.objects.all().delete()
    InvestCategory.objects.all().delete()

    BudgetTransaction.objects.all().delete()
    BudgetCategory.objects.all().delete()
    ChecklistItem.objects.all().delete()
    FinancialSettings.objects.all().delete()

    # 1. Configurações Padrão
    FinancialSettings.objects.create(
        profile_name="Portfólio Demonstrativo GreyWorks",
        patrimony_target=Decimal("150000.00"),
        contribution_target=Decimal("3500.00"),
        emergency_fund_target=Decimal("24000.00"),
        passive_income_target=Decimal("4500.00"),
        benchmark_annual_rate=Decimal("11.25"),
        simulator_monthly_rate=Decimal("0.95"),
        target_stocks_pct=Decimal("25.0"),
        target_fiis_pct=Decimal("25.0"),
        target_fixed_income_pct=Decimal("25.0"),
        target_global_pct=Decimal("25.0"),
    )

    ensure_default_checklist()

    # 2. Categorias de Investimento
    cat_acoes = InvestCategory.objects.create(name="Ações", description="Ações listadas na B3")
    cat_fiis = InvestCategory.objects.create(name="Fundos Imobiliários", description="FIIs de tijolo e papel")
    cat_rf = InvestCategory.objects.create(name="Renda Fixa", description="Tesouro Direto e CDBs de liquidez")
    cat_etf = InvestCategory.objects.create(name="ETFs & Global", description="Índices internacionais e Cripto")

    # 3. Ativos da Carteira Demo
    assets_spec = [
        ("WEGE3", "WEG S.A.", cat_acoes, Asset.AssetType.STOCK, Decimal("52.80")),
        ("ITUB4", "ITAÚ UNIBANCO HOLDING S.A.", cat_acoes, Asset.AssetType.STOCK, Decimal("36.40")),
        ("BBAS3", "BANCO DO BRASIL S.A.", cat_acoes, Asset.AssetType.STOCK, Decimal("28.90")),
        ("EGIE3", "ENGIE BRASIL ENERGIA S.A.", cat_acoes, Asset.AssetType.STOCK, Decimal("43.50")),
        ("HGLG11", "CSHG LOGÍSTICA FII", cat_fiis, Asset.AssetType.FII, Decimal("161.50")),
        ("XPML11", "XP MALLS FII", cat_fiis, Asset.AssetType.FII, Decimal("112.40")),
        ("KNCR11", "KINEA RENDIMENTOS IMOBILIÁRIOS FII", cat_fiis, Asset.AssetType.FII, Decimal("104.80")),
        ("MXRF11", "MAXI RENDA FII", cat_fiis, Asset.AssetType.FII, Decimal("10.15")),
        ("SELIC29", "Tesouro Selic 2029 (Liquidez)", cat_rf, Asset.AssetType.FIXED_INCOME, Decimal("15420.00")),
        ("CDB_LIQ", "CDB Liquidez Diária (110% CDI)", cat_rf, Asset.AssetType.FIXED_INCOME, Decimal("12800.00")),
        ("IVVB11", "ISHARES S&P 500 ETF", cat_etf, Asset.AssetType.ETF, Decimal("345.00")),
        ("BTC", "Bitcoin Core (Self-Custody)", cat_etf, Asset.AssetType.CRYPTO, Decimal("410000.00")),
    ]

    asset_objs = {}
    for ticker, name, cat, atype, curr_price in assets_spec:
        asset_objs[ticker] = Asset.objects.create(
            ticker=ticker,
            name=name,
            category=cat,
            asset_type=atype,
            current_price=curr_price,
            is_active=True,
        )

    today = date.today()

    def months_ago_date(m_ago: int, day: int = 10) -> date:
        y = today.year
        m = today.month - m_ago
        while m <= 0:
            m += 12
            y -= 1
        return date(y, m, min(day, 28))

    # 4. Histórico de Compras (Construindo evolução patrimonial em ~18 meses)
    operations = [
        (18, "SELIC29", Decimal("0.5"), Decimal("13800.00"), "B3"),
        (17, "ITUB4", Decimal("200"), Decimal("30.20"), "B3"),
        (16, "HGLG11", Decimal("45"), Decimal("155.00"), "B3"),
        (15, "WEGE3", Decimal("150"), Decimal("39.80"), "B3"),
        (14, "IVVB11", Decimal("25"), Decimal("290.00"), "B3"),
        (13, "XPML11", Decimal("65"), Decimal("106.50"), "B3"),
        (12, "SELIC29", Decimal("0.5"), Decimal("14400.00"), "B3"),
        (11, "BBAS3", Decimal("250"), Decimal("26.10"), "B3"),
        (10, "KNCR11", Decimal("70"), Decimal("101.20"), "B3"),
        (9, "CDB_LIQ", Decimal("1.0"), Decimal("12000.00"), "Manual"),
        (8, "EGIE3", Decimal("120"), Decimal("40.50"), "B3"),
        (7, "MXRF11", Decimal("500"), Decimal("9.95"), "B3"),
        (6, "IVVB11", Decimal("20"), Decimal("315.00"), "B3"),
        (5, "BTC", Decimal("0.025"), Decimal("340000.00"), "Manual"),
        (4, "WEGE3", Decimal("80"), Decimal("46.50"), "B3"),
        (3, "HGLG11", Decimal("30"), Decimal("158.00"), "B3"),
        (2, "ITUB4", Decimal("120"), Decimal("34.10"), "B3"),
        (1, "XPML11", Decimal("35"), Decimal("110.00"), "B3"),
        (0, "BBAS3", Decimal("100"), Decimal("28.10"), "B3"),
    ]

    for m_ago, ticker, qty, price, broker in operations:
        src = InvestTransaction.Source.MANUAL if broker == "Manual" else InvestTransaction.Source.B3_IMPORT
        InvestTransaction.objects.create(
            asset=asset_objs[ticker],
            transaction_type=InvestTransaction.TransactionType.BUY,
            quantity=qty,
            price=price,
            total_value=(qty * price).quantize(Decimal("0.01")),
            date=months_ago_date(m_ago, 12),
            broker=broker,
            source=src,
            notes="Lançamento demonstrativo GreyWorks",
        )

    # 5. Proventos Mensais (Últimos 14 meses)
    div_payers = [
        ("HGLG11", Dividend.DividendType.INCOME, Decimal("1.10"), Decimal("75")),
        ("XPML11", Dividend.DividendType.INCOME, Decimal("0.92"), Decimal("100")),
        ("KNCR11", Dividend.DividendType.INCOME, Decimal("1.05"), Decimal("70")),
        ("MXRF11", Dividend.DividendType.INCOME, Decimal("0.10"), Decimal("500")),
        ("ITUB4", Dividend.DividendType.JCP, Decimal("0.25"), Decimal("320")),
        ("BBAS3", Dividend.DividendType.DIVIDEND, Decimal("0.42"), Decimal("350")),
        ("EGIE3", Dividend.DividendType.DIVIDEND, Decimal("0.55"), Decimal("120")),
        ("WEGE3", Dividend.DividendType.DIVIDEND, Decimal("0.18"), Decimal("230")),
    ]

    for m_ago in range(13, -1, -1):
        pay_date = months_ago_date(m_ago, 15)
        for idx, (ticker, dtype, vpu, qty_ref) in enumerate(div_payers):
            # Ações pagam trimestralmente/semestralmente, FIIs todos os meses
            if dtype != Dividend.DividendType.INCOME and (m_ago + idx) % 2 != 0:
                continue
            factor = Decimal("1.0") + (Decimal(str((13 - m_ago) * 0.015)))
            total_val = (vpu * qty_ref * factor).quantize(Decimal("0.01"))
            Dividend.objects.create(
                asset=asset_objs[ticker],
                dividend_type=dtype,
                value_per_unit=vpu,
                total_value=total_val,
                payment_date=pay_date,
            )

    # 6. Categorias e Transações da Carteira (Orçamento dos últimos 6 meses)
    bcat_salario = BudgetCategory.objects.create(name="Salário", description="Remuneração principal recorrente")
    bcat_consultoria = BudgetCategory.objects.create(name="Projetos & Consultoria", description="Receitas extras e dividendos")
    bcat_moradia = BudgetCategory.objects.create(name="Moradia & Contas", description="Aluguel, condomínio, energia e fibra")
    bcat_alimentacao = BudgetCategory.objects.create(name="Alimentação", description="Supermercado e restaurantes")
    bcat_transporte = BudgetCategory.objects.create(name="Mobilidade", description="Combustível, manutenção e apps")
    bcat_software = BudgetCategory.objects.create(name="Assinaturas & Cloud", description="Servidores, SaaS e ferramentas")
    bcat_lazer = BudgetCategory.objects.create(name="Lazer & Saúde", description="Academia, saúde e bem-estar")

    for m_ago in range(5, -1, -1):
        # Receitas
        BudgetTransaction.objects.create(
            description="Receita Principal Mensal",
            value=Decimal("9500.00"),
            category=bcat_salario,
            date=months_ago_date(m_ago, 2),
            is_credit=False,
            is_fixed_income=True,
            transaction_type=BudgetTransaction.TransactionType.INCOME,
        )
        extra_val = Decimal("1800.00") + Decimal(str((5 - m_ago) * 250))
        BudgetTransaction.objects.create(
            description="Projeto Engenharia de Dados / Consultoria",
            value=extra_val,
            category=bcat_consultoria,
            date=months_ago_date(m_ago, 14),
            is_credit=False,
            is_fixed_income=False,
            transaction_type=BudgetTransaction.TransactionType.INCOME,
        )

        # Despesas
        expenses_template = [
            ("Moradia, Condomínio & Energia", Decimal("2650.00"), bcat_moradia, False, True, 5),
            ("Supermercado & Empório", Decimal("1420.00") + Decimal(str((m_ago % 3) * 90)), bcat_alimentacao, True, False, 10),
            ("Infraestrutura Cloud & Licenças Tech", Decimal("380.00"), bcat_software, True, True, 12),
            ("Combustível & Mobilidade Urbana", Decimal("640.00"), bcat_transporte, True, False, 16),
            ("Academia, Saúde & Performance", Decimal("520.00"), bcat_lazer, False, True, 18),
            ("Restaurantes & Networking", Decimal("690.00"), bcat_alimentacao, True, False, 22),
        ]
        for desc, val, cat, is_cred, is_fix, day in expenses_template:
            BudgetTransaction.objects.create(
                description=desc,
                value=val,
                category=cat,
                date=months_ago_date(m_ago, day),
                is_credit=is_cred,
                is_fixed_expense=is_fix,
                transaction_type=BudgetTransaction.TransactionType.EXPENSE,
            )

