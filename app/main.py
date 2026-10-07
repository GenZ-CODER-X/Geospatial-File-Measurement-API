from fastapi import FastAPI,UploadFile,File,HTTPException,status
from pathlib import Path
from zip_utilis import inspect_zip,extract_zip,find_shapefile
import geopandas as gpd

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
        files_inside_zip = inspect_zip(file_path)
        extract_dir = UPLOAD_DIR / file_path.stem
        extract_dir.mkdir(exist_ok=True)
        extracted_files = extract_zip(file_path, extract_dir)
        shapefile = find_shapefile(extract_dir)
        gdf = gpd.read_file(shapefile)
        return {
    "filename": file.filename,
    "feature_count": len(gdf),
    "columns": list(gdf.columns),
    "geometry_types": gdf.geometry.geom_type.unique().tolist(),
    "crs": str(gdf.crs),
}

    
    
    return {
        "filename": file.filename,
        "message": "KML uploaded successfully"
    }
