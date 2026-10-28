# Apartment Management System

A mobile-first web app for running day-to-day apartment operations: apartment structure (blocks and flats),
residents and their vehicles, and a visitor log. Access is role-based, so each staff member sees and changes
only what their job needs.

> **Status:** in progress. The backend (data model, login, role-based permissions, tests) is working.
> The React + TypeScript frontend is being built screen by screen. See the [roadmap](#roadmap).

## Roles and permissions

Three roles. Visitors and workers are records in the system, not users who log in.

| Action | Admin | Secretary | Security |
|---|---|---|---|
| Apartment and blocks: create, update, delete | Yes | No | No |
| Apartment and blocks: read | Yes | Yes | Yes |
| Create staff users, reset passwords | Yes | No | No |
| Flats: create, update, delete | No | Yes | No |
| Flats: read | Yes | Yes | Yes |
| Residents and vehicles: create, update | No | Yes | Yes |
| Residents and vehicles: read | Yes | Yes | Yes |
| Residents and vehicles: delete | No | Yes | No |
| Visitors: create, update, check-out | No | No | Yes |
| Visitors: delete | No | No | No |
| Visitors and logs: read | Yes | Yes | Yes |
| Export visitor log (CSV) | No | Yes | Yes |

**Account rules**

- No self-registration. The admin creates accounts and hands over a temporary password.
- Password resets go through the admin. Only a bcrypt hash is stored, so nobody can read a password.
- The first admin is created by a one-time seed script.
- Login returns a time-limited JWT. Every request is checked on the server against the role stored in the database.
- Visitor entries are never deleted. Mistakes are corrected by editing, so the log stays trustworthy.
- Residents do not log in for now. The data model keeps an optional link from a resident to a user for later.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React, TypeScript, Vite, React Router |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2 |
| Auth | JWT (PyJWT) and bcrypt |
| Database | SQLite for local development, PostgreSQL (Supabase) for deployment |
| Testing | pytest |
| Hosting | Netlify (frontend), Northflank (backend), Supabase (database) |

## Data model

```
Role 1---* User 1---0..1 StaffProfile
Apartment 1---* Block 1---* Flat 1---* Resident 1---* Vehicle
```

Design rules: each fact is stored once and referenced by id, derived numbers such as total flats are computed
instead of stored, and block name plus flat number must be unique within an apartment.

## Project structure

```
apartment-management-system/
  README.md
  backend/
    app/
      main.py          app creation, routers, /health
      database.py      engine, session, Base, get_db
      models.py        database tables
      schemas.py       request and response shapes (Pydantic)
      security.py      password hashing and JWT helpers
      deps.py          current user and permission groups
      routers/         auth, users, setup, flats, residents
    scripts/seed.py    creates roles and the first admin
    tests/             permission tests
    requirements.txt
    requirements-dev.txt
  frontend/
    src/
      api/             typed API client and shared types
      auth/            auth context, provider, protected route
      components/      layout
      pages/           LoginPage, FlatsPage
```

## Run locally

### Backend

Run all commands from `backend/`.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m scripts.seed             # creates roles and the admin user (prompts for a password)
uvicorn app.main:app --reload      # http://localhost:8000/docs
python -m pytest                   # run the tests
```

Optional environment variables (defaults work for local development):

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Database connection string | `sqlite:///./avm.db` |
| `SECRET_KEY` | JWT signing key.| development-only key |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173` |

### Frontend

Run all commands from `frontend/`.

```bash
npm install
cp .env.example .env.local         # VITE_API_URL=http://localhost:8000
npm run dev                        # http://localhost:5173
```
## API overview

| Method | Path | Allowed roles |
|---|---|---|
| POST | `/auth/login` | public |
| GET | `/auth/me` | any logged-in user |
| PATCH | `/auth/me/duty` | security |
| GET, POST | `/users` | admin |
| PUT | `/users/{id}/password` | admin |
| POST | `/apartments`, `/blocks` | admin |
| GET | `/apartments`, `/blocks` | admin, secretary, security |
| POST | `/flats` | secretary |
| GET | `/flats` | admin, secretary, security |
| GET | `/residents`, `/residents/{id}` | admin, secretary, security |
| POST, PUT | `/residents[/{id}]` | secretary, security |
| DELETE | `/residents/{id}` | secretary |
| GET | `/health` | public |

## Testing

`backend/tests` contains a permission matrix test that runs every role against every protected endpoint, and a
test that fails if any route is added without a login requirement.

## Roadmap

**Phase 1: working product**

- [x] Database models and apartment setup
- [x] Login, roles, protected endpoints and permission tests
- [ ] React + TypeScript project, Login and Flats screens
- [ ] Vehicles, visitors, check-out and CSV export
- [ ] Remaining screens (admin, secretary, security dashboards)
- [ ] Alembic migrations
- [ ] Deployment

**Phase 2: AI features**

- [ ] Free-text visitor entry converted into a structured record, confirmed by the guard before saving
- [ ] Natural-language log search through a fixed set of safe query functions, never raw generated SQL
- [ ] Evaluation set with accuracy results, protection against prompt injection, and minimal personal data sent to the model provider

## Design decisions

- **Permissions live in one place.** `deps.py` defines named permission groups (for example `ADMIN_ONLY`, `FRONT_DESK`) and routers reference them.
- **The server is the authority.** The UI hides what a role cannot do, but every endpoint enforces it.
- **The role is read from the database, not the token.** A role change applies immediately and a forged token cannot grant access.
- **No visitor delete endpoint.** The safest permission is an endpoint that does not exist.
- **Residents cannot be deleted while visitor records reference them.** The API returns 409 to keep the log intact.
- **Tables are created on startup for now.** Alembic migrations replace this before deployment.

## Author

Naresh N. Full stack developer.
[GitHub](https://github.com/Naresh2028) | [LinkedIn](https://linkedin.com/in/naresh-fullstack)
