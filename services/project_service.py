from extensions import db
from models import Project

PROJECT_FIELDS = (
    "title",
    "short_description",
    "long_description",
    "image_path",
    "stack",
    "link_type",
    "git_link",
)


def _filter_fields(data: dict) -> dict:
    return {k: data.get(k) for k in PROJECT_FIELDS if k in data}


def create_project(data: dict) -> Project:
    project = Project(**_filter_fields(data))
    db.session.add(project)
    db.session.commit()
    return project


def update_project(project: Project, data: dict) -> Project:
    for field, value in _filter_fields(data).items():
        setattr(project, field, value)
    db.session.commit()
    return project


def delete_project(project: Project) -> None:
    db.session.delete(project)
    db.session.commit()
