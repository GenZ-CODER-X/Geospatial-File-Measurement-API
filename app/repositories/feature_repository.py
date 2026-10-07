from sqlalchemy.orm import Session

from app.models.feature import Feature


def create_feature(
    db: Session,
    feature: Feature,
) -> Feature:
    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature


def create_features(
    db: Session,
    features: list[Feature],
) -> list[Feature]:
    db.add_all(features)
    db.flush()

    for feature in features:
        db.refresh(feature)

    return features


def get_features_by_file_id(
    db: Session,
    file_id,
) -> list[Feature]:
    return (
        db.query(Feature)
        .filter(Feature.file_id == file_id)
        .all()
    )

"""
Why flush()?
db.add_all()
      ↓
db.flush()
      ↓
PostgreSQL generates Feature IDs
      ↓
we can use those IDs
      ↓
create Measurements
      ↓
final db.commit()
"""