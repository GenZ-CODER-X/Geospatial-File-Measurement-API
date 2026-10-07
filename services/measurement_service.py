import geopandas as gpd


def calculate_measurements(gdf: gpd.GeoDataFrame) -> list[dict]:
    if gdf.crs is None:
        raise ValueError(
            "Dataset has no CRS. Cannot calculate measurements safely."
        )

    projected_gdf = gdf

    if gdf.crs.is_geographic:
        projected_crs = gdf.estimate_utm_crs()

        if projected_crs is None:
            raise ValueError(
                "Could not determine a suitable projected CRS."
            )

        projected_gdf = gdf.to_crs(projected_crs)

    measurements = []

    for index, row in projected_gdf.iterrows():
        geometry = row.geometry
        geometry_type = geometry.geom_type

        result = {
            "id": index,
            "geometry_type": geometry_type,
            "area_m2": None,
            "length_m": None,
        }

        if geometry_type in ["Polygon", "MultiPolygon"]:
            result["area_m2"] = geometry.area

        elif geometry_type in ["LineString", "MultiLineString"]:
            result["length_m"] = geometry.length

        measurements.append(result)

    return measurements