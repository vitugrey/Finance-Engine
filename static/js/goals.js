// ==========================================================================
// SIMULADOR GRÁFICO DE JUROS COMPOSTOS & CHECKLIST DINÂMICO - GREYWORKS
// ==========================================================================
document.addEventListener("DOMContentLoaded", function() {
    const patrimonyInput = document.getElementById('calc-patrimony');
    const contributionInput = document.getElementById('calc-contribution');
    const rateSlider = document.getElementById('calc-rate');
    const yearsSlider = document.getElementById('calc-years');

    const labelPatrimony = document.getElementById('label-patrimony');
    const labelContribution = document.getElementById('label-contribution');
    const labelRate = document.getElementById('label-rate');
    const labelYears = document.getElementById('label-years');

    const summaryFinal = document.getElementById('summary-final-patrimony');
    const summaryInvested = document.getElementById('summary-total-invested');
    const summaryInterest = document.getElementById('summary-total-interest');
    const summaryPassive = document.getElementById('summary-passive-income');

    const cardEmergency = document.getElementById('card-emergency');
    const card100k = document.getElementById('card-100k');
    const cardMainGoal = document.getElementById('card-main-goal');
    const card1m = document.getElementById('card-1m');

    const timeEmergency = document.getElementById('time-emergency');
    const time100k = document.getElementById('time-100k');
    const timeMainGoal = document.getElementById('time-main-goal');
    const time1m = document.getElementById('time-1m');

    const chartCanvas = document.getElementById('compoundProjectionChart');
    let projectionChart = null;

    function formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    }

    function parseFormattedFloat(str) {
        if (!str) return 0;
        const clean = str.replace(/\./g, '').replace(',', '.');
        const num = parseFloat(clean);
        return isNaN(num) ? 0 : num;
    }

    function applyMaskAndValue(input, onUpdate) {
        input.addEventListener('input', function() {
            let val = input.value.replace(/\D/g, '');
            if (val === '') val = '0';
            const floatVal = parseFloat(val) / 100;
            input.value = floatVal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            onUpdate();
        });
    }

    function setupInputFormatting() {
        const pVal = parseFloat(patrimonyInput.value) || 0;
        const cVal = parseFloat(contributionInput.value) || 0;
        patrimonyInput.value = pVal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        contributionInput.value = cVal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function calculateCompoundInterest(P, A, r, months) {
        if (r === 0) return P + A * months;
        return P * Math.pow(1 + r, months) + A * ((Math.pow(1 + r, months) - 1) / r);
    }

    function calculateMonthsToTarget(P, A, r, target) {
        if (P >= target) return 0;
        if (A <= 0 && r <= 0) return Infinity;
        if (P * r + A <= 0) return Infinity;
        if (r === 0) return (target - P) / A;
        
        const numerator = target + A / r;
        const denominator = P + A / r;
        if (denominator <= 0 || numerator <= 0) return Infinity;
        return Math.log(numerator / denominator) / Math.log(1 + r);
    }

    function formatTime(months) {
        if (months === Infinity || isNaN(months)) return "Indefinido";
        if (months === 0) return "Alcançado ✓";
        
        const rounded = Math.ceil(months);
        const years = Math.floor(rounded / 12);
        const remainingMonths = rounded % 12;
        
        let result = "";
        if (years > 0) {
            result += `${years}a`;
        }
        if (remainingMonths > 0) {
            if (result !== "") result += " ";
            result += `${remainingMonths}m`;
        }
        return result;
    }

    function updateMilestoneCard(cardEl, timeEl, P, A, r) {
        if (!cardEl || !timeEl) return;
        const target = parseFloat(cardEl.getAttribute('data-target')) || 0;
        const months = calculateMonthsToTarget(P, A, r, target);
        timeEl.textContent = formatTime(months);
        if (months === 0) {
            cardEl.classList.add('target-reached');
        } else {
            cardEl.classList.remove('target-reached');
        }
    }

    function renderOrUpdateChart(P, A, r, horizonYears) {
        if (!chartCanvas || typeof Chart === 'undefined') return;
        const labels = [];
        const investedData = [];
        const interestData = [];

        for (let y = 1; y <= horizonYears; y++) {
            const m = y * 12;
            const totalVal = calculateCompoundInterest(P, A, r, m);
            const totalInvested = P + (A * m);
            const totalInterest = Math.max(0, totalVal - totalInvested);

            labels.push(`Ano ${y}`);
            investedData.push(Math.round(totalInvested));
            interestData.push(Math.round(totalInterest));
        }

        if (projectionChart) {
            projectionChart.data.labels = labels;
            projectionChart.data.datasets[0].data = investedData;
            projectionChart.data.datasets[1].data = interestData;
            projectionChart.update();
            return;
        }

        projectionChart = new Chart(chartCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Capital Desembolsado',
                        data: investedData,
                        backgroundColor: '#3B82F6',
                        borderRadius: 4
                    },
                    {
                        label: 'Juros Compostos Acumulados',
                        data: interestData,
                        backgroundColor: '#00DC82',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false },
                        ticks: {
                            color: '#64748B',
                            font: { family: "'JetBrains Mono', monospace", size: 10.5 }
                        }
                    },
                    y: {
                        stacked: true,
                        grid: { color: '#1E2330' },
                        ticks: {
                            color: '#64748B',
                            font: { family: "'JetBrains Mono', monospace", size: 10.5 },
                            callback: function(value) {
                                return new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL',
                                    notation: 'compact',
                                    maximumFractionDigits: 1
                                }).format(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#9CA3AF',
                            font: { family: "'Inter', sans-serif", size: 11.5 },
                            usePointStyle: true,
                            boxWidth: 8
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
                                return ' ' + context.dataset.label + ': ' + formatCurrency(context.raw);
                            }
                        }
                    }
                }
            }
        });
    }

    function updateCalculator() {
        if (!patrimonyInput || !contributionInput || !rateSlider || !yearsSlider) return;
        const P = parseFormattedFloat(patrimonyInput.value);
        const A = parseFormattedFloat(contributionInput.value);
        const ratePercent = parseFloat(rateSlider.value) || 0;
        const horizonYears = parseInt(yearsSlider.value, 10) || 10;
        const r = ratePercent / 100;
        const totalMonths = horizonYears * 12;

        if (labelPatrimony) labelPatrimony.textContent = formatCurrency(P);
        if (labelContribution) labelContribution.textContent = formatCurrency(A);
        if (labelRate) labelRate.textContent = `${ratePercent.toFixed(2)}% a.m.`;
        if (labelYears) labelYears.textContent = `${horizonYears} ${horizonYears === 1 ? 'ano' : 'anos'}`;

        // Atualiza Marcos
        updateMilestoneCard(cardEmergency, timeEmergency, P, A, r);
        updateMilestoneCard(card100k, time100k, P, A, r);
        updateMilestoneCard(cardMainGoal, timeMainGoal, P, A, r);
        updateMilestoneCard(card1m, time1m, P, A, r);

        // Calcula Resumo no Horizonte Escolhido
        const finalPatrimony = calculateCompoundInterest(P, A, r, totalMonths);
        const totalInvested = P + (A * totalMonths);
        const totalInterest = Math.max(0, finalPatrimony - totalInvested);
        const estimatedPassive = finalPatrimony * r;

        if (summaryFinal) summaryFinal.textContent = formatCurrency(finalPatrimony);
        if (summaryInvested) summaryInvested.textContent = formatCurrency(totalInvested);
        if (summaryInterest) summaryInterest.textContent = `+${formatCurrency(totalInterest)}`;
        if (summaryPassive) summaryPassive.textContent = `${formatCurrency(estimatedPassive)} / mês`;

        renderOrUpdateChart(P, A, r, horizonYears);
    }

    if (patrimonyInput && contributionInput && rateSlider && yearsSlider) {
        setupInputFormatting();
        applyMaskAndValue(patrimonyInput, updateCalculator);
        applyMaskAndValue(contributionInput, updateCalculator);
        rateSlider.addEventListener('input', updateCalculator);
        yearsSlider.addEventListener('input', updateCalculator);
        updateCalculator();
    }

    // ==========================================================================
    // PARTE 2: CHECKLIST EXECUTIVO PERSISTIDO NO BANCO DE DADOS
    // ==========================================================================
    const checklistItems = document.querySelectorAll('.checklist-item');
    const counterSpan = document.getElementById('checklist-counter');
    const progressFill = document.getElementById('checklist-progress');

    checklistItems.forEach(item => {
        item.addEventListener('click', function() {
            const toggleUrl = item.getAttribute('data-toggle-url');
            if (!toggleUrl) return;

            fetch(toggleUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': typeof csrfTokenGoals !== 'undefined' ? csrfTokenGoals : ''
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    if (data.is_completed) {
                        item.classList.add('checked');
                    } else {
                        item.classList.remove('checked');
                    }
                    if (counterSpan) {
                        counterSpan.textContent = `${data.done}/${data.total} (${data.percentage}%)`;
                    }
                    if (progressFill) {
                        progressFill.style.width = `${data.percentage}%`;
                    }
                }
            })
            .catch(() => {});
        });
    });
});
