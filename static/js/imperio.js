/**
 * Imperio Dashboard - Super Simple Version
 */

// Global variables
let dashboard = null;

// Simple data structure
const mockData = {
    cumulativeData: [
        {
            dateTime: "13/08/2025 09:30:00",
            valorUsado: 1200.00,
            vendas: 2800.00,
            roi: 2.33
        },
        {
            dateTime: "13/08/2025 10:15:00", 
            valorUsado: 1580.50,
            vendas: 3420.80,
            roi: 2.16
        },
        {
            dateTime: "13/08/2025 11:00:00",
            valorUsado: 2059.19,
            vendas: 4524.84,
            roi: 2.20
        },
        {
            dateTime: "13/08/2025 11:30:00",
            valorUsado: 2350.75,
            vendas: 5120.40,
            roi: 2.18
        }
    ],
    intervalData: [
        {
            dateTime: "13/08/2025 09:00:00 às 09:30:00",
            valorUsado: 180.25,
            vendas: 420.15,
            roi: 2.33
        },
        {
            dateTime: "13/08/2025 09:30:00 às 10:00:00",
            valorUsado: 200.50,
            vendas: 380.30,
            roi: 1.90
        },
        {
            dateTime: "13/08/2025 10:00:00 às 10:30:00",
            valorUsado: 239.51,
            vendas: 620.80,
            roi: 2.59
        },
        {
            dateTime: "13/08/2025 10:30:00 às 11:00:00",
            valorUsado: 291.25,
            vendas: 695.60,
            roi: 2.39
        }
    ]
};

// Utility functions
function formatCurrency(value) {
    if (!value || isNaN(value)) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatROI(roi) {
    if (!roi || isNaN(roi)) return '0.00';
    return parseFloat(roi).toFixed(2);
}

function getROIClass(roi) {
    const value = parseFloat(roi) || 0;
    if (value >= 2.0) return 'roi-excellent';
    if (value >= 1.0) return 'roi-good';
    return 'roi-attention';
}

function getStatusDot(roi) {
    const value = parseFloat(roi) || 0;
    let statusClass = 'status-attention';
    
    if (value >= 2.0) {
        statusClass = 'status-excellent';
    } else if (value >= 1.0) {
        statusClass = 'status-good';
    }
    
    return `<span class="status-dot ${statusClass}"></span>`;
}

// Main functions
function populateTable(tableId, data) {
    console.log('Populating table:', tableId, 'with data:', data);
    
    const tbody = document.getElementById(tableId);
    if (!tbody) {
        console.error('Table element not found:', tableId);
        return;
    }
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">Nenhum dado disponível</td></tr>';
        return;
    }
    
    let html = '';
    data.forEach(row => {
        html += `
            <tr>
                <td class="datetime">${row.dateTime}</td>
                <td class="currency">${formatCurrency(row.valorUsado)}</td>
                <td class="currency">${formatCurrency(row.vendas)}</td>
                <td><span class="${getROIClass(row.roi)}">${formatROI(row.roi)}</span></td>
                <td>${getStatusDot(row.roi)}</td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
    console.log('Table populated successfully:', tableId);
}

function loadAllData() {
    console.log('Loading all data...');
    populateTable('cumulativeData', mockData.cumulativeData);
    populateTable('intervalData', mockData.intervalData);
    console.log('All data loaded!');
}

// Global functions for HTML onclick events
window.applyDateFilter = function() {
    console.log('Apply date filter clicked');
    const dateInput = document.getElementById('dateFilter');
    if (!dateInput || !dateInput.value) {
        alert('Selecione uma data primeiro');
        return;
    }
    
    const selectedDate = dateInput.value;
    const [year, month, day] = selectedDate.split('-');
    const targetDate = `${day}/${month}/${year}`;
    
    console.log('Filtering by date:', targetDate);
    
    // Filter data
    const filteredCumulative = mockData.cumulativeData.filter(row => 
        row.dateTime.includes(targetDate)
    );
    const filteredInterval = mockData.intervalData.filter(row => 
        row.dateTime.includes(targetDate)
    );
    
    populateTable('cumulativeData', filteredCumulative);
    populateTable('intervalData', filteredInterval);
    
    if (filteredCumulative.length === 0 && filteredInterval.length === 0) {
        alert(`Nenhum dado encontrado para a data ${targetDate}`);
    }
};

window.clearDateFilter = function() {
    console.log('Clear date filter clicked');
    const dateInput = document.getElementById('dateFilter');
    if (dateInput) {
        dateInput.value = '';
    }
    loadAllData();
};

window.forceLoadData = function() {
    console.log('Force load data clicked');
    loadAllData();
};

// Navigation functions
function setupNavigation() {
    console.log('Setting up navigation');
    const menuItems = document.querySelectorAll('.menu-item[data-view]');
    
    menuItems.forEach(item => {
        if (item && item.addEventListener) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const view = this.getAttribute('data-view');
                console.log('Menu clicked:', view);
                
                // Update active menu item
                menuItems.forEach(mi => mi.classList.remove('active'));
                this.classList.add('active');
                
                // Update URL hash
                window.location.hash = view;
                
                // Update titles
                updateColumnTitles(view);
            });
        }
    });
    
    // Handle hash changes
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1);
        if (hash && ['geral', 'perfil', 'grupos'].includes(hash)) {
            updateActiveMenuItem(hash);
            updateColumnTitles(hash);
        }
    });
}

function updateActiveMenuItem(view) {
    const menuItems = document.querySelectorAll('.menu-item[data-view]');
    menuItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-view') === view) {
            item.classList.add('active');
        }
    });
}

function updateColumnTitles(view) {
    const titles = {
        'geral': {
            leftTitle: 'Data e Hora ↓',
            leftSubtitle: 'Valor Usado | Vendas | ROI (Cumulativo)',
            rightTitle: 'Data e Hora ↓',
            rightSubtitle: 'Valor Usado | Vendas | ROI (Última Faixa 30min)'
        },
        'perfil': {
            leftTitle: 'Data e Hora ↓',
            leftSubtitle: 'Valor Usado | Vendas | ROI (Instagram Total)',
            rightTitle: 'Data e Hora ↓',
            rightSubtitle: 'Valor Usado | Vendas | ROI (Instagram Faixa 30min)'
        },
        'grupos': {
            leftTitle: 'Data e Hora ↓',
            leftSubtitle: 'Valor Usado | Vendas | ROI (Grupos Total)',
            rightTitle: 'Data e Hora ↓',
            rightSubtitle: 'Valor Usado | Vendas | ROI (Grupos Faixa 30min)'
        }
    };

    const config = titles[view] || titles['geral'];
    
    const leftTitle = document.getElementById('leftColumnTitle');
    const leftSubtitle = document.getElementById('leftColumnSubtitle');
    const rightTitle = document.getElementById('rightColumnTitle');
    const rightSubtitle = document.getElementById('rightColumnSubtitle');
    
    if (leftTitle) leftTitle.textContent = config.leftTitle;
    if (leftSubtitle) leftSubtitle.textContent = config.leftSubtitle;
    if (rightTitle) rightTitle.textContent = config.rightTitle;
    if (rightSubtitle) rightSubtitle.textContent = config.rightSubtitle;
}

function setTodayDate() {
    const dateInput = document.getElementById('dateFilter');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
        console.log('Set today date:', today);
    }
}

// Initialize everything
function initDashboard() {
    console.log('Initializing Imperio Dashboard - Simple Version');
    
    // Set today's date
    setTodayDate();
    
    // Setup navigation
    setupNavigation();
    
    // Load initial view
    const hash = window.location.hash.substring(1) || 'geral';
    updateActiveMenuItem(hash);
    updateColumnTitles(hash);
    
    // Load data
    loadAllData();
    
    console.log('Dashboard initialized successfully!');
}

// Wait for DOM to load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

// Backup initialization
setTimeout(function() {
    if (!document.getElementById('cumulativeData') || !document.getElementById('intervalData')) {
        console.log('Elements still not found, trying again...');
        setTimeout(initDashboard, 1000);
    } else {
        console.log('Elements found, forcing data load...');
        loadAllData();
    }
}, 2000);

console.log('Imperio.js loaded successfully!');