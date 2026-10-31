"""Disease detection and agronomic recommendation routes."""

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
    get_disease_analysis_by_id,
    save_disease_analysis,
)
from app.services.report_service import generate_disease_report
from app.utils.auth import login_required
from app.utils.security import (
    allowed_file,
    generate_safe_filename,
    verify_image_integrity,
)
from app.utils.validation import ALL_CROPS, SUPPORTED_CROPS, validate_crop_input

disease_bp = Blueprint("disease", __name__, url_prefix="/disease")


@disease_bp.route("", methods=["GET"])
@disease_bp.route("/", methods=["GET"])
@login_required
def disease_view():
    """Render leaf upload and disease detection form."""
    sample_dir = Path(current_app.config["BASE_DIR"]) / "static" / "sample_images"
    sample_images = []
    if sample_dir.exists():
        sample_images = [f.name for f in sample_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}]

    selected_crop = request.args.get("crop", "")

    return render_template(
        "disease_detection.html",
        supported_crops=current_app.config["SUPPORTED_CROPS"],
        all_crops=ALL_CROPS,
        selected_crop=selected_crop,
        sample_images=sample_images,
        result=None,
    )


@disease_bp.route("/analyze", methods=["POST"])
@login_required
def analyze_disease():
    """Handle image upload, run neural network inference, and evaluate agronomic rules."""
    crop_raw = request.form.get("crop")
    crop_ok, crop_name, crop_err = validate_crop_input(crop_raw)

    if not crop_ok:
        flash(crop_err, "danger")
        return redirect(url_for("disease.disease_view"))

    # Check whether uploaded file or sample image selection was provided
    image_file = request.files.get("leaf_image")
    selected_sample = request.form.get("sample_image_name")

    saved_filename = ""
    saved_filepath = None
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])

    if image_file and image_file.filename:
        if not allowed_file(image_file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            flash("Invalid file format. Allowed extensions: JPG, JPEG, PNG.", "danger")
            return redirect(url_for("disease.disease_view"))

        saved_filename = generate_safe_filename(image_file.filename)
        saved_filepath = upload_folder / saved_filename
        image_file.save(str(saved_filepath))

        # Deep verification of image integrity
        is_valid_img, img_err = verify_image_integrity(saved_filepath)
        if not is_valid_img:
            if saved_filepath.exists():
                saved_filepath.unlink()
            flash(f"Image validation failed: {img_err}", "danger")
            return redirect(url_for("disease.disease_view"))

    elif selected_sample:
        # Load verified sample image for demonstration
        sample_source = Path(current_app.config["BASE_DIR"]) / "static" / "sample_images" / selected_sample
        if sample_source.exists():
            saved_filename = f"demo_{selected_sample}"
            saved_filepath = upload_folder / saved_filename
            import shutil
            shutil.copy2(sample_source, saved_filepath)
        else:
            flash(f"Sample image '{selected_sample}' not found.", "warning")
            return redirect(url_for("disease.disease_view"))
    else:
        flash("Please upload a leaf image file or select a demonstration sample.", "warning")
        return redirect(url_for("disease.disease_view"))

    # Run AI Model Inference
    classifier = current_app.classifier
    inference_result = classifier.predict(saved_filepath)

    if not inference_result.get("success"):
        flash(f"Inference error: {inference_result.get('error')}", "danger")
        return redirect(url_for("disease.disease_view"))

    predicted_class = inference_result["predicted_class"]
    confidence_score = inference_result["confidence_score"]
    alternatives = inference_result.get("alternatives", [])

    # Run Rule-Based Recommendation Engine
    rec_engine = current_app.recommendation_engine
    recommendation = rec_engine.evaluate_recommendation(
        predicted_class=predicted_class,
        confidence=confidence_score,
        declared_crop=crop_name,
        top_predictions=alternatives,
    )

    # Persist record in SQLite
    db_path = Path(current_app.config["DATABASE_PATH"])
    record_id = save_disease_analysis(
        db_path=db_path,
        crop_declared=crop_name,
        predicted_class=predicted_class,
        disease_name=recommendation.get("common_name", predicted_class),
        confidence_score=confidence_score,
        is_conclusive=recommendation.get("is_conclusive", False),
        crop_matched=recommendation.get("crop_matched", False),
        top_alternatives_json=json.dumps(alternatives),
        symptoms="; ".join(recommendation.get("observable_symptoms", [])),
        management_guidance=recommendation.get("crop_management_advice", ""),
        recommendation_source=recommendation.get("source_name", ""),
        warning_message="; ".join(recommendation.get("warnings", [])),
        image_filename=saved_filename,
    )

    combined_result = {
        "record_id": record_id,
        "crop_declared": crop_name,
        "inference": inference_result,
        "recommendation": recommendation,
        "image_url": url_for("static", filename=f"uploads/{saved_filename}"),
    }

    # If requested as JSON API
    if request.headers.get("Accept") == "application/json" or request.args.get("format") == "json":
        return jsonify(combined_result)

    sample_dir = Path(current_app.config["BASE_DIR"]) / "static" / "sample_images"
    sample_images = [f.name for f in sample_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}] if sample_dir.exists() else []

    return render_template(
        "disease_detection.html",
        supported_crops=current_app.config["SUPPORTED_CROPS"],
        all_crops=ALL_CROPS,
        sample_images=sample_images,
        result=combined_result,
    )


@disease_bp.route("/report/<int:record_id>")
@login_required
def download_report(record_id: int):
    """Download plain text analysis report for a given record ID."""
    db_path = Path(current_app.config["DATABASE_PATH"])
    record = get_disease_analysis_by_id(db_path, record_id)

    if not record:
        flash("Record not found.", "warning")
        return redirect(url_for("history.history_view"))

    # Reconstruct data dict for report generator
    report_dict = {
        "crop_declared": record.get("crop_declared"),
        "predicted_class": record.get("predicted_class"),
        "common_name": record.get("disease_name"),
        "confidence_pct": round(float(record.get("confidence_score", 0.0)) * 100.0, 1),
        "is_conclusive": bool(record.get("is_conclusive")),
        "crop_matched": bool(record.get("crop_matched")),
        "observable_symptoms": [s.strip() for s in (record.get("symptoms") or "").split(";") if s.strip()],
        "preventive_practices": [],
        "crop_management_advice": record.get("management_guidance"),
        "source_name": record.get("recommendation_source"),
        "warnings": [w.strip() for w in (record.get("warning_message") or "").split(";") if w.strip()],
    }

    report_text = generate_disease_report(report_dict)

    return Response(
        report_text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=Disease_Report_{record_id}.txt"},
    )
