
from flask import Blueprint, jsonify, request
from database import get_db_connection

# A Blueprint is a way to organize routes in Flask
# Instead of putting all routes in app.py, we split them into separate files
data_sources_bp = Blueprint('data_sources', __name__)

# GET all data sources
@data_sources_bp.route('/api/data-sources', methods=['GET'])
def get_data_sources():
    conn = get_db_connection()
    
    search = request.args.get('search', '')
    
    if search:
        # If a search term was provided, filter by name
        data_sources = conn.execute(
            'SELECT * FROM data_sources WHERE name LIKE ?',
            (f'%{search}%',)
        ).fetchall()
    else:
        # Otherwise return all data sources
        data_sources = conn.execute(
            'SELECT * FROM data_sources'
        ).fetchall()
    
    conn.close()
    
    # Convert rows to a list of dictionaries
    return jsonify([dict(row) for row in data_sources])


# GET a single data source by id
@data_sources_bp.route('/api/data-sources/<int:id>', methods=['GET'])
def get_data_source(id):
    conn = get_db_connection()
    
    data_source = conn.execute(
        'SELECT * FROM data_sources WHERE id = ?', (id,)
    ).fetchone()
    
    if data_source is None:
        return jsonify({'error': 'Data source not found'}), 404
    
    # Also get all dashboards linked to this data source
    dashboards = conn.execute('''
        SELECT d.id, d.name, d.category, d.status
        FROM dashboards d
        JOIN dashboard_data_sources dds ON d.id = dds.dashboard_id
        WHERE dds.data_source_id = ?
    ''', (id,)).fetchall()
    
    conn.close()
    
    result = dict(data_source)
    result['dashboards'] = [dict(d) for d in dashboards]
    
    return jsonify(result)


# POST create a new data source
@data_sources_bp.route('/api/data-sources', methods=['POST'])
def create_data_source():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    if not data.get('type'):
        return jsonify({'error': 'Type is required'}), 400
    if data.get('type') not in ['Database', 'File', 'API']:
        return jsonify({'error': 'Type must be Database, File, or API'}), 400
    
    conn = get_db_connection()
    
    try:
        conn.execute(
            'INSERT INTO data_sources (name, type, description) VALUES (?, ?, ?)',
            (data['name'], data['type'], data.get('description', ''))
        )
        conn.commit()
    except Exception as e:
        # This catches duplicate name errors
        return jsonify({'error': 'A data source with this name already exists'}), 400
    finally:
        conn.close()
    
    return jsonify({'message': 'Data source created successfully'}), 201


# PUT update a data source
@data_sources_bp.route('/api/data-sources/<int:id>', methods=['PUT'])
def update_data_source(id):
    data = request.get_json()
    conn = get_db_connection()
    
    # Check it exists first
    existing = conn.execute(
        'SELECT * FROM data_sources WHERE id = ?', (id,)
    ).fetchone()
    
    if existing is None:
        conn.close()
        return jsonify({'error': 'Data source not found'}), 404
    
    # Use new values if provided, otherwise keep existing ones
    name = data.get('name', existing['name'])
    type_ = data.get('type', existing['type'])
    description = data.get('description', existing['description'])
    
    if type_ not in ['Database', 'File', 'API']:
        conn.close()
        return jsonify({'error': 'Type must be Database, File, or API'}), 400
    
    try:
        conn.execute(
            'UPDATE data_sources SET name = ?, type = ?, description = ? WHERE id = ?',
            (name, type_, description, id)
        )
        conn.commit()
    except Exception as e:
        return jsonify({'error': 'A data source with this name already exists'}), 400
    finally:
        conn.close()
    
    return jsonify({'message': 'Data source updated successfully'})


# DELETE a data source
@data_sources_bp.route('/api/data-sources/<int:id>', methods=['DELETE'])
def delete_data_source(id):
    conn = get_db_connection()
    
    # Check it exists
    existing = conn.execute(
        'SELECT * FROM data_sources WHERE id = ?', (id,)
    ).fetchone()
    
    if existing is None:
        conn.close()
        return jsonify({'error': 'Data source not found'}), 404
    
    # Check if it is linked to any dashboards
    links = conn.execute(
        'SELECT * FROM dashboard_data_sources WHERE data_source_id = ?', (id,)
    ).fetchall()
    
    if links:
        conn.close()
        return jsonify({
            'error': 'Cannot delete this data source because it is linked to one or more dashboards. Remove those links first.'
        }), 400
    
    conn.execute('DELETE FROM data_sources WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Data source deleted successfully'})