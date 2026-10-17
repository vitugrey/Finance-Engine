import os
from datetime import date, timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Sum

from investments.models import Asset, Dividend, Transaction as InvestTransaction
from budget.models import Transaction as BudgetTransaction


def _to_float(val) -> float:
    """Converte Decimal para float arredondado a 2 casas decimais."""
    if val is None:
        return 0.0
    return float(round(Decimal(str(val)), 2))


@require_GET
def api_status(request):
    """Retorna o status da API financeira e mapa de rotas disponíveis."""
    return JsonResponse({
        "status": "online",
        "service": "KaLLia-Finance API",
        "version": "1.0.0",
        "endpoints": {
            "resumo": "/api/resumo/",
            "investimentos": "/api/investimentos/",
            "proventos": "/api/proventos/",
            "orcamento": "/api/orcamento/",
            "metas": "/api/metas/",
        }
    })


@require_GET
def api_summary(request):
    """
    Retorna o resumo consolidado de finanças:
    Patrimônio investido, receitas do mês, despesas do mês, saldo e taxa de poupança.
    """
    today = date.today()

    # 1. Investimentos (Patrimônio Total)
    assets = Asset.objects.filter(is_active=True)
    total_patrimony = Decimal('0')
    total_invested = Decimal('0')

    for a in assets:
        qty = a.quantity
        if qty > 0:
            pm = a.average_price
            preco_atual = a.current_price if a.current_price > 0 else pm
            total_patrimony += qty * preco_atual
            total_invested += qty * pm

    # 2. Fluxo de Caixa do Mês Atual
    month_income = BudgetTransaction.objects.filter(
        transaction_type='income',
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0')

    month_expense = BudgetTransaction.objects.filter(
        transaction_type='expense',
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0')

    month_balance = month_income - month_expense
    total_consolidated = total_patrimony + month_balance

    # Taxa de poupança do mês
    savings_pct = Decimal('0')
    if month_income > 0 and month_balance > 0:
        savings_pct = ((month_balance / month_income) * Decimal('100')).quantize(Decimal('0.1'))

    rentabilidade_total = total_patrimony - total_invested
    rentabilidade_pct = ((rentabilidade_total / total_invested) * 100) if total_invested > 0 else Decimal('0')

    months_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    return JsonResponse({
        "mes_referencia": f"{months_pt.get(today.month, '')}/{today.year}",
        "patrimonio_investido": _to_float(total_patrimony),
        "total_investido": _to_float(total_invested),
        "rentabilidade_total": _to_float(rentabilidade_total),
        "rentabilidade_perc": _to_float(rentabilidade_pct),
        "saldo_mes": _to_float(month_balance),
        "receitas_mes": _to_float(month_income),
        "despesas_mes": _to_float(month_expense),
        "taxa_poupanca_perc": _to_float(savings_pct),
        "patrimonio_consolidado": _to_float(total_consolidated),
    })


@require_GET
def api_investments(request):
    """
    Retorna a composição da carteira, alocação por classe (metodologia ARCA)
    e lista detalhada dos ativos em carteira.
    """
    assets = Asset.objects.filter(is_active=True).order_by('asset_type', 'ticker', 'name')

    total_patrimony = Decimal('0')
    total_invested = Decimal('0')
    patrimony_by_type = {}
    ativos_list = []

    for a in assets:
        qty = a.quantity
        if qty > 0:
            pm = a.average_price
            preco_atual = a.current_price if a.current_price > 0 else pm
            patrimonio = qty * preco_atual
            aportado = qty * pm
            rentabilidade = patrimonio - aportado

            total_patrimony += patrimonio
            total_invested += aportado

            type_name = a.get_asset_type_display()
            if type_name not in patrimony_by_type:
                patrimony_by_type[type_name] = Decimal('0')
            patrimony_by_type[type_name] += patrimonio

            ativos_list.append({
                "ticker": a.ticker or a.name,
                "nome": a.name,
                "tipo": type_name,
                "categoria": a.category.name if a.category else "",
                "quantidade": _to_float(qty),
                "preco_medio": _to_float(pm),
                "preco_atual": _to_float(preco_atual),
                "patrimonio": _to_float(patrimonio),
                "total_investido": _to_float(aportado),
                "rentabilidade": _to_float(rentabilidade),
                "rentabilidade_perc": _to_float((rentabilidade / aportado * 100) if aportado > 0 else 0),
            })

    # Alocação por classe
    alocacao = []
    for t_name, t_val in patrimony_by_type.items():
        perc = (t_val / total_patrimony * 100) if total_patrimony > 0 else Decimal('0')
        status = "Equilíbrio"
        if perc < 20:
            status = "Abaixo da meta (Aportar)"
        elif perc > 30:
            status = "Sobrealocado"

        alocacao.append({
            "classe": t_name,
            "valor": _to_float(t_val),
            "porcentagem": _to_float(perc),
            "status": status
        })

    ativos_list.sort(key=lambda x: x["patrimonio"], reverse=True)
    alocacao.sort(key=lambda x: x["valor"], reverse=True)

    rentabilidade_total = total_patrimony - total_invested
    rentabilidade_pct = (rentabilidade_total / total_invested * 100) if total_invested > 0 else Decimal('0')

    return JsonResponse({
        "total_patrimonio": _to_float(total_patrimony),
        "total_investido": _to_float(total_invested),
        "rentabilidade_total": _to_float(rentabilidade_total),
        "rentabilidade_perc": _to_float(rentabilidade_pct),
        "quantidade_ativos": len(ativos_list),
        "alocacao": alocacao,
        "ativos": ativos_list,
    })


@require_GET
def api_dividends(request):
    """
    Retorna estatísticas de proventos e dividendos recebidos:
    Mês atual, ano atual, acumulado últimos 12 meses e média mensal.
    """
    today = date.today()
    cutoff_12m = today - timedelta(days=365)

    month_divs = Dividend.objects.filter(
        payment_date__year=today.year,
        payment_date__month=today.month
    ).aggregate(total=Sum('total_value'))['total'] or Decimal('0')

    year_divs = Dividend.objects.filter(
        payment_date__year=today.year
    ).aggregate(total=Sum('total_value'))['total'] or Decimal('0')

    ttm_divs = Dividend.objects.filter(
        payment_date__gte=cutoff_12m
    ).aggregate(total=Sum('total_value'))['total'] or Decimal('0')

    all_time_divs = Dividend.objects.aggregate(total=Sum('total_value'))['total'] or Decimal('0')

    media_mensal_12m = (ttm_divs / 12) if ttm_divs > 0 else Decimal('0')

    # Top ativos que mais pagaram proventos nos últimos 12 meses
    top_payers = []
    assets = Asset.objects.filter(is_active=True)
    for a in assets:
        div_a = a.ttm_dividends
        if div_a > 0:
            top_payers.append({
                "ticker": a.ticker or a.name,
                "nome": a.name,
                "tipo": a.get_asset_type_display(),
                "total_proventos_12m": _to_float(div_a),
                "media_mensal": _to_float(a.ttm_dividends_monthly),
            })
    top_payers.sort(key=lambda x: x["total_proventos_12m"], reverse=True)

    return JsonResponse({
        "proventos_mes_atual": _to_float(month_divs),
        "proventos_ano_atual": _to_float(year_divs),
        "proventos_ultimos_12m": _to_float(ttm_divs),
        "media_mensal_12m": _to_float(media_mensal_12m),
        "proventos_total_historico": _to_float(all_time_divs),
        "maiores_pagadores_12m": top_payers[:10],
    })


@require_GET
def api_budget(request):
    """
    Retorna o detalhamento do fluxo de caixa e orçamento do mês:
    Receitas, despesas, despesas fixas recorrentes, compras no cartão e gastos por categoria.
    """
    today = date.today()

    transactions = BudgetTransaction.objects.filter(
        date__year=today.year,
        date__month=today.month
    )

    income_total = transactions.filter(transaction_type='income').aggregate(total=Sum('value'))['total'] or Decimal('0')
    expense_total = transactions.filter(transaction_type='expense').aggregate(total=Sum('value'))['total'] or Decimal('0')
    fixed_expense = transactions.filter(transaction_type='expense', is_fixed_expense=True).aggregate(total=Sum('value'))['total'] or Decimal('0')
    credit_expense = transactions.filter(transaction_type='expense', is_credit=True).aggregate(total=Sum('value'))['total'] or Decimal('0')

    # Gastos por categoria
    expenses_by_cat = transactions.filter(transaction_type='expense').values('category__name').annotate(total=Sum('value')).order_by('-total')

    categorias = [
        {
            "categoria": item["category__name"] or "Outros",
            "valor": _to_float(item["total"]),
            "porcentagem": _to_float((item["total"] / expense_total * 100) if expense_total > 0 else 0)
        }
        for item in expenses_by_cat
    ]

    balance = income_total - expense_total

    return JsonResponse({
        "ano": today.year,
        "mes": today.month,
        "receitas_total": _to_float(income_total),
        "despesas_total": _to_float(expense_total),
        "saldo": _to_float(balance),
        "despesas_fixas": _to_float(fixed_expense),
        "despesas_cartao": _to_float(credit_expense),
        "gastos_por_categoria": categorias,
    })


@require_GET
def api_goals(request):
    """
    Retorna o progresso das metas financeiras (R$ 50k, 100k, 1M)
    com base no patrimônio acumulado atual.
    """
    assets = Asset.objects.filter(is_active=True)
    total_patrimony = Decimal('0')
    for a in assets:
        qty = a.quantity
        if qty > 0:
            preco = a.current_price if a.current_price > 0 else a.average_price
            total_patrimony += qty * preco

    marcos_valores = [
        ("R$ 50.000 (Primeiro Marco)", Decimal('50000')),
        ("R$ 100.000 (Mundo dos 6 dígitos)", Decimal('100000')),
        ("R$ 1.000.000 (Independência Financeira)", Decimal('1000000')),
    ]

    metas = []
    for nome, meta_val in marcos_valores:
        atingida = total_patrimony >= meta_val
        progresso = min(Decimal('100'), (total_patrimony / meta_val * Decimal('100'))) if meta_val > 0 else Decimal('0')
        restante = max(Decimal('0'), meta_val - total_patrimony)

        metas.append({
            "meta": nome,
            "valor_alvo": _to_float(meta_val),
            "atingida": atingida,
            "progresso_perc": _to_float(progresso),
            "valor_restante": _to_float(restante),
        })

    return JsonResponse({
        "patrimonio_atual": _to_float(total_patrimony),
        "metas": metas,
    })
