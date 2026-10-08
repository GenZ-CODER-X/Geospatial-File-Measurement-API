from pathlib import Path

import geopandas as gpd

from app.zip_utilis import extract_zip, find_shapefile

import pandas as pd


def process_zip(file_path: Path) -> gpd.GeoDataFrame:
    extract_dir = file_path.parent / file_path.stem
    extract_dir.mkdir(exist_ok=True)

    extract_zip(file_path, extract_dir)

    shapefile = find_shapefile(extract_dir)

    return gpd.read_file(shapefile)


def process_kml(file_path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(file_path, driver="KML")


def process_file(file_path: Path) -> gpd.GeoDataFrame:
    suffix = file_path.suffix.lower()

    if suffix == ".zip":
        return process_zip(file_path)

    if suffix == ".kml":
        return process_kml(file_path)

    raise ValueError(f"Unsupported file format: {suffix}")


def extract_features(gdf: gpd.GeoDataFrame) -> list[dict]:
    features = []

    for index, row in gdf.iterrows():
        properties = row.drop("geometry").to_dict()

        properties = {
    key: None if pd.isna(value) else value
    for key, value in properties.items()
}

        features.append(
            {
                "id": index,
                "geometry_type": row.geometry.geom_type,
                "geometry": row.geometry.__geo_interface__,
                "properties": properties,
            }
        )

    return features