// Enhanced RoadSense Frontend
const API_BASE = '/api';
let authToken = localStorage.getItem('auth_token');
let currentUser = null;

// ============================================================================
// AUTHENTICATION
// ============================================================================

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            showAlert('Invalid credentials', 'error');
            return;
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('auth_token', authToken);
        getCurrentUser();
        showDashboard();
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Login failed', 'error');
    }
}

async function logout() {
    authToken = null;
    localStorage.removeItem('auth_token');
    currentUser = null;
    showLoginForm();
}

async function register(username, email, password, city) {
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, city })
        });
        
        if (response.ok) {
            showAlert('Registration successful. Please login.', 'success');
            showLoginForm();
        } else {
            const error = await response.json();
            showAlert(error.error, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Registration failed', 'error');
    }
}

async function getCurrentUser() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/auth/user`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateUserMenu();
        } else {
            logout();
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
}

// ============================================================================
// ROAD STATUS & DASHBOARD
// ============================================================================

async function getRoadsStatus() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/roads/status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayRoadsMap(data.roads);
            displayRoadTable(data.roads);
            return data;
        }
    } catch (error) {
        console.error('Error fetching roads:', error);
    }
}

async function getDashboardSummary() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/dashboard/summary`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayDashboardKPIs(data);
            return data;
        }
    } catch (error) {
        console.error('Error fetching dashboard:', error);
    }
}

function displayDashboardKPIs(data) {
    const kpiContainer = document.getElementById('kpi-container');
    if (!kpiContainer) return;
    
    const kpis = data.kpis;
    kpiContainer.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Roads</div>
                <div class="kpi-value">${kpis.total_roads}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Green Roads</div>
                <div class="kpi-value" style="color: #4caf50;">${data.roads_summary.green}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Yellow Roads</div>
                <div class="kpi-value" style="color: #ff9800;">${data.roads_summary.yellow}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Red Roads</div>
                <div class="kpi-value" style="color: #f44336;">${data.roads_summary.red}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Open Alerts</div>
                <div class="kpi-value">${kpis.open_alerts}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Pending Work Orders</div>
                <div class="kpi-value">${kpis.pending_work_orders}</div>
            </div>
        </div>
    `;
}

// ============================================================================
// ALERTS MANAGEMENT
// ============================================================================

async function getAlerts() {
    if (!authToken) return [];
    
    try {
        const response = await fetch(`${API_BASE}/alerts`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.alerts;
        }
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
    return [];
}

async function createAlert(roadId, roadName, severity, description) {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/alerts`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ road_id: roadId, road_name: roadName, severity, description })
        });
        
        if (response.ok) {
            showAlert('Alert created', 'success');
            getAlerts();
        }
    } catch (error) {
        console.error('Error creating alert:', error);
    }
}

function displayAlertsTable(alerts) {
    const container = document.getElementById('alerts-container');
    if (!container) return;
    
    if (alerts.length === 0) {
        container.innerHTML = '<p>No alerts</p>';
        return;
    }
    
    let html = `<table>
        <thead>
            <tr>
                <th>Road</th>
                <th>Severity</th>
                <th>Description</th>
                <th>Created</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>`;
    
    alerts.forEach(alert => {
        const statusClass = `status-${alert.severity.toLowerCase()}`;
        const date = new Date(alert.created_at).toLocaleDateString();
        html += `<tr>
            <td>${alert.road_name}</td>
            <td><span class="status-badge ${statusClass}">${alert.severity}</span></td>
            <td>${alert.description || '-'}</td>
            <td>${date}</td>
            <td>${alert.status}</td>
            <td>
                ${alert.status === 'open' ? `<button class="btn btn-secondary" onclick="resolveAlert(${alert.id})">Resolve</button>` : '-'}
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function resolveAlert(alertId) {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/resolve`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            showAlert('Alert resolved', 'success');
            getAlerts();
        }
    } catch (error) {
        console.error('Error resolving alert:', error);
    }
}

// ============================================================================
// WORK ORDERS
// ============================================================================

async function getWorkOrders() {
    if (!authToken) return [];
    
    try {
        const response = await fetch(`${API_BASE}/work-orders`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.work_orders;
        }
    } catch (error) {
        console.error('Error fetching work orders:', error);
    }
    return [];
}

async function createWorkOrder(roadId, roadName, workType, contractor, estimatedCost, notes) {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/work-orders`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                road_id: roadId,
                road_name: roadName,
                work_type: workType,
                contractor,
                estimated_cost: estimatedCost,
                notes
            })
        });
        
        if (response.ok) {
            showAlert('Work order created', 'success');
            getWorkOrders();
            return true;
        }
    } catch (error) {
        console.error('Error creating work order:', error);
    }
    return false;
}

function displayWorkOrdersTable(workOrders) {
    const container = document.getElementById('work-orders-container');
    if (!container) return;
    
    if (workOrders.length === 0) {
        container.innerHTML = '<p>No work orders</p>';
        return;
    }
    
    let html = `<table>
        <thead>
            <tr>
                <th>Road</th>
                <th>Type</th>
                <th>Contractor</th>
                <th>Estimated Cost</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>`;
    
    workOrders.forEach(wo => {
        const date = new Date(wo.created_at).toLocaleDateString();
        html += `<tr>
            <td>${wo.road_name}</td>
            <td>${wo.work_type}</td>
            <td>${wo.contractor || '-'}</td>
            <td>${wo.estimated_cost ? '₹' + wo.estimated_cost : '-'}</td>
            <td><span class="status-badge status-${wo.status.toLowerCase()}">${wo.status}</span></td>
            <td>${date}</td>
            <td>
                <select onchange="updateWorkOrderStatus(${wo.id}, this.value)">
                    <option value="pending" ${wo.status === 'pending' ? 'selected' : ''}>Pending</option>
                    <option value="in_progress" ${wo.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="completed" ${wo.status === 'completed' ? 'selected' : ''}>Completed</option>
                </select>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function updateWorkOrderStatus(workOrderId, status) {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE}/work-orders/${workOrderId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });
        
        if (response.ok) {
            showAlert('Work order updated', 'success');
        }
    } catch (error) {
        console.error('Error updating work order:', error);
    }
}

// ============================================================================
// CITIZEN REPORTS
// ============================================================================

async function createCitizenReport(latitude, longitude, issueType, description) {
    try {
        const response = await fetch(`${API_BASE}/reports/citizen`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude,
                longitude,
                issue_type: issueType,
                description
            })
        });
        
        if (response.ok) {
            showAlert('Report submitted successfully', 'success');
            return true;
        }
    } catch (error) {
        console.error('Error submitting report:', error);
        showAlert('Failed to submit report', 'error');
    }
    return false;
}

async function getCitizenReports() {
    if (!authToken) return [];
    
    try {
        const response = await fetch(`${API_BASE}/reports/citizen`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.reports;
        }
    } catch (error) {
        console.error('Error fetching citizen reports:', error);
    }
    return [];
}

// ============================================================================
// UI UTILITIES
// ============================================================================

function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    alertsContainer.insertBefore(alert, alertsContainer.firstChild);
    
    setTimeout(() => alert.remove(), 5000);
}

function updateUserMenu() {
    const userMenuDiv = document.getElementById('user-menu');
    if (!userMenuDiv || !currentUser) return;
    
    userMenuDiv.innerHTML = `
        <span>${currentUser.username} (${currentUser.role})</span>
        <button class="btn-logout" onclick="logout()">Logout</button>
    `;
}

function displayRoadTable(roads) {
    const container = document.getElementById('roads-table-container');
    if (!container) return;
    
    let html = `<table>
        <thead>
            <tr>
                <th>Road ID</th>
                <th>Name</th>
                <th>City</th>
                <th>Condition</th>
                <th>Days Since Repair</th>
                <th>Material</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>`;
    
    roads.forEach(road => {
        const statusClass = `status-${road.condition.toLowerCase()}`;
        html += `<tr>
            <td>${road.id}</td>
            <td>${road.name}</td>
            <td>${road.city}</td>
            <td><span class="status-badge ${statusClass}">${road.condition}</span></td>
            <td>${road.days_since_repair}</td>
            <td>${road.material}</td>
            <td>
                <button class="btn btn-primary" onclick="showCreateWorkOrderModal('${road.id}', '${road.name}')">Create WO</button>
                <button class="btn btn-secondary" onclick="showCreateAlertModal('${road.id}', '${road.name}')">Alert</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function displayRoadsMap(roads) {
    const mapContainer = document.getElementById('roads-map');
    if (!mapContainer) return;
    
    // Simple map visualization
    let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px;">';
    
    roads.forEach(road => {
        const color = road.condition === 'RED' ? '#f44336' : road.condition === 'YELLOW' ? '#ff9800' : '#4caf50';
        html += `<div style="background: ${color}; color: white; padding: 10px; border-radius: 4px; text-align: center; cursor: pointer;" 
                      title="${road.name}">${road.id}</div>`;
    });
    
    html += '</div>';
    mapContainer.innerHTML = html;
}

function showCreateWorkOrderModal(roadId, roadName) {
    const modal = document.getElementById('work-order-modal');
    if (!modal) return;
    
    document.getElementById('wo-road-id').value = roadId;
    document.getElementById('wo-road-name').value = roadName;
    modal.classList.add('active');
}

function showCreateAlertModal(roadId, roadName) {
    const modal = document.getElementById('alert-modal');
    if (!modal) return;
    
    document.getElementById('alert-road-id').value = roadId;
    document.getElementById('alert-road-name').value = roadName;
    modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        getCurrentUser();
        showDashboard();
    } else {
        showLoginForm();
    }
});

function showDashboard() {
    if (document.getElementById('dashboard')) {
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('login-form').style.display = 'none';
        getDashboardSummary();
        getRoadsStatus();
        getAlerts();
        getWorkOrders();
    }
}

function showLoginForm() {
    if (document.getElementById('login-form')) {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('dashboard').style.display = 'none';
    }
}
