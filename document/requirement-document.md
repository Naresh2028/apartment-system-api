# Apartment Management System: Project Overview

Owner : Naresh N · 

## 1. Description

A mobile-first web application for running the day-to-day operations of an apartment community. 
It replaces paper registers with one place to record the apartment structure (blocks and flats), residents and 
their vehicles, and every visitor who enters the premises. Access is role-based: the admin sets up the apartment and 
staff accounts, the secretary maintains flats and residents, and security guards record visitors and manage their duty status.

The project is also a portfolio piece for a move from .NET and Angular full stack development into AI engineering. 
Phase 2 adds LLM features on top of the working product.

## 2. Goals and non-goals

**Goals**

- One trusted record of who lives where, which vehicles belong to whom, and who visited and when.
- Fast data entry for guards on a phone at the gate.
- Strict role separation so each person sees and changes only what their job needs.
- A simple weekly and monthly visitor log export.

**Non-goals for now**

- Online payments, maintenance billing and accounting.
- A resident-facing app or resident logins (the data model leaves room for it later).
- SMS or push notifications.

## 3. Roles and permissions

Three staff roles. Visitors and workers are records in the system, not users who log in.

| Action | Admin | Secretary | Security |
| --- | --- | --- | --- |
| Apartment and blocks: create, update, delete | Yes | No | No |
| Apartment and blocks: read | Yes | Yes | Yes |
| Create staff users, reset passwords | Yes | No | No |
| Flats: create, update, delete | No | Yes | No |
| Flats: read | No | Yes | Yes |
| Residents and vehicles: create, update | No | Yes | Yes |
| Residents and vehicles: read | No | Yes | Yes |
| Residents and vehicles: delete | No | Yes | No |
| Visitors: create, update, delete | No | No | Yes |
| Visitors and logs: read | Yes | Yes | Yes |
| Export visitor log (CSV) | No | No | Yes |

**Account rules**

- No self-registration. The admin creates accounts and hands over a temporary password.
- Password resets go through the admin. Nobody, including the admin, can read an existing password because only a hash is stored.
- The first admin is created by a one-time seed script.
- Login returns a time-limited token. Every request is checked on the server against the role stored in the database.

## 4. Core features

**Admin**

- Set up the apartment profile and its blocks (name, floors, flats per floor).
- Create secretary and security accounts with a staff profile (name, phone, address, shift).
- Reset staff passwords.
- View the visitor log.

**Secretary**

- Register flats under a block, with floor, flat number and occupied status. The system rejects a floor higher than the block allows and a duplicate flat number in a block.
- Register residents (owner or rental) against a flat, and their vehicles (two, three or four wheeler plus number).
- Search and update resident records. Delete a resident only if no visitor records depend on them.
- View the visitor log.

**Security**

- Switch between On Duty and Off Duty.
- Search residents by name, phone or flat to find the flat being visited.
- Record a visitor: name, purpose, optional vehicle number, flat, optional resident, automatic check-in time.
- Mark check-out, edit or delete entries.
- View the log and export it for the last week or month.

## 5. Data model

| Entity | Key fields | Relationships |
| --- | --- | --- |
| Role | role name (admin, secretary, security) | has many users |
| User | username, password hash | belongs to one role, has one optional staff profile |
| Staff profile | full name, phone, address, shift (day or night), on duty flag | one-to-one with user |
| Apartment | name, address | has many blocks |
| Block | name, total floors, flats per floor | belongs to an apartment, has many flats |
| Flat | floor, flat number, occupied | belongs to a block, has many residents and visitors |
| Resident | name, phone, type (owner or rental) | belongs to a flat, optional link to a user, has many vehicles |
| Vehicle | type, vehicle number | belongs to a resident |
| Visitor | name, purpose, vehicle number, check-in, check-out | belongs to a flat, optional resident, recorded by a user |

Design rules: every fact is stored once and referenced by id, derived numbers such as total flats are computed rather than stored, and block name plus flat number must be unique within the apartment.

## 6. Screens (MVP)

1. **Login**: username and password, role-based redirect.
2. **Admin dashboard**: apartment and blocks setup, staff user list, create user, reset password.
3. **Secretary dashboard**: flats list and form, residents list and form, vehicles under each resident.
4. **Security dashboard**: duty toggle, resident search, new visitor form, today's visitors with check-out.
5. **Visitor log and export**: filterable list, week and month CSV export.

Design direction: mobile-first, large touch targets, one primary action per screen, minimal typing at the gate.

## 7. Tech stack and deployment

| Layer | Choice |
| --- | --- |
| Frontend | React with Vite, deployed on Netlify (free) |
| Backend | Python and FastAPI with SQLAlchemy, deployed on Northflank
| Database | SQLite for local development, PostgreSQL on Supabase (free) for deployment |
| Auth | JWT tokens and bcrypt password hashing |

## 8. Roadmap

**Phase 1: working product**

- Database models and apartment setup (done).
- Login, roles and protected endpoints (in progress).
- Vehicles, visitors and CSV export.
- React screens and role-based routing.
- Tests, migrations and deployment.

**Phase 2: AI features** 

- Free-text visitor entry converted into a structured record, confirmed by the guard before saving.
- Natural-language log search using a fixed set of safe query functions, never raw generated SQL.
- Evaluation set with accuracy numbers, guardrails against prompt injection, and minimal personal data sent to the model provider.


