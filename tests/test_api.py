from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Geospatial File Measurement API is running"


def test_upload_invalid_file_type():
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.txt",
                BytesIO(b"this is not a geospatial file"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only .zip and .kml files are supported"
    )

def test_upload_kml():
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Polygon</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            77.0,13.0,0
                            77.01,13.0,0
                            77.01,13.01,0
                            77.0,13.01,0
                            77.0,13.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>
"""

    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test_api.kml",
                kml_content.encode(),
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["filename"] == "test_api.kml"
    assert data["feature_count"] == 1
    assert "Polygon" in data["geometry_types"]
    assert data["crs"] is not None
    assert len(data["features"]) == 1
    assert len(data["measurements"]) == 1

    measurement = data["measurements"][0]

    assert measurement["geometry_type"] == "Polygon"
    assert measurement["area_m2"] is not None
    assert measurement["area_m2"] > 0

def test_get_file():
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Polygon</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            77.0,13.0,0
                            77.01,13.0,0
                            77.01,13.01,0
                            77.0,13.01,0
                            77.0,13.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>
"""

    upload_response = client.post(
        "/api/files/",
        files={
            "file": (
                "test_get.kml",
                kml_content.encode(),
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert upload_response.status_code == 200

    file_id = upload_response.json()["id"]

    response = client.get(f"/api/files/{file_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == file_id
    assert data["filename"] == "test_get.kml"
    assert data["feature_count"] == 1
    assert len(data["features"]) == 1
    assert len(data["measurements"]) == 1


def test_get_measurements():
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Polygon</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
                            77.0,13.0,0
                            77.01,13.0,0
                            77.01,13.01,0
                            77.0,13.01,0
                            77.0,13.0,0
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>
    </Document>
</kml>
"""

    upload_response = client.post(
        "/api/files/",
        files={
            "file": (
                "test_measurements.kml",
                kml_content.encode(),
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert upload_response.status_code == 200

    file_id = upload_response.json()["id"]

    response = client.get(
        f"/api/files/{file_id}/measurements/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["file_id"] == file_id
    assert len(data["measurements"]) == 1

    measurement = data["measurements"][0]

    assert measurement["geometry_type"] == "Polygon"
    assert measurement["area_m2"] is not None
    assert measurement["area_m2"] > 0