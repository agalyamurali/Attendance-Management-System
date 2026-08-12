# Mini Attendance Management System

A full-stack employee and attendance management system built with **FastAPI, React, and MySQL**. The system provides JWT authentication, employee management, attendance tracking, dashboard analytics, and CSV/Excel export.

## Features

### Authentication

* JWT-based authentication
* Secure password hashing with bcrypt
* Protected API routes
* Centralized authentication state

### Employee Management

* Create, view, update, and deactivate employees
* Search and filter employees
* Department and status filtering
* Pagination and sorting
* Soft deletion to preserve attendance history

### Attendance Management

* Mark daily attendance
* Attendance status validation
* Check-in and check-out time validation
* Duplicate attendance prevention
* Attendance filtering and pagination
* Employee attendance history
* Date-range attendance summaries
* CSV and Excel export

### Dashboard

* Total employees
* Active employees
* Present and absent employees
* Department-wise employee statistics
* Server-side aggregated statistics
* 
## Architecture

### Backend

Router → Service → Repository → SQLAlchemy → MySQL
* **Router:** Handles HTTP requests and responses
* **Service:** Contains business rules and validation
* **Repository:** Handles database operations
* **Models:** Define database entities using SQLAlchemy

### Frontend

Pages / Components → Service Layer → Axios → FastAPI
* Reusable React components
* Centralized API service layer
* Shared Axios configuration
* JWT-based request authentication
* React Context for authentication state

## Technology Stack

| Layer          | Technologies                                  |
| -------------- | --------------------------------------------- |
| Frontend       | React 18, Vite, React Router, Axios, CSS      |
| Backend        | FastAPI, Pydantic v2, SQLAlchemy 2.0, PyMySQL |
| Authentication | JWT, python-jose, bcrypt                      |
| Database       | MySQL                                         |
| Export         | Python CSV, openpyxl                          |

## Database Design

The system uses three core tables:

users
  │
  └── Administrator accounts

employees
  │
  └──< attendance

### Tables

* `users` — Authentication and administrator accounts
* `employees` — Employee information
* `attendance` — Daily attendance records

### Key Database Constraints

* Unique employee email/code
* Unique attendance record per employee and date
* Foreign key relationship between employees and attendance
* `ON DELETE RESTRICT` to protect attendance history
* Employee deletion implemented as a soft delete

The complete database schema is available at: database/init.sql

## API Documentation

Interactive Swagger documentation is available at:

http://localhost:8000/docs

### Authentication

| Method | Endpoint          | Auth | Description                    |
| ------ | ----------------- | ---- | ------------------------------ |
| POST   | `/api/auth/login` | No   | Authenticate and receive JWT   |
| GET    | `/api/auth/me`    | Yes  | Get current authenticated user |

### Employees

| Method | Endpoint              | Auth | Description               |
| ------ | --------------------- | ---- | ------------------------- |
| POST   | `/api/employees`      | Yes  | Create employee           |
| GET    | `/api/employees`      | Yes  | List and filter employees |
| GET    | `/api/employees/{id}` | Yes  | Get employee              |
| PUT    | `/api/employees/{id}` | Yes  | Update employee           |
| DELETE | `/api/employees/{id}` | Yes  | Deactivate employee       |

### Attendance

| Method | Endpoint                        | Auth | Description                     |
| ------ | ------------------------------- | ---- | ------------------------------- |
| POST   | `/api/attendance`               | Yes  | Mark attendance                 |
| GET    | `/api/attendance`               | Yes  | List and filter attendance      |
| GET    | `/api/attendance/summary`       | Yes  | Get attendance summary          |
| GET    | `/api/attendance/employee/{id}` | Yes  | Get employee attendance history |
| GET    | `/api/attendance/export`        | Yes  | Export attendance records       |

### Dashboard

| Method | Endpoint               | Auth | Description              |
| ------ | ---------------------- | ---- | ------------------------ |
| GET    | `/api/dashboard/stats` | Yes  | Get dashboard statistics |

Protected endpoints require:

Authorization: Bearer <JWT_TOKEN>

## Project Structure

twite-attendance/
│
├── database/
│   └── init.sql
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── routers/
│   │   └── core/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── services/
│   │   ├── context/
│   │   ├── routes/
│   │   ├── components/
│   │   └── pages/
│   │
│   ├── package.json
│   ├── .env.example
│   └── ...
│
└── README.md

## Environment Variables

### Backend

Create:
backend/.env
using `backend/.env.example` as a template.

.env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/attendance_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=90
CORS_ORIGINS=http://localhost:5173

### Frontend

Create:
frontend/.env
using `frontend/.env.example`.

.env
VITE_API_BASE_URL=http://localhost:8000

Do not commit `.env` files.

## Installation & Setup

### 1. Clone the Repository

git clone <repository-url>
cd filename


### 2. Setup Database

Create the database using:

mysql -u root -p < database/init.sql

### 3. Setup Backend


cd backend
python -m venv venv
Windows:venv\Scripts\activate
Linux/macOS:source venv/bin/activate

Install dependencies:

pip install -r requirements.txt
Create `.env` from `.env.example`, configure the database and JWT settings, then start the server:
uvicorn app.main:app --reload

Backend: http://localhost:8000

Swagger: http://localhost:8000/docs


### 4. Setup Frontend

Open another terminal:

cd frontend
npm install
Create `.env` from `.env.example`, then run:
npm run dev

Frontend: http://localhost:5173


## Business Rules

### Attendance

| Status   | Check-in    | Check-out   |
| -------- | ----------- | ----------- |
| PRESENT  | Required    | Optional    |
| HALF_DAY | Required    | Optional    |
| ABSENT   | Not allowed | Not allowed |
| ON_LEAVE | Not allowed | Not allowed |

Attendance validation ensures:

1. Employee exists.
2. Employee is active.
3. Only one attendance record exists per employee per date.
4. Check-in/check-out values follow the selected status.
5. Check-out cannot be earlier than check-in.

### Employee Deactivation

Employees are not permanently deleted.

When an employee is deleted:
ACTIVE → INACTIVE
Existing attendance records remain available for historical reporting.

## Demo Credentials

For local evaluation:

Username: admin
Password: Admin@123

> Change the default credentials before deploying the application to a production environment.

## Postman Collection

A Postman collection containing the application's API endpoints is available in:

postman/
└── Twite-Attendance-API.postman_collection.json

Import the collection into Postman to test the API.

## Database Script

The database initialization script is available at:
database/init.sql
It contains the required database schema, tables, constraints, indexes, and seed data.

## API Testing

The API can be tested using:

* Swagger UI
* Postman

Swagger:

http://localhost:8000/docs


## License

This project was developed as part of a technical assessment and is provided for evaluation purposes.
