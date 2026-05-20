
# Dashboard Registry

A web application that acts as a catalogue of dashboards used in a company.
It stores information about dashboards so people can find the right one quickly.

## Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite
- **API:** REST / JSON

## Project Structure

dashboard-registry/
├── routes/
│   ├── dashboards.py      # Dashboard API endpoints
│   └── data_sources.py    # Data source API endpoints
├── models/
├── app.py                 # Flask app entry point
├── database.py            # Database connection and table setup
├── seed.py                # Sample data
└── README.md

## How to Run Locally

1. Clone the repository

git clone https://github.com/reezariaaz/dashboard-registry.git
cd dashboard-registry

2. Create and activate virtual environment

python -m venv venv
venv\Scripts\activate

3. Install dependencies

pip install flask

4. Run the app

python app.py

5. Load sample data (optional)

python seed.py

The app runs on http://127.0.0.1:5000

## API Endpoints

### Dashboards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboards | Get all dashboards (supports ?search= &category= &status=) |
| POST | /api/dashboards | Create a new dashboard |
| GET | /api/dashboards/:id | Get a single dashboard with linked data sources |
| PUT | /api/dashboards/:id | Update a dashboard |
| DELETE | /api/dashboards/:id | Delete a dashboard |

### Data Sources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/data-sources | Get all data sources (supports ?search=) |
| POST | /api/data-sources | Create a new data source |
| GET | /api/data-sources/:id | Get a single data source with linked dashboards |
| PUT | /api/data-sources/:id | Update a data source |
| DELETE | /api/data-sources/:id | Delete a data source |

## Design Decisions

### Deleting Data Sources
If a data source is still linked to one or more dashboards, the delete request
will be blocked and return an error message. The user must remove the links
from the dashboards first before deleting the data source. This prevents
accidental data loss and keeps the registry consistent.

### Status Values
Dashboard status is restricted to: Up, Down, or Unknown.

### Data Source Types
Data source type is restricted to: Database, File, or API.