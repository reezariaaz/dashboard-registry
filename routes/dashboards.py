
from flask import Blueprint, jsonify, request
from database import get_db_connection

dashboards_bp = Blueprint('dashboards', __name__)

# GET all dashboards (with optional search, category, status filters)
@dashboards_bp.route('/api/dashboards', methods=['GET'])
def get_dashboards():
    conn = get_db_connection()
    
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    query = 'SELECT * FROM dashboards WHERE 1=1'
    params = []
    
    if search:
        query += ' AND name LIKE ?'
        params.append(f'%{search}%')
    if category:
        query += ' AND category = ?'
        params.append(category)
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    dashboards = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in dashboards])


# GET a single dashboard by id
@dashboards_bp.route('/api/dashboards/<int:id>', methods=['GET'])
def get_dashboard(id):
    conn = get_db_connection()
    
    dashboard = conn.execute(
        'SELECT * FROM dashboards WHERE id = ?', (id,)
    ).fetchone()
    
    if dashboard is None:
        conn.close()
        return jsonify({'error': 'Dashboard not found'}), 404
    
    # Get linked data sources
    data_sources = conn.execute('''
        SELECT ds.id, ds.name, ds.type, ds.description
        FROM data_sources ds
        JOIN dashboard_data_sources dds ON ds.id = dds.data_source_id
        WHERE dds.dashboard_id = ?
    ''', (id,)).fetchall()
    
    conn.close()
    
    result = dict(dashboard)
    result['data_sources'] = [dict(ds) for ds in data_sources]
    
    return jsonify(result)


# POST create a new dashboard
@dashboards_bp.route('/api/dashboards', methods=['POST'])
def create_dashboard():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    if not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400
    if not data.get('category'):
        return jsonify({'error': 'Category is required'}), 400
    if not data.get('owner_name'):
        return jsonify({'error': 'Owner name is required'}), 400
    if data.get('status') not in ['Up', 'Down', 'Unknown']:
        return jsonify({'error': 'Status must be Up, Down, or Unknown'}), 400
    
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            INSERT INTO dashboards (name, description, url, category, owner_name, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['url'],
            data['category'],
            data['owner_name'],
            data.get('status', 'Unknown')
        ))
        
        dashboard_id = cursor.lastrowid
        
        # Link data sources if provided
        data_source_ids = data.get('data_source_ids', [])
        for ds_id in data_source_ids:
            conn.execute('''
                INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
                VALUES (?, ?)
            ''', (dashboard_id, ds_id))
        
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': 'A dashboard with this name already exists'}), 400
    finally:
        conn.close()
    
    return jsonify({'message': 'Dashboard created successfully'}), 201


# PUT update a dashboard
@dashboards_bp.route('/api/dashboards/<int:id>', methods=['PUT'])
def update_dashboard(id):
    data = request.get_json()
    conn = get_db_connection()
    
    existing = conn.execute(
        'SELECT * FROM dashboards WHERE id = ?', (id,)
    ).fetchone()
    
    if existing is None:
        conn.close()
        return jsonify({'error': 'Dashboard not found'}), 404
    
    name = data.get('name', existing['name'])
    description = data.get('description', existing['description'])
    url = data.get('url', existing['url'])
    category = data.get('category', existing['category'])
    owner_name = data.get('owner_name', existing['owner_name'])
    status = data.get('status', existing['status'])
    
    if status not in ['Up', 'Down', 'Unknown']:
        conn.close()
        return jsonify({'error': 'Status must be Up, Down, or Unknown'}), 400
    
    try:
        conn.execute('''
            UPDATE dashboards
            SET name = ?, description = ?, url = ?, category = ?,
                owner_name = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, description, url, category, owner_name, status, id))
        
        # Update data source links if provided
        if 'data_source_ids' in data:
            conn.execute(
                'DELETE FROM dashboard_data_sources WHERE dashboard_id = ?', (id,)
            )
            for ds_id in data['data_source_ids']:
                conn.execute('''
                    INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
                    VALUES (?, ?)
                ''', (id, ds_id))
        
        conn.commit()
    except Exception as e:
        return jsonify({'error': 'A dashboard with this name already exists'}), 400
    finally:
        conn.close()
    
    return jsonify({'message': 'Dashboard updated successfully'})


# DELETE a dashboard
@dashboards_bp.route('/api/dashboards/<int:id>', methods=['DELETE'])
def delete_dashboard(id):
    conn = get_db_connection()
    
    existing = conn.execute(
        'SELECT * FROM dashboards WHERE id = ?', (id,)
    ).fetchone()
    
    if existing is None:
        conn.close()
        return jsonify({'error': 'Dashboard not found'}), 404
    
    # Remove links first then delete the dashboard
    conn.execute(
        'DELETE FROM dashboard_data_sources WHERE dashboard_id = ?', (id,)
    )
    conn.execute('DELETE FROM dashboards WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Dashboard deleted successfully'})