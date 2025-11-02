// ============================================
// AÇÃO PRINCIPAL - JAVASCRIPT
// ============================================

// Variável global para armazenar dados
let mainActionData = {
    actions: [],
    yearly: {}
};

// Mostrar modal de adicionar ação
function showAddActionModal() {
    document.getElementById('addActionModal').style.display = 'flex';
    document.getElementById('new-action-id').value = '';
    document.getElementById('add-action-error').style.display = 'none';
}

// Fechar modal de adicionar ação
function closeAddActionModal() {
    document.getElementById('addActionModal').style.display = 'none';
}

// Adicionar nova ação
async function addNewAction() {
    const productId = document.getElementById('new-action-id').value.trim();
    const errorDiv = document.getElementById('add-action-error');
    const errorMessage = document.getElementById('add-action-error-message');
    const submitBtn = document.getElementById('add-action-submit-btn');

    if (!productId) {
        errorMessage.textContent = 'Por favor, insira o ID do produto/sorteio.';
        errorDiv.style.display = 'block';
        return;
    }

    // Desabilitar botão e mostrar loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 5px;"></i>Coletando dados...';
    errorDiv.style.display = 'none';

    try {
        // Chamar API para coletar dados
        const response = await fetch('/api/main-action/collect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            // Sucesso - fechar modal e recarregar dados
            closeAddActionModal();
            await loadMainActionData();

            // Mostrar mensagem de sucesso
            showSuccessMessage('Ação adicionada com sucesso! Os dados estão sendo coletados.');
        } else {
            // Erro
            errorMessage.textContent = result.detail || 'Erro ao adicionar ação. Verifique o ID e tente novamente.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Erro ao adicionar ação:', error);
        errorMessage.textContent = 'Erro ao conectar com o servidor. Tente novamente.';
        errorDiv.style.display = 'block';
    } finally {
        // Reativar botão
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus" style="margin-right: 5px;"></i>Adicionar e Coletar Dados';
    }
}

// Mostrar mensagem de sucesso
function showSuccessMessage(message) {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #52c41a, #73d13d);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        font-weight: 600;
    `;
    notification.innerHTML = `<i class="fas fa-check-circle" style="margin-right: 10px;"></i>${message}`;

    document.body.appendChild(notification);

    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Carregar dados da Ação Principal
async function loadMainActionData() {
    try {
        console.log('Carregando dados da Ação Principal...');

        // Mostrar loading
        document.getElementById('acaoprincipal-loading').style.display = 'block';
        document.getElementById('acaoprincipal-error').style.display = 'none';
        document.getElementById('acaoprincipal-content').style.display = 'none';

        // Buscar ano selecionado
        const yearFilter = document.getElementById('action-year-filter');
        const year = yearFilter ? yearFilter.value : '2025';

        // Buscar dados da API
        const response = await fetch(`/api/main-action/all?year=${year}`);
        const result = await response.json();

        if (result.status === 'success' && result.data) {
            mainActionData.actions = result.data.actions || [];
            mainActionData.yearly = result.data.yearly_summary || {};

            // Renderizar dados
            renderMainActionData();

            // Ocultar loading e mostrar conteúdo
            document.getElementById('acaoprincipal-loading').style.display = 'none';
            document.getElementById('acaoprincipal-content').style.display = 'block';
        } else {
            throw new Error(result.message || 'Erro ao carregar dados');
        }
    } catch (error) {
        console.error('Erro ao carregar Ação Principal:', error);

        // Mostrar erro
        document.getElementById('acaoprincipal-loading').style.display = 'none';
        document.getElementById('acaoprincipal-error').style.display = 'block';
        document.getElementById('acaoprincipal-error-message').textContent = error.message;
    }
}

// Renderizar todos os dados
function renderMainActionData() {
    renderKPICards();
    renderActionsList();
}

// Renderizar KPI Cards no topo
function renderKPICards() {
    const container = document.getElementById('acaoprincipal-kpi-cards');
    const yearly = mainActionData.yearly;

    const cards = [
        {
            label: 'Receita Total',
            value: formatActionCurrency(yearly.total_revenue || 0),
            subtitle: `${mainActionData.actions.length} ações`,
            class: 'success'
        },
        {
            label: 'Custos Facebook',
            value: formatActionCurrency(yearly.total_fb_cost || 0),
            subtitle: 'Investimento'
        },
        {
            label: 'Taxa 3%',
            value: formatActionCurrency(yearly.total_platform_fee || 0),
            subtitle: 'Plataforma'
        },
        {
            label: 'Lucro Total',
            value: formatActionCurrency(yearly.total_profit || 0),
            subtitle: `ROI: ${(yearly.avg_roi || 0).toFixed(2)}%`,
            class: (yearly.total_profit || 0) > 0 ? 'success' : ''
        }
    ];

    container.innerHTML = cards.map(card => `
        <div class="action-kpi-card ${card.class || ''}">
            <div class="kpi-label">${card.label}</div>
            <div class="kpi-value">${card.value}</div>
            <div class="kpi-subtitle">${card.subtitle}</div>
        </div>
    `).join('');
}

// Renderizar lista de ações
function renderActionsList() {
    const container = document.getElementById('acaoprincipal-actions-list');
    const emptyState = document.getElementById('acaoprincipal-empty');
    const actions = mainActionData.actions;

    if (!actions || actions.length === 0) {
        container.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    container.innerHTML = actions.map(action => {
        // Determinar status
        let statusClass, statusLabel;
        if (action.is_current) {
            statusClass = 'current';
            statusLabel = 'Vigente';
        } else if (action.is_active) {
            statusClass = 'active';
            statusLabel = 'Ativa';
        } else {
            statusClass = 'finished';
            statusLabel = 'Finalizada';
        }

        return `
            <div class="action-bar" id="action-${action.id}">
                <div class="action-bar-header" onclick="toggleActionDetails(${action.id})">
                    <div class="action-bar-title">
                        <span class="action-status-badge ${statusClass}">${statusLabel}</span>
                        <div class="action-bar-info">
                            <div class="action-bar-name">${action.name || 'Sem nome'}</div>
                            <div class="action-bar-prize">Prêmio: ${formatActionCurrency(action.prize_value || 0)}</div>
                        </div>
                    </div>
                    <div class="action-bar-metrics">
                        <div class="action-metric">
                            <div class="action-metric-label">Receita</div>
                            <div class="action-metric-value">${formatActionCurrency(action.total_revenue || 0)}</div>
                        </div>
                        <div class="action-metric">
                            <div class="action-metric-label">Lucro</div>
                            <div class="action-metric-value">${formatActionCurrency(action.total_profit || 0)}</div>
                        </div>
                        <div class="action-metric">
                            <div class="action-metric-label">ROI</div>
                            <div class="action-metric-value" style="color: ${(action.total_roi || 0) >= 0 ? '#52c41a' : '#ff4d4f'};">
                                ${(action.total_roi || 0).toFixed(2)}%
                            </div>
                        </div>
                    </div>
                    <i class="fas fa-chevron-down action-expand-icon"></i>
                </div>
                <div class="action-details" id="action-details-${action.id}">
                    <!-- Detalhes carregados via JS -->
                </div>
            </div>
        `;
    }).join('');
}

// Toggle de expandir/recolher ação
async function toggleActionDetails(actionId) {
    const actionBar = document.getElementById(`action-${actionId}`);
    const detailsDiv = document.getElementById(`action-details-${actionId}`);

    // Se já está expandido, recolher
    if (actionBar.classList.contains('expanded')) {
        actionBar.classList.remove('expanded');
        detailsDiv.style.display = 'none';
        return;
    }

    // Expandir e carregar detalhes
    actionBar.classList.add('expanded');
    detailsDiv.style.display = 'block';

    // Se já tem conteúdo, não recarregar
    if (detailsDiv.innerHTML.trim()) {
        return;
    }

    // Mostrar loading
    detailsDiv.innerHTML = `
        <div style="text-align: center; padding: 30px;">
            <i class="fas fa-spinner fa-spin" style="font-size: 24px; color: #FFD700;"></i>
            <p style="color: #999; margin-top: 10px;">Carregando detalhes...</p>
        </div>
    `;

    try {
        // Buscar detalhes da API
        const response = await fetch(`/api/main-action/${actionId}/details`);
        const result = await response.json();

        if (result.status === 'success' && result.data) {
            renderActionDetails(actionId, result.data);
        } else {
            detailsDiv.innerHTML = `
                <div style="text-align: center; padding: 30px;">
                    <p style="color: #ff6b6b;">Erro ao carregar detalhes</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        detailsDiv.innerHTML = `
            <div style="text-align: center; padding: 30px;">
                <p style="color: #ff6b6b;">Erro ao carregar detalhes</p>
                <p style="color: #999; font-size: 12px;">${error.message}</p>
            </div>
        `;
    }
}

// Renderizar detalhes completos de uma ação
function renderActionDetails(actionId, data) {
    const detailsDiv = document.getElementById(`action-details-${actionId}`);
    const action = data.action || data;
    const dailyData = data.daily_records || data.daily || [];

    // Informações gerais
    const infoSection = `
        <div class="action-details-header">
            <div class="action-detail-item">
                <div class="action-detail-label">Product ID</div>
                <div class="action-detail-value">${action.product_id || 'N/A'}</div>
            </div>
            <div class="action-detail-item">
                <div class="action-detail-label">Período</div>
                <div class="action-detail-value">${formatActionDate(action.start_date)} até ${action.end_date ? formatActionDate(action.end_date) : 'Em andamento'}</div>
            </div>
            <div class="action-detail-item">
                <div class="action-detail-label">Duração</div>
                <div class="action-detail-value">${dailyData.length} dias registrados</div>
            </div>
            <div class="action-detail-item">
                <div class="action-detail-label">Status</div>
                <div class="action-detail-value">
                    ${action.is_current ? '<span style="color: #52c41a;">✓ Vigente</span>' :
                      (action.is_active ? '<span style="color: #faad14;">● Ativa</span>' :
                       '<span style="color: #999;">● Finalizada</span>')}
                </div>
            </div>
        </div>
    `;

    // Tabela de dados diários
    let tableHTML = '';
    if (dailyData.length > 0) {
        // Calcular totais - usando os campos corretos do modelo
        const totals = dailyData.reduce((acc, day) => ({
            revenue: acc.revenue + (day.daily_revenue || 0),
            orders: acc.orders + (day.daily_orders || 0),
            tickets: acc.tickets + (day.daily_tickets || 0),
            fb_cost: acc.fb_cost + (day.daily_fb_cost || 0),
            fee: acc.fee + (day.daily_platform_fee || 0),
            profit: acc.profit + (day.daily_profit || 0)
        }), { revenue: 0, orders: 0, tickets: 0, fb_cost: 0, fee: 0, profit: 0 });

        const avgROI = totals.fb_cost > 0 ? ((totals.profit / totals.fb_cost) * 100) : 0;

        tableHTML = `
            <h4 style="color: #FFD700; margin: 20px 0 15px 0; font-size: 16px;">
                <i class="fas fa-chart-line" style="margin-right: 8px;"></i>Detalhamento Diário
            </h4>
            <table class="action-daily-table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Receita</th>
                        <th>Pedidos</th>
                        <th>Números</th>
                        <th>Facebook Ads</th>
                        <th>Taxa 3%</th>
                        <th>Lucro</th>
                        <th>ROI</th>
                    </tr>
                </thead>
                <tbody>
                    ${dailyData.map(day => {
                        const roi = day.daily_roi || 0;
                        const roiClass = roi >= 0 ? 'roi-positive' : 'roi-negative';
                        const profitClass = (day.daily_profit || 0) >= 0 ? 'roi-positive' : 'roi-negative';

                        return `
                            <tr>
                                <td class="date-cell">${formatActionDate(day.date)}</td>
                                <td class="value-cell">${formatActionCurrency(day.daily_revenue || 0)}</td>
                                <td style="text-align: center;">${day.daily_orders || 0}</td>
                                <td style="text-align: center;">${day.daily_tickets || 0}</td>
                                <td class="value-cell">${formatActionCurrency(day.daily_fb_cost || 0)}</td>
                                <td class="value-cell">${formatActionCurrency(day.daily_platform_fee || 0)}</td>
                                <td class="value-cell ${profitClass}">${formatActionCurrency(day.daily_profit || 0)}</td>
                                <td class="roi-cell ${roiClass}">${roi.toFixed(2)}%</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
                <tfoot>
                    <tr>
                        <td><strong>TOTAIS</strong></td>
                        <td>${formatActionCurrency(totals.revenue)}</td>
                        <td style="text-align: center;">${totals.orders}</td>
                        <td style="text-align: center;">${totals.tickets}</td>
                        <td>${formatActionCurrency(totals.fb_cost)}</td>
                        <td>${formatActionCurrency(totals.fee)}</td>
                        <td class="${totals.profit >= 0 ? 'roi-positive' : 'roi-negative'}">${formatActionCurrency(totals.profit)}</td>
                        <td class="${avgROI >= 0 ? 'roi-positive' : 'roi-negative'}">${avgROI.toFixed(2)}%</td>
                    </tr>
                </tfoot>
            </table>
        `;
    } else {
        tableHTML = `
            <div style="text-align: center; padding: 30px;">
                <i class="fas fa-inbox" style="font-size: 36px; color: #666;"></i>
                <p style="color: #999; margin-top: 15px;">Nenhum dado diário disponível</p>
            </div>
        `;
    }

    detailsDiv.innerHTML = infoSection + tableHTML;
}

// Formatar moeda (usando função existente ou criando se não existir)
function formatActionCurrency(value) {
    if (typeof formatCurrency === 'function') {
        return formatCurrency(value);
    }
    return `R$ ${(value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Formatar data (usando função existente ou criando se não existir)
function formatActionDate(dateString) {
    if (typeof formatDate === 'function') {
        return formatDate(dateString);
    }
    if (!dateString) return 'N/A';
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}

// Inicializar quando abrir a view
function showMainActionView() {
    // Ocultar outras views
    const orcamentoDashboard = document.getElementById('orcamentoDashboard');
    const twoColumnView = document.getElementById('twoColumnView');
    const horaPixView = document.getElementById('horaPixView');
    const acaoPrincipalView = document.getElementById('acaoprincipal-view');

    if (orcamentoDashboard) orcamentoDashboard.style.display = 'none';
    if (twoColumnView) twoColumnView.style.display = 'none';
    if (horaPixView) horaPixView.style.display = 'none';

    // Mostrar a view
    if (acaoPrincipalView) acaoPrincipalView.style.display = 'block';

    // Trocar logo de volta para Império
    updateLogoForView('default');

    // Carregar dados se ainda não carregou
    if (mainActionData.actions.length === 0) {
        loadMainActionData();
    }

    console.log('Ação Principal view shown');
}
