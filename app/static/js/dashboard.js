// JavaScript customizado para o Dashboard ROI

// Configurações globais do Chart.js
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatNumber(value, decimals = 2) {
    return value.toLocaleString('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Loading spinner para gráficos
function showChartLoading(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = '#6c757d';
        ctx.textAlign = 'center';
        ctx.fillText('Carregando...', canvas.width / 2, canvas.height / 2);
    }
}

// Error handling para requests
async function fetchWithErrorHandling(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erro ao buscar ${url}:`, error);
        return null;
    }
}

// Auto-refresh functionality
let autoRefreshInterval;

function startAutoRefresh(callback, intervalMs = 30000) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    autoRefreshInterval = setInterval(callback, intervalMs);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}