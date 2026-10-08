Perfect. Let's make the README now.

Replace the contents of `README.md` with this:

```markdown
# Geospatial File Measurement API

A FastAPI backend for uploading geospatial datasets, extracting their features and metadata, and calculating geometry measurements with CRS-aware processing.

## Features

- Upload `.zip` files containing Shapefiles
- Upload `.kml` files
- Extract feature geometry and properties
- Detect geometry types
- Detect and preserve CRS information
- Calculate polygon area in square meters
- Calculate LineString length in meters
- Skip measurements for Point geometries
- Prevent measurement when CRS information is missing
- Store processed data in PostgreSQL
- REST API with Swagger/OpenAPI documentation
- Structured service and repository layers
- Graceful handling of invalid files and processing errors

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- GeoPandas
- Shapely
- Pydantic
- Uvicorn

## Architecture

The application follows a layered architecture:

```text
Client
  |
  v
FastAPI API Layer
  |
  v
Service Layer
  |
  +---- File Processing
  |
  +---- Measurement Service
  |
  v
Repository Layer
  |
  v
PostgreSQL
```

### Layers

#### API Layer

Responsible for:

- HTTP requests and responses
- File uploads
- Request validation
- HTTP error handling

#### Service Layer

Responsible for:

- File processing orchestration
- Feature extraction
- Measurement calculation
- Database transaction management

#### Repository Layer

Responsible for:

- Database queries
- Creating file records
- Creating feature records
- Creating measurement records
- Retrieving stored data

#### Database Layer

PostgreSQL stores:

- Uploaded file metadata
- Extracted features
- Feature properties
- Measurements

## Project Structure

```text
Geospatial File Measurement API/
│
├── app/
│   ├── api/
│   │   └── files.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── uploaded_file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   │
│   ├── repositories/
│   │   ├── file_repository.py
│   │   ├── feature_repository.py
│   │   └── measurement_repository.py
│   │
│   ├── schemas/
│   │   ├── file.py
│   │   ├── feature.py
│   │   └── measurement.py
│   │
│   ├── services/
│   │   ├── file_service.py
│   │   ├── file_processor.py
│   │   └── measurement_service.py
│   │
│   ├── zip_utilis.py
│   └── main.py
│
├── uploads/
├── tests/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- PostgreSQL
- pip

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd "Geospatial File Measurement API"
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE geospatial_file_measurment;
```

Configure the database connection in `.env`.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/geospatial_file_measurment
```

Initialize the database tables:

```bash
python -m app.db.init_db
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### 1. Upload File

```http
POST /api/files/
```

Accepts:

- `.zip` containing a Shapefile
- `.kml`

Example:

```bash
curl -X POST \
  http://127.0.0.1:8000/api/files/ \
  -H "accept: application/json" \
  -F "file=@test_parcels.zip"
```

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

Example:

```bash
curl http://127.0.0.1:8000/api/files/{file_id}
```

### 3. Get Measurements

```http
GET /api/files/{file_id}/measurements/
```

Returns the calculated measurements for the uploaded dataset.

Example:

```bash
curl http://127.0.0.1:8000/api/files/{file_id}/measurements/
```

## Geometry Handling

The API supports geometry-specific measurements.

| Geometry Type | Measurement |
|---|---|
| Point | No measurement |
| MultiPoint | No measurement |
| LineString | Length |
| MultiLineString | Length |
| Polygon | Area |
| MultiPolygon | Area |

### Polygon

Polygon and MultiPolygon geometries are measured using:

```python
geometry.area
```

The resulting value is stored in:

```text
area_m2
```

### LineString

LineString and MultiLineString geometries are measured using:

```python
geometry.length
```

The resulting value is stored in:

```text
length_m
```

### Point

Point geometries do not have an area or length measurement.

Both values remain:

```json
{
  "area_m2": null,
  "length_m": null
}
```

## CRS Handling

Measurements must not be calculated directly using geographic coordinates such as latitude and longitude.

For example:

```text
EPSG:4326
```

uses degrees rather than meters.

When the input dataset uses a geographic CRS, the application estimates a suitable projected CRS and transforms the geometry before calculating area or length.

```text
Input Dataset
     |
     v
Check CRS
     |
     +---- Missing CRS
     |       |
     |       v
     |    Reject
     |
     +---- Geographic CRS
     |       |
     |       v
     |   Estimate projected CRS
     |       |
     |       v
     |   Transform geometry
     |
     v
Calculate measurement
```

### Missing CRS

If a dataset does not contain CRS information, measurement processing is rejected:

```text
Dataset has no CRS.
Cannot calculate measurements safely.
```

This prevents potentially incorrect measurements.

## File Processing Flow

```text
Upload File
    |
    v
Validate Extension
    |
    +---- ZIP
    |      |
    |      v
    |   Extract ZIP
    |      |
    |      v
    |   Find Shapefile
    |
    +---- KML
           |
           v
      Read KML
           |
           v
      GeoDataFrame
           |
           v
      Extract Features
           |
           v
      Calculate Measurements
           |
           v
      Store in PostgreSQL
           |
           v
      Return API Response
```

## Error Handling

The API distinguishes between expected input errors and unexpected internal errors.

### Invalid File

Unsupported extensions return:

```text
400 Bad Request
```

Example:

```json
{
  "detail": "Only .zip and .kml files are supported"
}
```

### Invalid ZIP

If a ZIP does not contain a Shapefile:

```text
400 Bad Request
```

Example:

```json
{
  "detail": "No Shapefile (.shp) found in ZIP"
}
```

### Missing CRS

Datasets without CRS information are rejected:

```text
400 Bad Request
```

### Unexpected Errors

Unexpected internal failures return:

```text
500 Internal Server Error
```

without exposing internal implementation details to the API client.

## Example Response

```json
{
  "id": "04ac1746-59e9-4405-945b-0adaebd5c0ea",
  "filename": "test_parcels.zip",
  "feature_count": 3,
  "columns": [
    "name",
    "category",
    "geometry"
  ],
  "geometry_types": [
    "Polygon"
  ],
  "crs": "EPSG:4326",
  "features": [],
  "measurements": [
    {
      "id": 7,
      "geometry_type": "Polygon",
      "area_m2": 1233312.23,
      "length_m": null
    }
  ]
}
```

## Design Decisions

### PostgreSQL

PostgreSQL is used for persistent storage of file metadata, features, properties, and measurements.

### SQLAlchemy

SQLAlchemy provides the database ORM and separates database models from API schemas.

### GeoPandas

GeoPandas is used for reading and processing geospatial datasets.

### Layered Architecture

The application separates API, service, repository, database model, and schema responsibilities to keep the code maintainable and testable.

### CRS-Aware Measurement

Measurements are calculated only after ensuring that the geometry is in an appropriate projected coordinate system.

### Transaction Safety

File, feature, and measurement records are persisted within a database transaction. Processing failures trigger a rollback.

## Testing

The application has been manually verified with:

- ZIP containing Shapefile
- KML Polygon
- KML LineString
- Point geometry
- Missing CRS
- Invalid ZIP
- Missing values in KML properties
- Expected API errors
- Unexpected internal error handling

Automated tests can be added under:

```text
tests/
```

## Future Improvements

Potential future improvements include:

- Automated unit and integration tests
- Background processing for large datasets
- Object storage for uploaded files
- More advanced CRS selection
- Additional geometry types
- Asynchronous processing
- Agentic natural-language geospatial analysis

## License

This project is developed as part of a technical assignment.
```

### Then save and commit

```bash
git add README.md
git commit -m "docs: add project README"
git push origin main
```

