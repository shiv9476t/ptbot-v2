from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
