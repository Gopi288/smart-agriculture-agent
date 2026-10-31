"""Database persistence module for Smart Agriculture Agent.

Manages SQLite schema creation, connection handling, and parameterized
CRUD operations for disease predictions, irrigation assessments, and audit records.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from werkzeug.security import check_password_hash, generate_password_hash


def get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        sqlite3.Connection with Row factory enabled.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    """Initialize the SQLite database schema if tables do not exist.

    Args:
        db_path: Path to the SQLite database file.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Disease analysis table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS disease_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                crop_declared TEXT NOT NULL,
                predicted_class TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                is_conclusive INTEGER NOT NULL,
                crop_matched INTEGER NOT NULL,
                top_alternatives_json TEXT,
                symptoms TEXT,
                management_guidance TEXT,
                recommendation_source TEXT,
                warning_message TEXT,
                image_filename TEXT
            );
            """
        )

        # Irrigation assessment table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS irrigation_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                crop TEXT NOT NULL,
                growth_stage TEXT,
                soil_type TEXT,
                soil_moisture REAL,
                soil_moisture_source TEXT,
                recent_rainfall REAL,
                rainfall_period_hours INTEGER,
                rainfall_source TEXT,
                temperature_c REAL,
                humidity_pct REAL,
                weather_source TEXT,
                recommendation TEXT NOT NULL,
                action_urgency TEXT NOT NULL,
                rationale TEXT NOT NULL,
                missing_data_notes TEXT
            );
            """
        )

        # System audit & experiment logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS experiment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                experiment_type TEXT NOT NULL,
                model_name TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                notes TEXT
            );
            """
        )

        # Users table for secure authentication
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL DEFAULT 'farmer',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            """
        )

        conn.commit()


def save_disease_analysis(
    db_path: Path,
    crop_declared: str,
    predicted_class: str,
    disease_name: str,
    confidence_score: float,
    is_conclusive: bool,
    crop_matched: bool,
    top_alternatives_json: str = "[]",
    symptoms: str = "",
    management_guidance: str = "",
    recommendation_source: str = "",
    warning_message: str = "",
    image_filename: str = "",
) -> int:
    """Persist a crop disease analysis record.

    Uses parameterized SQL to guard against injection.
    """
    timestamp = datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO disease_analyses (
                timestamp, crop_declared, predicted_class, disease_name,
                confidence_score, is_conclusive, crop_matched,
                top_alternatives_json, symptoms, management_guidance,
                recommendation_source, warning_message, image_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                timestamp,
                crop_declared,
                predicted_class,
                disease_name,
                float(confidence_score),
                1 if is_conclusive else 0,
                1 if crop_matched else 0,
                top_alternatives_json,
                symptoms,
                management_guidance,
                recommendation_source,
                warning_message,
                image_filename,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_disease_analyses(
    db_path: Path, limit: int = 50, offset: int = 0, crop_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve historical disease analysis records with optional crop filter."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if crop_filter:
            cursor.execute(
                """
                SELECT * FROM disease_analyses
                WHERE LOWER(crop_declared) = LOWER(?)
                ORDER BY id DESC LIMIT ? OFFSET ?;
                """,
                (crop_filter, limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM disease_analyses
                ORDER BY id DESC LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_disease_analysis_by_id(db_path: Path, analysis_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single disease analysis record by its primary key."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM disease_analyses WHERE id = ?;", (analysis_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_irrigation_assessment(
    db_path: Path,
    crop: str,
    growth_stage: Optional[str],
    soil_type: Optional[str],
    soil_moisture: Optional[float],
    soil_moisture_source: str,
    recent_rainfall: Optional[float],
    rainfall_period_hours: Optional[int],
    rainfall_source: str,
    temperature_c: Optional[float],
    humidity_pct: Optional[float],
    weather_source: str,
    recommendation: str,
    action_urgency: str,
    rationale: str,
    missing_data_notes: str,
) -> int:
    """Persist an irrigation assessment record."""
    timestamp = datetime.now().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO irrigation_assessments (
                timestamp, crop, growth_stage, soil_type,
                soil_moisture, soil_moisture_source,
                recent_rainfall, rainfall_period_hours, rainfall_source,
                temperature_c, humidity_pct, weather_source,
                recommendation, action_urgency, rationale, missing_data_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                timestamp,
                crop,
                growth_stage,
                soil_type,
                soil_moisture,
                soil_moisture_source,
                recent_rainfall,
                rainfall_period_hours,
                rainfall_source,
                temperature_c,
                humidity_pct,
                weather_source,
                recommendation,
                action_urgency,
                rationale,
                missing_data_notes,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_irrigation_assessments(
    db_path: Path, limit: int = 50, offset: int = 0
) -> List[Dict[str, Any]]:
    """Retrieve historical irrigation assessments."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM irrigation_assessments
            ORDER BY id DESC LIMIT ? OFFSET ?;
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_system_counts(db_path: Path) -> Dict[str, int]:
    """Retrieve counts of saved disease, irrigation, and user records."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM disease_analyses;")
        disease_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM irrigation_assessments;")
        irrigation_count = cursor.fetchone()[0]
        try:
            cursor.execute("SELECT COUNT(*) FROM users;")
            users_count = cursor.fetchone()[0]
        except Exception:
            users_count = 0
        return {
            "disease_analyses_count": disease_count,
            "irrigation_assessments_count": irrigation_count,
            "users_count": users_count,
        }


def create_user(
    db_path: Path,
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    role: str = "farmer",
) -> int:
    """Create a new user with securely hashed password.

    Args:
        db_path: Path to the SQLite database file.
        username: Unique normalized username.
        email: Unique normalized email address.
        password: Plaintext password (will be hashed with scrypt/pbkdf2).
        full_name: Optional display name.
        role: Account role ('farmer', 'agronomist', 'admin').

    Returns:
        Created user ID.
    """
    clean_username = username.strip().lower()
    clean_email = email.strip().lower()
    password_hash = generate_password_hash(password)
    now_iso = datetime.now().isoformat()

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?);
            """,
            (clean_username, clean_email, password_hash, full_name or username, role, now_iso),
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_user_by_id(db_path: Path, user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user dictionary by primary key."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, full_name, role, is_active, created_at FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_username_or_email(db_path: Path, identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record including password hash by username or email."""
    clean_id = identifier.strip().lower()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, email, password_hash, full_name, role, is_active, created_at
            FROM users
            WHERE username = ? OR email = ?;
            """,
            (clean_id, clean_id),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def verify_user_credentials(db_path: Path, identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials using secure password hash comparison.

    Returns user dictionary (without password_hash) if valid and active, else None.
    """
    user = get_user_by_username_or_email(db_path, identifier)
    if not user:
        return None

    if not user.get("is_active"):
        return None

    if check_password_hash(user["password_hash"], password):
        # Exclude password_hash from returned user profile
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name") or user["username"],
            "role": user.get("role", "farmer"),
            "created_at": user.get("created_at"),
        }
    return None


def init_default_demo_user(db_path: Path) -> None:
    """Seed an initial demonstration farmer account if no users exist.

    Also resets the demo account password to the known demo credential if
    the stored hash is stale (e.g. after a manual DB edit or migration).
    """
    _DEMO_USERNAME = "farmer_demo"
    _DEMO_PASSWORD = "FarmerPassword123!"

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]

    if count == 0:
        create_user(
            db_path=db_path,
            username=_DEMO_USERNAME,
            email="demo@smartagri.local",
            password=_DEMO_PASSWORD,
            full_name="Demonstration Farmer",
            role="farmer",
        )
        print(f"[*] Seeded initial demonstration account ({_DEMO_USERNAME} / {_DEMO_PASSWORD})")
    else:
        # Ensure the demo account password matches the displayed credential.
        # If the hash was generated from a different password (e.g. migration
        # artifact), silently reset it so the login page "Click to Fill" works.
        verified = verify_user_credentials(db_path, _DEMO_USERNAME, _DEMO_PASSWORD)
        if verified is None:
            new_hash = generate_password_hash(_DEMO_PASSWORD)
            with get_db_connection(db_path) as conn:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (new_hash, _DEMO_USERNAME),
                )
                conn.commit()
            print(f"[*] Demo account password re-synced ({_DEMO_USERNAME} / {_DEMO_PASSWORD})")
