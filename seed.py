
from database import get_db_connection, init_db

def seed():
    # Make sure tables exist first
    init_db()
    
    conn = get_db_connection()
    
    # Clear existing data so we don't get duplicates
    conn.execute('DELETE FROM dashboard_data_sources')
    conn.execute('DELETE FROM dashboards')
    conn.execute('DELETE FROM data_sources')
    
    # Add sample data sources
    conn.execute('''
        INSERT INTO data_sources (name, type, description)
        VALUES (?, ?, ?)
    ''', ('Sales Database', 'Database', 'Main sales transactions database'))
    
    conn.execute('''
        INSERT INTO data_sources (name, type, description)
        VALUES (?, ?, ?)
    ''', ('HR Monthly Export', 'File', 'Monthly HR data export in CSV format'))
    
    conn.execute('''
        INSERT INTO data_sources (name, type, description)
        VALUES (?, ?, ?)
    ''', ('Finance API', 'API', 'Live finance data from external provider'))
    
    # Add sample dashboards
    conn.execute('''
        INSERT INTO dashboards (name, description, url, category, owner_name, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Sales Overview', 'Monthly sales performance by region', 
          'https://example.com/sales', 'Finance', 'John Smith', 'Up'))
    
    conn.execute('''
        INSERT INTO dashboards (name, description, url, category, owner_name, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Staff Headcount', 'Current headcount across all departments', 
          'https://example.com/headcount', 'HR', 'Sarah Jones', 'Up'))
    
    conn.execute('''
        INSERT INTO dashboards (name, description, url, category, owner_name, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Budget Tracker', 'Quarterly budget vs actual spending', 
          'https://example.com/budget', 'Finance', 'Mike Peters', 'Unknown'))
    
    conn.commit()
    
    # Now link dashboards to data sources
    # Get the IDs we just inserted
    sales_db = conn.execute(
        'SELECT id FROM data_sources WHERE name = ?', ('Sales Database',)
    ).fetchone()
    
    hr_export = conn.execute(
        'SELECT id FROM data_sources WHERE name = ?', ('HR Monthly Export',)
    ).fetchone()
    
    finance_api = conn.execute(
        'SELECT id FROM data_sources WHERE name = ?', ('Finance API',)
    ).fetchone()
    
    sales_dash = conn.execute(
        'SELECT id FROM dashboards WHERE name = ?', ('Sales Overview',)
    ).fetchone()
    
    headcount_dash = conn.execute(
        'SELECT id FROM dashboards WHERE name = ?', ('Staff Headcount',)
    ).fetchone()
    
    budget_dash = conn.execute(
        'SELECT id FROM dashboards WHERE name = ?', ('Budget Tracker',)
    ).fetchone()
    
    # Sales Overview uses Sales Database and Finance API
    conn.execute('''
        INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
        VALUES (?, ?)
    ''', (sales_dash['id'], sales_db['id']))
    
    conn.execute('''
        INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
        VALUES (?, ?)
    ''', (sales_dash['id'], finance_api['id']))
    
    # Staff Headcount uses HR Monthly Export
    conn.execute('''
        INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
        VALUES (?, ?)
    ''', (headcount_dash['id'], hr_export['id']))
    
    # Budget Tracker uses Finance API
    conn.execute('''
        INSERT INTO dashboard_data_sources (dashboard_id, data_source_id)
        VALUES (?, ?)
    ''', (budget_dash['id'], finance_api['id']))
    
    conn.commit()
    conn.close()
    
    print("Sample data added successfully!")

if __name__ == '__main__':
    seed()