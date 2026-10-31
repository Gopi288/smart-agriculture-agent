"""Flask Application Factory for Smart Agriculture Agent.

Initializes configuration, persistence schema, service singletons,
and registers route blueprints and global exception handlers.

Render deployment notes:
- The CropDiseaseClassifier uses LAZY model loading: weights are only read
  from disk on the first call to predict(), not at create_app() time.
  This keeps worker startup fast and avoids OOM on Render free tier.
- /healthz is a lightweight, model-free endpoint for Render health checks.
"""

from pathlib import Path
from flask import Flask, g, render_template
from config import Config, get_config
from app.models.database import init_db, init_default_demo_user
from app.services.disease_classifier import CropDiseaseClassifier
from app.services.irrigation_engine import IrrigationDecisionEngine
from app.services.recommendation_engine import DiseaseRecommendationEngine
from app.services.weather_service import WeatherService
from app.utils.auth import generate_csrf_token, get_current_user


def create_app(config_object=None) -> Flask:
    """Create and configure an instance of the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(Config.BASE_DIR / "templates"),
        static_folder=str(Config.BASE_DIR / "static"),
    )

    if config_object is None:
        config_object = get_config()

    app.config.from_object(config_object)

    # Ensure upload folder exists
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)

    # Initialize SQLite database schema & seed initial demonstration account
    db_path = Path(app.config["DATABASE_PATH"])
    init_db(db_path)
    init_default_demo_user(db_path)

    # Security cookie settings — must be assigned directly, not setdefault,
    # because Flask 3.x may already have defaults that setdefault() won't override.
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # SESSION_COOKIE_SECURE should be True in production (HTTPS).
    # On Render all traffic is HTTPS, so set based on env.
    import os as _os
    app.config["SESSION_COOKIE_SECURE"] = _os.getenv("FLASK_ENV", "development").lower() == "production"

    # Hook user loading before each request
    @app.before_request
    def load_user_context():
        g.current_user = get_current_user()

    # Expose current_user and CSRF token generator to all Jinja templates
    @app.context_processor
    def inject_global_template_context():
        return {
            "current_user": g.get("current_user"),
            "csrf_token": generate_csrf_token,
        }

    # -----------------------------------------------------------------------
    # Initialize service instances
    # CropDiseaseClassifier is lazy: NO model weights are loaded here.
    # Weights are loaded on first predict() call inside a request context.
    # This keeps worker startup memory under ~150MB on Render free tier.
    # -----------------------------------------------------------------------
    classifier = CropDiseaseClassifier(
        model_path=Path(app.config["MODEL_PATH"]),
        class_indices_path=Path(app.config["CLASS_INDICES_PATH"]),
        confidence_threshold=float(app.config["CONFIDENCE_THRESHOLD"]),
        uncertainty_margin=float(app.config["UNCERTAINTY_MARGIN"]),
    )

    rec_engine = DiseaseRecommendationEngine(
        knowledge_base_path=Path(app.config["KNOWLEDGE_BASE_PATH"]),
        confidence_threshold=float(app.config["CONFIDENCE_THRESHOLD"]),
    )

    irr_engine = IrrigationDecisionEngine()

    weather_svc = WeatherService(
        api_key=app.config.get("OPENWEATHER_API_KEY", ""),
        timeout=app.config.get("WEATHER_API_TIMEOUT", 5),
    )

    # Store services in app extensions for clean dependency injection in routes
    app.classifier = classifier  # type: ignore
    app.recommendation_engine = rec_engine  # type: ignore
    app.irrigation_engine = irr_engine  # type: ignore
    app.weather_service = weather_svc  # type: ignore

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.disease_routes import disease_bp
    from app.routes.irrigation_routes import irrigation_bp
    from app.routes.history_routes import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(irrigation_bp)
    app.register_blueprint(history_bp)

    # Global error handlers
    @app.errorhandler(400)
    def handle_bad_request(err):
        return render_template("error.html", code=400, message=str(err)), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        return render_template("error.html", code=404, message="The requested page or resource could not be found."), 404

    @app.errorhandler(413)
    def handle_file_too_large(err):
        return render_template("error.html", code=413, message="Uploaded file exceeds the maximum 8 MB limit."), 413

    @app.errorhandler(500)
    def handle_server_error(err):
        return render_template("error.html", code=500, message="An internal server error occurred. Please check application logs."), 500

    return app
