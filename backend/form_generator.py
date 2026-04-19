from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io

GSPCB_GREEN = colors.HexColor("#1a6b3c")
GSPCB_LIGHT = colors.HexColor("#e8f5ee")
GSPCB_ORANGE = colors.HexColor("#e65c00")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY = colors.HexColor("#cccccc")

def generate_form_a(fusion_result, sarpanch_name="", village_name="", gram_panchayat=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Header styles
    header_style = ParagraphStyle("header", fontSize=13, fontName="Helvetica-Bold",
                                   textColor=GSPCB_GREEN, alignment=TA_CENTER, spaceAfter=2)
    sub_header = ParagraphStyle("subheader", fontSize=10, fontName="Helvetica",
                                 textColor=colors.HexColor("#444444"), alignment=TA_CENTER, spaceAfter=4)
    section_title = ParagraphStyle("section", fontSize=10, fontName="Helvetica-Bold",
                                    textColor=GSPCB_GREEN, spaceBefore=6, spaceAfter=3)
    normal = ParagraphStyle("normal", fontSize=9, fontName="Helvetica", spaceAfter=2)
    bold_val = ParagraphStyle("boldval", fontSize=9, fontName="Helvetica-Bold", spaceAfter=2)
    alert_style = ParagraphStyle("alert", fontSize=10, fontName="Helvetica-Bold",
                                  textColor=GSPCB_ORANGE, alignment=TA_CENTER)
    small = ParagraphStyle("small", fontSize=8, fontName="Helvetica",
                            textColor=colors.HexColor("#666666"), spaceAfter=2)

    # ─── LOGO / HEADER ───
    story.append(Paragraph("GUJARAT POLLUTION CONTROL BOARD (GSPCB)", header_style))
    story.append(Paragraph("Paryavaran Bhavan, Sector-10A, Gandhinagar – 382 010", sub_header))
    story.append(HRFlowable(width="100%", thickness=2, color=GSPCB_GREEN))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("FORM – A", ParagraphStyle("formtitle", fontSize=14, fontName="Helvetica-Bold",
                                                         alignment=TA_CENTER, textColor=GSPCB_GREEN)))
    story.append(Paragraph("Complaint of Air / Water / Noise Pollution", sub_header))
    story.append(Paragraph("[Under the Environment (Protection) Act, 1986 & Air (Prevention and Control of Pollution) Act, 1981]",
                            ParagraphStyle("act", fontSize=7.5, fontName="Helvetica", alignment=TA_CENTER,
                                           textColor=colors.HexColor("#555555"))))
    story.append(Spacer(1, 4*mm))

    # ─── AUTO-GENERATED NOTICE ───
    ts = fusion_result.get("timestamp", datetime.now().isoformat())
    try:
        dt = datetime.fromisoformat(ts)
        display_dt = dt.strftime("%d %B %Y, %I:%M %p")
        display_date = dt.strftime("%d/%m/%Y")
        display_time = dt.strftime("%I:%M %p")
    except:
        display_dt = ts
        display_date = datetime.now().strftime("%d/%m/%Y")
        display_time = datetime.now().strftime("%I:%M %p")

    auto_table = Table([[
        Paragraph("⚡ AUTO-GENERATED via TS-09 Hyperlocal Pollution Evidence Engine", alert_style),
        Paragraph(f"Generated: {display_dt}", ParagraphStyle("ts", fontSize=8, fontName="Helvetica",
                                                               alignment=TA_RIGHT, textColor=colors.HexColor("#888")))
    ]], colWidths=[130*mm, 50*mm])
    auto_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fff8f0")),
        ("BOX", (0,0), (-1,-1), 0.5, GSPCB_ORANGE),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(auto_table)
    story.append(Spacer(1, 4*mm))

    def section_header(text):
        story.append(Table([[Paragraph(text, ParagraphStyle("sh", fontSize=9, fontName="Helvetica-Bold",
                                                              textColor=colors.white))]],
                           colWidths=[174*mm]))
        story[-1].setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), GSPCB_GREEN),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(Spacer(1, 1*mm))

    def field_row(label, value, highlight=False):
        bg = colors.HexColor("#fff3e0") if highlight else colors.white
        t = Table([
            [Paragraph(label, ParagraphStyle("lbl", fontSize=8.5, fontName="Helvetica-Bold", textColor=colors.HexColor("#333"))),
             Paragraph(str(value), ParagraphStyle("val", fontSize=8.5, fontName="Helvetica", textColor=colors.HexColor("#111")))]
        ], colWidths=[65*mm, 109*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("BOX", (0,0), (-1,-1), 0.3, MID_GRAY),
            ("LINEAFTER", (0,0), (0,-1), 0.5, MID_GRAY),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*mm))

    # ─── PART A: COMPLAINANT DETAILS ───
    section_header("PART A — COMPLAINANT DETAILS")
    field_row("Name of Sarpanch / Complainant:", sarpanch_name or "[To be filled by Sarpanch]")
    field_row("Village (Gram Panchayat):", gram_panchayat or village_name or fusion_result.get("village", ""))
    field_row("Taluka / District:", "Vapi / Valsad" if "Vapi" in fusion_result.get("village","") else
                                    "Ankleshwar / Bharuch" if "Ankleshwar" in fusion_result.get("village","") else
                                    "Vatva / Ahmedabad")
    field_row("Date of Complaint:", display_date)
    field_row("Time of Incident:", display_time)
    field_row("Mobile Number:", "[Complainant to fill]")
    story.append(Spacer(1, 3*mm))

    # ─── PART B: POLLUTION EVENT ───
    section_header("PART B — POLLUTION EVENT DETAILS (Auto-filled from Sensor Data)")

    pm25 = fusion_result.get("pm25", 0)
    so2 = fusion_result.get("so2", 0)
    alert_level = fusion_result.get("alert_level", "NORMAL")
    source_type = fusion_result.get("source_type", {})
    top_source = fusion_result.get("top_probable_source", {})

    field_row("Nature of Complaint:", "Air Pollution — Abnormal emission surge detected by hyperlocal sensor network")
    field_row("PM2.5 Concentration:", f"{pm25} µg/m³   (CPCB 24-hr Standard: 60 µg/m³  |  Deviation: +{round(max(0,pm25-60),1)} µg/m³)", highlight=pm25>60)
    field_row("SO2 Concentration:", f"{so2} µg/m³   (CPCB 24-hr Standard: 80 µg/m³  |  Deviation: +{round(max(0,so2-80),1)} µg/m³)", highlight=so2>80)
    field_row("Alert Level:", f"⚠ {alert_level}", highlight=(alert_level!="NORMAL"))
    field_row("AQI (at time of event):", f"{fusion_result.get('aqi', 'N/A')} — {fusion_result.get('aqi_label', '')}" if fusion_result.get('aqi') else "See sensor log")
    field_row("Probable Source Type:", f"{source_type.get('type','N/A')} (Confidence: {source_type.get('confidence','N/A')})")
    field_row("Classification Reason:", source_type.get("reason", "N/A"))
    story.append(Spacer(1, 3*mm))

    # ─── PART C: SOURCE DIRECTION ───
    section_header("PART C — PROBABLE SOURCE DIRECTION (Wind Vector Analysis)")

    wind_dir = fusion_result.get("wind_direction_deg", "N/A")
    wind_from = fusion_result.get("wind_from", "N/A")
    source_dir = fusion_result.get("source_direction", "N/A")
    source_bearing = fusion_result.get("source_bearing", "N/A")

    field_row("Wind Direction (measured):", f"{wind_dir}° — Wind blowing FROM {wind_from}")
    field_row("Probable Emission Source Direction:", f"{source_bearing}° ({source_dir}) — upwind of sensor network", highlight=True)
    field_row("Wind Speed at Detection:", f"{fusion_result.get('wind_speed', 'N/A')} km/h" if fusion_result.get('wind_speed') else "See sensor log")
    story.append(Spacer(1, 3*mm))

    # ─── PART D: PROBABLE INDUSTRY ───
    section_header("PART D — PROBABLE POLLUTING INDUSTRY / SOURCE UNIT")

    if top_source:
        field_row("Name of Probable Source:", top_source.get("name", "N/A"), highlight=True)
        field_row("Location of Industry:", top_source.get("location", "N/A"))
        field_row("Industry Type:", top_source.get("type", "N/A"))
        field_row("Known Pollutants:", ", ".join(top_source.get("pollutants", [])))
        field_row("Shift Active at Detection:", "YES — Industry was in active shift" if top_source.get("is_active") else "NO — Outside normal operating hours")
        field_row("Distance from Village:", f"{top_source.get('distance_km', 'N/A')} km")
        field_row("Direction from Village:", f"{top_source.get('direction_from_village_deg', 'N/A')}° ({fusion_result.get('source_direction','N/A')})")
        field_row("Source Match Confidence Score:", f"{top_source.get('match_score', 'N/A')} / 155")
    else:
        field_row("Probable Source:", "No registered GIDC unit matched the upwind direction at this time. Manual investigation required.")

    story.append(Spacer(1, 3*mm))

    # ─── PART E: SENSOR EVIDENCE ───
    section_header("PART E — SENSOR NODE EVIDENCE LOG")

    node_id = fusion_result.get("node_id", "Multiple Nodes")
    coords = f"{fusion_result.get('lat','N/A')}, {fusion_result.get('lng','N/A')}" if fusion_result.get('lat') else "See network log"

    field_row("Sensor Node ID:", node_id)
    field_row("GPS Coordinates (Sensor):", coords)
    field_row("Timestamp (IST):", display_dt)
    field_row("Data Collection Method:", "Continuous Ambient Air Quality Monitoring — Simulated IoT Sensor Network (TS-09)")
    field_row("Corroborating Nodes:", f"{len(fusion_result.get('probable_industries', []))} sensor nodes in network concurred")
    story.append(Spacer(1, 3*mm))

    # ─── PART F: DECLARATION ───
    section_header("PART F — DECLARATION BY COMPLAINANT")
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "I hereby declare that the above information is true and correct to the best of my knowledge. "
        "I request the Gujarat Pollution Control Board to take necessary action against the probable polluting unit "
        "and conduct an independent on-site inspection to verify the above findings.",
        ParagraphStyle("decl", fontSize=8.5, fontName="Helvetica", leading=13)))
    story.append(Spacer(1, 8*mm))

    sig_table = Table([
        [Paragraph("Signature of Complainant / Sarpanch", small),
         Paragraph("Seal of Gram Panchayat", small),
         Paragraph("Date: " + display_date, small)],
        [Paragraph("_______________________", normal),
         Paragraph("_______________________", normal),
         Paragraph("_______________________", normal)],
    ], colWidths=[58*mm, 58*mm, 58*mm])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 2),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 4*mm))

    # ─── FOOTER ───
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "This document was auto-generated by the TS-09 Hyperlocal Pollution Evidence Engine. "
        "Sensor data is simulated for demonstration. For official complaints, verify readings with calibrated instruments. "
        "Submit to: Regional Officer, GSPCB — or email: ro-vapi@gpcb.gov.in",
        ParagraphStyle("footer", fontSize=7, fontName="Helvetica", textColor=colors.HexColor("#888888"), alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    # Test generation
    test_result = {
        "village": "Vapi", "timestamp": datetime.now().isoformat(),
        "pm25": 187.4, "so2": 62.1, "wind_direction_deg": 112, "wind_speed": 11.2,
        "wind_from": "ESE", "source_bearing": 292, "source_direction": "WNW",
        "aqi": 340, "aqi_label": "Very Poor", "alert_level": "HIGH",
        "node_id": "VPI-N02", "lat": 20.3893, "lng": 72.9106,
        "source_type": {"type": "Industrial", "confidence": "HIGH",
                        "reason": "SO2 and PM2.5 both elevated — typical of chemical factory emissions"},
        "top_probable_source": {
            "name": "Aarti Industries Ltd", "location": "Vapi GIDC Phase-1",
            "type": "Chemical", "pollutants": ["SO2","PM2.5","NOx"],
            "is_active": True, "distance_km": 1.4,
            "direction_from_village_deg": 285, "match_score": 132.5
        },
        "probable_industries": [{}]
    }
    buf = generate_form_a(test_result, "Rameshbhai Patel", "Vapi", "Vapi Gram Panchayat")
    with open("/tmp/test_form_a.pdf", "wb") as f:
        f.write(buf.read())
    print("PDF generated: /tmp/test_form_a.pdf")
