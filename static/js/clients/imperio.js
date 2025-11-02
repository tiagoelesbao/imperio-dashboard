// Imperio Dashboard JavaScript
let currentView = 'geral';
let charts = {};
let autoRefreshInterval;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeMenuItems();
    updateDateTime();
    loadView('geral');
    // startAutoRefresh(); // DESABILITADO - apenas manual ou scheduler backend
});

// Sidebar Toggle
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
        
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Restore saved state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }
}

// Menu Items
function initializeMenuItems() {
    const menuItems = document.querySelectorAll('.menu-item[data-view]');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            menuItems.forEach(mi => mi.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Load the view
            const view = this.dataset.view;
            loadView(view);
        });
    });
}

// Load View
async function loadView(view) {
    currentView = view;
    showLoading();
    
    try {
        const response = await fetch(`/api/imperio/${view}`);
        const data = await response.json();
        
        renderView(view, data);
        updatePageHeader(view);
    } catch (error) {
        console.error('Error loading view:', error);
        showError('Erro ao carregar dados. Tentando novamente...');
    } finally {
        hideLoading();
    }
}

// Render View
function renderView(view, data) {
    const container = document.getElementById('contentContainer');
    
    switch(view) {
        case 'geral':
            renderGeralView(data);
            break;
        case 'perfil':
            renderPerfilView(data);
            break;
        case 'grupos':
            renderGruposView(data);
            break;
        case 'comparativo':
            renderComparativoView(data);
            break;
        default:
            renderGeralView(data);
    }
}

// Render Geral View
function renderGeralView(data) {
    const container = document.getElementById('contentContainer');
    
    const html = `
        <!-- KPI Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Valor Usado</span>
                    <div class="kpi-icon warning">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.valorUsado || 0)}</div>
                <div class="kpi-change ${data.valorUsadoChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.valorUsadoChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.valorUsadoChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Vendas</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.vendas || 0)}</div>
                <div class="kpi-change ${data.vendasChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.vendasChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.vendasChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">ROI</span>
                    <div class="kpi-icon ${data.roi >= 2 ? 'success' : data.roi >= 1 ? 'warning' : 'danger'}">
                        <i class="fas fa-chart-line"></i>
                    </div>
                </div>
                <div class="kpi-value">${(data.roi || 0).toFixed(2)}</div>
                <div class="kpi-change ${data.roiChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.roiChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.roiChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Lucro</span>
                    <div class="kpi-icon ${data.lucro >= 0 ? 'success' : 'danger'}">
                        <i class="fas fa-coins"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.lucro || 0)}</div>
                <div class="kpi-change ${data.lucroChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.lucroChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.lucroChange || 0)}% vs ontem
                </div>
            </div>
        </div>
        
        <!-- Charts Row -->
        <div class="row">
            <div class="col-lg-8">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Evolução ROI por Hora</h3>
                    </div>
                    <canvas id="roiChart" height="100"></canvas>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Distribuição de Gastos</h3>
                    </div>
                    <canvas id="spendChart" height="200"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Data Table -->
        <div class="data-table-container">
            <div class="table-header">
                <h3 class="table-title">Histórico Detalhado</h3>
                <button class="btn btn-sm btn-outline-warning" onclick="exportData()">
                    <i class="fas fa-download"></i> Exportar
                </button>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Data e Hora</th>
                        <th>Valor Usado</th>
                        <th>Vendas</th>
                        <th>ROI</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
                    ${renderTableRows(data.history || [])}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Initialize charts
    setTimeout(() => {
        initializeCharts(data);
    }, 100);
}

// Render Perfil (Instagram) View
function renderPerfilView(data) {
    const container = document.getElementById('contentContainer');
    
    const html = `
        <!-- Instagram KPIs -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Ticket Médio</span>
                    <div class="kpi-icon warning">
                        <i class="fab fa-instagram"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.ticketMedio || 0)}</div>
                <div class="kpi-change positive">
                    <i class="fas fa-info-circle"></i>
                    Média por venda
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Quantidade de Vendas</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-shopping-bag"></i>
                    </div>
                </div>
                <div class="kpi-value">${data.quantidade || 0}</div>
                <div class="kpi-change ${data.quantidadeChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.quantidadeChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.quantidadeChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total Vendas</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.totalVendas || 0)}</div>
                <div class="kpi-change ${data.totalVendasChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.totalVendasChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.totalVendasChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Taxa de Conversão</span>
                    <div class="kpi-icon ${data.conversao >= 2 ? 'success' : 'warning'}">
                        <i class="fas fa-percentage"></i>
                    </div>
                </div>
                <div class="kpi-value">${(data.conversao || 0).toFixed(2)}%</div>
                <div class="kpi-change positive">
                    <i class="fas fa-chart-line"></i>
                    Performance Instagram
                </div>
            </div>
        </div>
        
        <!-- Instagram Analytics -->
        <div class="row">
            <div class="col-lg-12">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Performance Instagram - Últimos 7 dias</h3>
                    </div>
                    <canvas id="instagramChart" height="80"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Instagram Table -->
        <div class="data-table-container">
            <div class="table-header">
                <h3 class="table-title">Histórico Instagram</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Ticket Médio</th>
                        <th>Quantidade</th>
                        <th>Total</th>
                        <th>Performance</th>
                    </tr>
                </thead>
                <tbody>
                    ${renderInstagramTableRows(data.history || [])}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    setTimeout(() => {
        initializeInstagramChart(data);
    }, 100);
}

// Render Grupos View
function renderGruposView(data) {
    const container = document.getElementById('contentContainer');
    
    const html = `
        <!-- Grupos KPIs -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Ticket Médio Grupos</span>
                    <div class="kpi-icon warning">
                        <i class="fas fa-users"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.ticketMedio || 0)}</div>
                <div class="kpi-change positive">
                    <i class="fas fa-info-circle"></i>
                    Média consolidada
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total de Vendas</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                </div>
                <div class="kpi-value">${data.quantidade || 0}</div>
                <div class="kpi-change ${data.quantidadeChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.quantidadeChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.quantidadeChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Receita Total</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.totalVendas || 0)}</div>
                <div class="kpi-change ${data.totalVendasChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.totalVendasChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.totalVendasChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Grupos Ativos</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-check-circle"></i>
                    </div>
                </div>
                <div class="kpi-value">${data.gruposAtivos || 2}</div>
                <div class="kpi-change positive">
                    <i class="fas fa-users"></i>
                    WhatsApp + Telegram
                </div>
            </div>
        </div>
        
        <!-- Groups Performance -->
        <div class="row">
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Comparativo de Grupos</h3>
                    </div>
                    <canvas id="groupsCompareChart" height="150"></canvas>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Evolução Grupos - 7 dias</h3>
                    </div>
                    <canvas id="groupsTrendChart" height="150"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Groups Table -->
        <div class="data-table-container">
            <div class="table-header">
                <h3 class="table-title">Detalhamento por Grupo</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Grupo</th>
                        <th>Ticket Médio</th>
                        <th>Quantidade</th>
                        <th>Total</th>
                        <th>Performance</th>
                    </tr>
                </thead>
                <tbody>
                    ${renderGruposTableRows(data.history || [])}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    setTimeout(() => {
        initializeGruposCharts(data);
    }, 100);
}

// Render Comparativo View
function renderComparativoView(data) {
    const container = document.getElementById('contentContainer');
    
    const html = `
        <!-- Comparativo Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> Comparativo entre todos os canais de venda
                </div>
            </div>
        </div>
        
        <!-- Comparativo KPIs -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Melhor Canal</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-trophy"></i>
                    </div>
                </div>
                <div class="kpi-value">${data.melhorCanal || 'Instagram'}</div>
                <div class="kpi-change positive">
                    <i class="fas fa-crown"></i>
                    Maior ROI
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total Consolidado</span>
                    <div class="kpi-icon warning">
                        <i class="fas fa-calculator"></i>
                    </div>
                </div>
                <div class="kpi-value">R$ ${formatNumber(data.totalConsolidado || 0)}</div>
                <div class="kpi-change positive">
                    <i class="fas fa-plus"></i>
                    Soma todos canais
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">ROI Médio</span>
                    <div class="kpi-icon ${data.roiMedio >= 2 ? 'success' : 'warning'}">
                        <i class="fas fa-chart-line"></i>
                    </div>
                </div>
                <div class="kpi-value">${(data.roiMedio || 0).toFixed(2)}</div>
                <div class="kpi-change ${data.roiMedioChange >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${data.roiMedioChange >= 0 ? 'up' : 'down'}"></i>
                    ${Math.abs(data.roiMedioChange || 0)}% vs ontem
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Eficiência</span>
                    <div class="kpi-icon success">
                        <i class="fas fa-tachometer-alt"></i>
                    </div>
                </div>
                <div class="kpi-value">${(data.eficiencia || 0).toFixed(1)}%</div>
                <div class="kpi-change positive">
                    <i class="fas fa-check"></i>
                    Taxa de conversão geral
                </div>
            </div>
        </div>
        
        <!-- Comparative Charts -->
        <div class="row">
            <div class="col-lg-12">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Comparativo de Canais</h3>
                    </div>
                    <canvas id="comparativoChart" height="100"></canvas>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Distribuição de Vendas</h3>
                    </div>
                    <canvas id="distributionChart" height="150"></canvas>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3 class="chart-title">Tendência ROI - 30 dias</h3>
                    </div>
                    <canvas id="trendChart" height="150"></canvas>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    setTimeout(() => {
        initializeComparativoCharts(data);
    }, 100);
}

// Initialize Charts
function initializeCharts(data) {
    // ROI Evolution Chart
    const roiCtx = document.getElementById('roiChart');
    if (roiCtx) {
        if (charts.roi) charts.roi.destroy();
        
        charts.roi = new Chart(roiCtx, {
            type: 'line',
            data: {
                labels: data.labels || generateHourLabels(),
                datasets: [{
                    label: 'ROI',
                    data: data.roiData || [],
                    borderColor: '#ffd700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
    
    // Spend Distribution Chart
    const spendCtx = document.getElementById('spendChart');
    if (spendCtx) {
        if (charts.spend) charts.spend.destroy();
        
        charts.spend = new Chart(spendCtx, {
            type: 'doughnut',
            data: {
                labels: ['Facebook Ads', 'Google Ads', 'Instagram', 'Outros'],
                datasets: [{
                    data: data.spendData || [45, 30, 20, 5],
                    backgroundColor: [
                        '#3b5998',
                        '#4285f4',
                        '#e1306c',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
}

// Initialize Instagram Chart
function initializeInstagramChart(data) {
    const ctx = document.getElementById('instagramChart');
    if (ctx) {
        if (charts.instagram) charts.instagram.destroy();
        
        charts.instagram = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || generateDayLabels(7),
                datasets: [{
                    label: 'Vendas',
                    data: data.salesData || [],
                    backgroundColor: '#e1306c',
                    borderRadius: 5
                }, {
                    label: 'Ticket Médio',
                    data: data.ticketData || [],
                    backgroundColor: '#ffd700',
                    borderRadius: 5,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#8f9397'
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
}

// Initialize Grupos Charts
function initializeGruposCharts(data) {
    // Compare Chart
    const compareCtx = document.getElementById('groupsCompareChart');
    if (compareCtx) {
        if (charts.groupsCompare) charts.groupsCompare.destroy();
        
        charts.groupsCompare = new Chart(compareCtx, {
            type: 'bar',
            data: {
                labels: ['WhatsApp', 'Telegram'],
                datasets: [{
                    label: 'Vendas Hoje',
                    data: data.compareData || [150000, 120000],
                    backgroundColor: ['#25d366', '#0088cc']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397',
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
    
    // Trend Chart
    const trendCtx = document.getElementById('groupsTrendChart');
    if (trendCtx) {
        if (charts.groupsTrend) charts.groupsTrend.destroy();
        
        charts.groupsTrend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: generateDayLabels(7),
                datasets: [{
                    label: 'WhatsApp',
                    data: data.whatsappTrend || [],
                    borderColor: '#25d366',
                    backgroundColor: 'rgba(37, 211, 102, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Telegram',
                    data: data.telegramTrend || [],
                    borderColor: '#0088cc',
                    backgroundColor: 'rgba(0, 136, 204, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#8f9397'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
}

// Initialize Comparativo Charts
function initializeComparativoCharts(data) {
    // Main Comparison Chart
    const mainCtx = document.getElementById('comparativoChart');
    if (mainCtx) {
        if (charts.comparativo) charts.comparativo.destroy();
        
        charts.comparativo = new Chart(mainCtx, {
            type: 'bar',
            data: {
                labels: ['Geral', 'Instagram', 'WhatsApp', 'Telegram'],
                datasets: [{
                    label: 'Vendas',
                    data: data.vendasComparativo || [500000, 200000, 150000, 120000],
                    backgroundColor: '#ffd700'
                }, {
                    label: 'Gastos',
                    data: data.gastosComparativo || [250000, 80000, 70000, 60000],
                    backgroundColor: '#fc424a'
                }, {
                    label: 'ROI',
                    data: data.roiComparativo || [2.0, 2.5, 2.14, 2.0],
                    backgroundColor: '#00d25b',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#8f9397'
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397',
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
    
    // Distribution Chart
    const distCtx = document.getElementById('distributionChart');
    if (distCtx) {
        if (charts.distribution) charts.distribution.destroy();
        
        charts.distribution = new Chart(distCtx, {
            type: 'pie',
            data: {
                labels: ['Instagram', 'WhatsApp', 'Telegram', 'Outros'],
                datasets: [{
                    data: data.distributionData || [40, 30, 24, 6],
                    backgroundColor: [
                        '#e1306c',
                        '#25d366',
                        '#0088cc',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
    
    // Trend Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        if (charts.trend) charts.trend.destroy();
        
        charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: generateDayLabels(30),
                datasets: [{
                    label: 'ROI Médio',
                    data: data.trendData || [],
                    borderColor: '#ffd700',
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#8f9397'
                        }
                    }
                }
            }
        });
    }
}

// Helper Functions
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

function generateHourLabels() {
    const labels = [];
    for (let i = 0; i < 24; i++) {
        labels.push(`${i.toString().padStart(2, '0')}:00`);
    }
    return labels;
}

function generateDayLabels(days) {
    const labels = [];
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
    }
    return labels;
}

function renderTableRows(history) {
    if (!history || history.length === 0) {
        return '<tr><td colspan="5" class="text-center">Nenhum dado disponível</td></tr>';
    }
    
    return history.map(row => {
        const roiClass = row.roi >= 2 ? 'high' : row.roi >= 1 ? 'medium' : 'low';
        return `
            <tr>
                <td>${row.dateTime}</td>
                <td>R$ ${formatNumber(row.valorUsado)}</td>
                <td>R$ ${formatNumber(row.vendas)}</td>
                <td><span class="roi-badge ${roiClass}">${row.roi.toFixed(2)}</span></td>
                <td>${getStatusBadge(row.roi)}</td>
            </tr>
        `;
    }).join('');
}

function renderInstagramTableRows(history) {
    if (!history || history.length === 0) {
        return '<tr><td colspan="5" class="text-center">Nenhum dado disponível</td></tr>';
    }
    
    return history.map(row => {
        return `
            <tr>
                <td>${row.date}</td>
                <td>R$ ${formatNumber(row.ticketMedio)}</td>
                <td>${row.quantidade}</td>
                <td>R$ ${formatNumber(row.total)}</td>
                <td>${getPerformanceBadge(row.performance)}</td>
            </tr>
        `;
    }).join('');
}

function renderGruposTableRows(history) {
    if (!history || history.length === 0) {
        return '<tr><td colspan="6" class="text-center">Nenhum dado disponível</td></tr>';
    }
    
    return history.map(row => {
        return `
            <tr>
                <td>${row.date}</td>
                <td>${row.grupo}</td>
                <td>R$ ${formatNumber(row.ticketMedio)}</td>
                <td>${row.quantidade}</td>
                <td>R$ ${formatNumber(row.total)}</td>
                <td>${getPerformanceBadge(row.performance)}</td>
            </tr>
        `;
    }).join('');
}

function getStatusBadge(roi) {
    if (roi >= 2) {
        return '<span class="badge bg-success">Excelente</span>';
    } else if (roi >= 1) {
        return '<span class="badge bg-warning">Bom</span>';
    } else {
        return '<span class="badge bg-danger">Atenção</span>';
    }
}

function getPerformanceBadge(performance) {
    if (performance >= 90) {
        return '<span class="badge bg-success">Ótimo</span>';
    } else if (performance >= 70) {
        return '<span class="badge bg-warning">Bom</span>';
    } else {
        return '<span class="badge bg-danger">Regular</span>';
    }
}

// Update Page Header
function updatePageHeader(view) {
    const titles = {
        'geral': 'Visão Geral',
        'perfil': 'Instagram',
        'grupos': 'Grupos',
        'comparativo': 'Comparativo'
    };
    
    const subtitles = {
        'geral': 'Dashboard completo com métricas consolidadas',
        'perfil': 'Análise de performance do Instagram',
        'grupos': 'Performance dos grupos WhatsApp e Telegram',
        'comparativo': 'Comparação entre todos os canais'
    };
    
    document.getElementById('pageTitle').textContent = titles[view] || 'Dashboard';
    document.getElementById('pageSubtitle').innerHTML = `
        <span id="currentDateTime"></span> | ${subtitles[view] || 'Atualização automática a cada 30 minutos'}
    `;
    
    updateDateTime();
}

// Update Date/Time
function updateDateTime() {
    const now = new Date();
    const formatted = now.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const elem = document.getElementById('currentDateTime');
    if (elem) {
        elem.textContent = formatted;
    }
}

// Loading States
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showError(message) {
    console.error(message);
    // Could show a toast notification here
}

// Auto Refresh - DESABILITADO
function startAutoRefresh() {
    // COLETAS AUTOMÁTICAS DESABILITADAS NO FRONTEND
    // Apenas o scheduler backend fará coletas a cada 30 min
    // autoRefreshInterval = setInterval(() => {
    //     loadView(currentView);
    // }, 30 * 60 * 1000);
    
    // Update datetime every minute (mantido)
    setInterval(updateDateTime, 60 * 1000);
}

// Export Data
function exportData() {
    window.location.href = `/api/imperio/export/${currentView}`;
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});