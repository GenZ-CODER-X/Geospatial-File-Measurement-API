from fastapi import FastAPI,UploadFile,File,HTTPException,status
from pathlib import Path

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

    return {
        "filename": file.filename,
        "message": "File uploaded successfully"
    }
