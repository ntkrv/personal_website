from flask import Blueprint, render_template, jsonify, request, current_app

errors_bp = Blueprint("errors", __name__)


def _wants_json() -> bool:
    return request.accept_mimetypes.best == "application/json" or request.path.startswith(
        "/api/"
    )


@errors_bp.app_errorhandler(403)
def forbidden(e):
    if _wants_json():
        return jsonify(error="Forbidden"), 403
    return render_template("errors/403.html"), 403


@errors_bp.app_errorhandler(404)
def not_found(e):
    if _wants_json():
        return jsonify(error="Not Found"), 404
    return render_template("404.html"), 404


@errors_bp.app_errorhandler(429)
def ratelimit(e):
    if _wants_json():
        return jsonify(error="Too many requests. Please try again later."), 429
    return render_template("errors/429.html"), 429


@errors_bp.app_errorhandler(500)
def server_error(e):
    current_app.logger.exception("Unhandled exception: %s", e)
    if _wants_json():
        return jsonify(error="Internal server error"), 500
    return render_template("errors/500.html"), 500
