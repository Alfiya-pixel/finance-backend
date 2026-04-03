# Finance Data Processing and Access Control Backend

A clean, well-structured REST API backend for a finance dashboard system — built with **Python**, **FastAPI**, and **SQLite**.

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | FastAPI | Modern, fast, async-ready, auto docs |
| Database | SQLite + SQLAlchemy | Simple setup, no external DB needed |
| Auth | JWT (python-jose) | Stateless, standard token auth |
| Validation | Pydantic v2 | Built-in with FastAPI, strong typing |
| Password Hashing | bcrypt (passlib) | Industry standard |

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py               # App entry, router registration, global error handler
│   ├── database.py           # SQLAlchemy engine + session dependency
│   ├── seed.py               # Seed script — creates test users and sample data
│   ├── core/
│   │   ├── config.py         # Settings (JWT secret, expiry, DB URL)
│   │   ├── security.py       # JWT creation and verification
│   │   └── roles.py          # Role enum + hierarchy logic
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM models (User, FinancialRecord)
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py           # POST /api/auth/login
│   │   ├── users.py          # User management endpoints
│   │   ├── records.py        # Financial records endpoints
│   │   └── dashboard.py      # Dashboard summary endpoint
│   ├── services/
│   │   ├── auth_service.py   # Password hashing, login logic
│   │   ├── user_service.py   # User CRUD business logic
│   │   ├── record_service.py # Records CRUD + pagination + filtering
│   │   └── dashboard_service.py # Aggregation/analytics logic
│   └── middleware/
│       └── dependencies.py   # get_current_user + require_role() guard
├── requirements.txt
└── README.md
```

---

## Setup and Installation

### 1. Clone and navigate
```bash
git clone <your-repo-url>
cd finance-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the database
```bash
python -m app.seed
```

This creates the SQLite database (`finance.db`) with 3 test users and 10 sample records.

### 5. Start the server
```bash
uvicorn app.main:app --reload
```

API is now running at: **http://localhost:8000**  
Interactive docs (Swagger UI): **http://localhost:8000/docs**  
Alternative docs (ReDoc): **http://localhost:8000/redoc**

---

## Test Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@finance.dev | admin123 | Admin |
| analyst@finance.dev | analyst123 | Analyst |
| viewer@finance.dev | viewer123 | Viewer |

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/login` | Login, get JWT token | Public |

**Login request:**
```json
{
  "email": "admin@finance.dev",
  "password": "admin123"
}
```
**Response:**
```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

Use this token in all subsequent requests:
```
Authorization: Bearer <jwt_token>
```

---

### Users

| Method | Endpoint | Description | Min Role |
|--------|----------|-------------|----------|
| POST | `/api/users/` | Create user | Admin |
| GET | `/api/users/` | List all users | Admin |
| GET | `/api/users/me` | Get own profile | Any |
| GET | `/api/users/{id}` | Get user by ID | Admin |
| PATCH | `/api/users/{id}` | Update role/status | Admin |
| DELETE | `/api/users/{id}` | Delete user | Admin |

**Create user body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secret123",
  "role": "analyst"
}
```

---

### Financial Records

| Method | Endpoint | Description | Min Role |
|--------|----------|-------------|----------|
| POST | `/api/records/` | Create record | Analyst |
| GET | `/api/records/` | List records (paginated + filtered) | Viewer |
| GET | `/api/records/{id}` | Get single record | Viewer |
| PATCH | `/api/records/{id}` | Update record | Analyst |
| DELETE | `/api/records/{id}` | Soft-delete record | Admin |

**Create record body:**
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "Freelance",
  "date": "2026-04-01T00:00:00Z",
  "notes": "Website design project"
}
```

**Filter & pagination query params:**
```
GET /api/records?page=1&page_size=10&type=expense&category=rent&date_from=2026-01-01&date_to=2026-04-01
```

---

### Dashboard

| Method | Endpoint | Description | Min Role |
|--------|----------|-------------|----------|
| GET | `/api/dashboard/summary` | Full summary + trends | Analyst |

**Response includes:**
- `total_income`, `total_expenses`, `net_balance`
- `category_totals` — per-category aggregation
- `recent_activity` — last 10 records
- `monthly_trends` — last 12 months with income, expense, net

---

## Access Control Matrix

| Action | Viewer | Analyst | Admin |
|--------|--------|---------|-------|
| View records | ✅ | ✅ | ✅ |
| Create records | ❌ | ✅ | ✅ |
| Update records | ❌ | ✅ | ✅ |
| Delete records | ❌ | ❌ | ✅ |
| View dashboard | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| View own profile | ✅ | ✅ | ✅ |

Roles follow a hierarchy: `viewer < analyst < admin`. The `require_role(minimum_role)` dependency enforces this across all endpoints.

---

## Design Decisions and Assumptions

### Soft Delete
Records are never permanently deleted — a `is_deleted` flag is set instead. This preserves audit history and is standard practice in financial systems.

### Role Hierarchy
Rather than discrete permission lists, roles follow a linear hierarchy (`viewer < analyst < admin`). This keeps the logic simple and predictable. The `has_minimum_role()` function centralizes this check.

### Separation of Concerns
- **Routers** handle HTTP concerns only (request parsing, response codes)
- **Services** contain all business logic
- **Models** define data shape
- **Schemas** define API contracts (separate from DB models intentionally)

### JWT Auth
Tokens are stateless and expire in 24 hours. The `sub` field stores the user ID. Role is also embedded in the token payload for quick checks, but the actual user record is always verified from the DB on each request.

### SQLite Choice
SQLite is used for simplicity and zero-config setup as appropriate for an assessment. Migrating to PostgreSQL only requires changing `DATABASE_URL` in config — SQLAlchemy handles the rest.

### Pagination
All list endpoints default to `page=1`, `page_size=20`, capped at 100 per page. This prevents accidental large data dumps.

---

## Optional Enhancements Included

- ✅ **JWT Authentication** — full Bearer token flow
- ✅ **Pagination** — on records listing with metadata (total, pages)
- ✅ **Soft Delete** — records are flagged, not removed
- ✅ **Auto API Docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- ✅ **Seed Script** — instant test data setup

---

## Environment Variables (optional)

Create a `.env` file to override defaults:

```env
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./finance.db
```
