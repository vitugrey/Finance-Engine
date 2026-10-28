// ==========================================================================
// GRÁFICOS E FILTROS DO DASHBOARD DE CARTEIRA (BUDGET) - GREYWORKS FINANCE
// ==========================================================================
document.addEventListener("DOMContentLoaded", function() {
    // 1. Gráfico de Rosca: Despesas por Categoria
    const catCanvas = document.getElementById('categoryChart');
    if (catCanvas && typeof categoryLabels !== 'undefined' && typeof categoryValues !== 'undefined') {
        const catCtx = catCanvas.getContext('2d');
        const colors = [
            '#00DC82', '#3B82F6', '#F59E0B', '#F87171', '#E2E8F0',
            '#10B981', '#60A5FA', '#FBBF24', '#EF4444', '#64748B'
        ];

        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: categoryLabels,
                datasets: [{
                    data: categoryValues,
                    backgroundColor: colors.slice(0, categoryLabels.length),
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#9CA3AF',
                            font: { family: "'Inter', sans-serif", size: 11.5 },
                            usePointStyle: true,
                            padding: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: '#181C24',
                        titleColor: '#FFFFFF',
                        bodyColor: '#E2E8F0',
                        borderColor: '#262B35',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                let val = context.parsed;
                                return ' ' + context.label + ': R$ ' + val.toLocaleString('pt-BR', {minimumFractionDigits: 2});
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Gráfico Combo: Evolução Mensal (Receitas, Despesas e Saldo Líquido)
    const evoCanvas = document.getElementById('evolutionChart');
    if (evoCanvas && typeof evolutionLabels !== 'undefined' && typeof evolutionIncome !== 'undefined' && typeof evolutionExpense !== 'undefined') {
        const evoCtx = evoCanvas.getContext('2d');
        const netData = (typeof evolutionNet !== 'undefined') ? evolutionNet : [];

        new Chart(evoCtx, {
            type: 'bar',
            data: {
                labels: evolutionLabels,
                datasets: [
                    {
                        type: 'line',
                        label: 'Saldo Líquido (R$)',
                        data: netData,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.14)',
                        borderWidth: 2.5,
                        pointBackgroundColor: '#3B82F6',
                        pointRadius: 4,
                        tension: 0.35,
                        order: 0
                    },
                    {
                        type: 'bar',
                        label: 'Receitas (R$)',
                        data: evolutionIncome,
                        backgroundColor: '#00DC82',
                        borderRadius: 6,
                        barPercentage: 0.55,
                        order: 1
                    },
                    {
                        type: 'bar',
                        label: 'Despesas (R$)',
                        data: evolutionExpense,
                        backgroundColor: '#F87171',
                        borderRadius: 6,
                        barPercentage: 0.55,
                        order: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748B', font: { family: "'JetBrains Mono', monospace", size: 11 } }
                    },
                    y: {
                        grid: { color: '#1E2330' },
                        ticks: {
                            color: '#64748B',
                            font: { family: "'JetBrains Mono', monospace", size: 11 },
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR', { maximumFractionDigits: 0 });
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: '#E2E8F0',
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { family: "'Inter', sans-serif", size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#181C24',
                        titleColor: '#FFFFFF',
                        bodyColor: '#E2E8F0',
                        borderColor: '#262B35',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const val = context.parsed.y || 0;
                                return context.dataset.label + ': ' + val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Filtro Instantâneo + Busca de Transações na Tabela
    const txTable = document.getElementById('budgetTransactionsTable');
    const searchInput = document.getElementById('txSearchInput');
    const filterPills = document.getElementById('txFilterPills');

    if (txTable) {
        const rows = txTable.querySelectorAll('tbody tr[data-tx-type]');
        let activeFilter = 'all';

        function applyTxFilters() {
            const q = (searchInput ? searchInput.value : '').trim().toLowerCase();

            rows.forEach(row => {
                const txType = row.getAttribute('data-tx-type');
                const isCredit = row.getAttribute('data-tx-credit') === 'true';
                const isFixed = row.getAttribute('data-tx-fixed') === 'true';
                const searchText = row.getAttribute('data-tx-search') || '';

                let matchesPill = true;
                if (activeFilter === 'income') matchesPill = (txType === 'income');
                else if (activeFilter === 'expense') matchesPill = (txType === 'expense');
                else if (activeFilter === 'credit') matchesPill = isCredit;
                else if (activeFilter === 'fixed') matchesPill = isFixed;

                const matchesSearch = !q || searchText.indexOf(q) !== -1;

                if (matchesPill && matchesSearch) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', applyTxFilters);
        }

        if (filterPills) {
            const pills = filterPills.querySelectorAll('.budget-pill');
            pills.forEach(pill => {
                pill.addEventListener('click', function() {
                    pills.forEach(p => p.classList.remove('active'));
                    this.classList.add('active');
                    activeFilter = this.getAttribute('data-filter') || 'all';
                    applyTxFilters();
                });
            });
        }
    }
});
