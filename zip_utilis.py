from pathlib import Path
from zipfile import ZipFile

def inspect_zip(file_path:Path)-> list:
    with ZipFile(file_path,'r') as zip_files:
        files=zip_files.namelist()
    return files
