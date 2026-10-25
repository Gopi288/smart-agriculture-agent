"""Script to generate a print-ready A5 technical conference poster PDF.

Uses exact ISO A5 page dimensions (148 x 210 mm) with crisp typography,
structured layout, and actual measured experimental results.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PDF_PATH = Path(__file__).resolve().parent / "POSTER_A5.pdf"


def generate_pdf():
    """Build the print-ready A5 poster."""
    # A5 dimensions: 148mm width x 210mm height
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A5,
        leftMargin=7 * mm,
        rightMargin=7 * mm,
        topMargin=7 * mm,
        bottomMargin=7 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "PosterTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#1b5e20"),
        alignment=1,  # Center
    )

    sub_style = ParagraphStyle(
        "PosterSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#33691e"),
        alignment=1,
    )

    meta_style = ParagraphStyle(
        "PosterMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor("#555555"),
        alignment=1,
    )

    sec_hdr_style = ParagraphStyle(
        "SecHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#1b5e20"),
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6,
        leading=7.5,
        textColor=colors.HexColor("#212529"),
    )

    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6,
        leading=7.5,
        textColor=colors.HexColor("#1b5e20"),
    )

    story = []

    # Title & Subtitle Banner
    story.append(Paragraph("SMART AGRICULTURE AGENT", title_style))
    story.append(Paragraph("AI-Based Crop Disease Detection &amp; Irrigation Advisory System", sub_style))
    story.append(Paragraph("B.Tech Computer Science &amp; Engineering Mini-Capstone Project &bull; Four-Member Team", meta_style))
    story.append(Spacer(1, 2.5 * mm))

    # Grid 1: Problem & Objective
    prob_text = Paragraph(
        "<b>Problem Statement:</b> Foliar diseases and unscientific irrigation reduce global crop yields by 20-40%. Smallholder farmers lack rapid laboratory diagnostics, leading to pesticide over-application and groundwater water waste.",
        body_style,
    )
    obj_text = Paragraph(
        "<b>Project Objective:</b> Deliver an edge-capable agricultural decision-support system coupling deep transfer learning (MobileNetV2) for foliar classification with deterministic FAO MAD irrigation water balance rules.",
        body_style,
    )

    t1 = Table([[prob_text, obj_text]], colWidths=[65 * mm, 69 * mm])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story.append(t1)
    story.append(Spacer(1, 2 * mm))

    # Architecture & AI Technique
    ai_tech = Paragraph(
        "<b>AI Technique (MobileNetV2):</b><br/>"
        "&bull; <b>Inverted Residuals:</b> Depthwise separable convolutions maximize feature representation on CPU.<br/>"
        "&bull; <b>Transfer Learning:</b> ImageNet backbone fine-tuned on PlantVillage (8 classes across Tomato, Potato, Corn).<br/>"
        "&bull; <b>Head:</b> Dense(1280&rarr;128) &rarr; ReLU &rarr; Dropout(0.3) &rarr; Dense(8).<br/>"
        "&bull; <b>Confidence Gating:</b> Threshold (&tau; = 70%) withholds unverified chemical prescriptions.",
        body_style,
    )

    irr_tech = Paragraph(
        "<b>Irrigation Rule Engine (FAO-56):</b><br/>"
        "&bull; <b>MAD Depletion:</b> Tomato (35%), Potato (40%), Corn (30%).<br/>"
        "&bull; <b>Soil Capacity:</b> Sandy (+6% trigger), Clayey (-5% trigger).<br/>"
        "&bull; <b>Precipitation Override:</b> Rain &ge; 12 mm in 24h defers watering to prevent root rot and hypoxia.<br/>"
        "&bull; <b>Data Integrity:</b> Missing sensor values are never assumed zero.",
        body_style,
    )

    t2 = Table([[ai_tech, irr_tech]], colWidths=[67 * mm, 67 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story.append(t2)
    story.append(Spacer(1, 2 * mm))

    # Actual Measured Results Banner
    story.append(Paragraph("ACTUAL MEASURED EXPERIMENTAL RESULTS (Held-Out Test Set)", sec_hdr_style))
    story.append(Spacer(1, 1 * mm))

    res_data = [
        [
            Paragraph("<b>Test Accuracy</b><br/><font size=9 color='#1b5e20'><b>85.19%</b></font>", body_style),
            Paragraph("<b>Macro F1-Score</b><br/><font size=9 color='#1b5e20'><b>0.8333</b></font>", body_style),
            Paragraph("<b>Mean CPU Latency</b><br/><font size=9 color='#1b5e20'><b>25.75 ms</b></font>", body_style),
            Paragraph("<b>Automated Pytest</b><br/><font size=9 color='#1b5e20'><b>31/31 Passed</b></font>", body_style),
        ]
    ]
    t3 = Table(res_data, colWidths=[33.5 * mm, 33.5 * mm, 33.5 * mm, 33.5 * mm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f5e9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#81c784")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#a5d6a7")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
    ]))
    story.append(t3)
    story.append(Spacer(1, 2 * mm))

    # Implementation & Architecture Box
    imp_text = Paragraph(
        "<b>Implementation &amp; Stack:</b> Python 3.12, PyTorch CPU 2.14, Flask 3.1, SQLite, Pillow, Scikit-learn, HTML5/CSS3. Modular blueprints, parameterized SQL queries, and zero hardcoded secrets.",
        body_style,
    )
    story.append(imp_text)
    story.append(Spacer(1, 1.5 * mm))

    # Team Responsibilities & Ethical Guardrails Table
    team_cell = Paragraph(
        "<b>Four-Member Team Distribution:</b><br/>"
        "&bull; <b>Member 1 (AI/Vision):</b> Dataset curation, MobileNetV2 fine-tuning, test evaluation.<br/>"
        "&bull; <b>Member 2 (Decision Engines):</b> Knowledge base, gating rules, FAO irrigation engine.<br/>"
        "&bull; <b>Member 3 (Full-Stack):</b> Flask architecture, responsive UI, database persistence.<br/>"
        "&bull; <b>Member 4 (QA &amp; Mentorship):</b> Pytest suite (31 tests), latency audits, poster/report.",
        body_style,
    )

    ethical_cell = Paragraph(
        "<b>Responsible AI &amp; Limitations:</b><br/>"
        "&bull; <b>Safe Decision Support:</b> Model confidence is explicitly labeled; synthetic chemical spray dosages are strictly withheld.<br/>"
        "&bull; <b>Crop Mismatch Warning:</b> Cross-checks farmer crop vs leaf feature prediction.<br/>"
        "&bull; <b>Limitations:</b> Laboratory images lack field background clutter; soil pathogens require in-person extension ground verification.",
        body_style,
    )

    t4 = Table([[team_cell, ethical_cell]], colWidths=[67 * mm, 67 * mm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#eceff1")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story.append(t4)
    story.append(Spacer(1, 2 * mm))

    # Conclusion & Citations Footer
    footer_text = Paragraph(
        "<b>Conclusion:</b> Successfully demonstrates an explainable, CPU-efficient AI assistance agent with verified 85.2% accuracy and sub-30ms latency.<br/>"
        "<b>References:</b> PlantVillage (Hughes &amp; Salath&eacute;, 2015) &bull; MobileNetV2 (Sandler et al., 2018) &bull; FAO-56 Irrigation &bull; UC IPM Guidelines.",
        body_style,
    )
    story.append(footer_text)

    doc.build(story)
    print(f"[*] Print-ready A5 PDF generated at: {PDF_PATH}")


if __name__ == "__main__":
    generate_pdf()
