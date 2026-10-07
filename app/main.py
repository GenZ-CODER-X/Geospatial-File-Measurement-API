from fastapi import FastAPI,UploadFile,File,HTTPException,status
from pathlib import Path
from zip_utilis import inspect_zip

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
        return {
            "filename": file.filename,
            "files_inside_zip": files_inside_zip
        }

    return {
        "filename": file.filename,
        "message": "KML uploaded successfully"
    }
