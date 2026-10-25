"""Rule-based intelligent irrigation advisor for Smart Agriculture Agent.

Implements transparent agronomic water-balance rules based on Management Allowed
Depletion (MAD), soil texture holding capacity, crop phenological growth stages,
and agrometeorological inputs. Fully testable independently of the disease classifier.
"""

from typing import Any, Dict, List, Optional


class IrrigationDecisionEngine:
    """Agronomic rule engine assessing crop irrigation requirements."""

    # Reference MAD thresholds (% volumetric or available depletion threshold)
    # Sourced from FAO Irrigation and Drainage Paper 56 and USDA NRCS National Engineering Handbook
    BASE_DEPLETION_THRESHOLDS: Dict[str, float] = {
        "Tomato": 35.0,  # Below 35% soil moisture, tomato enters water stress
        "Potato": 40.0,  # Potato has shallow root system (30-50 cm), sensitive below 40%
        "Corn": 30.0,    # Corn has extensive root zone (1-1.2 m), tolerates down to 30%
        "Pepper": 35.0,  # Bell pepper sensitive to moisture swings
        "Rice": 50.0,    # Semi-aquatic crop with high moisture demand
        "Wheat": 35.0,   # Moderate root zone depth
        "Cotton": 35.0,  # Deep taproot fiber crop
        "Chilli": 35.0,  # Solanaceous spice
        "Brinjal": 38.0, # Continuous fruiting vegetable
        "Groundnut": 32.0, # Geocarpic pod formation
        "Soybean": 35.0, # Flowering and pod filling
        "Sugarcane": 45.0, # Massive biomass and water demand
        "Banana": 45.0,  # Shallow roots with large leaf transpiration
        "Mango": 30.0,   # Deep root system
        "Grapes": 32.0,  # Managed deficit irrigation
        "Apple": 35.0,   # Orchard pome fruit
        "Citrus": 35.0,  # Evergreen tree
        "Cucumber": 40.0, # High fruit water content
        "Onion": 42.0,   # Extremely shallow 25-30 cm root zone
        "Chickpea": 28.0, # Drought-hardy pulse
        "Pigeon Pea": 28.0, # Deep taproot
        "Okra": 35.0,    # Continuous harvest
        "Mustard": 30.0, # Winter oilseed
        "Sunflower": 32.0, # Deep taproot composite
    }

    # Growth stage sensitivity adjustments to threshold
    STAGE_ADJUSTMENTS: Dict[str, float] = {
        "Seedling": 5.0,    # Young roots require higher moisture availability
        "Vegetative": 0.0,  # Standard baseline
        "Flowering": 8.0,   # Peak reproductive sensitivity (pollination/silking/flowering)
        "Fruiting": 6.0,    # High water demand for fruit expansion / tuber bulking
        "Mature": -5.0,     # Pre-harvest drying beneficial; lower sensitivity
    }

    # Soil texture drainage and water retention adjustments
    SOIL_ADJUSTMENTS: Dict[str, float] = {
        "Sandy": 6.0,     # Low water holding capacity; drains rapidly, higher threshold
        "Loamy": 0.0,     # Ideal loam baseline
        "Silt": -2.0,     # Good moisture retention
        "Clayey": -5.0,   # High retention; slow infiltration, lower threshold to prevent rot
        "Peaty": -2.0,    # High organic matter water retention
    }

    def assess_irrigation(
        self,
        crop: str,
        growth_stage: Optional[str] = None,
        soil_type: Optional[str] = None,
        soil_moisture: Optional[float] = None,
        soil_moisture_source: str = "Not Provided",
        recent_rainfall: Optional[float] = None,
        rainfall_period_hours: Optional[int] = 24,
        rainfall_source: str = "Not Provided",
        weather_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Assess irrigation requirement based on verified agronomic rules.

        Args:
            crop: Declared crop name ('Tomato', 'Potato', 'Corn').
            growth_stage: Crop phenological stage ('Seedling', 'Flowering', etc.).
            soil_type: Soil texture category ('Sandy', 'Loamy', 'Clayey', etc.).
            soil_moisture: Measured soil moisture percentage (0.0 to 100.0).
            soil_moisture_source: Data origin label.
            recent_rainfall: Cumulative rainfall in mm.
            rainfall_period_hours: Measurement timeframe (e.g. 24 or 48 hours).
            rainfall_source: Rainfall data origin label.
            weather_data: Agrometeorological dictionary from WeatherService.

        Returns:
            Dictionary containing recommendation, action urgency, rationale, rules triggered.
        """
        rules_triggered: List[str] = []
        factors_analyzed: List[str] = []
        missing_data_notes: List[str] = []

        # Standardize crop name
        crop_clean = crop.title() if crop else "Tomato"
        base_threshold = self.BASE_DEPLETION_THRESHOLDS.get(crop_clean, 35.0)

        # -------------------------------------------------------------
        # 1. Check for Missing Critical Data
        # -------------------------------------------------------------
        if soil_moisture is None and recent_rainfall is None:
            missing_data_notes.append(
                "Neither measured soil moisture (%) nor recent rainfall (mm) was provided."
            )
            rules_triggered.append(
                "RULE_INSUFFICIENT_DATA: Missing both primary soil sensor reading and precipitation records. "
                "Advisory withheld to prevent detrimental over- or under-watering."
            )
            return {
                "recommendation": "Insufficient data to recommend irrigation.",
                "action_urgency": "Data Required",
                "confidence_level": "Low (Uninformed)",
                "effective_threshold_pct": None,
                "rationale": (
                    "To generate a responsible irrigation advisory, the system requires either a current "
                    "soil moisture measurement or recent precipitation data. Operating without either "
                    "creates significant risk of crop stress or soil waterlogging."
                ),
                "next_action": (
                    "Measure soil moisture using a tensiometer, capacitive sensor, or the USDA Soil Feel "
                    "and Appearance method, then re-evaluate."
                ),
                "rules_triggered": rules_triggered,
                "factors_analyzed": ["Absence of soil moisture reading", "Absence of precipitation reading"],
                "missing_data_notes": missing_data_notes,
                "data_summary": {
                    "crop": crop_clean,
                    "growth_stage": growth_stage or "Unspecified",
                    "soil_type": soil_type or "Unspecified",
                    "soil_moisture": None,
                    "soil_moisture_source": soil_moisture_source,
                    "recent_rainfall": None,
                    "rainfall_period_hours": rainfall_period_hours,
                    "rainfall_source": rainfall_source,
                    "weather_available": weather_data.get("is_available", False) if weather_data else False,
                },
            }

        # -------------------------------------------------------------
        # 2. Calculate Effective Moisture Threshold
        # -------------------------------------------------------------
        stage_adj = self.STAGE_ADJUSTMENTS.get(growth_stage, 0.0) if growth_stage else 0.0
        soil_adj = self.SOIL_ADJUSTMENTS.get(soil_type, 0.0) if soil_type else 0.0
        effective_threshold = round(base_threshold + stage_adj + soil_adj, 1)

        factors_analyzed.append(
            f"Base {crop_clean} MAD threshold: {base_threshold}%"
        )
        if growth_stage:
            factors_analyzed.append(
                f"Growth stage '{growth_stage}' adjustment: {stage_adj:+.1f}%"
            )
        else:
            missing_data_notes.append("Growth stage omitted; using baseline vegetative threshold.")

        if soil_type:
            factors_analyzed.append(
                f"Soil texture '{soil_type}' adjustment: {soil_adj:+.1f}%"
            )
        else:
            missing_data_notes.append("Soil type omitted; using standard medium-loam assumption.")

        # -------------------------------------------------------------
        # 3. Weather & Atmospheric Demand Factors
        # -------------------------------------------------------------
        temp_c: Optional[float] = None
        humidity_pct: Optional[float] = None
        weather_active = False

        if weather_data and weather_data.get("is_available"):
            weather_active = True
            temp_c = weather_data.get("temperature_c")
            humidity_pct = weather_data.get("humidity_pct")

            if temp_c is not None and temp_c >= 32.0:
                effective_threshold += 3.0
                factors_analyzed.append(
                    f"High ambient temperature ({temp_c}°C) elevates evapotranspiration (+3.0% threshold)."
                )
            if humidity_pct is not None and humidity_pct >= 80.0:
                effective_threshold -= 2.0
                factors_analyzed.append(
                    f"High relative humidity ({humidity_pct}%) suppresses vapor pressure deficit (-2.0% threshold)."
                )
        else:
            missing_data_notes.append("Live agrometeorological weather feed is offline or unconfigured.")

        # -------------------------------------------------------------
        # 4. Precipitation Override Rule
        # -------------------------------------------------------------
        if recent_rainfall is not None and recent_rainfall >= 12.0:
            rules_triggered.append(
                f"RULE_RECENT_RAINFALL_OVERRIDE: Significant rainfall of {recent_rainfall} mm recorded in the "
                f"last {rainfall_period_hours} hours. Soil moisture replenishment in progress."
            )

            # If soil moisture is measured and critically depleted despite rain, advise reassessment
            if soil_moisture is not None and soil_moisture < (effective_threshold - 10.0):
                return {
                    "recommendation": "Reassess after monitoring soil conditions.",
                    "action_urgency": "Monitor Moisture",
                    "confidence_level": "Medium (Rainfall Recorded, Soil Still Dry)",
                    "effective_threshold_pct": effective_threshold,
                    "rationale": (
                        f"Recent rainfall of {recent_rainfall} mm was recorded, but measured root-zone moisture "
                        f"({soil_moisture}%) remains below the target ({effective_threshold}%). Precipitation "
                        "may have run off without fully penetrating the root zone."
                    ),
                    "next_action": (
                        "Allow 6-12 hours for gravitational percolation, then re-check moisture at root depth "
                        "(15-30 cm) before applying supplemental irrigation."
                    ),
                    "rules_triggered": rules_triggered,
                    "factors_analyzed": factors_analyzed,
                    "missing_data_notes": missing_data_notes,
                    "data_summary": self._build_data_summary(
                        crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                        recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
                    ),
                }

            return {
                "recommendation": "Irrigation may not be needed yet.",
                "action_urgency": "Defer Irrigation",
                "confidence_level": "High (Precipitation Confirmed)",
                "effective_threshold_pct": effective_threshold,
                "rationale": (
                    f"Recent precipitation ({recent_rainfall} mm over {rainfall_period_hours}h) satisfies current "
                    f"crop evapotranspiration demand for {crop_clean}. Applying additional water risks root hypoxia "
                    "and creates microclimates favorable to foliar fungal pathogens."
                ),
                "next_action": "Withhold irrigation; monitor soil drying over the next 48 to 72 hours.",
                "rules_triggered": rules_triggered,
                "factors_analyzed": factors_analyzed,
                "missing_data_notes": missing_data_notes,
                "data_summary": self._build_data_summary(
                    crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                    recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
                ),
            }

        # -------------------------------------------------------------
        # 5. Soil Moisture Rule Evaluation
        # -------------------------------------------------------------
        if soil_moisture is not None:
            factors_analyzed.append(
                f"Measured soil moisture: {soil_moisture}% vs Effective threshold: {effective_threshold}%"
            )

            # Case A: Deficit below threshold -> Irrigation Needed
            if soil_moisture <= effective_threshold:
                deficit = round(effective_threshold - soil_moisture, 1)
                urgency = "High" if growth_stage in {"Flowering", "Fruiting"} else "Moderate"

                rules_triggered.append(
                    f"RULE_MOISTURE_DEFICIT: Available soil moisture ({soil_moisture}%) has breached the "
                    f"calculated Management Allowed Depletion threshold ({effective_threshold}%)."
                )

                return {
                    "recommendation": "Irrigation may be needed.",
                    "action_urgency": urgency,
                    "confidence_level": "High (Measured Soil Sensor)",
                    "effective_threshold_pct": effective_threshold,
                    "rationale": (
                        f"Soil moisture reading of {soil_moisture}% is {deficit}% below the calculated management "
                        f"threshold ({effective_threshold}%) for {crop_clean} in the {growth_stage or 'vegetative'} "
                        f"stage. Continued deficit risks stomatal closure, reduced photosynthesis, and yield reduction."
                    ),
                    "next_action": (
                        f"Apply root-zone irrigation (preferably drip or furrow) early in the morning to restore "
                        f"available water capacity to field capacity while keeping foliage dry."
                    ),
                    "rules_triggered": rules_triggered,
                    "factors_analyzed": factors_analyzed,
                    "missing_data_notes": missing_data_notes,
                    "data_summary": self._build_data_summary(
                        crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                        recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
                    ),
                }

            # Case B: Buffer Zone -> Reassess / Monitor
            elif soil_moisture < (effective_threshold + 12.0):
                rules_triggered.append(
                    f"RULE_BUFFER_ZONE: Soil moisture ({soil_moisture}%) is above depletion ({effective_threshold}%) "
                    f"but approaching trigger margin."
                )

                return {
                    "recommendation": "Reassess after monitoring soil conditions.",
                    "action_urgency": "Monitor Closely",
                    "confidence_level": "High (Measured Soil Sensor)",
                    "effective_threshold_pct": effective_threshold,
                    "rationale": (
                        f"Current soil moisture ({soil_moisture}%) remains within the safe reserve range above "
                        f"the depletion threshold ({effective_threshold}%). Irrigation is not yet necessary but "
                        f"reserves will decline over the next 24-48 hours depending on weather."
                    ),
                    "next_action": "Recheck moisture in 24 hours; prepare irrigation infrastructure.",
                    "rules_triggered": rules_triggered,
                    "factors_analyzed": factors_analyzed,
                    "missing_data_notes": missing_data_notes,
                    "data_summary": self._build_data_summary(
                        crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                        recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
                    ),
                }

            # Case C: Ample Moisture -> Not Needed Yet
            else:
                rules_triggered.append(
                    f"RULE_SUFFICIENT_MOISTURE: Soil moisture ({soil_moisture}%) substantially exceeds depletion "
                    f"threshold ({effective_threshold}%)."
                )

                return {
                    "recommendation": "Irrigation may not be needed yet.",
                    "action_urgency": "Adequate Moisture",
                    "confidence_level": "High (Measured Soil Sensor)",
                    "effective_threshold_pct": effective_threshold,
                    "rationale": (
                        f"Current soil moisture ({soil_moisture}%) provides ample plant-available water above the "
                        f"threshold ({effective_threshold}%). Additional watering is unwarranted and would waste water "
                        f"or risk root zone leaching."
                    ),
                    "next_action": "Maintain routine crop monitoring; no irrigation needed at this time.",
                    "rules_triggered": rules_triggered,
                    "factors_analyzed": factors_analyzed,
                    "missing_data_notes": missing_data_notes,
                    "data_summary": self._build_data_summary(
                        crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                        recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
                    ),
                }

        # -------------------------------------------------------------
        # 6. Fallback: Rainfall Only Available
        # -------------------------------------------------------------
        rules_triggered.append(
            f"RULE_RAINFALL_ONLY: Evaluating based on recent rainfall of {recent_rainfall} mm without soil moisture sensor."
        )
        return {
            "recommendation": "Reassess after monitoring soil conditions.",
            "action_urgency": "Check Soil Manually",
            "confidence_level": "Medium (Precipitation Only)",
            "effective_threshold_pct": effective_threshold,
            "rationale": (
                f"Recent rainfall was recorded ({recent_rainfall} mm), but without a soil moisture sensor, "
                f"the actual retention in your specific '{soil_type or 'unspecified'}' soil profile cannot be verified."
            ),
            "next_action": "Conduct a manual soil feel test at 15 cm depth before activating irrigation pumps.",
            "rules_triggered": rules_triggered,
            "factors_analyzed": factors_analyzed,
            "missing_data_notes": missing_data_notes,
            "data_summary": self._build_data_summary(
                crop_clean, growth_stage, soil_type, soil_moisture, soil_moisture_source,
                recent_rainfall, rainfall_period_hours, rainfall_source, weather_active, temp_c, humidity_pct
            ),
        }

    def _build_data_summary(
        self,
        crop: str,
        growth_stage: Optional[str],
        soil_type: Optional[str],
        soil_moisture: Optional[float],
        soil_moisture_source: str,
        recent_rainfall: Optional[float],
        rainfall_period_hours: Optional[int],
        rainfall_source: str,
        weather_active: bool,
        temp_c: Optional[float],
        humidity_pct: Optional[float],
    ) -> Dict[str, Any]:
        """Helper to format input status summary."""
        return {
            "crop": crop,
            "growth_stage": growth_stage or "Unspecified (Defaulted)",
            "soil_type": soil_type or "Unspecified (Defaulted)",
            "soil_moisture": soil_moisture,
            "soil_moisture_source": soil_moisture_source,
            "recent_rainfall": recent_rainfall,
            "rainfall_period_hours": rainfall_period_hours,
            "rainfall_source": rainfall_source,
            "weather_available": weather_active,
            "temperature_c": temp_c,
            "humidity_pct": humidity_pct,
        }
