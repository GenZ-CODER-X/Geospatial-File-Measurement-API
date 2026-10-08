
# Geospatial File Measurement API

> A CRS-aware FastAPI backend for uploading geospatial datasets, extracting features and metadata, and calculating accurate geometry measurements.
>
> ![Go and see the meme](youshouldnthaveit-v0-yggsq2cwq5kh1.webp)

> **This changed my POV on using AI to code.**

##  Overview

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
| Automated tests | ✅ |

---

## 🏗️ Architecture

The application follows a layered architecture that separates HTTP handling, business logic, geospatial processing, and database access.

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
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
        File Processing        Measurement Service
                │                     │
                └──────────┬──────────┘
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

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| API | HTTP requests, validation, response handling |
| Services | Business logic and orchestration |
| File Processor | ZIP/KML processing and feature extraction |
| Measurement Service | CRS-aware area and length calculation |
| Repositories | Database access |
| Models | SQLAlchemy database models |
| Schemas | Pydantic API response models |
| PostgreSQL | Persistent storage |

---

## 🔄 File Processing Flow

```text
Upload
  │
  ▼
Validate File Extension
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
       Missing          Available
          │                │
          ▼                ▼
        Reject       Calculate Metrics
                           │
                           ▼
                    Persist to DB
                           │
                           ▼
                       Response
```

The processing pipeline is deterministic. File parsing, CRS handling, geometry processing, and measurement calculations are performed by the backend without relying on an LLM.

---

## 📏 Measurement Calculation Flow

After features are extracted, the system calculates measurements based on their geometry type.

```text
GeoDataFrame
     │
     ▼
Check CRS
     │
     ├── Missing CRS ──► Reject
     │
     ▼
Check CRS Type
     │
     ├── Geographic CRS
     │        │
     │        ▼
     │   Estimate projected CRS
     │        │
     │        ▼
     │   Transform geometry
     │
     └── Projected CRS
              │
              ▼
       Inspect Geometry
              │
       ┌──────┼──────────────┐
       │      │              │
     Point  LineString     Polygon
       │      │              │
       ▼      ▼              ▼
      None  length()        area()
              │              │
              └──────┬───────┘
                     ▼
             Store Measurement
                     │
                     ▼
                PostgreSQL
```

### Measurement Rules

| Geometry Type | Measurement |
|---|---|
| `Polygon` | Area in `m²` |
| `MultiPolygon` | Area in `m²` |
| `LineString` | Length in `m` |
| `MultiLineString` | Length in `m` |
| `Point` | No measurement |
| `MultiPoint` | No measurement |

---

## 📐 CRS-Aware Measurements

A major design requirement of this project is avoiding incorrect measurements caused by calculating distances or areas directly from geographic coordinates.

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

If a dataset uses a geographic CRS such as `EPSG:4326`, the application estimates a suitable projected CRS and transforms the geometry before calculating measurements.

If CRS information is missing, the system **rejects measurement processing** rather than returning potentially incorrect measurements.

This prevents treating latitude/longitude coordinates as planar meter-based coordinates.

---

## 🧩 Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn

### Geospatial

- GeoPandas
- Shapely

### Database

- PostgreSQL
- SQLAlchemy

### Validation / Serialization

- Pydantic

### Testing

- Pytest
- HTTPX

---

## 🔌 API

### 1. Upload Dataset

```http
POST /api/files/
```

Uploads a `.zip` Shapefile or `.kml` dataset, processes the dataset, stores the extracted information in PostgreSQL, and returns the processed result.

### Example

```bash
curl -X POST \
  http://127.0.0.1:8000/api/files/ \
  -F "file=@test_parcels.zip"
```

### Example Response

```json
{
  "id": "04ac1746-59e9-4405-945b-0adaebd5c0ea",
  "filename": "test_parcels.zip",
  "feature_count": 3,
  "columns": [
    "id",
    "name",
    "geometry"
  ],
  "geometry_types": [
    "Polygon"
  ],
  "crs": "EPSG:4326",
  "features": [
    {
      "id": 0,
      "geometry_type": "Polygon",
      "geometry": {
        "type": "Polygon"
      },
      "properties": {
        "name": "Parcel 1"
      }
    }
  ],
  "measurements": [
    {
      "id": 1,
      "geometry_type": "Polygon",
      "area_m2": 1233312.2333198993,
      "length_m": null
    }
  ]
}
```

The actual response contains the complete extracted feature geometry and properties.

### 2. Get File

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

### Example

```bash
curl \
  http://127.0.0.1:8000/api/files/04ac1746-59e9-4405-945b-0adaebd5c0ea
```

### Example Response Structure

```json
{
  "id": "04ac1746-59e9-4405-945b-0adaebd5c0ea",
  "filename": "test_parcels.zip",
  "feature_count": 3,
  "columns": [
    "id",
    "name",
    "geometry"
  ],
  "geometry_types": [
    "Polygon"
  ],
  "crs": "EPSG:4326",
  "features": [],
  "measurements": []
}
```

The `features` and `measurements` arrays contain the complete persisted records for the requested file.

### 3. Get Measurements

```http
GET /api/files/{file_id}/measurements/
```

Returns the calculated measurements for all supported geometries in the dataset.

### Example

```bash
curl \
  http://127.0.0.1:8000/api/files/04ac1746-59e9-4405-945b-0adaebd5c0ea/measurements/
```

### Example Response

```json
{
  "file_id": "04ac1746-59e9-4405-945b-0adaebd5c0ea",
  "measurements": [
    {
      "id": 1,
      "geometry_type": "Polygon",
      "area_m2": 1233312.2333198993,
      "length_m": null
    },
    {
      "id": 2,
      "geometry_type": "Polygon",
      "area_m2": 4933023.086767652,
      "length_m": null
    }
  ]
}
```

### Interactive API Documentation

FastAPI automatically provides Swagger/OpenAPI documentation.

```text
http://127.0.0.1:8000/docs
```

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## 🗄️ Data Model

```text
                    uploaded_files
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
         features                measurements
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
                     PostgreSQL
```

The database stores:

### `uploaded_files`

- File ID
- Filename
- Feature count
- Column names
- Geometry types
- CRS
- Creation timestamp

### `features`

- Feature ID
- File ID
- Feature index
- Geometry type
- Geometry
- Properties / attributes

### `measurements`

- Measurement ID
- File ID
- Feature ID
- Geometry type
- Area in square meters
- Length in meters

---

## 🛡️ Error Handling

The API distinguishes between expected client errors and unexpected server failures.

| Situation | Response |
|---|---|
| Unsupported file type | `400 Bad Request` |
| Invalid ZIP | `400 Bad Request` |
| Missing Shapefile | `400 Bad Request` |
| Missing CRS | `400 Bad Request` |
| File processing failure | `500 Internal Server Error` |
| File not found | `404 Not Found` |

For unexpected server errors, implementation details are not exposed to API clients.

Example:

```json
{
  "detail": "An unexpected error occurred while processing the file."
}
```

---

## 📁 Project Structure

```text
Geospatial-File-Measurement-API/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── files.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── uploaded_file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── file_repository.py
│   │   ├── feature_repository.py
│   │   └── measurement_repository.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py
│   │   ├── file_processor.py
│   │   └── measurement_service.py
│   │
│   ├── zip_utilis.py
│   └── main.py
│
├── tests/
│   ├── test_api.py
│   ├── test_file_processor.py
│   └── test_measurement_service.py
│
├── uploads/
├── .env.example
├── pytest.ini
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
git clone https://github.com/GenZ-CODER-X/Geospatial-File-Measurement-API.git

cd Geospatial-File-Measurement-API

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 🗃️ Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE geospatial_file_measurment;
```

Configure `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/geospatial_file_measurment
```

Initialize the database tables:

```bash
python -m app.db.init_db
```

---

## ▶️ Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Testing

The project includes automated unit and API tests.

### Measurement Service Tests

- Polygon area calculation
- LineString length calculation
- Point geometry handling
- Missing CRS handling

### File Processor Tests

- KML processing
- Feature extraction
- Invalid ZIP handling
- Unsupported file formats

### API Tests

- Root endpoint
- Invalid file type
- KML upload
- File retrieval
- Measurement retrieval

Run the complete test suite:

```bash
pytest -v
```

Current test suite:

```text
13 passed
```

The tests use the project's PostgreSQL database rather than replacing it with SQLite, keeping the test environment close to the actual application architecture.

---

## 🔬 Validation Performed

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

Automated tests additionally verify:

- ✅ Measurement calculations
- ✅ CRS validation
- ✅ File processing
- ✅ Feature extraction
- ✅ API upload
- ✅ API retrieval
- ✅ API measurement responses
- ✅ Error responses

---

## 📚 Learning

This project provided practical experience in backend, database, testing, and geospatial engineering.

### Backend Engineering

- Designing REST APIs with FastAPI
- FastAPI dependency injection
- Handling file uploads
- API error handling
- OpenAPI/Swagger documentation
- Separating API, service, repository, model, and schema layers

### Database Engineering

- PostgreSQL database design
- SQLAlchemy ORM
- Foreign-key relationships
- Repository-based database access
- Separating database models from API schemas

### Geospatial Engineering

- Shapefile and KML processing
- GeoPandas
- Shapely geometries
- CRS handling
- Geographic vs projected coordinate systems
- Area and length calculations
- Geometry-type-specific processing

### Testing

- Unit testing with Pytest
- API testing
- Testing expected error conditions
- Testing against PostgreSQL

A key learning from this project was that geospatial measurements cannot be treated like ordinary numeric calculations. The coordinate reference system directly affects the meaning and units of the result, making CRS handling an important part of the backend's business logic.

---
## Design Decisions

This project was designed to keep the geospatial processing deterministic while maintaining a clean backend architecture that can be extended later.

### 1. GeoPandas for Geospatial Processing

GeoPandas was chosen as the primary geospatial processing library because it provides a high-level interface for working with geospatial datasets while integrating closely with Pandas and Shapely.

We use GeoPandas for:

- Reading Shapefiles
- Reading KML files
- Representing datasets as `GeoDataFrame` objects
- Detecting and inspecting CRS information
- Transforming geometries between CRS systems
- Accessing geometry types
- Extracting feature attributes
- Performing geometry operations
- Calculating area and length

This allowed the application to focus on backend architecture and business logic instead of implementing low-level geospatial file parsing and coordinate transformation ourselves.

The central processing flow is:

```text
Geospatial File
      │
      ▼
   GeoPandas
      │
      ▼
 GeoDataFrame
      │
 ┌────┴──────────────┐
 ▼                   ▼
Attributes         Geometry
 │                   │
 ▼                   ▼
Pandas             Shapely
Data Handling      Operations
```

GeoPandas therefore acts as the main bridge between the uploaded geospatial file and the application's deterministic processing pipeline.

---

### 2. Pandas for Attribute Processing and Data Normalization

Pandas is used alongside GeoPandas because a `GeoDataFrame` is built on top of Pandas' tabular data model.

In this project, Pandas is particularly useful when extracting feature properties from each row of the `GeoDataFrame`.

For example, during feature extraction:

```python
properties = row.drop("geometry").to_dict()
```

The resulting properties can contain values originating from different geospatial file formats and attribute schemas.

A particularly important issue we encountered was that missing values from KML datasets could appear as Pandas values such as:

```text
NaN
NaT
```

These values are not directly JSON serializable and caused PostgreSQL JSON persistence to fail.

We therefore use Pandas to normalize missing values before storing feature properties:

```python
properties = {
    key: None if pd.isna(value) else value
    for key, value in properties.items()
}
```

This gives us:

```text
NaN / NaT
    │
    ▼
Pandas missing-value detection
    │
    ▼
None
    │
    ▼
JSON null
    │
    ▼
PostgreSQL JSON
```

### What leverage did we get from Pandas?

Using Pandas gave the project several practical advantages:

- Easy conversion of tabular feature attributes into dictionaries
- Consistent handling of missing values
- Compatibility with arbitrary dataset schemas
- Convenient row-wise feature extraction
- Seamless integration with GeoPandas
- Safe normalization of values before JSON serialization

This was especially useful because the API should not assume a fixed set of attributes. One dataset may contain `name` and `population`, while another may contain `parcel_id`, `owner`, or completely different fields.

Therefore, Pandas helps us preserve the original dataset attributes without requiring a predefined database schema for every possible property.

---

### 3. UUID for Uploaded File IDs

Uploaded files use UUIDs as their primary identifiers instead of sequential integer IDs.

```text
Uploaded File
      │
      ▼
UUID
04ac1746-59e9-4405-945b-0adaebd5c0ea
```

The UUID is generated when the upload request is received and is then used across the `uploaded_files`, `features`, and `measurements` tables.

#### Why UUID?

A file identifier is exposed through the API, so UUIDs provide several advantages:

- Avoid exposing predictable sequential IDs
- Lower risk of ID enumeration
- Globally unique identifiers
- Suitable for distributed systems if the application is expanded later
- No dependency on a database sequence for generating the public file identifier

For this project, the UUID is primarily used for **dataset-level identification**, while feature and measurement records use integer primary keys because they are internal database entities.

---

### 4. Separate Database Models from API Schemas

SQLAlchemy models and Pydantic schemas are kept separate.

```text
SQLAlchemy Models
       │
       ▼
   PostgreSQL

Pydantic Schemas
       │
       ▼
    API Response
```

For example:

- `UploadedFile` is a SQLAlchemy model.
- `FileResponse` is a Pydantic response schema.
- `Feature` and `FeatureResponse` are also separated.
- `Measurement` and `MeasurementResponse` are separated.

This prevents database representation from becoming tightly coupled to the public API contract.

It also makes it possible to change the database implementation without unnecessarily changing the API response structure.

---

### 5. Layered Architecture

The application uses separate API, service, repository, model, and schema layers.

```text
API
 │
 ▼
Service
 │
 ├── File Processing
 └── Measurement Calculation
 │
 ▼
Repository
 │
 ▼
PostgreSQL
```

The API layer handles HTTP concerns.

The service layer contains application and business logic.

The repository layer is responsible for database operations.

This means that changing how measurements are calculated does not require putting geospatial logic inside the FastAPI route.

It also makes the individual components easier to test.

---

### 6. Repository Layer for Database Access

All database operations are kept inside repository modules instead of directly querying SQLAlchemy models from API routes.

```text
file_repository.py
feature_repository.py
measurement_repository.py
```

The API does not directly perform database queries.

Instead:

```text
API
 │
 ▼
Service
 │
 ▼
Repository
 │
 ▼
SQLAlchemy
 │
 ▼
PostgreSQL
```

Potential improvements include:

- Expanded integration and end-to-end test coverage
- Background processing for large datasets
- Asynchronous job processing
- Object storage for uploaded files
- More advanced CRS selection strategies
- Additional geometry types and operations
- Dataset processing status and job tracking
- Pagination for large feature and measurement responses
- Better validation for malformed geospatial datasets
- Spatial indexing and advanced spatial queries
- Agentic natural-language geospatial analysis

---

##  Future Scope: Agentic Geospatial Analysis

A planned extension is an **agentic geospatial analysis layer** that sits on top of the deterministic processing backend.

The agent would allow users to interact with processed datasets using natural language.

For example:

```text
"Give me an overview of this dataset."

"Which features are longer than 10 km?"

"Does this dataset have any processing issues?"

"Are there any suspicious measurements?"
```

The agent would orchestrate read-only analysis tools while the existing deterministic geospatial engine remains responsible for:

- CRS handling
- Geometry processing
- Area calculation
- Length calculation
- Dataset validation

The LLM would **not** be responsible for calculating measurements or choosing the CRS.

This separation keeps numerical and geospatial correctness deterministic while allowing natural-language analysis on top of the processed data.

A future implementation could introduce:

```text
User
 │
 ▼
Natural Language Query
 │
 ▼
Agent / Orchestrator
 │
 ├── Dataset Overview Tool
 ├── Measurement Query Tool
 ├── Processing Issue Tool
 └── Other Analysis Tools
 │
 ▼
Deterministic Backend
 │
 ▼
PostgreSQL
```

---

##  License

This project was developed as part of a technical assignment.
---

### (THINGS I PERSONALLY REFERRED THE MOST IS FOR THIS ASSIGNMENT

I referred to the official GeoPandas documentation while learning about GeoDataFrames, CRS handling, and coordinate transformations:

[GeoPandas — Projections and Coordinate Reference Systems](https://geopandas.org/en/stable/docs/user_guide/projections.html)
