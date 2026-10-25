"""Unit tests for input validation and security utilities."""

from app.utils.security import allowed_file, verify_image_integrity
from app.utils.validation import (
    validate_crop_input,
    validate_irrigation_request,
    validate_rainfall,
    validate_soil_moisture,
)


def test_validate_crop_input():
    """Verify crop input validation and normalization."""
    # Valid crops
    assert validate_crop_input("Tomato")[0] is True
    assert validate_crop_input("tomato")[1] == "Tomato"
    assert validate_crop_input("POTATO")[1] == "Potato"
    assert validate_crop_input("Corn")[1] == "Corn"

    # Missing or unsupported crops
    assert validate_crop_input("")[0] is False
    assert validate_crop_input(None)[0] is False
    assert validate_crop_input("Banana")[0] is False
    assert "Unsupported crop" in validate_crop_input("Banana")[2]


def test_validate_soil_moisture():
    """Verify soil moisture percentage validation."""
    # Valid ranges
    assert validate_soil_moisture(45.5) == (True, 45.5, "")
    assert validate_soil_moisture("30.0") == (True, 30.0, "")
    assert validate_soil_moisture(0.0) == (True, 0.0, "")
    assert validate_soil_moisture(100.0) == (True, 100.0, "")

    # Optional omitted values
    assert validate_soil_moisture(None) == (True, None, "")
    assert validate_soil_moisture("") == (True, None, "")

    # Invalid values
    assert validate_soil_moisture(-5.0)[0] is False
    assert validate_soil_moisture(105.0)[0] is False
    assert validate_soil_moisture("not_a_number")[0] is False


def test_validate_rainfall():
    """Verify rainfall input validation and period constraints."""
    # Valid
    assert validate_rainfall(12.5, 24) == (True, 12.5, 24, "")
    assert validate_rainfall("0.0", "48") == (True, 0.0, 48, "")
    assert validate_rainfall(None, None) == (True, None, None, "")

    # Invalid
    assert validate_rainfall(-2.0, 24)[0] is False
    assert validate_rainfall(999.0, 24)[0] is False  # Exceeds max
    assert validate_rainfall(10.0, 0)[0] is False    # Invalid hours
    assert validate_rainfall(10.0, 200)[0] is False  # Exceeds 168 hours
    assert validate_rainfall("abc", 24)[0] is False


def test_validate_irrigation_request_payload():
    """Verify compound irrigation request validation."""
    # Valid payload
    valid_payload = {
        "crop": "Tomato",
        "growth_stage": "Flowering",
        "soil_type": "Sandy",
        "soil_moisture": "28.5",
        "recent_rainfall": "0.0",
        "rainfall_period_hours": "24",
    }
    is_valid, clean_data, errors = validate_irrigation_request(valid_payload)
    assert is_valid is True
    assert clean_data["crop"] == "Tomato"
    assert clean_data["soil_moisture"] == 28.5
    assert len(errors) == 0

    # Invalid payload with unsupported values
    invalid_payload = {
        "crop": "Soybean",
        "growth_stage": "InvalidStage",
        "soil_type": "VolcanicAsh",
        "soil_moisture": "150.0",
        "recent_rainfall": "-10.0",
    }
    is_valid, _, errors = validate_irrigation_request(invalid_payload)
    assert is_valid is False
    assert len(errors) >= 4


def test_security_allowed_file():
    """Verify extension filtering."""
    allowed = {"jpg", "jpeg", "png"}
    assert allowed_file("leaf.jpg", allowed) is True
    assert allowed_file("leaf.JPEG", allowed) is True
    assert allowed_file("leaf.png", allowed) is True
    assert allowed_file("leaf.exe", allowed) is False
    assert allowed_file("leaf.pdf", allowed) is False
    assert allowed_file("no_extension", allowed) is False


def test_security_verify_image_integrity(valid_test_image, corrupt_test_image):
    """Verify deep binary image validation."""
    ok, _ = verify_image_integrity(valid_test_image)
    assert ok is True

    corrupt_ok, err = verify_image_integrity(corrupt_test_image)
    assert corrupt_ok is False
    assert "not a recognized image" in err.lower() or "verification failed" in err.lower()
