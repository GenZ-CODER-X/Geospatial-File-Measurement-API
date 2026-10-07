from pathlib import Path
from zipfile import ZipFile

def inspect_zip(file_path:Path)-> list:
    with ZipFile(file_path,'r') as zip_files:
        files=zip_files.namelist()
    return files

def extract_zip(file_path: Path, extract_to: Path):
    with ZipFile(file_path, "r") as zip_file:
        zip_file.extractall(extract_to)

    return list(extract_to.iterdir())

def find_shapefile(extract_dir: Path):
    shapefiles = list(extract_dir.rglob("*.shp"))

    if not shapefiles:
        raise ValueError("No Shapefile (.shp) found in ZIP")

    if len(shapefiles) > 1:
        raise ValueError("Multiple Shapefiles found in ZIP")

    return shapefiles[0]