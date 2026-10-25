"""Main dashboard, explorer, analytics, and information routes for Smart Agriculture Agent."""

import json
from pathlib import Path
from flask import Blueprint, current_app, jsonify, render_template, request
from app.models.database import get_disease_analyses, get_system_counts
from app.services.assistant_service import AgriculturalAssistant
from app.utils.auth import login_required
from app.utils.crop_registry import CROP_REGISTRY
from ml.dataset_loader import SUPPORTED_CLASSES

main_bp = Blueprint("main", __name__)
assistant = AgriculturalAssistant()


@main_bp.route("/")
@login_required
def index():
    """Main dashboard view displaying system status, supported crops, and recent analyses."""
    db_path = Path(current_app.config["DATABASE_PATH"])
    counts = get_system_counts(db_path)
    recent_analyses = get_disease_analyses(db_path, limit=5)

    classifier = getattr(current_app, "classifier", None)
    weather_svc = getattr(current_app, "weather_service", None)

    status_info = {
        "model_loaded": classifier.is_model_ready if classifier else False,
        "confidence_threshold_pct": current_app.config["CONFIDENCE_THRESHOLD"] * 100,
        "weather_service_active": weather_svc.is_configured if weather_svc else False,
        "supported_crops": current_app.config["SUPPORTED_CROPS"],
        "supported_classes": SUPPORTED_CLASSES,
        "total_disease_records": counts["disease_analyses_count"],
        "total_irrigation_records": counts["irrigation_assessments_count"],
        "total_users": counts.get("users_count", 1),
    }

    return render_template(
        "dashboard.html",
        status=status_info,
        recent_analyses=recent_analyses,
    )


@main_bp.route("/crops")
@login_required
def crops_view():
    """Supported Crops Explorer: 24 agricultural crop profiles with FAO-56 and IPM data."""
    categories = sorted(list({data["category"] for data in CROP_REGISTRY.values()}))
    return render_template(
        "crops.html",
        crops=CROP_REGISTRY,
        categories=categories,
    )


@main_bp.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant_view():
    """Agricultural Decision Support Assistant: Q&A on agronomy, IPM, and irrigation."""
    query = ""
    response_data = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            response_data = assistant.answer_query(query)
    elif request.args.get("q"):
        query = request.args.get("q", "").strip()
        if query:
            response_data = assistant.answer_query(query)

    return render_template(
        "assistant.html",
        query=query,
        response=response_data,
        default_prompts=assistant.DEFAULT_PROMPTS,
    )


@main_bp.route("/performance")
@login_required
def performance_view():
    """Model Performance and Empirical Evaluation Dashboard."""
    metrics_path = Path(current_app.config["BASE_DIR"]) / "experiments" / "evaluation_metrics.json"
    metrics_data = {}
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            metrics_data = {}

    return render_template(
        "performance.html",
        metrics=metrics_data,
        supported_classes=SUPPORTED_CLASSES,
    )


@main_bp.route("/settings")
@login_required
def settings_view():
    """System settings, active threshold configuration, and environment status."""
    db_path = Path(current_app.config["DATABASE_PATH"])
    counts = get_system_counts(db_path)
    db_size_kb = round(db_path.stat().st_size / 1024, 1) if db_path.exists() else 0

    model_path = Path(current_app.config.get("MODEL_PATH", current_app.config["BASE_DIR"] / "ml" / "models" / "mobilenetv2_crop_disease.pth"))
    model_size_mb = round(model_path.stat().st_size / (1024 * 1024), 2) if model_path.exists() else 0

    return render_template(
        "settings.html",
        db_size_kb=db_size_kb,
        model_size_mb=model_size_mb,
        counts=counts,
    )


@main_bp.route("/about")
def about():
    """Project documentation, technical architecture, and team responsibility breakdown."""
    return render_template("about.html")


@main_bp.route("/api/health")
def health_check():
    """REST endpoint for health monitoring and uptime checks."""
    classifier = getattr(current_app, "classifier", None)
    weather_svc = getattr(current_app, "weather_service", None)

    return jsonify({
        "status": "healthy",
        "model_ready": classifier.is_model_ready if classifier else False,
        "weather_api_configured": weather_svc.is_configured if weather_svc else False,
        "database": str(current_app.config["DATABASE_PATH"].name),
    })
