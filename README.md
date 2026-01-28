
# 📐 System Design & Database Schema

## Overview
This project is a **Marketplace CSV Validation Service** built using **FastAPI**.  
It allows marketplaces to define validation templates and sellers to upload CSV files and mappings, which are then validated against those templates.

---

## 🧠 High-Level System Design

### Core Concept
The system separates responsibilities clearly:

- **Marketplace** defines *what data is expected*
- **Seller** provides *how their CSV maps to that expectation*

```
Marketplace Template (rules)
        ▲
        │
Seller Mapping (JSON)
        │
        ▼
   Seller CSV File
        │
        ▼
 Validation Engine
        │
        ▼
 Validation Result
```

---

## 🧩 Major Components

### 1. API Layer (FastAPI)
- Handles requests and responses
- Registers routes dynamically
- Applies authentication middleware

### 2. Authentication
- JWT-based authentication
- Middleware validates token for all protected routes

### 3. Handlers
- Encapsulate business logic
- Examples:
  - CSV upload
  - Template upload
  - Mapping upload
  - CSV validation

### 4. Validation Engine
- Applies field-level rules defined in templates
- Supports:
  - Required fields
  - Type validation
  - Length & range checks
  - Enum validation
  - Uniqueness constraints
  - Cross-field validation (price ≤ MRP)

### 5. Storage
- **Filesystem**: Stores CSV, template JSON, mapping JSON
- **Database**: Stores metadata and relationships

---

## 🗂️ Directory Architecture

```
source/
├── handlers/        # API handlers
├── utility/         # Validators & helpers
├── db/              # DB models & session
├── routes.py        # Route definitions
├── register.py      # Dynamic route registration
├── main.py          # App entry point
```


### 🟦 files

Stores all uploaded files.

| Column | Type | Description |
|------|------|------------|
| id | bigint (PK) | File identifier |
| file_name | string | Original filename |
| file_path | string (unique) | Disk path |
| file_type | string | csv / json |
| created_at | timestamp | Upload time |

---

### 🟦 marketplace_templates

Stores marketplace templates.

| Column | Type | Description |
|------|------|------------|
| id | bigint (PK) | Template ID |
| template_name | string | Marketplace name |
| version | string | Template version |
| file_id | bigint (FK) | Reference to files |
| created_at | timestamp | Created time |
| updated_at | timestamp | Updated time |

**Constraints**
- UNIQUE(template_name, version)

---

### 🟦 seller_csv_uploads

Tracks seller CSV uploads.

| Column | Type | Description |
|------|------|------------|
| id | bigint (PK) | Upload ID |
| seller_id | string | Seller identifier |
| csv_file_id | bigint (FK) | CSV file |
| created_at | timestamp | Upload time |

---

### 🟦 seller_template_mappings

Stores seller-to-template mappings.

| Column | Type | Description |
|------|------|------------|
| id | bigint (PK) | Mapping ID |
| seller_id | string | Seller identifier |
| marketplace | string | Marketplace name |
| template_id | bigint (FK) | Template |
| mapping_file_id | bigint (FK) | Mapping JSON |
| created_at | timestamp | Created time |

**Constraints**
- UNIQUE(seller_id, template_id)

---

Alright, here’s a **clean, professional “Setup Instructions” section** you can directly put into your `README.md`.
This is written assuming **local development**, **FastAPI**, and **PostgreSQL**, and matches how your project is actually built.

---

# ⚙️ Setup Instructions

This section explains how to set up and run the project locally for development and testing.

---

## 🧩 Prerequisites

Ensure the following are installed on your system:

* **Python** ≥ 3.10
* **pip** (comes with Python)
* **PostgreSQL** ≥ 13
* **Git**
* (Optional) **virtualenv** or **venv**

---

## 📥 Clone the Repository

```bash
git clone <repository-url>
cd <project-root>
```

---

## 🐍 Create & Activate Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

> Make sure `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2`, `pydantic`, and `jwt` are installed.

---

## 🗄️ Database Setup (PostgreSQL)

### 1️⃣ Create Database

```sql
CREATE DATABASE marketplace;
```

### 2️⃣ Create User (optional but recommended)

```sql
CREATE USER marketplace_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE marketplace TO marketplace_user;
```

---

## 🔐 Configuration Setup

Create a `config.json` file in the **project root**.

### 📄 `config.json`

```json
{
  "database": {
    "url": "postgresql://marketplace_user:password@localhost:5432/marketplace"
  }
}
```

> ⚠️ Do not commit `config.json` to version control.

---

## 📁 Directory Initialization

The following directories are required and will be auto-created on startup:

```
templates/   # Marketplace templates
uploads/     # Seller CSV uploads
mapping/     # Seller mapping JSON files
logs/        # Application logs
```

No manual action is needed.

---

## ▶️ Run the Application

```bash
uvicorn source.main:app --reload
```

The application will start at:

```
http://localhost:8000
```

---

## 📘 API Documentation (Swagger)

Once the server is running, access:

* **Swagger UI**
  👉 [http://localhost:8000/docs](http://localhost:8000/docs)

* **OpenAPI JSON**
  👉 [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🔑 Authentication Flow (Local)

1. Call `/token` using **Basic Auth**

   * Username: `admin`
   * Password: `Admin@123`

2. Receive JWT token

3. Use token in all protected APIs:

```http
Authorization: Bearer <JWT_TOKEN>
```

---

## 🧪 Run Tests

```bash
pytest
```

(Optional)

```bash
pytest --cov=source
```

---

## 🪵 Logs

Logs are written to:

```
logs/app.log
```

With:

* File rotation
* Console logging enabled

---

## 🛑 Common Issues & Fixes

### Database connection error

* Ensure PostgreSQL is running
* Verify `database.url` in `config.json`

### Permission issues

* Ensure write access for `templates/`, `uploads/`, `mapping/`, `logs/`

### Port already in use

```bash
uvicorn source.main:app --reload --port 8080
```

