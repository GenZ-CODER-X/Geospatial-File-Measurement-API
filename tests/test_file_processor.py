from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import pytest
from shapely.geometry import Point

from app.services.file_processor import (
    process_file,
    process_kml,
    extract_features,
)


def test_process_kml(tmp_path):
    kml_path = tmp_path / "test.kml"

    gdf = gpd.GeoDataFrame(
        {
            "name": ["Test Point"],
            "geometry": [Point(77.0, 13.0)],
        },
        crs="EPSG:4326",
    )

    gdf.to_file(kml_path, driver="KML")

    result = process_kml(kml_path)

    assert len(result) == 1
    assert result.crs is not None
    assert result.geometry.iloc[0].geom_type == "Point"


def test_extract_features():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Test"],
            "category": ["A"],
            "geometry": [Point(77.0, 13.0)],
        },
        crs="EPSG:4326",
    )

    features = extract_features(gdf)

    assert len(features) == 1
    assert features[0]["geometry_type"] == "Point"
    assert features[0]["properties"]["name"] == "Test"
    assert features[0]["properties"]["category"] == "A"
    assert features[0]["geometry"]["type"] == "Point"


def test_invalid_zip_raises_error(tmp_path):
    zip_path = tmp_path / "invalid.zip"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr("readme.txt", "not a shapefile")

    with pytest.raises(ValueError, match="No Shapefile"):
        process_file(zip_path)


def test_unsupported_file_format(tmp_path):
    txt_path = tmp_path / "test.txt"
    txt_path.write_text("unsupported")

    with pytest.raises(ValueError, match="Unsupported file format"):
        process_file(txt_path)