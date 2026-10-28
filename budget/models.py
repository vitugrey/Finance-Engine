from decimal import Decimal
from django.db import models


class Category(models.Model):
    """Categoria para organizar transações (ex: Alimentação, Transporte, Receita Operacional)."""

    name = models.CharField("Nome", max_length=100, unique=True)
    description = models.TextField("Descrição", blank=True, default="")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Registro de uma transação financeira (receita ou despesa)."""

    class TransactionType(models.TextChoices):
        INCOME = "income", "Receita"
        EXPENSE = "expense", "Despesa"

    description = models.CharField("Descrição", max_length=255)
    value = models.DecimalField("Valor", max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Categoria",
    )
    date = models.DateField("Data")
    is_credit = models.BooleanField("É crédito?", default=False)
    is_fixed_expense = models.BooleanField("Despesa fixa?", default=False)
    is_fixed_income = models.BooleanField("Receita fixa?", default=False)
    transaction_type = models.CharField(
        "Tipo",
        max_length=10,
        choices=TransactionType.choices,
        default=TransactionType.EXPENSE,
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        sinal = "+" if self.transaction_type == self.TransactionType.INCOME else "-"
        return f"{self.description} ({sinal} R${self.value})"


class FinancialSettings(models.Model):
    """Configurações personalizáveis de metas, benchmarks e alocação de carteira."""

    profile_name = models.CharField(
        "Nome do Perfil / Portfólio",
        max_length=120,
        default="Portfólio Executivo",
    )
    patrimony_target = models.DecimalField(
        "Meta Principal de Patrimônio (R$)",
        max_digits=14,
        decimal_places=2,
        default=Decimal("100000.00"),
    )
    contribution_target = models.DecimalField(
        "Meta de Aporte Mensal (R$)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("2500.00"),
    )
    emergency_fund_target = models.DecimalField(
        "Meta de Reserva de Liquidez (R$)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("18000.00"),
    )
    passive_income_target = models.DecimalField(
        "Meta de Renda Passiva Mensal (R$)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("5000.00"),
    )
    benchmark_annual_rate = models.DecimalField(
        "Benchmark Anual / CDI (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("11.25"),
    )
    simulator_monthly_rate = models.DecimalField(
        "Taxa Mensal Padrão do Simulador (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.90"),
    )
    target_stocks_pct = models.DecimalField(
        "Meta Alocação Ações (%)",
        max_digits=5,
        decimal_places=1,
        default=Decimal("25.0"),
    )
    target_fiis_pct = models.DecimalField(
        "Meta Alocação FIIs (%)",
        max_digits=5,
        decimal_places=1,
        default=Decimal("25.0"),
    )
    target_fixed_income_pct = models.DecimalField(
        "Meta Alocação Renda Fixa (%)",
        max_digits=5,
        decimal_places=1,
        default=Decimal("25.0"),
    )
    target_global_pct = models.DecimalField(
        "Meta Alocação ETFs / Global (%)",
        max_digits=5,
        decimal_places=1,
        default=Decimal("25.0"),
    )
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Configuração Financeira"
        verbose_name_plural = "Configurações Financeiras"

    def __str__(self):
        return f"Configurações ({self.profile_name})"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj


class ChecklistItem(models.Model):
    """Item configurável do checklist de rotina financeira mensal."""

    class TagType(models.TextChoices):
        APORTE = "aporte", "Aporte & Investimento"
        CONTAS = "contas", "Contas & Custos Fixos"
        CARTAO = "cartao", "Cartão de Crédito"
        REVISAO = "revisao", "Revisão & Auditoria"

    day_of_month = models.PositiveSmallIntegerField("Dia do Mês", default=1)
    title = models.CharField("Descrição da Tarefa", max_length=200)
    category_tag = models.CharField(
        "Tipo",
        max_length=20,
        choices=TagType.choices,
        default=TagType.APORTE,
    )
    is_completed = models.BooleanField("Concluído no mês?", default=False)
    order = models.PositiveSmallIntegerField("Ordem", default=0)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Item do Checklist"
        verbose_name_plural = "Itens do Checklist"
        ordering = ["day_of_month", "order", "id"]

    def __str__(self):
        return f"[Dia {self.day_of_month:02d}] {self.title}"
