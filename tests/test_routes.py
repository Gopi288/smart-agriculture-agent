"""Integration tests for Flask application routes and endpoints."""

import io
from app.services.weather_service import WeatherService


def test_unauthenticated_access_redirects(client):
    """Verify unauthenticated requests to protected endpoints redirect to login."""
    res_home = client.get("/")
    assert res_home.status_code == 302
    assert "/auth/login" in res_home.headers["Location"]

    res_disease = client.get("/disease/")
    assert res_disease.status_code == 302
    assert "/auth/login" in res_disease.headers["Location"]

    res_history = client.get("/history/")
    assert res_history.status_code == 302
    assert "/auth/login" in res_history.headers["Location"]

    # API request returns 401 JSON
    res_api = client.post("/irrigation/assess", headers={"Accept": "application/json"})
    assert res_api.status_code == 401
    assert res_api.get_json()["error"] == "Unauthorized"


def test_home_and_about_routes(auth_client):
    """Verify primary navigation pages render successfully for authenticated user."""
    r_home = auth_client.get("/")
    assert r_home.status_code == 200
    assert b"Smart Agriculture Agent" in r_home.data
    assert b"Decision Threshold" in r_home.data

    r_about = auth_client.get("/about")
    assert r_about.status_code == 200
    assert b"MobileNetV2" in r_about.data
    assert b"Four-Member Academic Team Distribution" in r_about.data


def test_api_health_endpoint(client):
    """Verify health check REST endpoint is public and returns JSON status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "model_ready" in data


def test_disease_detection_flow_with_sample(auth_client):
    """Verify disease detection using verified sample image selector."""
    response = auth_client.post(
        "/disease/analyze",
        data={
            "crop": "Tomato",
            "sample_image_name": "sample_Tomato___Early_blight_1.jpg",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Early Blight" in response.data or b"Tomato" in response.data
    assert b"Model Confidence" in response.data


def test_disease_detection_flow_with_upload(auth_client, valid_test_image):
    """Verify multipart file upload and inference execution."""
    with open(valid_test_image, "rb") as f:
        img_bytes = f.read()

    response = auth_client.post(
        "/disease/analyze",
        data={
            "crop": "Tomato",
            "leaf_image": (io.BytesIO(img_bytes), "test_leaf.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Model Confidence" in response.data


def test_disease_detection_invalid_crop(auth_client, valid_test_image):
    """Verify validation rejects unsupported crop selection."""
    with open(valid_test_image, "rb") as f:
        img_bytes = f.read()

    response = auth_client.post(
        "/disease/analyze",
        data={
            "crop": "UnsupportedCrop",
            "leaf_image": (io.BytesIO(img_bytes), "test_leaf.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Unsupported crop" in response.data


def test_disease_detection_corrupt_file(auth_client, corrupt_test_image):
    """Verify security utility rejects corrupt pseudo-images."""
    with open(corrupt_test_image, "rb") as f:
        corrupt_bytes = f.read()

    response = auth_client.post(
        "/disease/analyze",
        data={
            "crop": "Tomato",
            "leaf_image": (io.BytesIO(corrupt_bytes), "corrupt.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Image validation failed" in response.data


def test_irrigation_assessment_flow(auth_client):
    """Verify irrigation advisor form submission and decision output."""
    response = auth_client.post(
        "/irrigation/assess",
        data={
            "crop": "Tomato",
            "growth_stage": "Flowering",
            "soil_type": "Sandy",
            "soil_moisture": "22.0",
            "recent_rainfall": "0.0",
            "rainfall_period_hours": "24",
            "location": "Fresno",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Irrigation may be needed" in response.data
    assert b"Calculated MAD Threshold" in response.data


def test_irrigation_assessment_json_api(auth_client):
    """Verify irrigation endpoint supports headless JSON responses."""
    response = auth_client.post(
        "/irrigation/assess",
        data={
            "crop": "Potato",
            "soil_moisture": "45.0",
            "recent_rainfall": "25.0",
        },
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendation" in data
    assert "action_urgency" in data
    assert "rules_triggered" in data


def test_history_view(auth_client):
    """Verify history audit log renders table data."""
    res = auth_client.get("/history/")
    assert res.status_code == 200
    assert b"Audit" in res.data
    assert b"Historical Records" in res.data


def test_weather_service_graceful_offline():
    """Verify weather service operates safely without API key or network."""
    svc = WeatherService(api_key="")
    assert svc.is_configured is False
    res = svc.get_weather(location="Fresno")
    assert res["is_available"] is False
    assert "Unavailable" in res["source"]
    assert res["temperature_c"] is None
