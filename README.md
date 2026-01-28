# System Design & Database Schema

## Overview
This project is a **Marketplace CSV Validation Service** built using **FastAPI**.  
It allows marketplaces to define validation templates and sellers to upload CSV files and mappings, which are then validated against those templates.

This project is designed to be run using **Docker and Docker Compose**.  
Manual Python virtualenv, dependency installation, and database setup are not required.

---

## High-Level System Design

### Core Concept
The system separates responsibilities clearly:

- Marketplace defines what data is expected
- Seller provides how their CSV maps to that expectation

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

## Major Components

### API Layer (FastAPI)
- Handles requests and responses
- Registers routes dynamically
- Applies authentication middleware

### Authentication
- JWT-based authentication
- Middleware validates token for all protected routes

### Handlers
- Encapsulate business logic
- CSV upload, template upload, mapping upload, validation

### Validation Engine
- Rule-based CSV validation
- Required fields, type checks, enums, uniqueness
- Cross-field validation (price ≤ MRP)

### Storage
- Filesystem (Docker volumes): CSVs, templates, mappings, logs
- PostgreSQL: Metadata and relationships

---

## Directory Architecture

```
source/
├── handlers/
├── utility/
├── db/
├── routes.py
├── register.py
├── main.py
```

---

## Database Schema

The database stores metadata only.  
Actual files are stored on disk via Docker volumes.

### files
| Column | Type | Description |
|------|------|------------|
| id | bigint (PK) |
| file_name | string |
| file_path | string |
| file_type | string |
| created_at | timestamp |

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

## Running the Application (Docker)

### Prerequisites
- Docker
- Docker Compose

---

### Build and Run

```bash
docker compose up --build
```

---

### Application Access

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Authentication

```bash
curl -u admin:Admin@123 http://localhost:8000/token
```

Use the token as:

```http
Authorization: Bearer <JWT_TOKEN>
```

---

## Running Tests

```bash
docker compose exec api pytest
```

---

## Logs

```
logs/app.log
```

---

## Stopping the Application

```bash
docker compose down
```

To reset database data:

```bash
docker compose down -v
```


#  Marketplace API Documentation

Base URL:
```
http://localhost:8000
```

Authentication:
- **Basic Auth** → Token generation, CSV upload, mapping
- **Bearer Token (JWT)** → Template APIs

---

##  Get Access Token

**GET** `/token`

Generates a JWT token using **Basic Authentication**.

### Request
```http
GET /token
Authorization: Basic <base64(username:password)>
```

### Response – 200 OK
```json
{
  "creadentials": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

##  Upload Marketplace Template

**POST** `/v1/template`

Uploads a marketplace template file.

### Authentication
`Bearer <JWT_TOKEN>`

### Request
`multipart/form-data`

| Field | Type | Description |
|------|------|-------------|
| file | file | Template definition file |

### Response – 200 OK
```json
{
  "message": "Template uploaded successfully",
  "templateId": 1,
  "fileId": 1,
  "template_name": "MYNTRA",
  "version": "1.0"
}
```

---

##  Get Template by Marketplace

**GET** `/v1/template?marketplace_name=MYNTRA`

Fetches template details for a given marketplace.

### Authentication
`Bearer <JWT_TOKEN>`

### Query Parameters

| Name | Type | Required |
|------|------|----------|
| marketplace_name | string | Yes |

### Response – 200 OK
```json
{
  "marketplace": "MYNTRA",
  "template": {
    "templateName": "MYNTRA",
    "version": "1.0",
    "fields": {
      "productName": {
        "required": true,
        "type": "string",
        "maxLen": 200
      }
    }
  }
}
```

---

##  Upload Seller CSV File

**POST** `/v1/uploadfile?seller_id=1`

Uploads a seller product CSV file.

### Authentication
`Basic Auth`

### Query Parameters

| Name | Type | Required |
|------|------|----------|
| seller_id | integer | Yes |

### Request
`multipart/form-data`

| Field | Type | Description |
|------|------|-------------|
| file | file | CSV file |

### Response – 200 OK
```json
{
  "csvUploadId": 1,
  "fileId": 2,
  "headers": ["productName", "brand", "sku"],
  "rowCount": 10,
  "sampleRows": [
    {
      "productName": "TShirt",
      "brand": "Otto",
      "sku": "1000000"
    }
  ]
}
```

---

##  Upload Seller Mapping

**POST** `/v1/sellermapping?seller_id=1&template_id=1`

Uploads a seller-to-template mapping file.

### Authentication
`Basic Auth`

### Query Parameters

| Name | Type | Required |
|------|------|----------|
| seller_id | integer | Yes |
| template_id | integer | Yes |

### Request
`multipart/form-data`

| Field | Type | Description |
|------|------|-------------|
| file | file | Mapping file |

### Response – 200 OK
```json
{
  "status": "success",
  "mapping_id": 1,
  "mapping_file_id": 3,
  "template_id": 1,
  "marketplace": "MYNTRA"
}
```

---

##  Validate Mapping & Apply Rules

**POST** `/v1/mapping?seller_id=1&mapping_file_id=3`

Validates uploaded CSV rows against the marketplace template.

### Authentication
`Basic Auth`

### Query Parameters

| Name | Type | Required |
|------|------|----------|
| seller_id | integer | Yes |
| mapping_file_id | integer | Yes |

### Response – 200 OK
```json
{
  "seller_id": "1",
  "mapping_file_id": 3,
  "total": 10,
  "valid": 0,
  "errors": [
    {
      "row": 1,
      "valid": false,
      "errors": {
        "productName": "Validation failed",
        "sku": "Validation failed"
      }
    }
  ]
}
```

---

##  Health Check

**GET** `/v1`

### Response – 200 OK
```json
{
  "status": "ok"
}
```
