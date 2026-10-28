// ==========================================================================
// GRÁFICOS DE EVOLUÇÃO DE PATRIMÔNIO - GREYWORKS FINANCE
// ==========================================================================
document.addEventListener("DOMContentLoaded", function() {
    const monthlyCanvas = document.getElementById('monthlyChart');
    const yearlyCanvas = document.getElementById('yearlyChart');

    if (monthlyCanvas && typeof monthlyLabels !== 'undefined' && typeof monthlyData !== 'undefined') {
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
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
                            if (label) { label += ': '; }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#1E2330' },
                    ticks: {
                        color: '#64748B',
                        font: { family: "'JetBrains Mono', monospace", size: 11 },
                        callback: function(value) {
                            return 'R$' + new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 }).format(value);
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: {
                        color: '#64748B',
                        font: { family: "'JetBrains Mono', monospace", size: 11 },
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        };

        new Chart(monthlyCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: monthlyLabels,
                datasets: [{
                    label: 'Acumulado Mês a Mês',
                    data: monthlyData,
                    backgroundColor: 'rgba(0, 220, 130, 0.12)',
                    borderColor: '#00DC82',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#00DC82',
                    pointRadius: 3,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: commonOptions
        });

        if (yearlyCanvas && typeof yearlyLabels !== 'undefined' && typeof yearlyData !== 'undefined') {
            new Chart(yearlyCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: yearlyLabels,
                    datasets: [{
                        label: 'Acumulado por Ano',
                        data: yearlyData,
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderColor: '#3B82F6',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        ...commonOptions.scales,
                        x: {
                            ...commonOptions.scales.x,
                            ticks: { color: '#64748B', font: { family: "'JetBrains Mono', monospace", size: 11 } }
                        }
                    }
                }
            });
        }
    }
});
