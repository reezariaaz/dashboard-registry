
from flask import Flask
from database import init_db
from routes.data_sources import data_sources_bp
from routes.dashboards import dashboards_bp

# Create the Flask application
app = Flask(__name__)

# Register routes with the app
app.register_blueprint(data_sources_bp)
app.register_blueprint(dashboards_bp)

# When this file runs, initialize the database
if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
    app.run(debug=True)