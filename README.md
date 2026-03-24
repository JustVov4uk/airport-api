# ✈️ Airport API

A production-ready RESTful API service for airport management built with Django REST Framework. The system enables users to search flights, book tickets, and allows administrators to manage the entire airport infrastructure.

---

## 🚀 Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Backend        | Django 5.2 + Django REST Framework  |
| Database       | PostgreSQL                          |
| Authentication | JWT (djangorestframework-simplejwt) |
| Infrastructure | Docker + docker-compose             |
| Documentation  | drf-spectacular (Swagger / ReDoc)   |
| Testing        | Django TestCase + coverage (97%)    |
| Code Quality   | black, flake8, isort                |

---

## ✨ Features

- **JWT Authentication** — email-based login, token refresh
- **Role-based access control** — Anonymous / Authenticated / Admin
- **Dynamic ticket pricing** — price increases as flight fills up (50% / 80% / 100% thresholds)
- **Booking validation** — seat/row bounds, duplicate seat prevention, race condition protection via `unique_together`
- **Order cancellation policy** — cannot cancel within 24 hours of departure
- **Email notifications** — confirmation email on order creation
- **Flight filtering** — by source/destination airport, date range, seat availability
- **Analytics endpoints** — flight occupancy %, global statistics (admin only)
- **Image upload** — airplane photos via dedicated endpoint
- **API documentation** — Swagger UI and ReDoc
- **Pagination, throttling, CORS** — production-ready configuration

---

## 📦 Project Structure

```
airport-api/
├── airplane/       # Airplane and AirplaneType models
├── airport/        # Airport, City, Country, Route models
├── flight/         # Flight, Crew models + statistics
├── order/          # Order, Ticket models + email notifications
├── user/           # Custom User model (email-based auth)
├── core/           # Management commands (wait_for_db)
├── config/         # Django settings, URLs, permissions
├── Dockerfile
├── docker-compose.yaml
└── .env.example
```

---

## 🏃 Running with Docker

### 1. Clone the repository

```bash
git clone https://github.com/JustVov4uk/airport-api.git
cd airport-api
```

### 2. Create `.env` file

```bash
cp .env.example .env
```

Fill in your values:

```env
POSTGRES_DB=airport
POSTGRES_USER=airport
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Build and run

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### 4. Create superuser

```bash
docker-compose exec app python manage.py createsuperuser
```

### 5. Populate database with test data (optional)
```bash
docker-compose exec app python manage.py populate_db
```
This creates sample countries, cities, airports, airplanes, crew members, routes and flights.
---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| POST   | `/api/token/`         | Obtain JWT token pair |
| POST   | `/api/token/refresh/` | Refresh access token  |

### Airports
| Method    | Endpoint                      | Auth  | Description                          |
|-----------|-------------------------------|-------|--------------------------------------|
| GET       | `/api/airport/airports/`      | All   | List airports (search by name, city) |
| GET       | `/api/airport/airports/{id}/` | All   | Airport detail                       |
| POST      | `/api/airport/airports/`      | Admin | Create airport                       |
| PUT/PATCH | `/api/airport/airports/{id}/` | Admin | Update airport                       |
| DELETE    | `/api/airport/airports/{id}/` | Admin | Delete airport                       |

### Routes
| Method | Endpoint               | Auth  | Description  |
|--------|------------------------|-------|--------------|
| GET    | `/api/airport/routes/` | All   | List routes  |
| POST   | `/api/airport/routes/` | Admin | Create route |

### Flights
| Method | Endpoint                                    | Auth  | Description               |
|--------|---------------------------------------------|-------|---------------------------|
| GET    | `/api/flight/flights/`                      | All   | List flights with filters |
| GET    | `/api/flight/flights/{id}/`                 | All   | Flight detail with crew   |
| POST   | `/api/flight/flights/`                      | Admin | Create flight             |
| GET    | `/api/flight/flights/{id}/available-seats/` | All   | List available seats      |
| GET    | `/api/flight/flights/{id}/occupancy/`       | Admin | Flight occupancy %        |

### Orders
| Method | Endpoint                         | Auth          | Description               |
|--------|----------------------------------|---------------|---------------------------|
| GET    | `/api/order/orders/`             | Authenticated | List own orders           |
| POST   | `/api/order/orders/`             | Authenticated | Create order with tickets |
| POST   | `/api/order/orders/{id}/cancel/` | Authenticated | Cancel order              |

### Airplanes
| Method | Endpoint                                     | Auth  | Description           |
|--------|----------------------------------------------|-------|-----------------------|
| GET    | `/api/airplane/airplanes/`                   | All   | List airplanes        |
| POST   | `/api/airplane/airplanes/`                   | Admin | Create airplane       |
| POST   | `/api/airplane/airplanes/{id}/upload-image/` | Admin | Upload airplane photo |

### Analytics
| Method | Endpoint           | Auth  | Description       |
|--------|--------------------|-------|-------------------|
| GET    | `/api/statistics/` | Admin | Global statistics |

### Documentation
| Endpoint            | Description |
|---------------------|-------------|
| `/api/doc/swagger/` | Swagger UI  |
| `/api/doc/redoc/`   | ReDoc       |

---

## 💰 Dynamic Pricing Logic

Ticket price is calculated at booking time based on flight occupancy:

| Occupancy | Multiplier         |
|-----------|--------------------|
| 0 – 50%   | × 1.0 (base price) |
| 50 – 80%  | × 1.25             |
| 80 – 100% | × 1.5              |

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test airplane.tests airport.tests flight.tests order.tests

# Run with coverage
coverage run manage.py test airplane.tests airport.tests flight.tests order.tests
coverage report
```

Current coverage: **97%**

---

## 📝 Environment Variables

| Variable            | Description                         |
|---------------------|-------------------------------------|
| `SECRET_KEY`        | Django secret key                   |
| `DEBUG`             | Debug mode (True/False)             |
| `ALLOWED_HOSTS`     | Comma-separated allowed hosts       |
| `POSTGRES_DB`       | Database name                       |
| `POSTGRES_USER`     | Database user                       |
| `POSTGRES_PASSWORD` | Database password                   |
| `POSTGRES_HOST`     | Database host (use `db` for Docker) |
| `POSTGRES_PORT`     | Database port (5432)                |
