
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.data_sources import data_sources_bp
from routes.dashboards import dashboards_bp

# Create the Flask  application 
app = Flask(__name__)

# Allow frontend to talk to the API
CORS(app)

# Register routes with the app
app.register_blueprint(data_sources_bp)
app.register_blueprint(dashboards_bp)

# When this file runs, initialize the database
if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
    app.run(debug=True)