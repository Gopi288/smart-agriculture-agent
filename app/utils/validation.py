"""Input validation module for Smart Agriculture Agent.

Validates crop types, numeric sensor and weather readings, soil types,
growth stages, and text inputs with explicit missing-data handling.
"""

from typing import Any, Dict, List, Optional, Tuple
from app.utils.crop_registry import get_all_crop_names, get_ai_supported_crop_names

SUPPORTED_CROPS = ["Tomato", "Potato", "Corn"]
ALL_CROPS = get_all_crop_names()
SUPPORTED_GROWTH_STAGES = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Mature"]
SUPPORTED_SOIL_TYPES = ["Sandy", "Loamy", "Clayey", "Silt", "Peaty"]


def validate_crop_input(
    crop: Optional[str], allowed_crops: Optional[List[str]] = None
) -> Tuple[bool, Optional[str], str]:
    """Validate declared crop type.

    Args:
        crop: Farmer-selected crop string.
        allowed_crops: Optional list of acceptable crops. Defaults to SUPPORTED_CROPS (AI foliar models).

    Returns:
        Tuple of (is_valid: bool, normalized_crop: Optional[str], error_message: str).
    """
    if allowed_crops is None:
        allowed_crops = SUPPORTED_CROPS

    if not crop or not str(crop).strip():
        return False, None, "Crop selection is required. Please choose from supported crops."

    clean_crop = str(crop).strip()
    for supported in allowed_crops:
        if clean_crop.lower() == supported.lower():
            return True, supported, ""

    return (
        False,
        None,
        f"Unsupported crop: '{clean_crop}'. Currently supported crops: {', '.join(allowed_crops)}.",
    )


def validate_soil_moisture(value: Any) -> Tuple[bool, Optional[float], str]:
    """Validate optional soil moisture percentage.

    Explicitly rejects missing or empty as None (NOT zero).
    If present, enforces 0.0 <= moisture <= 100.0 %.

    Args:
        value: Input value (str, int, float, or None).

    Returns:
        Tuple of (is_valid: bool, parsed_value: Optional[float], error_message: str).
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return True, None, ""  # Optional, validly omitted

    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return False, None, f"Soil moisture must be a numeric percentage (received '{value}')."

    if val_float < 0.0 or val_float > 100.0:
        return (
            False,
            None,
            f"Soil moisture must be between 0.0% and 100.0% (received {val_float}%).",
        )

    return True, round(val_float, 2), ""


def validate_rainfall(
    rainfall_val: Any, period_hours_val: Any = 24
) -> Tuple[bool, Optional[float], Optional[int], str]:
    """Validate optional rainfall measurement and time window.

    Args:
        rainfall_val: Rainfall amount in mm.
        period_hours_val: Measurement window in hours (default: 24).

    Returns:
        Tuple of (is_valid: bool, rainfall_mm: Optional[float], hours: Optional[int], error_msg: str).
    """
    if rainfall_val is None or (isinstance(rainfall_val, str) and not rainfall_val.strip()):
        return True, None, None, ""  # Optional, validly omitted

    try:
        rain_float = float(rainfall_val)
    except (ValueError, TypeError):
        return False, None, None, f"Rainfall amount must be a numeric value in mm (received '{rainfall_val}')."

    if rain_float < 0.0:
        return False, None, None, f"Rainfall amount cannot be negative (received {rain_float} mm)."
    if rain_float > 500.0:
        return False, None, None, f"Rainfall amount exceeds realistic threshold ({rain_float} mm > 500 mm)."

    hours_int = 24
    if period_hours_val is not None and str(period_hours_val).strip():
        try:
            hours_int = int(period_hours_val)
            if hours_int <= 0 or hours_int > 168:
                return False, None, None, f"Rainfall period must be between 1 and 168 hours (received {hours_int})."
        except (ValueError, TypeError):
            return False, None, None, "Rainfall period must be an integer number of hours."

    return True, round(rain_float, 2), hours_int, ""


def validate_irrigation_request(form_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Validate complete irrigation request payload.

    Args:
        form_data: Dictionary of form parameters.

    Returns:
        Tuple of (is_valid: bool, clean_data: Dict[str, Any], errors: List[str]).
    """
    errors: List[str] = []
    clean_data: Dict[str, Any] = {}

    # Crop (supports all 24 registry crops for irrigation)
    crop_ok, crop_val, crop_err = validate_crop_input(
        form_data.get("crop"), allowed_crops=ALL_CROPS
    )
    if not crop_ok:
        errors.append(crop_err)
    else:
        clean_data["crop"] = crop_val

    # Soil moisture
    sm_ok, sm_val, sm_err = validate_soil_moisture(form_data.get("soil_moisture"))
    if not sm_ok:
        errors.append(sm_err)
    else:
        clean_data["soil_moisture"] = sm_val
        clean_data["soil_moisture_source"] = (
            "Farmer Reading (Manual)" if sm_val is not None else "Not Provided"
        )

    # Rainfall
    rf_ok, rf_val, rf_hours, rf_err = validate_rainfall(
        form_data.get("recent_rainfall"), form_data.get("rainfall_period_hours", 24)
    )
    if not rf_ok:
        errors.append(rf_err)
    else:
        clean_data["recent_rainfall"] = rf_val
        clean_data["rainfall_period_hours"] = rf_hours
        clean_data["rainfall_source"] = (
            f"Farmer Entry ({rf_hours}h)" if rf_val is not None else "Not Provided"
        )

    # Growth stage
    stage_raw = form_data.get("growth_stage")
    if stage_raw and str(stage_raw).strip():
        clean_stage = str(stage_raw).strip()
        matched_stage = next(
            (s for s in SUPPORTED_GROWTH_STAGES if s.lower() == clean_stage.lower()), None
        )
        if matched_stage:
            clean_data["growth_stage"] = matched_stage
        else:
            errors.append(
                f"Unsupported growth stage: '{clean_stage}'. Options: {', '.join(SUPPORTED_GROWTH_STAGES)}."
            )
    else:
        clean_data["growth_stage"] = None

    # Soil type
    soil_raw = form_data.get("soil_type")
    if soil_raw and str(soil_raw).strip():
        clean_soil = str(soil_raw).strip()
        matched_soil = next(
            (s for s in SUPPORTED_SOIL_TYPES if s.lower() == clean_soil.lower()), None
        )
        if matched_soil:
            clean_data["soil_type"] = matched_soil
        else:
            errors.append(
                f"Unsupported soil type: '{clean_soil}'. Options: {', '.join(SUPPORTED_SOIL_TYPES)}."
            )
    else:
        clean_data["soil_type"] = None

    # Location
    location_raw = form_data.get("location")
    clean_data["location"] = str(location_raw).strip()[:100] if location_raw else None

    return (len(errors) == 0), clean_data, errors
