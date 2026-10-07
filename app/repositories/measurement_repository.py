from sqlalchemy.orm import Session

from app.models.measurement import Measurement


def create_measurement(
    db: Session,
    measurement: Measurement,
) -> Measurement:
    db.add(measurement)
    db.flush()

    return measurement


def create_measurements(
    db: Session,
    measurements: list[Measurement],
) -> list[Measurement]:
    db.add_all(measurements)
    db.flush()

    for measurement in measurements:
        db.refresh(measurement)

    return measurements


def get_measurements_by_file_id(
    db: Session,
    file_id,
) -> list[Measurement]:
    return (
        db.query(Measurement)
        .filter(Measurement.file_id == file_id)
        .all()
    )