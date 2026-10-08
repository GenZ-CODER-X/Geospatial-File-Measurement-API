import geopandas as gpd
import pytest
from shapely.geometry import Polygon, LineString, Point

from app.services.measurement_service import calculate_measurements


def test_polygon_area():
    geometry = Polygon([
        (77.0, 13.0),
        (77.01, 13.0),
        (77.01, 13.01),
        (77.0, 13.01),
    ])

    gdf = gpd.GeoDataFrame(
        {"geometry": [geometry]},
        crs="EPSG:4326",
    )

    measurements = calculate_measurements(gdf)

    assert len(measurements) == 1
    assert measurements[0]["geometry_type"] == "Polygon"
    assert measurements[0]["area_m2"] is not None
    assert measurements[0]["area_m2"] > 0
    assert measurements[0]["length_m"] is None


def test_linestring_length():
    geometry = LineString([
        (77.0, 13.0),
        (77.01, 13.0),
    ])

    gdf = gpd.GeoDataFrame(
        {"geometry": [geometry]},
        crs="EPSG:4326",
    )

    measurements = calculate_measurements(gdf)

    assert len(measurements) == 1
    assert measurements[0]["geometry_type"] == "LineString"
    assert measurements[0]["length_m"] is not None
    assert measurements[0]["length_m"] > 0
    assert measurements[0]["area_m2"] is None


def test_point_has_no_measurement():
    geometry = Point(77.0, 13.0)

    gdf = gpd.GeoDataFrame(
        {"geometry": [geometry]},
        crs="EPSG:4326",
    )

    measurements = calculate_measurements(gdf)

    assert len(measurements) == 1
    assert measurements[0]["geometry_type"] == "Point"
    assert measurements[0]["area_m2"] is None
    assert measurements[0]["length_m"] is None


def test_missing_crs_raises_error():
    geometry = Polygon([
        (77.0, 13.0),
        (77.01, 13.0),
        (77.01, 13.01),
        (77.0, 13.01),
    ])

    gdf = gpd.GeoDataFrame(
        {"geometry": [geometry]},
        crs=None,
    )

    with pytest.raises(ValueError, match="no CRS"):
        calculate_measurements(gdf)