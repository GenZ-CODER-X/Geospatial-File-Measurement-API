from pathlib import Path

from sqlalchemy.orm import Session

from app.models.uploaded_file import UploadedFile
from app.models.feature import Feature
from app.models.measurement import Measurement

from app.repositories.file_repository import create_file, get_file_by_id
from app.repositories.feature_repository import create_features, get_features_by_file_id
from app.repositories.measurement_repository import create_measurements, get_measurements_by_file_id

from app.services.file_processor import process_file, extract_features
from app.services.measurement_service import calculate_measurements


def build_file_response(uploaded_file, features, measurements):
    return {
        "id": str(uploaded_file.id),
        "filename": uploaded_file.filename,
        "feature_count": uploaded_file.feature_count,
        "columns": uploaded_file.columns,
        "geometry_types": uploaded_file.geometry_types,
        "crs": uploaded_file.crs,
        "features": features,
        "measurements": measurements,
    }


def process_uploaded_file(
    db: Session,
    file_id,
    file_path: Path,
    filename: str,
):
    try:
        # 1. Process the uploaded file
        gdf = process_file(file_path)

        # 2. Extract features
        feature_data = extract_features(gdf)

        # 3. Calculate measurements
        measurement_data = calculate_measurements(gdf)

        # 4. Create uploaded file
        uploaded_file = UploadedFile(
            id=file_id,
            filename=filename,
            feature_count=len(gdf),
            columns=list(gdf.columns),
            geometry_types=gdf.geometry.geom_type.unique().tolist(),
            crs=str(gdf.crs),
        )

        create_file(db, uploaded_file)

        # 5. Create feature records
        feature_models = [
            Feature(
                file_id=file_id,
                feature_index=feature["id"],
                geometry_type=feature["geometry_type"],
                geometry=feature["geometry"],
                properties=feature["properties"],
            )
            for feature in feature_data
        ]

        create_features(db, feature_models)

        # 6. Create measurement records
        measurement_models = [
            Measurement(
                file_id=file_id,
                feature_id=feature_model.id,
                geometry_type=measurement["geometry_type"],
                area_m2=measurement["area_m2"],
                length_m=measurement["length_m"],
            )
            for feature_model, measurement in zip(
                feature_models,
                measurement_data,
            )
        ]

        create_measurements(db, measurement_models)

        # 7. Commit everything
        db.commit()

        # 8. Fetch created records for response
        features = get_features_by_file_id(db, file_id)
        measurements = get_measurements_by_file_id(db, file_id)

        return build_file_response(
                uploaded_file,
                features,
                measurements,
            )

    except Exception:
        db.rollback()
        raise

def get_file_details(
    db: Session,
    file_id,
):
    uploaded_file = get_file_by_id(db, file_id)

    if uploaded_file is None:
        raise ValueError("File not found")

    features = get_features_by_file_id(db, file_id)
    measurements = get_measurements_by_file_id(db, file_id)

    return build_file_response(
    uploaded_file,
    features,
    measurements,
)