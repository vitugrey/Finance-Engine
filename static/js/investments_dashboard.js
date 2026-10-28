// ==========================================================================
// GRÁFICOS E INTERATIVIDADE DE INVESTIMENTOS - GREYWORKS FINANCE
// ==========================================================================
document.addEventListener("DOMContentLoaded", function() {
    // 1. Gráfico de Rosca Concêntrico Duplo (Anel Externo: Meta Ideal | Anel Interno: Realidade da Carteira)
    const allocCanvas = document.getElementById('allocationChart');
    if (allocCanvas && typeof strategicLabels !== 'undefined' && typeof strategicActualPcts !== 'undefined' && typeof strategicTargetPcts !== 'undefined') {
        const ctx = allocCanvas.getContext('2d');

        const baseColors = (typeof strategicColors !== 'undefined' && strategicColors.length)
            ? strategicColors
            : ['#F59E0B', '#3B82F6', '#00DC82', '#E2E8F0'];

        // Anel Externo (Metas) com transparência + borda tracejada/destacada e Anel Interno (Realidade sólida)
        const outerTargetColors = [
            'rgba(245, 158, 11, 0.50)',
            'rgba(59, 130, 246, 0.50)',
            'rgba(0, 220, 130, 0.50)',
            'rgba(226, 232, 240, 0.50)'
        ];

        const displayLabels = strategicLabels.map((lbl, i) => {
            const act = strategicActualPcts[i] !== undefined ? Number(strategicActualPcts[i]).toFixed(1) : '0.0';
            const tgt = strategicTargetPcts[i] !== undefined ? Number(strategicTargetPcts[i]).toFixed(0) : '0';
            return `${lbl}: ${act}% (Meta ${tgt}%)`;
        });

        const formatBRL = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: displayLabels,
                datasets: [
                    {
                        label: 'Meta Estratégica (Anel Externo)',
                        data: strategicTargetPcts,
                        backgroundColor: outerTargetColors,
                        hoverBackgroundColor: baseColors,
                        borderColor: '#181C24',
                        borderWidth: 3,
                        weight: 0.9,
                        hoverOffset: 4
                    },
                    {
                        label: 'Realidade da Carteira (Anel Interno)',
                        data: strategicActualPcts,
                        backgroundColor: baseColors,
                        hoverBackgroundColor: baseColors,
                        borderColor: '#181C24',
                        borderWidth: 3,
                        weight: 1.3,
                        hoverOffset: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '45%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#E2E8F0',
                            font: {
                                family: "'JetBrains Mono', monospace",
                                size: 11.5
                            },
                            usePointStyle: true,
                            boxWidth: 10,
                            padding: 16
                        }
                    },
                    tooltip: {
                        backgroundColor: '#141722',
                        titleColor: '#FFFFFF',
                        bodyColor: '#E2E8F0',
                        borderColor: '#262B35',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            title: function(context) {
                                if (!context || !context.length) return '';
                                const item = context[0];
                                const className = strategicLabels[item.dataIndex] || item.label;
                                const ringName = item.datasetIndex === 0
                                    ? 'Meta Ideal (Anel Externo)'
                                    : 'Realidade da Carteira (Anel Interno)';
                                return `${className} — ${ringName}`;
                            },
                            label: function(context) {
                                const idx = context.dataIndex;
                                const isTargetRing = context.datasetIndex === 0;
                                const pct = context.parsed !== null ? Number(context.parsed).toFixed(1) : '0.0';
                                const finVal = isTargetRing
                                    ? (typeof strategicTargetVals !== 'undefined' ? strategicTargetVals[idx] : 0)
                                    : (typeof strategicActualVals !== 'undefined' ? strategicActualVals[idx] : 0);
                                const otherPct = isTargetRing
                                    ? Number(strategicActualPcts[idx] || 0).toFixed(1)
                                    : Number(strategicTargetPcts[idx] || 0).toFixed(1);
                                const otherLabel = isTargetRing ? 'Atual na Carteira' : 'Meta Definida';

                                return [
                                    ` Participação: ${pct}% (${formatBRL(finVal)})`,
                                    ` Comparativo (${otherLabel}): ${otherPct}%`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Gráfico Empilhado de Proventos Mensais (12 Meses)
    const divMonthlyCanvas = document.getElementById('dividendsMonthlyChart');
    if (divMonthlyCanvas && typeof dividendsMonthlyLabels !== 'undefined' && typeof dividendsMonthlyDatasets !== 'undefined') {
        const ctx = divMonthlyCanvas.getContext('2d');
        
        const chartColors = [
            '#00DC82', // Signature Green
            '#3B82F6', // Azul
            '#F59E0B', // Âmbar
            '#E2E8F0', // Prata
            '#F87171', // Coral
            '#10B981', // Emerald
            '#60A5FA', // Sky
            '#9CA3AF', // Cinza Metálico
            '#64748B'  // Slate
        ];

        const datasetsWithColors = dividendsMonthlyDatasets.map((dataset, idx) => {
            const color = chartColors[idx % chartColors.length];
            return {
                label: dataset.label,
                data: dataset.data,
                backgroundColor: color,
                hoverBackgroundColor: color,
                borderRadius: 4,
                borderSkipped: false
            };
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dividendsMonthlyLabels,
                datasets: datasetsWithColors
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#9CA3AF',
                            font: {
                                family: "'JetBrains Mono', monospace",
                                size: 11
                            },
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 15
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
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.raw !== null) {
                                    label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.raw);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            color: '#1E2330',
                            borderColor: 'transparent'
                        },
                        ticks: {
                            color: '#64748B',
                            font: {
                                family: "'JetBrains Mono', monospace",
                                size: 11
                            }
                        }
                    },
                    y: {
                        stacked: true,
                        grid: {
                            color: '#1E2330',
                            borderColor: 'transparent'
                        },
                        ticks: {
                            color: '#64748B',
                            font: {
                                family: "'JetBrains Mono', monospace",
                                size: 11
                            },
                            callback: function(value) {
                                return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Filtro Instantâneo por Classe na Tabela de Posições
    const filterContainer = document.getElementById('assetFilterPills');
    const positionsTable = document.getElementById('portfolioPositionsTable');
    if (filterContainer && positionsTable) {
        const pills = filterContainer.querySelectorAll('.inv-pill');
        const rows = positionsTable.querySelectorAll('tbody tr[data-asset-type]');

        pills.forEach(pill => {
            pill.addEventListener('click', function() {
                pills.forEach(p => p.classList.remove('active'));
                this.classList.add('active');

                const filterVal = this.getAttribute('data-filter');
                rows.forEach(row => {
                    const rowType = row.getAttribute('data-asset-type');
                    if (filterVal === 'all' || rowType === filterVal) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        });
    }

    // 4. Sincronização de Cotações Yahoo Finance (Sem alert())
    const syncBtn = document.getElementById('btnSyncYFinance');
    const syncText = document.getElementById('syncText');
    const syncBanner = document.getElementById('syncStatusBanner');
    const syncMsg = document.getElementById('syncStatusMsg');

    if (syncBtn) {
        syncBtn.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            const csrf = this.getAttribute('data-csrf');
            if (!url) return;

            syncBtn.disabled = true;
            if (syncText) syncText.textContent = 'Sincronizando B3...';

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(resp => resp.json())
            .then(data => {
                if (syncBanner && syncMsg) {
                    syncBanner.style.display = 'flex';
                    syncMsg.textContent = 'Cotações B3 sincronizadas (' + (data.updated || 0) + ' ativos atualizados). Recarregando painel...';
                }
                setTimeout(() => window.location.reload(), 900);
            })
            .catch(() => {
                syncBtn.disabled = false;
                if (syncText) syncText.textContent = 'Atualizar Cotações';
            });
        });
    }
});
