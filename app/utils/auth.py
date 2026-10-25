"""Authentication and session management utilities for Smart Agriculture Agent.

Provides session-based user authentication, password security wrappers,
route protection decorators, open redirect validation, and CSRF token protection.
"""

from functools import wraps
from pathlib import Path
import secrets
from urllib.parse import urlparse, urljoin
from flask import current_app, flash, g, has_request_context, jsonify, redirect, request, session, url_for
from app.models.database import get_user_by_id


def is_safe_url(target: str) -> bool:
    """Validate that target redirect URL is on the same host to prevent open redirects.

    Args:
        target: Target redirect URL.

    Returns:
        True if URL is safe and internal, False otherwise.
    """
    if not target or not isinstance(target, str):
        return False
    host_url = request.host_url if has_request_context() else "http://localhost/"
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def generate_csrf_token() -> str:
    """Generate or retrieve unique per-session CSRF token."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(token: str) -> bool:
    """Compare supplied token with session CSRF token using constant-time comparison."""
    session_token = session.get("csrf_token")
    if not session_token or not token:
        return False
    return secrets.compare_digest(str(session_token), str(token))


def login_user(user: dict, remember: bool = False) -> None:
    """Store authenticated user identity in the signed session cookie.

    Args:
        user: User profile dictionary.
        remember: Whether to mark the session permanent.
    """
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user.get("full_name") or user["username"]
    session["role"] = user.get("role", "farmer")
    if remember:
        session.permanent = True
    else:
        session.permanent = False
    g.current_user = user


def logout_user() -> None:
    """Clear session data and current user context."""
    session.clear()
    g.current_user = None


def get_current_user() -> dict | None:
    """Retrieve currently authenticated user from active session."""
    if hasattr(g, "current_user") and g.current_user is not None:
        return g.current_user

    user_id = session.get("user_id")
    if not user_id:
        return None

    try:
        db_path = Path(current_app.config["DATABASE_PATH"])
        user = get_user_by_id(db_path, int(user_id))
        g.current_user = user
        return user
    except Exception:
        return None


def login_required(f):
    """Decorator requiring active session authentication for protected views and endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            # Check if API request expecting JSON
            is_api = (
                request.path.startswith("/api/")
                or request.headers.get("Accept") == "application/json"
                or request.is_json
            )
            if is_api:
                return (
                    jsonify({
                        "error": "Unauthorized",
                        "message": "Authentication required. Please sign in.",
                    }),
                    401,
                )

            flash("Please sign in to access this page.", "warning")
            next_url = request.full_path if request.query_string else request.path
            if next_url.endswith("?"):
                next_url = next_url[:-1]
            return redirect(url_for("auth.login_view", next=next_url))

        return f(*args, **kwargs)

    return decorated_function
