"""Case-study image uploads.

Files live outside the code checkout (instance/uploads/projects/ by
default, override with UPLOAD_DIR) so a deploy that replaces the
checkout doesn't wipe them, and are served by `main.uploaded_image`.

Images uploaded before this module existed sit in static/uploads/
projects/ with /static/... paths; they keep working, get cleaned up the
same way, and `flask migrate-uploads` moves them over.
"""
import os
import re
import secrets
import shutil

from flask import current_app

from extensions import db
from models import Project

UPLOAD_URL_PREFIX = "/uploads/projects/"
LEGACY_URL_PREFIX = "/static/uploads/projects/"

# Randomised names written by save_image(); anything else is never
# touched on disk.
_STORED_NAME_RE = re.compile(r"^[0-9a-f]{32}\.(?:jpg|jpeg|png|webp)$")


def upload_dir() -> str:
    return current_app.config.get("UPLOAD_DIR") or os.path.join(
        current_app.instance_path, "uploads", "projects"
    )


def legacy_upload_dir() -> str:
    return os.path.join(current_app.static_folder, "uploads", "projects")


def sniff_image_ext(file_storage) -> str | None:
    """Return the real extension from the file's magic bytes, or None
    if it isn't a JPEG / PNG / WebP. Leaves the stream at position 0."""
    stream = file_storage.stream
    head = stream.read(12)
    stream.seek(0)

    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None


def save_image(file_storage) -> str | None:
    """Store an uploaded image and return its public path, or None if
    nothing was uploaded or it isn't a supported image. The extension
    comes from the content, not from the client-supplied filename."""
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    ext = sniff_image_ext(file_storage)
    if ext is None:
        return None

    dest_dir = upload_dir()
    os.makedirs(dest_dir, exist_ok=True)

    name = secrets.token_hex(16) + ext
    file_storage.save(os.path.join(dest_dir, name))
    return UPLOAD_URL_PREFIX + name


def _disk_path(public_path: str | None) -> str | None:
    if not public_path:
        return None
    for prefix, directory in (
        (UPLOAD_URL_PREFIX, upload_dir),
        (LEGACY_URL_PREFIX, legacy_upload_dir),
    ):
        if public_path.startswith(prefix):
            name = public_path[len(prefix):]
            if _STORED_NAME_RE.match(name):
                return os.path.join(directory(), name)
    return None


def delete_image_if_orphaned(public_path: str | None) -> None:
    """Remove an uploaded file once no project references it. External
    URLs and anything that isn't one of our stored files are ignored.
    Call after the DB change that dropped the reference is committed."""
    disk_path = _disk_path(public_path)
    if disk_path is None:
        return
    if db.session.query(Project.id).filter_by(image_path=public_path).first():
        return
    try:
        os.remove(disk_path)
    except FileNotFoundError:
        pass
    except OSError:
        current_app.logger.exception("Couldn't delete orphaned upload %s", disk_path)


def migrate_legacy_uploads() -> tuple[int, list[str]]:
    """Move images referenced by /static/uploads/... paths into
    upload_dir() and repoint the projects. Returns (moved, missing)."""
    dest_dir = upload_dir()
    os.makedirs(dest_dir, exist_ok=True)

    moved, missing = 0, []
    for project in Project.query.filter(
        Project.image_path.startswith(LEGACY_URL_PREFIX)
    ).all():
        source = _disk_path(project.image_path)
        if source is None or not os.path.exists(source):
            missing.append(project.image_path)
            continue
        name = os.path.basename(source)
        shutil.move(source, os.path.join(dest_dir, name))
        # Commit per file so an interrupted run never leaves a project
        # pointing at a file that has already moved.
        project.image_path = UPLOAD_URL_PREFIX + name
        db.session.commit()
        moved += 1

    return moved, missing
