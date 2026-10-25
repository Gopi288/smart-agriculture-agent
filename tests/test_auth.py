"""Unit and integration tests for authentication and session security."""

from pathlib import Path
from app.models.database import (
    create_user,
    get_user_by_username_or_email,
    verify_user_credentials,
)
from app.utils.auth import is_safe_url


def test_login_page_renders(client):
    """Verify login page renders with agricultural elements and form inputs."""
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert b"Smart Agriculture Agent" in res.data
    assert b"Intelligent Crop Care. Smarter Farming." in res.data
    assert b"Demo Credentials" in res.data
    assert b"farmer_demo" in res.data
    assert b"csrf_token" in res.data
    assert b"password" in res.data


def test_login_success_and_session(client):
    """Verify valid login authenticates and sets session cookie."""
    # Obtain valid CSRF token from page
    page = client.get("/auth/login")
    with client.session_transaction() as sess:
        token = sess.get("csrf_token")

    res = client.post(
        "/auth/login",
        data={
            "csrf_token": token,
            "identifier": "farmer_demo",
            "password": "FarmerPassword123!",
            "remember": "on",
        },
        follow_redirects=False,
    )
    # Redirects to dashboard
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/")

    # Verify session is now populated
    with client.session_transaction() as sess:
        assert sess.get("username") == "farmer_demo"
        assert sess.get("user_id") is not None


def test_login_invalid_credentials_fails_safely(client):
    """Verify bad credentials show safe generic error without disclosing user existence."""
    page = client.get("/auth/login")
    with client.session_transaction() as sess:
        token = sess.get("csrf_token")

    res = client.post(
        "/auth/login",
        data={
            "csrf_token": token,
            "identifier": "farmer_demo",
            "password": "WrongPassword999!",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Invalid credentials" in res.data


def test_open_redirect_prevention(client):
    """Verify login rejects external redirect targets."""
    # Internal URLs are safe
    assert is_safe_url("/disease/") is True
    assert is_safe_url("/history/?crop=Tomato") is True

    # External malicious targets are rejected
    assert is_safe_url("https://malicious-phishing.com") is False
    assert is_safe_url("http://evil.com/login") is False
    assert is_safe_url("//evil.com") is False
    assert is_safe_url("javascript:alert(1)") is False


def test_safe_redirect_after_login(client):
    """Verify valid internal next URL is honored upon successful login."""
    client.get("/auth/login")
    with client.session_transaction() as sess:
        token = sess.get("csrf_token")

    res = client.post(
        "/auth/login",
        data={
            "csrf_token": token,
            "identifier": "farmer_demo",
            "password": "FarmerPassword123!",
            "next": "/irrigation/",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/irrigation/")


def test_logout_clears_session(auth_client):
    """Verify logout invalidates session and subsequent protected access redirects."""
    # Verify logged in
    r_check = auth_client.get("/")
    assert r_check.status_code == 200

    # Logout
    r_logout = auth_client.get("/auth/logout", follow_redirects=True)
    assert r_logout.status_code == 200
    assert b"You have been signed out" in r_logout.data

    # Protected access is now blocked
    r_protected = auth_client.get("/")
    assert r_protected.status_code == 302
    assert "/auth/login" in r_protected.headers["Location"]


def test_user_registration_flow(client, app):
    """Verify new user registration with password validation and duplicate rejection."""
    client.get("/auth/register")
    with client.session_transaction() as sess:
        token = sess.get("csrf_token")

    # 1. Reject short password
    res_short = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "newfarmer",
            "email": "new@farmer.org",
            "password": "short",
            "confirm_password": "short",
        },
        follow_redirects=True,
    )
    assert b"at least 8 characters" in res_short.data

    # 2. Reject mismatch password
    res_mismatch = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "newfarmer",
            "email": "new@farmer.org",
            "password": "ValidPassword123!",
            "confirm_password": "DifferentPassword123!",
        },
        follow_redirects=True,
    )
    assert b"Passwords do not match" in res_mismatch.data

    # 3. Successful registration
    res_success = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "newfarmer",
            "email": "new@farmer.org",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
            "full_name": "New Farmer",
        },
        follow_redirects=True,
    )
    assert b"Account created successfully" in res_success.data

    # 4. Duplicate rejection
    res_dup = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "newfarmer",
            "email": "other@farmer.org",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!",
        },
        follow_redirects=True,
    )
    assert b"already registered" in res_dup.data


def test_passwords_are_securely_hashed(app):
    """Verify passwords are never stored in plaintext in the database."""
    db_path = Path(app.config["DATABASE_PATH"])
    user = get_user_by_username_or_email(db_path, "farmer_demo")
    assert user is not None
    assert "password_hash" in user
    assert user["password_hash"] != "FarmerPassword123!"
    assert user["password_hash"].startswith("scrypt:") or user["password_hash"].startswith("pbkdf2:")
