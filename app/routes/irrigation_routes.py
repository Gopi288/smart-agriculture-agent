"""Intelligent irrigation advisor routes."""

import json
from pathlib import Path
from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from app.models.database import (
    get_db_connection,
    save_irrigation_assessment,
)
from app.services.report_service import generate_irrigation_report
from app.utils.auth import login_required
from app.utils.validation import (
    ALL_CROPS,
    SUPPORTED_CROPS,
    SUPPORTED_GROWTH_STAGES,
    SUPPORTED_SOIL_TYPES,
    validate_irrigation_request,
)

irrigation_bp = Blueprint("irrigation", __name__, url_prefix="/irrigation")


@irrigation_bp.route("", methods=["GET"])
@irrigation_bp.route("/", methods=["GET"])
@login_required
def irrigation_view():
    """Render irrigation advisor form and scenarios."""
    sample_inputs_path = Path(current_app.config["SAMPLE_INPUTS_PATH"])
    scenarios = []
    if sample_inputs_path.exists():
        try:
            with open(sample_inputs_path, "r", encoding="utf-8") as f:
                scenarios = json.load(f).get("scenarios", [])
        except Exception:
            scenarios = []

    selected_crop = request.args.get("crop", "")

    return render_template(
        "irrigation_advisor.html",
        supported_crops=ALL_CROPS,
        selected_crop=selected_crop,
        growth_stages=SUPPORTED_GROWTH_STAGES,
        soil_types=SUPPORTED_SOIL_TYPES,
        scenarios=scenarios,
        result=None,
    )


@irrigation_bp.route("/assess", methods=["POST"])
@login_required
def assess_irrigation():
    """Evaluate soil moisture, precipitation, and agrometeorology against agronomic rules."""
    form_dict = request.form.to_dict()

    is_valid, clean_data, errors = validate_irrigation_request(form_dict)
    if not is_valid:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("irrigation.irrigation_view"))

    # Fetch weather data if location provided or key configured
    weather_svc = current_app.weather_service
    location = clean_data.get("location")
    weather_data = weather_svc.get_weather(location)

    # Run Irrigation Rule Engine
    irr_engine = current_app.irrigation_engine
    assessment = irr_engine.assess_irrigation(
        crop=clean_data["crop"],
        growth_stage=clean_data.get("growth_stage"),
        soil_type=clean_data.get("soil_type"),
        soil_moisture=clean_data.get("soil_moisture"),
        soil_moisture_source=clean_data.get("soil_moisture_source", "Not Provided"),
        recent_rainfall=clean_data.get("recent_rainfall"),
        rainfall_period_hours=clean_data.get("rainfall_period_hours", 24),
        rainfall_source=clean_data.get("rainfall_source", "Not Provided"),
        weather_data=weather_data,
    )

    # Persist in SQLite
    db_path = Path(current_app.config["DATABASE_PATH"])
    record_id = save_irrigation_assessment(
        db_path=db_path,
        crop=clean_data["crop"],
        growth_stage=clean_data.get("growth_stage"),
        soil_type=clean_data.get("soil_type"),
        soil_moisture=clean_data.get("soil_moisture"),
        soil_moisture_source=clean_data.get("soil_moisture_source", "Not Provided"),
        recent_rainfall=clean_data.get("recent_rainfall"),
        rainfall_period_hours=clean_data.get("rainfall_period_hours"),
        rainfall_source=clean_data.get("rainfall_source", "Not Provided"),
        temperature_c=weather_data.get("temperature_c"),
        humidity_pct=weather_data.get("humidity_pct"),
        weather_source=weather_data.get("source", "Offline"),
        recommendation=assessment.get("recommendation", "Unknown"),
        action_urgency=assessment.get("action_urgency", "Normal"),
        rationale=assessment.get("rationale", ""),
        missing_data_notes="; ".join(assessment.get("missing_data_notes", [])),
    )

    assessment["record_id"] = record_id
    assessment["weather_info"] = weather_data

    # Return JSON if requested
    if request.headers.get("Accept") == "application/json" or request.args.get("format") == "json":
        return jsonify(assessment)

    sample_inputs_path = Path(current_app.config["SAMPLE_INPUTS_PATH"])
    scenarios = []
    if sample_inputs_path.exists():
        try:
            with open(sample_inputs_path, "r", encoding="utf-8") as f:
                scenarios = json.load(f).get("scenarios", [])
        except Exception:
            scenarios = []

    return render_template(
        "irrigation_advisor.html",
        supported_crops=ALL_CROPS,
        growth_stages=SUPPORTED_GROWTH_STAGES,
        soil_types=SUPPORTED_SOIL_TYPES,
        scenarios=scenarios,
        result=assessment,
        form_data=clean_data,
    )


@irrigation_bp.route("/report/<int:record_id>")
@login_required
def download_report(record_id: int):
    """Download plain text irrigation report for a given record ID."""
    db_path = Path(current_app.config["DATABASE_PATH"])
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM irrigation_assessments WHERE id = ?;", (record_id,))
        row = cursor.fetchone()

    if not row:
        flash("Record not found.", "warning")
        return redirect(url_for("history.history_view"))

    record = dict(row)
    data_dict = {
        "recommendation": record.get("recommendation"),
        "action_urgency": record.get("action_urgency"),
        "confidence_level": "Audited Log",
        "effective_threshold_pct": None,
        "rationale": record.get("rationale"),
        "next_action": "Follow prescribed water schedule.",
        "factors_analyzed": [f"Soil moisture: {record.get('soil_moisture')}%", f"Rainfall: {record.get('recent_rainfall')} mm"],
        "missing_data_notes": [record.get("missing_data_notes")] if record.get("missing_data_notes") else [],
        "rules_triggered": ["LOGGED_PERSISTENT_RECORD"],
        "data_summary": {
            "crop": record.get("crop"),
            "growth_stage": record.get("growth_stage"),
            "soil_type": record.get("soil_type"),
            "soil_moisture": record.get("soil_moisture"),
            "soil_moisture_source": record.get("soil_moisture_source"),
            "recent_rainfall": record.get("recent_rainfall"),
            "rainfall_period_hours": record.get("rainfall_period_hours"),
            "rainfall_source": record.get("rainfall_source"),
        },
    }

    report_text = generate_irrigation_report(data_dict)

    return Response(
        report_text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=Irrigation_Report_{record_id}.txt"},
    )
