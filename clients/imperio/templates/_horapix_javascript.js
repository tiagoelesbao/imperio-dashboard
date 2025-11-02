// ============================================
// HORA DO PIX - JAVASCRIPT
// ============================================

// Carregar dados do Hora do Pix
async function loadHoraPixData() {
    console.log('Loading Hora do Pix data...');

    try {
        const response = await fetch('/api/imperio/horapix/latest');
        const result = await response.json();

        if (result.status === 'success' && result.data) {
            updateHoraPixUI(result.data);
        } else {
            console.warn('Nenhum dado Hora do Pix disponível');
            showEmptyHoraPixState();
        }
    } catch (error) {
        console.error('Erro ao carregar Hora do Pix:', error);
        showHoraPixError();
    }
}

// Atualizar UI com dados
function updateHoraPixUI(data) {
    const totals = data.totals || {};
    const draws = data.draws || [];

    // Atualizar cards de totais
    document.getElementById('horaPixTotalPrize').textContent =
        `R$ ${totals.total_prize_value?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) || '0,00'}`;
    document.getElementById('horaPixDrawsCount').textContent =
        `${totals.total_draws || 0} sorteios`;

    document.getElementById('horaPixTotalRevenue').textContent =
        `R$ ${totals.total_revenue?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) || '0,00'}`;
    document.getElementById('horaPixActiveDraws').textContent =
        `${totals.active_draws || 0} ativos`;

    document.getElementById('horaPixTotalProfit').textContent =
        `R$ ${totals.total_profit?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) || '0,00'}`;
    document.getElementById('horaPixFinishedDraws').textContent =
        `${totals.finished_draws || 0} finalizados`;

    document.getElementById('horaPixTotalROI').textContent =
        `${totals.total_roi?.toFixed(2) || '0.00'}%`;

    // Atualizar badges
    document.getElementById('badgeActive').textContent = totals.active_draws || 0;
    document.getElementById('badgeFinished').textContent = totals.finished_draws || 0;

    // Atualizar última atualização
    if (data.collection_time) {
        const time = new Date(data.collection_time);
        document.getElementById('horaPixLastUpdate').textContent =
            `Última atualização: ${time.toLocaleString('pt-BR')}`;
    }

    // Renderizar sorteios
    renderDraws(draws);
}

// Renderizar sorteios
function renderDraws(draws) {
    const active = draws.filter(d => d.status === 'active');
    const finished = draws.filter(d => d.status === 'done');

    // Renderizar ativos
    const activeList = document.getElementById('activeDrawsList');
    if (active.length > 0) {
        activeList.innerHTML = active.map(draw => createDrawCard(draw)).join('');
    } else {
        activeList.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <i class="fas fa-info-circle fa-3x mb-3"></i>
                <p>Nenhum sorteio ativo no momento</p>
            </div>
        `;
    }

    // Renderizar finalizados
    const finishedList = document.getElementById('finishedDrawsList');
    if (finished.length > 0) {
        finishedList.innerHTML = finished.map(draw => createDrawCard(draw, true)).join('');
    } else {
        finishedList.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <i class="fas fa-check-circle fa-3x mb-3"></i>
                <p>Nenhum sorteio finalizado hoje</p>
            </div>
        `;
    }
}

// Criar card de sorteio
function createDrawCard(draw, isFinished = false) {
    const statusBadge = isFinished ?
        '<span class="badge bg-success">Finalizado</span>' :
        '<span class="badge bg-primary">Ativo</span>';

    const percentSold = draw.qty_total > 0 ?
        (draw.qty_paid / draw.qty_total * 100).toFixed(1) : 0;

    const roiColor = draw.roi > 0 ? 'success' : 'danger';

    return `
        <div class="col-md-6 col-lg-4">
            <div class="card h-100" style="border-left: 4px solid ${isFinished ? '#28a745' : '#007bff'};">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <small class="text-muted">#${draw.id?.substring(0, 8)}</small>
                    ${statusBadge}
                </div>
                <div class="card-body">
                    <h6 class="card-title">${draw.title}</h6>
                    <div class="mb-2">
                        <div class="d-flex justify-content-between mb-1">
                            <small>Vendido</small>
                            <small><strong>${draw.qty_paid}/${draw.qty_total}</strong> (${percentSold}%)</small>
                        </div>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar ${isFinished ? 'bg-success' : 'bg-primary'}"
                                 style="width: ${percentSold}%"></div>
                        </div>
                    </div>
                    <div class="row g-2 text-center mt-3">
                        <div class="col-6">
                            <div class="p-2" style="background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <small class="d-block text-muted">Prêmio</small>
                                <strong>R$ ${draw.prize_value?.toLocaleString('pt-BR')}</strong>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2" style="background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <small class="d-block text-muted">Receita</small>
                                <strong>R$ ${draw.revenue?.toLocaleString('pt-BR')}</strong>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2" style="background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <small class="d-block text-muted">Lucro</small>
                                <strong class="text-${roiColor}">
                                    R$ ${draw.profit?.toLocaleString('pt-BR')}
                                </strong>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2" style="background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <small class="d-block text-muted">ROI</small>
                                <strong class="text-${roiColor}">${draw.roi?.toFixed(2)}%</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Coletar dados agora
async function collectHoraPixNow() {
    const btn = document.getElementById('btnCollectHoraPix');
    const originalText = btn.innerHTML;

    try {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Coletando...';
        btn.disabled = true;

        const response = await fetch('/api/imperio/horapix/collect', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.status === 'success') {
            console.log('Coleta realizada com sucesso');
            // Recarregar dados
            await loadHoraPixData();
        } else {
            console.error('Erro na coleta:', result.error);
            alert('Erro ao coletar dados: ' + result.error);
        }
    } catch (error) {
        console.error('Erro ao coletar dados:', error);
        alert('Erro ao coletar dados. Verifique o console.');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Mostrar estado vazio
function showEmptyHoraPixState() {
    document.getElementById('horaPixTotalPrize').textContent = 'R$ 0,00';
    document.getElementById('horaPixDrawsCount').textContent = '0 sorteios';
    document.getElementById('horaPixTotalRevenue').textContent = 'R$ 0,00';
    document.getElementById('horaPixActiveDraws').textContent = '0 ativos';
    document.getElementById('horaPixTotalProfit').textContent = 'R$ 0,00';
    document.getElementById('horaPixFinishedDraws').textContent = '0 finalizados';
    document.getElementById('horaPixTotalROI').textContent = '0.00%';

    document.getElementById('activeDrawsList').innerHTML = `
        <div class="col-12 text-center text-muted py-5">
            <i class="fas fa-info-circle fa-3x mb-3"></i>
            <p>Nenhum dado disponível. Clique em "Atualizar Agora" para coletar.</p>
        </div>
    `;
}

// Mostrar erro
function showHoraPixError() {
    document.getElementById('activeDrawsList').innerHTML = `
        <div class="col-12 text-center text-danger py-5">
            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
            <p>Erro ao carregar dados. Tente novamente.</p>
        </div>
    `;
}

// Mostrar view Hora do Pix
function showHoraPixView() {
    const orcamentoDashboard = document.getElementById('orcamentoDashboard');
    const twoColumnView = document.getElementById('twoColumnView');
    const horaPixView = document.getElementById('horaPixView');

    if (orcamentoDashboard) orcamentoDashboard.style.display = 'none';
    if (twoColumnView) twoColumnView.style.display = 'none';
    if (horaPixView) horaPixView.style.display = 'block';

    console.log('Hora do Pix view shown');
}
