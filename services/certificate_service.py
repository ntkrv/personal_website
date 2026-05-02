from extensions import db
from models import Certificate

CERTIFICATE_FIELDS = ("title", "issuer", "skills", "link")


def _filter_fields(data: dict) -> dict:
    return {k: data.get(k) for k in CERTIFICATE_FIELDS if k in data}


def create_certificate(data: dict) -> Certificate:
    certificate = Certificate(**_filter_fields(data))
    db.session.add(certificate)
    db.session.commit()
    return certificate


def update_certificate(certificate: Certificate, data: dict) -> Certificate:
    for field, value in _filter_fields(data).items():
        setattr(certificate, field, value)
    db.session.commit()
    return certificate


def delete_certificate(certificate: Certificate) -> None:
    db.session.delete(certificate)
    db.session.commit()
