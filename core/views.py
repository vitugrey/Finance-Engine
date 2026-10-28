import json
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from budget.models import Category as BudgetCategory
from budget.models import ChecklistItem, FinancialSettings
from budget.models import Transaction as BudgetTransaction
from investments.models import Asset, Dividend
from investments.models import Transaction as InvestTransaction

from .demo_seed import ensure_default_checklist, reset_and_seed_demo


def _parse_decimal(raw_val, default: Decimal) -> Decimal:
    if raw_val is None:
        return default
    s = str(raw_val).strip()
    if not s:
        return default
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        val = Decimal(s)
        return val if val >= 0 else default
    except (InvalidOperation, ValueError):
        return default


def _calculate_portfolio_totals():
    assets = Asset.objects.filter(is_active=True)
    total_patrimony = Decimal("0")
    total_invested = Decimal("0")
    fixed_income_patrimony = Decimal("0")
    arca_classes = {
        "Ações": Decimal("0"),
        "FIIs": Decimal("0"),
        "Renda Fixa": Decimal("0"),
        "ETFs/Global": Decimal("0"),
    }
    top_assets = []

    for a in assets:
        qty = a.quantity
        if qty > 0:
            pm = a.average_price
            price = a.current_price if a.current_price > 0 else pm
            val = qty * price
            cost = qty * pm
            profit = val - cost
            profit_pct = ((profit / cost) * Decimal("100")).quantize(Decimal("0.1")) if cost > 0 else Decimal("0.0")

            total_patrimony += val
            total_invested += cost

            if a.asset_type in ["stock", "bdr"]:
                arca_classes["Ações"] += val
            elif a.asset_type == "fii":
                arca_classes["FIIs"] += val
            elif a.asset_type == "fixed_income":
                arca_classes["Renda Fixa"] += val
                fixed_income_patrimony += val
            else:
                arca_classes["ETFs/Global"] += val

            top_assets.append(
                {
                    "ticker": a.ticker or a.name,
                    "name": a.name,
                    "type": a.get_asset_type_display(),
                    "patrimony": val,
                    "profit": profit,
                    "profit_pct": profit_pct,
                }
            )

    top_assets.sort(key=lambda x: x["patrimony"], reverse=True)
    return total_patrimony, total_invested, fixed_income_patrimony, arca_classes, top_assets


def overview(request):
    config = FinancialSettings.get_solo()
    ensure_default_checklist()
    total_patrimony, total_invested, fixed_income_patrimony, arca_classes, top_assets = _calculate_portfolio_totals()

    today = date.today()
    month_tx = BudgetTransaction.objects.filter(date__year=today.year, date__month=today.month)

    month_income = month_tx.filter(transaction_type="income").aggregate(total=Sum("value"))["total"] or Decimal("0")
    month_expense = month_tx.filter(transaction_type="expense").aggregate(total=Sum("value"))["total"] or Decimal("0")
    fixed_expenses_month = (
        month_tx.filter(transaction_type="expense", is_fixed_expense=True).aggregate(total=Sum("value"))["total"]
        or Decimal("0")
    )
    credit_expenses_month = (
        month_tx.filter(transaction_type="expense", is_credit=True).aggregate(total=Sum("value"))["total"]
        or Decimal("0")
    )

    month_balance = month_income - month_expense
    total_consolidated = total_patrimony + month_balance

    # Taxas e Eficiência do Mês
    savings_pct = Decimal("0.0")
    if month_income > 0 and month_balance > 0:
        savings_pct = min(Decimal("100.0"), ((month_balance / month_income) * Decimal("100"))).quantize(Decimal("0.1"))

    expense_commitment_pct = Decimal("0.0")
    if month_income > 0:
        expense_commitment_pct = min(Decimal("100.0"), ((month_expense / month_income) * Decimal("100"))).quantize(
            Decimal("0.1")
        )

    fixed_expense_pct = (
        ((fixed_expenses_month / month_expense) * Decimal("100")).quantize(Decimal("0.1"))
        if month_expense > 0
        else Decimal("0.0")
    )
    credit_expense_pct = (
        ((credit_expenses_month / month_expense) * Decimal("100")).quantize(Decimal("0.1"))
        if month_expense > 0
        else Decimal("0.0")
    )

    # Rentabilidade da Carteira
    total_rentabilidade = total_patrimony - total_invested
    total_rentabilidade_perc = (
        ((total_rentabilidade / total_invested) * Decimal("100")).quantize(Decimal("0.2"))
        if total_invested > 0
        else Decimal("0.00")
    )

    # Proventos (12m e último mês)
    one_year_ago = today - timedelta(days=365)
    ttm_dividends = (
        Dividend.objects.filter(payment_date__gte=one_year_ago).aggregate(total=Sum("total_value"))["total"]
        or Decimal("0")
    )
    avg_dividend = (ttm_dividends / Decimal("12")).quantize(Decimal("0.01"))
    dividend_yield_ttm = (
        ((ttm_dividends / total_patrimony) * Decimal("100")).quantize(Decimal("0.2"))
        if total_patrimony > 0
        else Decimal("0.00")
    )

    # Progresso das Metas Principais
    patrimony_progress = (
        min(Decimal("100.0"), (total_consolidated / config.patrimony_target * Decimal("100"))).quantize(Decimal("0.1"))
        if config.patrimony_target > 0
        else Decimal("0.0")
    )
    passive_progress = (
        min(Decimal("100.0"), (avg_dividend / config.passive_income_target * Decimal("100"))).quantize(Decimal("0.1"))
        if config.passive_income_target > 0
        else Decimal("0.0")
    )

    # Autonomia (Runway) baseada na média de despesas 6m
    six_months_ago = today - timedelta(days=180)
    total_expenses_6m = (
        BudgetTransaction.objects.filter(transaction_type="expense", date__gte=six_months_ago).aggregate(
            total=Sum("value")
        )["total"]
        or Decimal("0")
    )
    avg_monthly_expense = (total_expenses_6m / Decimal("6")).quantize(Decimal("0.01"))
    runway_months = (
        (fixed_income_patrimony / avg_monthly_expense).quantize(Decimal("0.1"))
        if avg_monthly_expense > 0
        else Decimal("0.0")
    )

    # Alocação Resumida das 4 Classes
    class_colors = {
        "Ações": "#F59E0B",
        "FIIs": "#3B82F6",
        "Renda Fixa": "#00DC82",
        "ETFs/Global": "#E2E8F0",
    }
    allocation_summary = []
    for cname, cval in arca_classes.items():
        cpct = ((cval / total_patrimony) * Decimal("100")).quantize(Decimal("0.1")) if total_patrimony > 0 else Decimal("0.0")
        allocation_summary.append(
            {
                "name": cname,
                "value": cval,
                "pct": cpct,
                "color": class_colors.get(cname, "#00DC82"),
            }
        )

    # Evolução dos últimos 6 meses (Fluxo de Caixa) para o gráfico da Visão Geral
    start_y = today.year
    start_m = today.month - 5
    if start_m <= 0:
        start_m += 12
        start_y -= 1
    six_m_start = date(start_y, start_m, 1)

    monthly_stats = (
        BudgetTransaction.objects.filter(date__gte=six_m_start)
        .annotate(month_trunc=TruncMonth("date"))
        .values("month_trunc", "transaction_type")
        .annotate(total=Sum("value"))
        .order_by("month_trunc")
    )

    months_data = {}
    ty, tm = start_y, start_m
    for _ in range(6):
        m_key = f"{tm:02d}/{ty}"
        months_data[m_key] = {"income": 0.0, "expense": 0.0}
        tm += 1
        if tm > 12:
            tm = 1
            ty += 1

    for stat in monthly_stats:
        if stat["month_trunc"]:
            m_key = stat["month_trunc"].strftime("%m/%Y")
            if m_key in months_data:
                months_data[m_key][stat["transaction_type"]] = float(stat["total"] or 0)

    ov_labels = list(months_data.keys())
    ov_income = [months_data[m]["income"] for m in ov_labels]
    ov_expense = [months_data[m]["expense"] for m in ov_labels]
    ov_net = [round(months_data[m]["income"] - months_data[m]["expense"], 2) for m in ov_labels]

    # Últimas 5 transações e status do checklist
    recent_tx = BudgetTransaction.objects.select_related("category").order_by("-date", "-created_at")[:5]
    checklist_total = ChecklistItem.objects.count()
    checklist_done = ChecklistItem.objects.filter(is_completed=True).count()
    checklist_pct = round((checklist_done / checklist_total) * 100) if checklist_total > 0 else 0

    months_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    current_month_name = months_pt.get(today.month, "")

    context = {
        "config": config,
        "profile_name": config.profile_name,
        "total_patrimony": total_patrimony,
        "total_invested": total_invested,
        "total_rentabilidade": total_rentabilidade,
        "total_rentabilidade_perc": total_rentabilidade_perc,
        "fixed_income_patrimony": fixed_income_patrimony,
        "month_income": month_income,
        "month_expense": month_expense,
        "month_balance": month_balance,
        "total_consolidated": total_consolidated,
        "savings_pct": savings_pct,
        "expense_commitment_pct": expense_commitment_pct,
        "fixed_expenses_month": fixed_expenses_month,
        "fixed_expense_pct": fixed_expense_pct,
        "credit_expenses_month": credit_expenses_month,
        "credit_expense_pct": credit_expense_pct,
        "ttm_dividends": ttm_dividends,
        "avg_dividend": avg_dividend,
        "dividend_yield_ttm": dividend_yield_ttm,
        "patrimony_progress": patrimony_progress,
        "passive_progress": passive_progress,
        "runway_months": runway_months,
        "allocation_summary": allocation_summary,
        "top_assets": top_assets[:4],
        "recent_tx": recent_tx,
        "checklist_done": checklist_done,
        "checklist_total": checklist_total,
        "checklist_pct": checklist_pct,
        "ov_labels": json.dumps(ov_labels),
        "ov_income": json.dumps(ov_income),
        "ov_expense": json.dumps(ov_expense),
        "ov_net": json.dumps(ov_net),
        "current_month_name": current_month_name,
    }
    return render(request, "overview.html", context)


def goals(request):
    today = date.today()
    config = FinancialSettings.get_solo()
    ensure_default_checklist()

    total_patrimony, _, fixed_income_patrimony, arca_classes, _ = _calculate_portfolio_totals()

    six_months_ago = today - timedelta(days=180)
    buys = (
        InvestTransaction.objects.filter(transaction_type="buy", date__gte=six_months_ago).aggregate(
            total=Sum("total_value")
        )["total"]
        or Decimal("0")
    )
    sells = (
        InvestTransaction.objects.filter(transaction_type="sell", date__gte=six_months_ago).aggregate(
            total=Sum("total_value")
        )["total"]
        or Decimal("0")
    )

    avg_contribution = ((buys - sells) / Decimal("6")).quantize(Decimal("0.01"))
    if avg_contribution < 0:
        avg_contribution = Decimal("0.00")

    total_expenses_6m = (
        BudgetTransaction.objects.filter(transaction_type="expense", date__gte=six_months_ago).aggregate(
            total=Sum("value")
        )["total"]
        or Decimal("0")
    )
    avg_monthly_expense = (total_expenses_6m / Decimal("6")).quantize(Decimal("0.01"))
    runway_months = (
        (fixed_income_patrimony / avg_monthly_expense).quantize(Decimal("0.1"))
        if avg_monthly_expense > 0
        else Decimal("0.0")
    )

    one_year_ago = today - timedelta(days=365)
    total_dividends_12m = (
        Dividend.objects.filter(payment_date__gte=one_year_ago).aggregate(total=Sum("total_value"))["total"]
        or Decimal("0")
    )
    avg_dividend = (total_dividends_12m / Decimal("12")).quantize(Decimal("0.01"))

    target_weights = {
        "Ações": config.target_stocks_pct,
        "FIIs": config.target_fiis_pct,
        "Renda Fixa": config.target_fixed_income_pct,
        "ETFs/Global": config.target_global_pct,
    }

    arca_data = []
    for name, value in arca_classes.items():
        target_pct = target_weights.get(name, Decimal("25.0"))
        percentage = (
            (value / total_patrimony * Decimal("100")).quantize(Decimal("0.1"))
            if total_patrimony > 0
            else Decimal("0.0")
        )
        target_value = (total_patrimony * (target_pct / Decimal("100"))).quantize(Decimal("0.01"))
        difference = value - target_value

        lower_bound = max(Decimal("0.0"), target_pct - Decimal("5.0"))
        upper_bound = target_pct + Decimal("5.0")

        if percentage < lower_bound:
            status_color = "#F59E0B"
            status_class = "status-below"
        elif percentage > upper_bound:
            status_color = "#3B82F6"
            status_class = "status-above"
        else:
            status_color = "#00DC82"
            status_class = "status-within"

        arca_data.append(
            {
                "name": name,
                "value": value,
                "percentage": percentage,
                "target_percentage": target_pct,
                "target_value": target_value,
                "difference": difference,
                "abs_difference": abs(difference),
                "status_color": status_color,
                "status_class": status_class,
            }
        )

    patrimony_target = config.patrimony_target
    patrimony_missing = max(Decimal("0.00"), patrimony_target - total_patrimony)
    patrimony_progress = (
        min(Decimal("100.0"), (total_patrimony / patrimony_target * Decimal("100"))).quantize(Decimal("0.1"))
        if patrimony_target > 0
        else Decimal("0.0")
    )

    contribution_target = config.contribution_target
    contribution_missing = max(Decimal("0.00"), contribution_target - avg_contribution)
    contribution_progress = (
        min(Decimal("100.0"), (avg_contribution / contribution_target * Decimal("100"))).quantize(Decimal("0.1"))
        if contribution_target > 0
        else Decimal("0.0")
    )

    emergency_target = config.emergency_fund_target
    emergency_missing = max(Decimal("0.00"), emergency_target - fixed_income_patrimony)
    emergency_progress = (
        min(Decimal("100.0"), (fixed_income_patrimony / emergency_target * Decimal("100"))).quantize(Decimal("0.1"))
        if emergency_target > 0
        else Decimal("0.0")
    )

    passive_target = config.passive_income_target
    passive_progress = (
        min(Decimal("100.0"), (avg_dividend / passive_target * Decimal("100"))).quantize(Decimal("0.1"))
        if passive_target > 0
        else Decimal("0.0")
    )

    yield_pct = (
        ((avg_dividend / total_patrimony) * Decimal("100")).quantize(Decimal("0.02"))
        if total_patrimony > 0
        else Decimal("0.00")
    )

    checklist_items = ChecklistItem.objects.all()
    checklist_total = checklist_items.count()
    checklist_done = checklist_items.filter(is_completed=True).count()
    checklist_pct = round((checklist_done / checklist_total) * 100) if checklist_total > 0 else 0

    context = {
        "config": config,
        "total_patrimony": total_patrimony,
        "fixed_income_patrimony": fixed_income_patrimony,
        "avg_contribution": avg_contribution,
        "avg_dividend": avg_dividend,
        "runway_months": runway_months,
        "arca_data": arca_data,
        "patrimony_target": patrimony_target,
        "patrimony_missing": patrimony_missing,
        "patrimony_progress": patrimony_progress,
        "contribution_target": contribution_target,
        "contribution_missing": contribution_missing,
        "contribution_progress": contribution_progress,
        "emergency_target": emergency_target,
        "emergency_missing": emergency_missing,
        "emergency_progress": emergency_progress,
        "passive_target": passive_target,
        "passive_progress": passive_progress,
        "yield_pct": yield_pct,
        "checklist_items": checklist_items,
        "checklist_total": checklist_total,
        "checklist_done": checklist_done,
        "checklist_pct": checklist_pct,
    }

    return render(request, "goals.html", context)


def settings_view(request):
    """Página de Configurações para personalizar metas, alocação, rotina e dados demo."""
    config = FinancialSettings.get_solo()
    ensure_default_checklist()

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "save_financial_settings":
            profile_name = (request.POST.get("profile_name") or "").strip()[:120]
            if profile_name:
                config.profile_name = profile_name

            config.patrimony_target = _parse_decimal(
                request.POST.get("patrimony_target"), config.patrimony_target
            )
            config.contribution_target = _parse_decimal(
                request.POST.get("contribution_target"), config.contribution_target
            )
            config.emergency_fund_target = _parse_decimal(
                request.POST.get("emergency_fund_target"), config.emergency_fund_target
            )
            config.passive_income_target = _parse_decimal(
                request.POST.get("passive_income_target"), config.passive_income_target
            )
            config.benchmark_annual_rate = _parse_decimal(
                request.POST.get("benchmark_annual_rate"), config.benchmark_annual_rate
            )
            config.simulator_monthly_rate = _parse_decimal(
                request.POST.get("simulator_monthly_rate"), config.simulator_monthly_rate
            )
            config.save()
            messages.success(request, "Parâmetros e metas financeiras atualizados com sucesso!")
            return redirect("settings")

        elif action == "save_allocation":
            stocks = _parse_decimal(request.POST.get("target_stocks_pct"), config.target_stocks_pct)
            fiis = _parse_decimal(request.POST.get("target_fiis_pct"), config.target_fiis_pct)
            rf = _parse_decimal(request.POST.get("target_fixed_income_pct"), config.target_fixed_income_pct)
            glob_pct = _parse_decimal(request.POST.get("target_global_pct"), config.target_global_pct)

            total_pct = stocks + fiis + rf + glob_pct
            if abs(total_pct - Decimal("100.0")) > Decimal("0.5"):
                messages.error(
                    request,
                    f"A soma dos pesos das 4 classes deve ser 100% (soma informada: {total_pct:.1f}%).",
                )
            else:
                config.target_stocks_pct = stocks
                config.target_fiis_pct = fiis
                config.target_fixed_income_pct = rf
                config.target_global_pct = glob_pct
                config.save()
                messages.success(request, "Pesos da estratégia de alocação salvos com sucesso!")
            return redirect("settings")

        elif action == "add_checklist_item":
            title = (request.POST.get("title") or "").strip()[:200]
            day_raw = request.POST.get("day_of_month", "1")
            tag = request.POST.get("category_tag", ChecklistItem.TagType.APORTE)
            valid_tags = {choice[0] for choice in ChecklistItem.TagType.choices}
            if tag not in valid_tags:
                tag = ChecklistItem.TagType.APORTE
            try:
                day = max(1, min(31, int(day_raw)))
            except ValueError:
                day = 1

            if title:
                ChecklistItem.objects.create(
                    day_of_month=day,
                    title=title,
                    category_tag=tag,
                    order=ChecklistItem.objects.count() + 1,
                )
                messages.success(request, "Nova tarefa adicionada à rotina mensal!")
            else:
                messages.error(request, "Informe a descrição da tarefa.")
            next_url = request.POST.get("next")
            if next_url == "goals":
                return redirect("goals")
            return redirect("settings")

        elif action == "reset_checklist_status":
            ChecklistItem.objects.all().update(is_completed=False)
            messages.success(request, "Progresso do checklist mensal reiniciado para um novo ciclo!")
            next_url = request.POST.get("next")
            if next_url == "goals":
                return redirect("goals")
            return redirect("settings")

        elif action == "seed_demo_data":
            reset_and_seed_demo()
            messages.success(
                request,
                "Ambiente restaurado com os dados demonstrativos oficiais da GreyWorks Finance!",
            )
            return redirect("overview")

        elif action == "clear_all_data":
            InvestTransaction.objects.all().delete()
            Dividend.objects.all().delete()
            Asset.objects.all().delete()
            BudgetTransaction.objects.all().delete()
            messages.success(request, "Todos os ativos e lançamentos foram removidos. O banco está limpo!")
            return redirect("settings")

    checklist_items = ChecklistItem.objects.all()
    budget_categories = BudgetCategory.objects.all()

    context = {
        "config": config,
        "checklist_items": checklist_items,
        "budget_categories": budget_categories,
        "tag_choices": ChecklistItem.TagType.choices,
    }
    return render(request, "settings.html", context)


@require_POST
def toggle_checklist_item(request, item_id: int):
    item = get_object_or_404(ChecklistItem, id=item_id)
    item.is_completed = not item.is_completed
    item.save()

    total = ChecklistItem.objects.count()
    done = ChecklistItem.objects.filter(is_completed=True).count()
    pct = round((done / total) * 100) if total > 0 else 0

    return JsonResponse(
        {
            "status": "success",
            "id": item.id,
            "is_completed": item.is_completed,
            "done": done,
            "total": total,
            "percentage": pct,
        }
    )


@require_POST
def delete_checklist_item(request, item_id: int):
    item = get_object_or_404(ChecklistItem, id=item_id)
    item.delete()
    messages.success(request, "Tarefa removida da rotina mensal.")
    next_url = request.POST.get("next")
    if next_url == "goals":
        return redirect("goals")
    return redirect("settings")
