from pathlib import Path

import geopandas as gpd

from services.file_processor import process_file, extract_features
from services.measurement_service import calculate_measurements


def process_uploaded_file(file_path: Path):
    gdf: gpd.GeoDataFrame = process_file(file_path)

    features = extract_features(gdf)

    measurements = calculate_measurements(gdf)

    return {
        "feature_count": len(gdf),
        "columns": list(gdf.columns),
        "geometry_types": gdf.geometry.geom_type.unique().tolist(),
        "crs": str(gdf.crs),
        "features": features,
        "measurements": measurements,
    }