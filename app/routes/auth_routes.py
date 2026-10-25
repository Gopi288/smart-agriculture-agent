"""Authentication and user management routes for Smart Agriculture Agent."""

from pathlib import Path
import re
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from app.models.database import (
    create_user,
    get_user_by_username_or_email,
    verify_user_credentials,
)
from app.utils.auth import (
    is_safe_url,
    login_user,
    logout_user,
    validate_csrf_token,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET"])
def login_view():
    """Render agricultural login page."""
    # If already logged in, redirect directly to dashboard
    if g.get("current_user"):
        return redirect(url_for("main.index"))

    next_target = request.args.get("next", "")
    return render_template("auth/login.html", next=next_target)


@auth_bp.route("/login", methods=["POST"])
def login_post():
    """Authenticate credentials and establish user session."""
    # CSRF Verification
    csrf_token = request.form.get("csrf_token", "")
    if not validate_csrf_token(csrf_token):
        flash("Invalid or expired session security token. Please try again.", "danger")
        return redirect(url_for("auth.login_view"))

    identifier = request.form.get("identifier", "").strip()
    password = request.form.get("password", "")
    remember = bool(request.form.get("remember"))
    next_url = request.form.get("next", "").strip()

    if not identifier or not password:
        flash("Please provide both your username/email and password.", "warning")
        return render_template("auth/login.html", next=next_url, identifier=identifier)

    db_path = Path(current_app.config["DATABASE_PATH"])
    user = verify_user_credentials(db_path, identifier, password)

    if not user:
        # Generic error message to prevent username enumeration
        flash("Invalid credentials. Please verify your username/email and password.", "danger")
        return render_template("auth/login.html", next=next_url, identifier=identifier)

    # Establish session
    login_user(user, remember=remember)
    flash(f"Welcome back, {user.get('full_name', user['username'])}!", "success")

    # Safe redirect
    if next_url and is_safe_url(next_url):
        return redirect(next_url)
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET"])
def register_view():
    """Render user registration page."""
    if g.get("current_user"):
        return redirect(url_for("main.index"))
    return render_template("auth/register.html")


@auth_bp.route("/register", methods=["POST"])
def register_post():
    """Register a new farmer account."""
    csrf_token = request.form.get("csrf_token", "")
    if not validate_csrf_token(csrf_token):
        flash("Invalid or expired session security token.", "danger")
        return redirect(url_for("auth.register_view"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    full_name = request.form.get("full_name", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Validation rules
    errors = []
    if not username or len(username) < 3 or len(username) > 30 or not re.match(r"^[a-zA-Z0-9_]+$", username):
        errors.append("Username must be between 3 and 30 characters (letters, numbers, and underscores only).")

    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors.append("Please provide a valid email address.")

    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    db_path = Path(current_app.config["DATABASE_PATH"])

    # Check duplicates
    if not errors:
        if get_user_by_username_or_email(db_path, username):
            errors.append("Username is already registered. Please choose another or sign in.")
        elif get_user_by_username_or_email(db_path, email):
            errors.append("Email address is already registered. Please sign in.")

    if errors:
        for err in errors:
            flash(err, "danger")
        return render_template(
            "auth/register.html",
            username=username,
            email=email,
            full_name=full_name,
        )

    try:
        # Default role is strictly 'farmer' - prevent role escalation
        create_user(
            db_path=db_path,
            username=username,
            email=email,
            password=password,
            full_name=full_name or username,
            role="farmer",
        )
        flash("Account created successfully! You can now sign in.", "success")
        return redirect(url_for("auth.login_view"))
    except Exception as exc:
        flash(f"Registration failed: {str(exc)}", "danger")
        return render_template("auth/register.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Terminate authenticated session."""
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("auth.login_view"))
