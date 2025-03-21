// Main JavaScript file for Swing Trading Journal

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    console.log('Swing Trading Journal application loaded');
    
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Dark mode toggle functionality
    initDarkMode();
    
    const riskFreeRateInput = document.getElementById('risk-free-rate-input');
    
    if (riskFreeRateInput) {
        // Set initial value from localStorage or default to 0
        const savedRiskFreeRate = localStorage.getItem('riskFreeRate') || '0';
        riskFreeRateInput.value = savedRiskFreeRate;
        
        // Update Sharpe Ratio when the input changes
        riskFreeRateInput.addEventListener('change', function() {
            const riskFreeRate = this.value;
            
            // Save to localStorage
            localStorage.setItem('riskFreeRate', riskFreeRate);
            
            // Update Sharpe Ratio
            updateSharpeRatio(riskFreeRate);
        });
        
        // Add click handler for update button
        const updateSharpeRatioButton = document.getElementById('update-sharpe-ratio');
        if (updateSharpeRatioButton) {
            updateSharpeRatioButton.addEventListener('click', function() {
                updateSharpeRatio(riskFreeRateInput.value);
            });
        }
        
        // Initial update
        updateSharpeRatio(riskFreeRateInput.value);
    }
});

// Initialize dark mode
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Check for saved dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Apply dark mode if saved preference exists
    if (isDarkMode) {
        body.classList.add('dark-mode');
        updateDarkModeIcon(true);
    }
    
    // Add click event listener to toggle
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const isDarkModeActive = body.classList.contains('dark-mode');
            
            if (isDarkModeActive) {
                body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
                updateDarkModeIcon(false);
            } else {
                body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
                updateDarkModeIcon(true);
            }
            
            // Update charts if they exist (Plotly)
            updateChartsForDarkMode();
        });
    }
}

// Update dark mode icon
function updateDarkModeIcon(isDarkMode) {
    const icon = document.querySelector('#darkModeToggle i');
    if (icon) {
        if (isDarkMode) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
}

// Update charts for dark mode
function updateChartsForDarkMode() {
    if (typeof Plotly !== 'undefined') {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const charts = document.querySelectorAll('.plotly-graph-div');
        
        charts.forEach(chart => {
            const layout = {
                paper_bgcolor: isDarkMode ? '#343a40' : '#ffffff',
                plot_bgcolor: isDarkMode ? '#343a40' : '#ffffff',
                font: {
                    color: isDarkMode ? '#f8f9fa' : '#343a40'
                }
            };
            
            Plotly.relayout(chart, layout);
        });
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format percentage
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

// Calculate profit/loss
function calculateProfitLoss(entryPrice, exitPrice, positionSize, tradeType) {
    if (tradeType === 'LONG') {
        return (exitPrice - entryPrice) * positionSize;
    } else {
        return (entryPrice - exitPrice) * positionSize;
    }
}

// Calculate profit/loss percentage
function calculateProfitLossPercentage(entryPrice, exitPrice, tradeType) {
    if (tradeType === 'LONG') {
        return ((exitPrice - entryPrice) / entryPrice) * 100;
    } else {
        return ((entryPrice - exitPrice) / entryPrice) * 100;
    }
}

// Calculate holding period in days
function calculateHoldingPeriod(entryDate, exitDate) {
    const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
    const diffDays = Math.round(Math.abs((new Date(exitDate) - new Date(entryDate)) / oneDay));
    return diffDays;
}

// Update Sharpe Ratio based on risk-free rate
function updateSharpeRatio(riskFreeRate) {
    // Get the current risk-free rate value
    const riskFreeRateValue = parseFloat(riskFreeRate) || 0;
    
    // Update the API endpoint URL with the risk-free rate parameter
    const apiUrl = `/api/stats?risk_free_rate=${riskFreeRateValue}`;
    
    // Fetch updated stats with the new risk-free rate
    fetch(apiUrl)
        .then(response => response.json())
        .then(stats => {
            // Update the Sharpe Ratio display
            const sharpeRatioElement = document.getElementById('stat-sharpe-ratio');
            if (sharpeRatioElement) {
                sharpeRatioElement.textContent = stats.sharpe_ratio.toFixed(2);
            }
        })
        .catch(error => {
            console.error('Error updating Sharpe Ratio:', error);
        });
}
