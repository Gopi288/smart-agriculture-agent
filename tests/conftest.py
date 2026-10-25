"""Pytest fixtures and configuration for Smart Agriculture Agent test suite."""

import os
import shutil
import sys
import tempfile
from pathlib import Path
import pytest
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from config import TestingConfig


@pytest.fixture(scope="session")
def test_dirs():
    """Create a temporary directory tree for test artifacts."""
    temp_dir = Path(tempfile.mkdtemp(prefix="smart_agri_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def valid_test_image(test_dirs):
    """Generate a clean, valid RGB image file for testing."""
    img_path = test_dirs / "valid_leaf.jpg"
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    img.save(img_path, format="JPEG")
    return img_path


@pytest.fixture(scope="session")
def corrupt_test_image(test_dirs):
    """Generate a pseudo-image file with corrupt binary header."""
    corrupt_path = test_dirs / "corrupt_leaf.jpg"
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_AN_IMAGE_RANDOM_CORRUPT_BYTES_123456789")
    return corrupt_path


@pytest.fixture
def app(test_dirs):
    """Instantiate Flask application in testing mode with isolated test database."""
    test_db_path = test_dirs / "test_smart_agri.db"

    class DynamicTestingConfig(TestingConfig):
        DATABASE_PATH = test_db_path
        UPLOAD_FOLDER = test_dirs / "uploads"

    app_instance = create_app(DynamicTestingConfig)
    app_instance.config["TESTING"] = True

    yield app_instance

    # Cleanup DB after test
    if test_db_path.exists():
        try:
            os.remove(test_db_path)
        except Exception:
            pass


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    """Flask test client with an active authenticated session."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "farmer_demo"
        sess["full_name"] = "Demonstration Farmer"
        sess["role"] = "farmer"
    return client
