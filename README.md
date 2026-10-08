```markdown
# 🌍 Geospatial File Measurement API

> A CRS-aware FastAPI backend for uploading geospatial datasets, extracting features and metadata, and calculating accurate geometry measurements.

## 🚀 Overview

The **Geospatial File Measurement API** processes geospatial datasets such as Shapefiles and KML files and exposes their metadata, features, and geometry measurements through a REST API.

The system is designed around a simple principle:

> **Never calculate geospatial measurements directly from latitude/longitude coordinates.**

When a dataset uses a geographic CRS such as `EPSG:4326`, the system automatically determines a suitable projected CRS, transforms the geometries, and then calculates measurements in meters.

### What it supports

| Capability | Support |
|---|---|
| Shapefile (`.zip`) | ✅ |
| KML (`.kml`) | ✅ |
| Polygon area | ✅ |
| MultiPolygon area | ✅ |
| LineString length | ✅ |
| MultiLineString length | ✅ |
| Point measurements | N/A |
| CRS detection | ✅ |
| Geographic → projected CRS transformation | ✅ |
| PostgreSQL persistence | ✅ |
| REST API | ✅ |
| Swagger/OpenAPI | ✅ |
| Layered architecture | ✅ |

---

## 🏗️ Architecture

```text
                         Client
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │ API Layer   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Service   │
                    │    Layer    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        File Processor  Measurement  Validation
              │            │
              └──────┬─────┘
                     │
                     ▼
              ┌─────────────┐
              │ Repository  │
              │    Layer    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ PostgreSQL  │
              └─────────────┘
```

### Processing Pipeline

```text
Upload
  │
  ▼
Validate File
  │
  ├── ZIP ──► Extract ──► Find Shapefile
  │
  └── KML ──► Read KML
                  │
                  ▼
             GeoDataFrame
                  │
                  ▼
            Extract Features
                  │
                  ▼
             Validate CRS
                  │
          ┌───────┴────────┐
          │                │
       Missing          Geographic
          │                │
          ▼                ▼
        Reject       Project to CRS
                           │
                           ▼
                    Calculate Metrics
                           │
                           ▼
                    Persist to DB
                           │
                           ▼
                       Response
```

---

## 📐 CRS-Aware Measurements

A major design requirement of this project is avoiding incorrect measurements caused by calculating distances or areas directly in geographic coordinates.

For example:

```text
EPSG:4326
Latitude / Longitude
       │
       ▼
 Geographic CRS
       │
       ▼
Estimate suitable projected CRS
       │
       ▼
Transform geometry
       │
       ▼
Calculate area / length
       │
       ▼
Square meters / meters
```

If CRS information is missing, the system **rejects measurement processing** rather than returning potentially incorrect measurements.

---

## 🧩 Tech Stack

**Backend**

- Python
- FastAPI
- Uvicorn

**Geospatial**

- GeoPandas
- Shapely

**Database**

- PostgreSQL
- SQLAlchemy

**Validation / Serialization**

- Pydantic

---

## 🔌 API

### Upload Dataset

```http
POST /api/files/
```

Upload a `.zip` Shapefile or `.kml` dataset.

```bash
curl -X POST \
  http://127.0.0.1:8000/api/files/ \
  -F "file=@test_parcels.zip"
```

### Get File

```http
GET /api/files/{file_id}
```

Returns:

- File metadata
- Feature count
- Columns
- Geometry types
- CRS
- Extracted features
- Measurements

### Get Measurements

```http
GET /api/files/{file_id}/measurements/
```

Returns calculated measurements for the dataset.

### Interactive API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## 🗄️ Data Model

```text
uploaded_files
      │
      ├───────────────┐
      ▼               ▼
   features      measurements
      │               │
      └───────┬───────┘
              │
        PostgreSQL
```

The database stores:

- Uploaded file metadata
- CRS information
- Feature geometry
- Feature properties
- Geometry types
- Calculated measurements

---

## 🛡️ Error Handling

The API distinguishes between expected client errors and unexpected server failures.

| Situation | Response |
|---|---|
| Unsupported file type | `400 Bad Request` |
| Invalid ZIP | `400 Bad Request` |
| Missing Shapefile | `400 Bad Request` |
| Missing CRS | `400 Bad Request` |
| Processing failure | `500 Internal Server Error` |

Internal implementation details are not exposed to API clients for unexpected failures.

---

## 📁 Project Structure

```text
Geospatial File Measurement API/
│
├── app/
│   ├── api/
│   │   └── files.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── database.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── uploaded_file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   ├── repositories/
│   │   ├── file_repository.py
│   │   ├── feature_repository.py
│   │   └── measurement_repository.py
│   ├── schemas/
│   │   ├── file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   ├── services/
│   │   ├── file_service.py
│   │   ├── file_processor.py
│   │   └── measurement_service.py
│   ├── zip_utilis.py
│   └── main.py
│
├── uploads/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### Requirements

- Python 3.11+
- PostgreSQL
- pip

### Installation

```bash
git clone <your-repository-url>
cd "Geospatial File Measurement API"

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Database

Create the PostgreSQL database:

```sql
CREATE DATABASE geospatial_file_measurment;
```

Configure `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/geospatial_file_measurment
```

Initialize tables:

```bash
python -m app.db.init_db
```

### Run

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Validation Performed

The implementation has been manually verified against:

- ✅ ZIP containing Shapefile
- ✅ KML Polygon
- ✅ KML LineString
- ✅ Point geometry
- ✅ Missing CRS
- ✅ Invalid ZIP
- ✅ Missing values in KML properties
- ✅ Expected API errors
- ✅ Unexpected internal errors

Automated tests are being added under:

```text
tests/
```

---

## 🔮 Future Improvements

- Automated unit and integration tests
- Background processing for large datasets
- Object storage for uploaded files
- More advanced CRS selection
- Additional geometry support
- Asynchronous processing
- Agentic natural-language geospatial analysis

---

## 📌 Engineering Decisions

### Why PostgreSQL?

Provides persistent storage for file metadata, features, properties, and measurements.

### Why SQLAlchemy?

Separates database models from API schemas and keeps database access inside the repository layer.

### Why GeoPandas?

Provides robust geospatial file parsing, CRS handling, geometry transformation, and spatial operations.

### Why a layered architecture?

Keeps HTTP handling, business logic, geospatial processing, and database access separated and independently testable.

### Why CRS-aware measurement?

Calculating area or distance directly from geographic coordinates can produce incorrect units and results. The system therefore transforms geographic datasets into a suitable projected CRS before measurement.

---

## 🤖 Future: Agentic Geospatial Analysis

A planned extension is an **agentic geospatial analysis layer** that sits on top of the deterministic processing backend.

The agent would be able to answer natural-language questions such as:

```text
"Which features are longer than 10 km?"

"Does this dataset have any processing issues?"

"Give me an overview of this dataset."

"Are there any suspicious measurements?"
```

The LLM would orchestrate read-only analysis tools while the existing deterministic geospatial engine remains responsible for:

- CRS handling
- Geometry processing
- Area calculation
- Length calculation
- Dataset validation

This keeps measurement correctness deterministic while allowing natural-language interaction.

---

## 📄 License

This project was developed as part of a technical assignment.
