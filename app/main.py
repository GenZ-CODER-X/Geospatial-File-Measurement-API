from fastapi import FastAPI,UploadFile,File,HTTPException,status
from pathlib import Path
from app.zip_utilis import inspect_zip,extract_zip,find_shapefile
import geopandas as gpd
from app.measurement import calculate_measurements
import uuid
from app.schemas import FileRecord

files_db={}

UPLOAD_DIR=Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app=FastAPI(title="Geospatial File Measurement API")

@app.get("/")
def root():
    return {"message": "Geospatial File Measurement API is running"}


@app.post("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith((".zip",".kml")): #As we only need kml or zip file contaning (.shp,shx,dbf etc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only .zip and .kml files are supported") 
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)
    if file.filename.endswith(".zip"):
        inspect_zip(file_path)
        extract_dir = UPLOAD_DIR / file_path.stem
        extract_dir.mkdir(exist_ok=True)
        extract_zip(file_path, extract_dir)

        shapefile = find_shapefile(extract_dir)

        gdf = gpd.read_file(shapefile)

        measurements = calculate_measurements(gdf)

        file_id = str(uuid.uuid4())

        features = []
        for index, row in gdf.iterrows():
            properties = row.drop("geometry").to_dict()

            features.append({
                "id": index,
                "geometry_type": row.geometry.geom_type,
                "geometry": row.geometry.__geo_interface__,
                "properties": properties,
    })
        return {
    "filename": file.filename,
    "feature_count": len(gdf),
    "columns": list(gdf.columns),
    "geometry_types": gdf.geometry.geom_type.unique().tolist(),
    "crs": str(gdf.crs),
    "features": features,
    "measurements":measurements
}   
    return {
        "filename": file.filename,
        "message": "KML uploaded successfully"
    }


@app.get("/api/files/{file_id}")
def get_file(file_id: str):

    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return files_db[file_id]

@app.get("/api/files/{file_id}/measurements/")
def get_measurements(file_id: str):

    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return {
        "file_id": file_id,
        "measurements": files_db[file_id]["measurements"]
    }