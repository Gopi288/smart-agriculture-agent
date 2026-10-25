"""Audit history and persistent records routes."""

from pathlib import Path
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
)
from app.models.database import (
    get_disease_analyses,
    get_irrigation_assessments,
)
from app.utils.auth import login_required
from app.utils.validation import SUPPORTED_CROPS

history_bp = Blueprint("history", __name__, url_prefix="/history")


@history_bp.route("", methods=["GET"])
@history_bp.route("/", methods=["GET"])
@login_required
def history_view():
    """Display chronological audit log of disease predictions and irrigation assessments."""
    crop_filter = request.args.get("crop", "").strip() or None
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    db_path = Path(current_app.config["DATABASE_PATH"])

    disease_records = get_disease_analyses(db_path, limit=limit, offset=offset, crop_filter=crop_filter)
    irrigation_records = get_irrigation_assessments(db_path, limit=limit, offset=offset)

    return render_template(
        "history.html",
        disease_records=disease_records,
        irrigation_records=irrigation_records,
        supported_crops=SUPPORTED_CROPS,
        selected_crop=crop_filter,
    )
