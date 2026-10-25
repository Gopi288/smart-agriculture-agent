"""Report generation service for Smart Agriculture Agent.

Produces structured, downloadable decision-support summaries in Markdown/Text
format for field records and academic demonstration.
"""

from datetime import datetime
from typing import Any, Dict, Optional


def generate_disease_report(data: Dict[str, Any]) -> str:
    """Generate a formatted agronomic analysis report for a disease query.

    Args:
        data: Dictionary of analysis and recommendation results.

    Returns:
        Formatted multi-line report string.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 65,
        "   SMART AGRICULTURE AGENT - CROP DISEASE DECISION SUPPORT REPORT",
        "=" * 65,
        f"Generated Timestamp : {now}",
        f"Declared Crop       : {data.get('crop_declared', 'N/A')}",
        f"Predicted Class     : {data.get('predicted_class', 'N/A')}",
        f"Disease Common Name : {data.get('common_name', 'N/A')}",
        f"Pathogen Sourced    : {data.get('pathogen', 'N/A')}",
        f"Model Confidence    : {data.get('confidence_pct', 0.0)}% (Model Confidence Score)",
        f"Conclusive Status   : {'Conclusive' if data.get('is_conclusive') else 'Inconclusive / Review Required'}",
        f"Crop Match Verified : {'Yes' if data.get('crop_matched') else 'MISMATCH DETECTED'}",
        "-" * 65,
        "OBSERVABLE SYMPTOMS:",
    ]

    symptoms = data.get("observable_symptoms", [])
    if symptoms:
        for s in symptoms:
            lines.append(f"  * {s}")
    else:
        lines.append("  (No specific symptoms logged)")

    lines.extend([
        "-" * 65,
        "INTEGRATED PEST MANAGEMENT (IPM) & CULTURAL PRACTICES:",
    ])
    practices = data.get("preventive_practices", [])
    if practices:
        for p in practices:
            lines.append(f"  * {p}")

    sanitation = data.get("sanitation_guidance", [])
    if sanitation:
        lines.append("\nSANITATION GUIDANCE:")
        for s in sanitation:
            lines.append(f"  * {s}")

    lines.extend([
        "-" * 65,
        f"CROP MANAGEMENT ADVICE:\n  {data.get('crop_management_advice', 'N/A')}",
        f"\nRECOMMENDED NEXT ACTION:\n  {data.get('recommended_next_step', 'N/A')}",
        "-" * 65,
        "RULES TRIGGERED:",
    ])

    rules = data.get("rules_triggered", [])
    for r in rules:
        lines.append(f"  [Rule] {r}")

    warnings = data.get("warnings", [])
    if warnings:
        lines.append("\nWARNINGS & ADVISORIES:")
        for w in warnings:
            lines.append(f"  [!] {w}")

    lines.extend([
        "-" * 65,
        f"KNOWLEDGE BASE REFERENCE:\n  Source: {data.get('source_name', 'N/A')}",
        f"  URL:    {data.get('source_url', 'N/A')}",
        f"  Reviewed: {data.get('date_reviewed', 'N/A')}",
        f"  Known Limitations: {data.get('important_limitations', 'N/A')}",
        "=" * 65,
        "DISCLAIMER: This analysis is an AI decision-support recommendation and",
        "does not constitute a laboratory diagnosis. Never apply synthetic chemicals",
        "without accredited agricultural extension verification.",
        "=" * 65,
    ])

    return "\n".join(lines)


def generate_irrigation_report(data: Dict[str, Any]) -> str:
    """Generate a formatted irrigation assessment report.

    Args:
        data: Dictionary of irrigation assessment results.

    Returns:
        Formatted multi-line report string.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = data.get("data_summary", {})

    lines = [
        "=" * 65,
        "   SMART AGRICULTURE AGENT - IRRIGATION ADVISORY REPORT",
        "=" * 65,
        f"Generated Timestamp     : {now}",
        f"Target Crop             : {summary.get('crop', 'N/A')}",
        f"Growth Stage            : {summary.get('growth_stage', 'Unspecified')}",
        f"Soil Texture            : {summary.get('soil_type', 'Unspecified')}",
        f"Soil Moisture Reading   : {summary.get('soil_moisture') if summary.get('soil_moisture') is not None else 'Not Provided'}% ({summary.get('soil_moisture_source', 'N/A')})",
        f"Recent Rainfall         : {summary.get('recent_rainfall') if summary.get('recent_rainfall') is not None else 'Not Provided'} mm in {summary.get('rainfall_period_hours', 24)}h ({summary.get('rainfall_source', 'N/A')})",
        f"Effective MAD Threshold : {data.get('effective_threshold_pct') if data.get('effective_threshold_pct') is not None else 'N/A'}%",
        "-" * 65,
        f"ADVISORY RECOMMENDATION : {data.get('recommendation', 'N/A')}",
        f"ACTION URGENCY          : {data.get('action_urgency', 'N/A')}",
        f"CONFIDENCE LEVEL        : {data.get('confidence_level', 'N/A')}",
        "-" * 65,
        f"AGRONOMIC RATIONALE:\n  {data.get('rationale', 'N/A')}",
        f"\nRECOMMENDED ACTION:\n  {data.get('next_action', 'N/A')}",
        "-" * 65,
        "FACTORS ANALYZED:",
    ]

    factors = data.get("factors_analyzed", [])
    for f in factors:
        lines.append(f"  * {f}")

    notes = data.get("missing_data_notes", [])
    if notes:
        lines.append("\nMISSING / UNMEASURED DATA NOTES:")
        for n in notes:
            lines.append(f"  [i] {n}")

    lines.extend([
        "-" * 65,
        "RULES TRIGGERED:",
    ])
    rules = data.get("rules_triggered", [])
    for r in rules:
        lines.append(f"  [Rule] {r}")

    lines.extend([
        "=" * 65,
        "REFERENCE: FAO Irrigation and Drainage Paper 56 & USDA NRCS",
        "=" * 65,
    ])

    return "\n".join(lines)
