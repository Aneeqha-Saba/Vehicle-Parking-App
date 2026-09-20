# Vehicle Parking App

A full-stack web application for managing vehicle parking lots, spots, and reservations. The system supports two roles — **Admin** and **User** — with role-based dashboards, real-time spot availability, booking workflows, analytics, and background jobs for reports and notifications.

**Student ID:** 23f1001225

---

## Features

### Admin
- Create, edit, and delete parking lots
- View all parking spots and their occupancy status
- Monitor registered users and their parking history
- Search users by ID
- View summary charts (available vs. occupied spots per lot)
- Export parking data as CSV (async background job)

### User
- Register and log in with JWT authentication
- Browse available parking lots and reserve a spot
- Release a parked spot and view calculated parking cost
- View booking history and profile details
- Search parking lots by location name
- View usage summary charts (bookings per lot)

### Background Jobs (Celery)
- **CSV Export** — User-triggered async export of all reservation records
- **Monthly Report** — Scheduled HTML email report with parking activity (spots booked, most-used lots, amount spent)
- **Notifications** — Google Chat webhook alerts when a new parking lot is created

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Vue 3, Vue Router, Vite, Bootstrap 5, Chart.js, Axios |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Caching |
| **Database** | SQLite |
| **Task Queue** | Celery |
| **Cache / Broker** | Redis |
| **Email** | SMTP (MailHog for local development) |

---

## Project Structure

```
23f1001225-Vehicle-Parking-App/
├── backend/
│   ├── app.py                  # Flask application entry point
│   ├── celery_config.py        # Celery broker & result backend config
│   ├── requirements.txt        # Python dependencies
│   ├── application/
│   │   ├── config.py           # App configuration (DB, JWT secret)
│   │   ├── database.py         # SQLAlchemy instance
│   │   ├── models.py           # User, Parkinglot, ParkingSpot, Reservation
│   │   ├── routes.py           # REST API endpoints
│   │   ├── security.py         # JWT setup
│   │   ├── tasks.py            # Celery background tasks
│   │   └── mail.py             # Email sending utility
│   └── static/                 # Generated CSV exports
└── frontend/
    ├── src/
    │   ├── components/         # Vue page components
    │   ├── routes.js           # Vue Router configuration
    │   └── main.js             # App entry point
    ├── package.json
    └── vite.config.js
```

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- **Redis** server (for caching and Celery)
- **MailHog** (optional, for testing email reports locally)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd 23f1001225-Vehicle-Parking-App
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Initialize the database (run once from the `backend` directory):

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Create an admin user (run in Python shell after DB is created):

```python
from app import app, db
from application.models import User

with app.app_context():
    admin = User(
        username="admin",
        email="admin@example.com",
        address="Admin Address",
        pincode=600001,
        password="admin123",
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Start Redis

Make sure Redis is running on `localhost:6379` before starting the backend or Celery worker.

```bash
# Windows (if installed via Chocolatey or WSL)
redis-server

# macOS (Homebrew)
brew services start redis

# Linux
sudo systemctl start redis
```

### 5. Start MailHog (optional, for email reports)

```bash
mailhog
```

MailHog listens on `localhost:1025` (SMTP) and provides a web UI at `http://localhost:8025`.

---

## Running the Application

Open **four separate terminals**:

**Terminal 1 — Flask backend** (port 5000)

```bash
cd backend
venv\Scripts\activate   # or source venv/bin/activate
python app.py
```

**Terminal 2 — Celery worker**

```bash
cd backend
venv\Scripts\activate
celery -A app.celery worker --loglevel=info
```

**Terminal 3 — Celery beat** (for scheduled monthly reports)

```bash
cd backend
venv\Scripts\activate
celery -A app.celery beat --loglevel=info
```

**Terminal 4 — Vue frontend** (port 5173)

```bash
cd frontend
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5173 |
| Backend API | http://127.0.0.1:5000 |
| MailHog UI | http://localhost:8025 |

---

## Usage

1. Open http://127.0.0.1:5173 in your browser.
2. **Register** a new user account, or **log in** as admin using the credentials created during setup.
3. **Admin** — create parking lots, manage spots, view users, and export CSV reports from the dashboard.
4. **User** — browse lots, reserve a spot with a vehicle number, and release it when leaving (cost is calculated automatically).

---

## API Endpoints

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/register` | Register a new user | Public |
| POST | `/api/login` | Login and receive JWT token | Public |
| GET | `/api/dashboard` | Role-based dashboard data | Auth |
| POST | `/api/create_lot` | Create a parking lot | Admin |
| GET/PUT | `/api/edit_lot/<id>` | View or update a lot | Admin |
| DELETE | `/api/delete_lot/<id>` | Delete a lot | Admin |
| DELETE | `/api/parking_spot/<id>` | Delete an available spot | Admin |
| GET | `/api/users` | List all users | Admin |
| POST | `/api/reserve_spot/` | Book a parking spot | User |
| POST | `/api/release_spot/` | Release a parked spot | User |
| GET | `/api/user/lots` | List lots with availability | User |
| POST | `/api/search` | Search users or lots | Auth |
| GET | `/api/summary` | Summary data for charts | Auth |
| POST | `/api/update_profile` | Update profile details | Auth |
| GET | `/export_csv` | Trigger CSV export job | Public |
| GET | `/api/csv_result/<id>` | Download exported CSV | Public |

All authenticated endpoints require a Bearer token in the `Authorization` header.

---

## Database Models

- **User** — username, email, address, pincode, password, role (`admin` / `user`)
- **Parkinglot** — location name, price per hour, address, pin code, number of spots
- **ParkingSpot** — linked to a lot, status (`A` = Available, `O` = Occupied)
- **Reservation** — links a user to a spot with vehicle number, timestamps, and parking cost

---

## Configuration

Key settings are in `backend/application/config.py`:

| Setting | Default |
|---------|---------|
| Database | `sqlite:///parkingdb.sqlite3` |
| JWT Secret | `top-secret-key` |
| Redis Cache | `localhost:6379` |
| Celery Broker | `redis://localhost:6379/0` |
| SMTP Server | `localhost:1025` (MailHog) |

Update these values for production deployments.

---

## License

This project was developed as part of an academic assignment (MAD-II).
