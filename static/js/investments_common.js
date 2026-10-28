// ==========================================================================
// FUNÇÕES REUTILIZÁVEIS E COMUNS - INVESTIMENTOS GREYWORKS
// ==========================================================================

function openTab(evt, tabId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        tabcontent[i].classList.remove("active");
    }
    tablinks = document.getElementsByClassName("tab-btn");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.style.display = "block";
        activeTab.classList.add("active");
    }
    if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add("active");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const btnUpdatePrices = document.getElementById('btnUpdatePrices');
    const banner = document.getElementById('priceStatusBanner');

    function showBanner(msg, isError) {
        if (!banner) return;
        banner.style.display = 'flex';
        banner.className = isError ? 'alert alert-error' : 'alert alert-success';
        banner.textContent = msg;
    }

    if (btnUpdatePrices) {
        btnUpdatePrices.addEventListener('click', function() {
            const btn = this;
            const icon = btn.querySelector('i');
            const span = btn.querySelector('span');
            
            if (icon) icon.classList.add('bx-spin');
            if (span) span.textContent = 'Sincronizando Cotações...';
            btn.style.opacity = '0.7';
            btn.style.pointerEvents = 'none';

            const csrfToken = typeof csrfTokenVal !== 'undefined' ? csrfTokenVal : '';
            const updateUrl = typeof updatePricesUrl !== 'undefined' ? updatePricesUrl : '/investimentos/api/update-prices/';

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showBanner('Cotações sincronizadas com sucesso! Recarregando...', false);
                    setTimeout(() => window.location.reload(), 600);
                } else {
                    showBanner('Não foi possível atualizar as cotações neste momento.', true);
                    if (icon) icon.classList.remove('bx-spin');
                    if (span) span.textContent = 'Atualizar Cotações (Yahoo Finance)';
                    btn.style.opacity = '1';
                    btn.style.pointerEvents = 'auto';
                }
            })
            .catch(() => {
                showBanner('Erro de comunicação ao consultar cotações.', true);
                if (icon) icon.classList.remove('bx-spin');
                if (span) span.textContent = 'Atualizar Cotações (Yahoo Finance)';
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            });
        });
    }
});
