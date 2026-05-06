// ============================================
// Expense Tracker - Complete Frontend Application
// ============================================

const API_BASE = 'http://localhost:8000';
let currentPage = 1;
const itemsPerPage = 10;
let charts = {};
let notifications = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNavigation();
    initDateInputs();
    loadDashboard();
    setupEventListeners();
    checkNotifications();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
    // Re-render charts with new colors
    setTimeout(() => loadDashboard(), 100);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggle');
    const icon = btn.querySelector('i');
    const text = btn.querySelector('span');
    if (theme === 'dark') {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
    } else {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark Mode';
    }
}

// Navigation
function initNavigation() {
    const menuItems = document.querySelectorAll('.sidebar-menu li');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            if (page) switchPage(page);
        });
    });

    document.getElementById('sidebarToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
}

function switchPage(pageId) {
    // Update sidebar
    document.querySelectorAll('.sidebar-menu li').forEach(li => {
        li.classList.toggle('active', li.dataset.page === pageId);
    });

    // Update pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.toggle('active', page.id === pageId);
    });

    // Load page data
    switch(pageId) {
        case 'dashboard': loadDashboard(); break;
        case 'transactions': loadTransactions(); break;
        case 'budgets': loadBudgets(); break;
        case 'goals': loadGoals(); break;
        case 'recurring': loadRecurring(); break;
        case 'analytics': loadAnalytics(); break;
    }
}

// Date Inputs Default Values
function initDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    const firstDay = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
    
    document.getElementById('expenseDate').value = today;
    document.getElementById('budgetStartDate').value = firstDay;
    document.getElementById('recurringDate').value = today;
    document.getElementById('filterStartDate').value = firstDay;
    document.getElementById('filterEndDate').value = today;
}

// ============================================
// API Helpers
// ============================================

async function api(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        return await response.json();
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// ============================================
// Dashboard
// ============================================

async function loadDashboard() {
    try {
        const data = await api('/analytics/dashboard');
        
        // Update stats
        document.getElementById('monthlyIncome').textContent = formatCurrency(data.monthly_income);
        document.getElementById('monthlyExpenses').textContent = formatCurrency(data.monthly_expenses);
        document.getElementById('monthlySavings').textContent = formatCurrency(data.monthly_savings);
        document.getElementById('netBalance').textContent = formatCurrency(data.total_balance);
        document.getElementById('savingsRate').textContent = `${data.savings_rate}% savings rate`;

        // Recent transactions
        renderRecentTransactions(data.recent_transactions);

        // Budget alerts
        renderBudgetAlerts(data.budget_alerts);

        // Upcoming bills
        renderUpcomingBills(data.upcoming_bills);

        // Charts
        renderSpendingChart();
        renderCategoryChart(data.top_categories);

    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

function renderRecentTransactions(transactions) {
    const container = document.getElementById('recentTransactions');
    if (!transactions || transactions.length === 0) {
        container.innerHTML = emptyState('No recent transactions');
        return;
    }

    container.innerHTML = transactions.map(t => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-icon" style="background: ${getCategoryColor(t.category)}20; color: ${getCategoryColor(t.category)}">
                    <i class="fas ${getCategoryIcon(t.category)}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${t.description || t.category}</h4>
                    <p>${formatDate(t.date)} • ${t.category}</p>
                </div>
            </div>
            <span class="transaction-amount ${t.is_income ? 'income' : 'expense'}">
                ${t.is_income ? '+' : '-'}${formatCurrency(t.amount)}
            </span>
        </div>
    `).join('');
}

function renderBudgetAlerts(alerts) {
    const container = document.getElementById('budgetAlerts');
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><h3>All budgets on track!</h3></div>';
        return;
    }

    container.innerHTML = alerts.map(a => `
        <div class="alert-item">
            <div class="alert-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="alert-info">
                <h4>${a.category}</h4>
                <p>${formatCurrency(a.spent)} of ${formatCurrency(a.budgeted)} (${a.percentage_used}%)</p>
            </div>
        </div>
    `).join('');
}

function renderUpcomingBills(bills) {
    const container = document.getElementById('upcomingBills');
    if (!bills || bills.length === 0) {
        container.innerHTML = emptyState('No upcoming bills');
        return;
    }

    container.innerHTML = bills.map(b => `
        <div class="bill-item">
            <div class="bill-info">
                <h4>${b.name}</h4>
                <p>Due in ${b.days_until} days</p>
            </div>
            <div>
                <span class="bill-amount">${formatCurrency(b.amount)}</span>
                <div class="bill-due">${formatDate(b.due_date)}</div>
            </div>
        </div>
    `).join('');
}

// ============================================
// Transactions Page
// ============================================

async function loadTransactions() {
    const category = document.getElementById('filterCategory').value;
    const startDate = document.getElementById('filterStartDate').value;
    const endDate = document.getElementById('filterEndDate').value;
    const search = document.getElementById('filterSearch').value;

    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (search) params.append('search', search);
    params.append('skip', (currentPage - 1) * itemsPerPage);
    params.append('limit', itemsPerPage);

    try {
        const data = await api(`/expenses/?${params}`);
        renderTransactionsTable(data);
    } catch (error) {
        console.error('Transactions load error:', error);
    }
}

function renderTransactionsTable(transactions) {
    const tbody = document.getElementById('transactionsBody');
    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><i class="fas fa-inbox"></i><h3>No transactions found</h3></td></tr>`;
        return;
    }

    tbody.innerHTML = transactions.map(t => `
        <tr>
            <td>${formatDate(t.date)}</td>
            <td>${t.description || t.category}</td>
            <td><span class="cat-${t.category.toLowerCase().replace(/[^a-z]/g, '')}"><i class="fas ${getCategoryIcon(t.category)}"></i> ${t.category}</span></td>
            <td class="${t.is_income ? 'income' : 'expense'}">${t.is_income ? '+' : '-'}${formatCurrency(t.amount)}</td>
            <td><span class="badge ${t.is_income ? 'success' : 'danger'}">${t.is_income ? 'Income' : 'Expense'}</span></td>
            <td class="actions">
                <button onclick="editExpense(${t.id})" title="Edit"><i class="fas fa-edit"></i></button>
                <button onclick="deleteExpense(${t.id})" class="delete" title="Delete"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');

    document.getElementById('pageInfo').textContent = `Page ${currentPage}`;
    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.getElementById('nextBtn').disabled = transactions.length < itemsPerPage;
}

function applyFilters() {
    currentPage = 1;
    loadTransactions();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadTransactions();
    }
}

function nextPage() {
    currentPage++;
    loadTransactions();
}

async function saveExpense(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    data.amount = parseFloat(data.amount);
    data.is_income = data.is_income === 'true';
    
    try {
        await api('/expenses/', {
            method: 'POST',
            body: data
        });
        closeModal();
        form.reset();
        initDateInputs();
        showToast('Transaction saved successfully!', 'success');
        loadDashboard();
        if (document.getElementById('transactions').classList.contains('active')) {
            loadTransactions();
        }
    } catch (error) {
        console.error('Save expense error:', error);
    }
}

async function editExpense(id) {
    try {
        const expense = await api(`/expenses/${id}`);
        // Populate form and show modal
        const form = document.getElementById('expenseForm');
        form.querySelector('[name="amount"]').value = expense.amount;
        form.querySelector('[name="description"]').value = expense.description || '';
        form.querySelector('[name="category"]').value = expense.category;
        form.querySelector('[name="date"]').value = expense.date;
        form.querySelector('[name="is_income"]').value = expense.is_income.toString();
        form.querySelector('[name="payment_method"]').value = expense.payment_method;
        form.querySelector('[name="tags"]').value = expense.tags || '';
        
        // Change form submit handler
        form.onsubmit = async (e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(form));
            data.amount = parseFloat(data.amount);
            data.is_income = data.is_income === 'true';
            
            await api(`/expenses/${id}`, {
                method: 'PUT',
                body: data
            });
            closeModal();
            form.onsubmit = saveExpense; // Reset handler
            form.reset();
            showToast('Transaction updated!', 'success');
            loadDashboard();
            loadTransactions();
        };
        
        openModal('addExpense');
    } catch (error) {
        console.error('Edit error:', error);
    }
}

async function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    
    try {
        await api(`/expenses/${id}`, { method: 'DELETE' });
        showToast('Transaction deleted', 'success');
        loadTransactions();
        loadDashboard();
    } catch (error) {
        console.error('Delete error:', error);
    }
}

// ============================================
// Budgets Page
// ============================================

async function loadBudgets() {
    try {
        const budgets = await api('/budgets/');
        renderBudgets(budgets);
    } catch (error) {
        console.error('Budgets load error:', error);
    }
}

function renderBudgets(budgets) {
    const container = document.getElementById('budgetsGrid');
    if (!budgets || budgets.length === 0) {
        container.innerHTML = emptyState('No budgets set. Create your first budget!');
        return;
    }

    container.innerHTML = budgets.map(b => {
        const percentage = b.percentage_used || 0;
        const status = percentage >= 100 ? 'danger' : percentage >= b.alert_threshold ? 'warning' : 'safe';
        
        return `
        <div class="budget-card">
            <div class="budget-header">
                <span class="budget-category"><i class="fas ${getCategoryIcon(b.category)}"></i> ${b.category}</span>
                <span class="budget-amount">${formatCurrency(b.spent || 0)} / ${formatCurrency(b.amount)}</span>
            </div>
            <div class="budget-progress">
                <div class="budget-progress-bar ${status}" style="width: ${Math.min(percentage, 100)}%"></div>
            </div>
            <div class="budget-stats">
                <span>${percentage}% used</span>
                <span>${formatCurrency(b.remaining || 0)} left</span>
            </div>
            <div class="actions" style="margin-top: 1rem; justify-content: flex-end;">
                <button onclick="deleteBudget(${b.id})" class="delete"><i class="fas fa-trash"></i></button>
            </div>
        </div>
        `;
    }).join('');
}

async function saveBudget(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    data.amount = parseFloat(data.amount);
    data.alert_threshold = parseFloat(data.alert_threshold);
    
    try {
        await api('/budgets/', {
            method: 'POST',
            body: data
        });
        closeModal();
        form.reset();
        showToast('Budget created!', 'success');
        loadBudgets();
    } catch (error) {
        console.error('Save budget error:', error);
    }
}

async function deleteBudget(id) {
    if (!confirm('Delete this budget?')) return;
    try {
        await api(`/budgets/${id}`, { method: 'DELETE' });
        showToast('Budget deleted', 'success');
        loadBudgets();
    } catch (error) {
        console.error('Delete budget error:', error);
    }
}

// ============================================
// Goals Page
// ============================================

async function loadGoals() {
    try {
        const goals = await api('/goals/');
        renderGoals(goals);
    } catch (error) {
        console.error('Goals load error:', error);
    }
}

function renderGoals(goals) {
    const container = document.getElementById('goalsGrid');
    if (!goals || goals.length === 0) {
        container.innerHTML = emptyState('No savings goals yet. Start saving!');
        return;
    }

    container.innerHTML = goals.map(g => {
        const percentage = g.percentage_complete || 0;
        const circumference = 2 * Math.PI * 52;
        const offset = circumference - (percentage / 100) * circumference;
        
        return `
        <div class="goal-card" style="--goal-color: ${g.color}">
            <div class="goal-header">
                <div class="goal-name">${g.name}</div>
                <div class="goal-target">Target: ${formatCurrency(g.target_amount)}</div>
            </div>
            <div class="goal-progress-ring">
                <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="52" fill="none" stroke="${g.color}20" stroke-width="8"/>
                    <circle cx="60" cy="60" r="52" fill="none" stroke="${g.color}" stroke-width="8"
                        stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                        stroke-linecap="round"/>
                </svg>
                <div class="goal-progress-text" style="color: ${g.color}">${percentage}%</div>
            </div>
            <div class="goal-footer">
                <div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">Saved</div>
                    <div style="font-weight: 600;">${formatCurrency(g.current_amount)}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">Remaining</div>
                    <div style="font-weight: 600;">${formatCurrency(g.target_amount - g.current_amount)}</div>
                </div>
            </div>
            <div class="actions" style="margin-top: 1rem; justify-content: center; gap: 1rem;">
                <button onclick="updateGoalAmount(${g.id}, -10)" class="btn btn-secondary" style="padding: 0.375rem 0.75rem;"><i class="fas fa-minus"></i></button>
                <button onclick="updateGoalAmount(${g.id}, 10)" class="btn btn-primary" style="padding: 0.375rem 0.75rem;"><i class="fas fa-plus"></i> $10</button>
                <button onclick="deleteGoal(${g.id})" class="delete"><i class="fas fa-trash"></i></button>
            </div>
        </div>
        `;
    }).join('');
}

async function saveGoal(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    data.target_amount = parseFloat(data.target_amount);
    data.current_amount = parseFloat(data.current_amount) || 0;
    
    try {
        await api('/goals/', {
            method: 'POST',
            body: data
        });
        closeModal();
        form.reset();
        showToast('Goal created!', 'success');
        loadGoals();
    } catch (error) {
        console.error('Save goal error:', error);
    }
}

async function updateGoalAmount(id, amount) {
    try {
        const goal = await api(`/goals/${id}`);
        const newAmount = Math.max(0, goal.current_amount + amount);
        await api(`/goals/${id}`, {
            method: 'PUT',
            body: { current_amount: newAmount }
        });
        showToast(`Updated goal progress!`, 'success');
        loadGoals();
    } catch (error) {
        console.error('Update goal error:', error);
    }
}

async function deleteGoal(id) {
    if (!confirm('Delete this goal?')) return;
    try {
        await api(`/goals/${id}`, { method: 'DELETE' });
        showToast('Goal deleted', 'success');
        loadGoals();
    } catch (error) {
        console.error('Delete goal error:', error);
    }
}

// ============================================
// Recurring Page
// ============================================

async function loadRecurring() {
    try {
        const items = await api('/recurring/');
        renderRecurring(items);
    } catch (error) {
        console.error('Recurring load error:', error);
    }
}

function renderRecurring(items) {
    const tbody = document.getElementById('recurringBody');
    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state"><i class="fas fa-sync"></i><h3>No recurring expenses</h3></td></tr>`;
        return;
    }

    tbody.innerHTML = items.map(item => `
        <tr>
            <td><strong>${item.name}</strong></td>
            <td>${formatCurrency(item.amount)}</td>
            <td><span class="cat-${item.category.toLowerCase().replace(/[^a-z]/g, '')}">${item.category}</span></td>
            <td><span class="badge">${item.frequency}</span></td>
            <td>${formatDate(item.next_due_date)}</td>
            <td><span class="badge ${item.is_active ? 'success' : 'danger'}">${item.is_active ? 'Active' : 'Inactive'}</span></td>
            <td class="actions">
                <button onclick="deleteRecurring(${item.id})" class="delete"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

async function saveRecurring(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    data.amount = parseFloat(data.amount);
    data.auto_pay = data.auto_pay === 'true';
    
    try {
        await api('/recurring/', {
            method: 'POST',
            body: data
        });
        closeModal();
        form.reset();
        initDateInputs();
        showToast('Recurring expense added!', 'success');
        loadRecurring();
    } catch (error) {
        console.error('Save recurring error:', error);
    }
}

async function deleteRecurring(id) {
    if (!confirm('Delete this recurring expense?')) return;
    try {
        await api(`/recurring/${id}`, { method: 'DELETE' });
        showToast('Deleted', 'success');
        loadRecurring();
    } catch (error) {
        console.error('Delete recurring error:', error);
    }
}

// ============================================
// Analytics Page
// ============================================

async function loadAnalytics() {
    const months = document.getElementById('analyticsPeriod').value;
    
    try {
        const [trend, breakdown, daily] = await Promise.all([
            api(`/analytics/monthly-trend?months=${months}`),
            api('/analytics/category-breakdown'),
            api('/analytics/spending-by-day')
        ]);
        
        renderTrendChart(trend);
        renderBudgetActualChart();
        renderDailyChart(daily);
    } catch (error) {
        console.error('Analytics load error:', error);
    }
}

// ============================================
// Charts
// ============================================

function renderSpendingChart() {
    const ctx = document.getElementById('spendingChart');
    if (!ctx) return;
    
    if (charts.spending) charts.spending.destroy();
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
    const textColor = isDark ? '#94a3b8' : '#64748b';

    charts.spending = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Expenses',
                data: [45, 80, 35, 120, 65, 150, 90],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }, {
                label: 'Income',
                data: [0, 0, 500, 0, 0, 0, 0],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: textColor } }
            },
            scales: {
                x: { grid: { color: gridColor }, ticks: { color: textColor } },
                y: { grid: { color: gridColor }, ticks: { color: textColor } }
            }
        }
    });
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    if (charts.category) charts.category.destroy();

    const data = categories || [];
    const labels = data.map(c => c.category);
    const values = data.map(c => c.amount);
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.length ? labels : ['No Data'],
            datasets: [{
                data: values.length ? values : [1],
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 15, usePointStyle: true } }
            }
        }
    });
}

function renderTrendChart(data) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    if (charts.trend) charts.trend.destroy();
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';

    charts.trend = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Income',
                data: data.map(d => d.income),
                backgroundColor: '#10b981',
                borderRadius: 4
            }, {
                label: 'Expenses',
                data: data.map(d => d.expenses),
                backgroundColor: '#ef4444',
                borderRadius: 4
            }, {
                label: 'Savings',
                data: data.map(d => d.savings),
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: textColor } }
            },
            scales: {
                x: { grid: { color: gridColor }, ticks: { color: textColor } },
                y: { grid: { color: gridColor }, ticks: { color: textColor } }
            }
        }
    });
}

function renderBudgetActualChart() {
    const ctx = document.getElementById('budgetActualChart');
    if (!ctx) return;
    
    if (charts.budgetActual) charts.budgetActual.destroy();

    charts.budgetActual = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Food', 'Transport', 'Housing', 'Entertainment'],
            datasets: [{
                label: 'Budget',
                data: [500, 300, 1200, 200],
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }, {
                label: 'Actual',
                data: [450, 280, 1100, 250],
                backgroundColor: '#ef4444',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function renderDailyChart(data) {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;
    
    if (charts.daily) charts.daily.destroy();

    const labels = data.map(d => d.date.slice(5));
    const values = data.map(d => d.amount);

    charts.daily = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Spending',
                data: values,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// ============================================
// Modal Management
// ============================================

function openModal(type) {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById(`${type}Modal`);
    if (modal) {
        overlay.classList.add('active');
        modal.classList.add('active');
    }
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
    // Reset form handlers
    document.getElementById('expenseForm').onsubmit = saveExpense;
}

// ============================================
// Notifications
// ============================================

function checkNotifications() {
    // In production, this would poll the backend
    const badge = document.getElementById('notificationBadge');
    const count = Math.floor(Math.random() * 3);
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
}

function toggleNotifications() {
    const panel = document.getElementById('notificationPanel');
    panel.classList.toggle('active');
    
    if (panel.classList.contains('active')) {
        renderNotifications();
    }
}

function closeNotifications() {
    document.getElementById('notificationPanel').classList.remove('active');
}

function renderNotifications() {
    const content = document.getElementById('notificationContent');
    content.innerHTML = `
        <div class="notification-item alert">
            <h4>Budget Alert</h4>
            <p>Food & Dining budget is at 85% of limit</p>
        </div>
        <div class="notification-item">
            <h4>Upcoming Bill</h4>
            <p>Netflix subscription due in 3 days</p>
        </div>
        <div class="notification-item success">
            <h4>Goal Milestone</h4>
            <p>You've reached 50% of your Emergency Fund goal!</p>
        </div>
    `;
}

// ============================================
// Export
// ============================================

function exportCSV() {
    const rows = [
        ['Date', 'Description', 'Category', 'Amount', 'Type'],
        ['2026-05-01', 'Grocery Store', 'Food & Dining', '85.50', 'Expense'],
        ['2026-05-02', 'Salary', 'Income', '5000.00', 'Income'],
        ['2026-05-03', 'Gas Station', 'Transportation', '45.00', 'Expense']
    ];
    
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('CSV exported successfully!', 'success');
}

// ============================================
// Utilities
// ============================================

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount || 0);
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function getCategoryColor(category) {
    const colors = {
        'Food & Dining': '#f59e0b',
        'Transportation': '#3b82f6',
        'Housing & Utilities': '#8b5cf6',
        'Entertainment': '#ec4899',
        'Shopping': '#10b981',
        'Health & Fitness': '#ef4444',
        'Travel': '#06b6d4',
        'Education': '#6366f1',
        'Subscriptions': '#f97316',
        'Other': '#6b7280',
        'Income': '#10b981'
    };
    return colors[category] || '#6b7280';
}

function getCategoryIcon(category) {
    const icons = {
        'Food & Dining': 'fa-utensils',
        'Transportation': 'fa-car',
        'Housing & Utilities': 'fa-home',
        'Entertainment': 'fa-film',
        'Shopping': 'fa-shopping-bag',
        'Health & Fitness': 'fa-heartbeat',
        'Travel': 'fa-plane',
        'Education': 'fa-graduation-cap',
        'Subscriptions': 'fa-sync',
        'Other': 'fa-tag',
        'Income': 'fa-arrow-up'
    };
    return icons[category] || 'fa-tag';
}

function emptyState(message) {
    return `
        <div class="empty-state">
            <i class="fas fa-inbox"></i>
            <h3>${message}</h3>
        </div>
    `;
}

function showToast(message, type = 'success') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Modal overlay click to close
    document.getElementById('modalOverlay').addEventListener('click', closeModal);
    
    // Notification button
    document.getElementById('notificationBtn').addEventListener('click', toggleNotifications);
    
    // Chart period change
    document.getElementById('chartPeriod')?.addEventListener('change', () => {
        renderSpendingChart();
    });
    
    // Analytics period change
    document.getElementById('analyticsPeriod')?.addEventListener('change', loadAnalytics);
    
    // Global search
    document.getElementById('globalSearch')?.addEventListener('input', (e) => {
        if (e.target.value.length > 2) {
            document.getElementById('filterSearch').value = e.target.value;
            switchPage('transactions');
            applyFilters();
        }
    });
    
    // Form submissions
    document.getElementById('budgetForm').addEventListener('submit', saveBudget);
    document.getElementById('goalForm').addEventListener('submit', saveGoal);
    document.getElementById('recurringForm').addEventListener('submit', saveRecurring);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeNotifications();
        }
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            openModal('addExpense');
        }
    });
}


