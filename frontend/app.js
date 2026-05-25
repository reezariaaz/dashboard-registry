
const API = 'http://127.0.0.1:5000/api';

// ============================================
// SCREEN NAVIGATION
// ============================================

function showScreen(screen) {
    // Hide all screens
    document.getElementById('screen-dashboards').style.display = 'none';
    document.getElementById('screen-data-sources').style.display = 'none';

    // Remove active class from all nav buttons
    document.getElementById('nav-dashboards').classList.remove('active');
    document.getElementById('nav-data-sources').classList.remove('active');

    // Show the selected screen and mark button as active
    document.getElementById('screen-' + screen).style.display = 'block';
    document.getElementById('nav-' + screen).classList.add('active');

    // Load data for the screen
    if (screen === 'dashboards') loadDashboards();
    if (screen === 'data-sources') loadDataSources();
}

// ============================================
// MODAL HELPERS
// ============================================

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// ============================================
// DASHBOARDS
// ============================================

async function loadDashboards() {
    const search = document.getElementById('dashboard-search').value;
    const category = document.getElementById('dashboard-category').value;
    const status = document.getElementById('dashboard-status').value;

    // Build the URL with filters
    let url = `${API}/dashboards?search=${search}&category=${category}&status=${status}`;

    const response = await fetch(url);
    const dashboards = await response.json();

    const tbody = document.getElementById('dashboards-tbody');

    // Show empty state if no dashboards
    if (dashboards.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No dashboards found</td></tr>';
        return;
    }

    // Build table rows
    tbody.innerHTML = dashboards.map(d => `
        <tr>
            <td>${d.name}</td>
            <td>${d.category}</td>
            <td>${d.owner_name}</td>
            <td><span class="status-${d.status.toLowerCase()}">${d.status}</span></td>
            <td>
                <button class="btn-view" onclick="viewDashboard(${d.id})">View</button>
                <button class="btn-edit" onclick="editDashboard(${d.id})">Edit</button>
                <button class="btn-delete" onclick="deleteDashboard(${d.id}, '${d.name}')">Delete</button>
                <button class="btn-primary" onclick="window.open('${d.url}', '_blank')">Open</button>
            </td>
        </tr>
    `).join('');
}

async function viewDashboard(id) {
    const response = await fetch(`${API}/dashboards/${id}`);
    const d = await response.json();

    document.getElementById('dashboard-modal-title').textContent = d.name;
    document.getElementById('dashboard-modal-body').innerHTML = `
        <div class="detail-field">
            <label>Description</label>
            <span>${d.description || 'No description'}</span>
        </div>
        <div class="detail-field">
            <label>URL</label>
            <span><a href="${d.url}" target="_blank">${d.url}</a></span>
        </div>
        <div class="detail-field">
            <label>Category</label>
            <span>${d.category}</span>
        </div>
        <div class="detail-field">
            <label>Owner</label>
            <span>${d.owner_name}</span>
        </div>
        <div class="detail-field">
            <label>Status</label>
            <span class="status-${d.status.toLowerCase()}">${d.status}</span>
        </div>
        <div class="detail-field">
            <label>Data Sources</label>
            <div class="detail-tags">
                ${d.data_sources.length > 0
                    ? d.data_sources.map(ds => `<span class="tag">${ds.name} (${ds.type})</span>`).join('')
                    : '<span>No data sources linked</span>'
                }
            </div>
        </div>
        <div class="form-actions">
            <button class="btn-cancel" onclick="closeModal('dashboard-modal')">Close</button>
        </div>
    `;

    document.getElementById('dashboard-modal').style.display = 'flex';
}

async function openDashboardModal(id = null) {
    // Load all data sources for the multi-select
    const dsResponse = await fetch(`${API}/data-sources`);
    const dataSources = await dsResponse.json();

    let dashboard = null;
    let linkedIds = [];

    if (id) {
        const response = await fetch(`${API}/dashboards/${id}`);
        dashboard = await response.json();
        linkedIds = dashboard.data_sources.map(ds => ds.id);
    }

    document.getElementById('dashboard-modal-title').textContent = id ? 'Edit Dashboard' : 'Add Dashboard';
    document.getElementById('dashboard-modal-body').innerHTML = `
        <div id="dashboard-form-error"></div>
        <div class="form-group">
            <label>Name *</label>
            <input type="text" id="form-name" value="${dashboard ? dashboard.name : ''}">
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea id="form-description">${dashboard ? dashboard.description : ''}</textarea>
        </div>
        <div class="form-group">
            <label>URL *</label>
            <input type="text" id="form-url" value="${dashboard ? dashboard.url : ''}">
        </div>
        <div class="form-group">
            <label>Category *</label>
            <select id="form-category">
                <option value="">Select category</option>
                <option value="Finance" ${dashboard && dashboard.category === 'Finance' ? 'selected' : ''}>Finance</option>
                <option value="HR" ${dashboard && dashboard.category === 'HR' ? 'selected' : ''}>HR</option>
                <option value="Operations" ${dashboard && dashboard.category === 'Operations' ? 'selected' : ''}>Operations</option>
                <option value="Marketing" ${dashboard && dashboard.category === 'Marketing' ? 'selected' : ''}>Marketing</option>
            </select>
        </div>
        <div class="form-group">
            <label>Owner Name *</label>
            <input type="text" id="form-owner" value="${dashboard ? dashboard.owner_name : ''}">
        </div>
        <div class="form-group">
            <label>Status *</label>
            <select id="form-status">
                <option value="Unknown" ${!dashboard || dashboard.status === 'Unknown' ? 'selected' : ''}>Unknown</option>
                <option value="Up" ${dashboard && dashboard.status === 'Up' ? 'selected' : ''}>Up</option>
                <option value="Down" ${dashboard && dashboard.status === 'Down' ? 'selected' : ''}>Down</option>
            </select>
        </div>
        <div class="form-group">
            <label>Data Sources (hold Ctrl to select multiple)</label>
            <select id="form-data-sources" multiple style="height: 100px;">
                ${dataSources.map(ds => `
                    <option value="${ds.id}" ${linkedIds.includes(ds.id) ? 'selected' : ''}>
                        ${ds.name} (${ds.type})
                    </option>
                `).join('')}
            </select>
        </div>
        <div class="form-actions">
            <button class="btn-cancel" onclick="closeModal('dashboard-modal')">Cancel</button>
            <button class="btn-primary" onclick="saveDashboard(${id})">Save</button>
        </div>
    `;

    document.getElementById('dashboard-modal').style.display = 'flex';
}

async function saveDashboard(id) {
    const name = document.getElementById('form-name').value;
    const description = document.getElementById('form-description').value;
    const url = document.getElementById('form-url').value;
    const category = document.getElementById('form-category').value;
    const owner_name = document.getElementById('form-owner').value;
    const status = document.getElementById('form-status').value;

    // Get selected data source IDs
    const select = document.getElementById('form-data-sources');
    const data_source_ids = Array.from(select.selectedOptions).map(o => parseInt(o.value));

    const body = { name, description, url, category, owner_name, status, data_source_ids };

    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `${API}/dashboards/${id}` : `${API}/dashboards`;

    const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    const result = await response.json();

    if (!response.ok) {
        document.getElementById('dashboard-form-error').innerHTML = `
            <div class="error-message">${result.error}</div>
        `;
        return;
    }

    closeModal('dashboard-modal');
    loadDashboards();
}

async function editDashboard(id) {
    openDashboardModal(id);
}

async function deleteDashboard(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    const response = await fetch(`${API}/dashboards/${id}`, { method: 'DELETE' });
    const result = await response.json();

    if (!response.ok) {
        alert(result.error);
        return;
    }

    loadDashboards();
}

// ============================================
// DATA SOURCES
// ============================================

async function loadDataSources() {
    const search = document.getElementById('datasource-search').value;
    const response = await fetch(`${API}/data-sources?search=${search}`);
    const dataSources = await response.json();

    const tbody = document.getElementById('datasources-tbody');

    if (dataSources.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No data sources found</td></tr>';
        return;
    }

    tbody.innerHTML = dataSources.map(ds => `
        <tr>
            <td>${ds.name}</td>
            <td>${ds.type}</td>
            <td>${ds.description || '-'}</td>
            <td>
                <button class="btn-view" onclick="viewDataSource(${ds.id})">View</button>
                <button class="btn-edit" onclick="openDataSourceModal(${ds.id})">Edit</button>
                <button class="btn-delete" onclick="deleteDataSource(${ds.id}, '${ds.name}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function viewDataSource(id) {
    const response = await fetch(`${API}/data-sources/${id}`);
    const ds = await response.json();

    document.getElementById('datasource-modal-title').textContent = ds.name;
    document.getElementById('datasource-modal-body').innerHTML = `
        <div class="detail-field">
            <label>Type</label>
            <span>${ds.type}</span>
        </div>
        <div class="detail-field">
            <label>Description</label>
            <span>${ds.description || 'No description'}</span>
        </div>
        <div class="detail-field">
            <label>Used by Dashboards</label>
            <div class="detail-tags">
                ${ds.dashboards.length > 0
                    ? ds.dashboards.map(d => `<span class="tag">${d.name}</span>`).join('')
                    : '<span>Not used by any dashboards</span>'
                }
            </div>
        </div>
        <div class="form-actions">
            <button class="btn-cancel" onclick="closeModal('datasource-modal')">Close</button>
        </div>
    `;

    document.getElementById('datasource-modal').style.display = 'flex';
}

async function openDataSourceModal(id = null) {
    let ds = null;

    if (id) {
        const response = await fetch(`${API}/data-sources/${id}`);
        ds = await response.json();
    }

    document.getElementById('datasource-modal-title').textContent = id ? 'Edit Data Source' : 'Add Data Source';
    document.getElementById('datasource-modal-body').innerHTML = `
        <div id="datasource-form-error"></div>
        <div class="form-group">
            <label>Name *</label>
            <input type="text" id="ds-form-name" value="${ds ? ds.name : ''}">
        </div>
        <div class="form-group">
            <label>Type *</label>
            <select id="ds-form-type">
                <option value="Database" ${ds && ds.type === 'Database' ? 'selected' : ''}>Database</option>
                <option value="File" ${ds && ds.type === 'File' ? 'selected' : ''}>File</option>
                <option value="API" ${ds && ds.type === 'API' ? 'selected' : ''}>API</option>
            </select>
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea id="ds-form-description">${ds ? ds.description : ''}</textarea>
        </div>
        <div class="form-actions">
            <button class="btn-cancel" onclick="closeModal('datasource-modal')">Cancel</button>
            <button class="btn-primary" onclick="saveDataSource(${id})">Save</button>
        </div>
    `;

    document.getElementById('datasource-modal').style.display = 'flex';
}

async function saveDataSource(id) {
    const name = document.getElementById('ds-form-name').value;
    const type = document.getElementById('ds-form-type').value;
    const description = document.getElementById('ds-form-description').value;

    const body = { name, type, description };

    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `${API}/data-sources/${id}` : `${API}/data-sources`;

    const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    const result = await response.json();

    if (!response.ok) {
        document.getElementById('datasource-form-error').innerHTML = `
            <div class="error-message">${result.error}</div>
        `;
        return;
    }

    closeModal('datasource-modal');
    loadDataSources();
}

async function deleteDataSource(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    const response = await fetch(`${API}/data-sources/${id}`, { method: 'DELETE' });
    const result = await response.json();

    if (!response.ok) {
        alert(result.error);
        return;
    }

    loadDataSources();
}

// ============================================
// INITIALISE
// ============================================

// Load dashboards when page first opens
loadDashboards();