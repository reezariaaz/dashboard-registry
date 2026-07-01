
import sqlite3

# The name of our database file
DATABASE = 'dashboard_registry.db'

def get_db_connection():
    """Create and return a connection to the  database"""
    conn = sqlite3.connect(DATABASE)
    
    # This makes rows behave like dictionaries
    # so we can access columns by name e.g. row['name']
    # instead of by index e.g. row[0]
    conn.row_factory = sqlite3.Row
    
    return conn

def init_db():
    """Create all tables if they don't already exist"""
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            url TEXT NOT NULL,
            category TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dashboard_data_sources (
            dashboard_id INTEGER NOT NULL,
            data_source_id INTEGER NOT NULL,
            PRIMARY KEY (dashboard_id, data_source_id),
            FOREIGN KEY (dashboard_id) REFERENCES dashboards(id),
            FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
        )
    ''')
    
    conn.commit()
    conn.close()