"""
Rule-based AI chat service for farmer queries.
Phase 3: Replace generate_response() with Claude API / LLaMA call.
"""

import re
from data.mock_data import LATEST_DETECTION
from services.disease_service import DISEASE_INFO, SEVERITY_CONFIG, get_disease_info


def _match(pattern: str, text: str) -> bool:
    """Case-insensitive regex match helper."""
    return bool(re.search(pattern, text, re.IGNORECASE))


def generate_response(user_message: str) -> tuple[str, str]:
    """
    Generate a bot response and context label for a given user message.
    Returns: (response_text, context_used)
    """
    msg = user_message.strip()
    det = LATEST_DETECTION
    disease_class = det.detection_result.disease_class
    info = get_disease_info(disease_class)
    severity = det.detection_result.severity_class
    sev_cfg = SEVERITY_CONFIG.get(severity, SEVERITY_CONFIG["healthy"])
    display_name = info["display_name"]
    confidence = round(det.detection_result.confidence * 100)
    env = det.environmental_data
    loc = det.rover_location

    # ── Greetings ─────────────────────────────────────────────────────────────
    if _match(r"^(hi|hello|hey|namaste|vanakkam|hai)", msg):
        return (
            f"🌿 Hello, farmer! I'm your AgriRover assistant.\n\n"
            f"I'm monitoring your bitter gourd pandal farm right now.\n"
            f"Latest scan detected **{display_name}** in **Row {loc.row}, Section {loc.section}**.\n\n"
            f"What would you like to know?",
            "greeting",
        )

    # ── Disease name ──────────────────────────────────────────────────────────
    if _match(r"what disease|which disease|kya bimari|enna noi|disease name|what is wrong|what happened", msg):
        return (
            f"🔍 **Disease Detected: {display_name}**\n"
            f"*Scientific name: {info['scientific_name']}*\n\n"
            f"{info['description']}\n\n"
            f"AI Confidence: **{confidence}%** — this is a very reliable detection.",
            "latest_detection",
        )

    # ── Severity / seriousness ────────────────────────────────────────────────
    if _match(r"how serious|how bad|kitna serious|severe|urgency|critical|danger|worse|is it bad", msg):
        pct = det.detection_result.affected_area_percentage
        return (
            f"⚠️ **Severity: {sev_cfg['label']}**\n\n"
            f"{sev_cfg['description']}\n\n"
            f"🚨 *{sev_cfg['urgency']}*\n\n"
            f"**{pct}%** of the plant area is currently affected.",
            "severity",
        )

    # ── Location ──────────────────────────────────────────────────────────────
    if _match(r"where|location|which area|kahan|section|row|place|spot", msg):
        return (
            f"📍 **Disease Location:**\n\n"
            f"• Row: **{loc.row}**\n"
            f"• Section: **{loc.section}**\n"
            f"• Distance from start: **{loc.distance_from_start_meters}m**\n\n"
            f"Open the **Farm Map** page to see the exact cell highlighted on your pandal.",
            "location",
        )

    # ── Treatment / what to do ────────────────────────────────────────────────
    if _match(r"what to do|how to treat|treatment|cure|spray|medicine|dawa|solution|fix|help|action|steps", msg):
        steps = "\n".join(
            f"{i+1}. {r}" for i, r in enumerate(info["recommendations"]["immediate"])
        )
        return (
            f"🌱 **Immediate Actions for {display_name}:**\n\n{steps}\n\n"
            f"👉 Visit the **Disease Details** page for full treatment guide and preventive steps.",
            "treatment",
        )

    # ── Symptoms ──────────────────────────────────────────────────────────────
    if _match(r"symptoms|signs|what does it look|look like|appearance|spots|leaves", msg):
        symptoms = "\n".join(f"• {s}" for s in info["symptoms"])
        detected = det.detection_result.symptoms_detected
        detected_str = ", ".join(detected) if detected else "None visible"
        return (
            f"🔎 **Symptoms of {display_name}:**\n\n{symptoms}\n\n"
            f"**Currently detected on your plant:** {detected_str}",
            "symptoms",
        )

    # ── Weather / environment ─────────────────────────────────────────────────
    if _match(r"weather|temperature|humidity|moisture|water|environment|sensor|climate|rain|hot|cold", msg):
        advice = ""
        if env.humidity_percentage > 80:
            advice = "⚠️ Humidity is high — this promotes fungal disease spread. Improve ventilation."
        elif env.temperature_celsius > 33:
            advice = "⚠️ Temperature is high — this stresses plants. Ensure adequate watering."
        else:
            advice = "✅ Conditions are within acceptable range."

        return (
            f"🌡️ **Current Farm Conditions:**\n\n"
            f"• 🌡️ Temperature: **{env.temperature_celsius}°C**\n"
            f"• 💧 Humidity: **{env.humidity_percentage}%**\n"
            f"• 🌱 Soil Moisture: **{env.soil_moisture_percentage}%**\n"
            f"• ☀️ Light Intensity: **{env.light_intensity_lux} lux**\n\n"
            f"{advice}",
            "weather",
        )

    # ── Confidence ────────────────────────────────────────────────────────────
    if _match(r"confidence|sure|accurate|reliable|percentage|how certain|correct", msg):
        return (
            f"📊 **AI Confidence: {confidence}%**\n\n"
            f"This is considered **very high accuracy**.\n"
            f"The model analyzed the plant image and identified clear visual signatures "
            f"of {display_name}.",
            "confidence",
        )

    # ── Prevention ────────────────────────────────────────────────────────────
    if _match(r"prevent|avoid|stop|future|recurring|before|protection|safe", msg):
        steps = "\n".join(
            f"{i+1}. {r}" for i, r in enumerate(info["recommendations"]["preventive"])
        )
        return (
            f"🛡️ **Prevention Tips for {display_name}:**\n\n{steps}",
            "prevention",
        )

    # ── History ───────────────────────────────────────────────────────────────
    if _match(r"history|past|before|previous|trend|how many times|last week|last month", msg):
        return (
            f"📅 **Detection History (Last 14 Days):**\n\n"
            f"• Powdery Mildew: **2 incidents**\n"
            f"• Downy Mildew: **2 incidents**\n"
            f"• Fungal Leaf Spot: **1 incident**\n"
            f"• Viral Symptoms: **1 incident**\n"
            f"• Pest Damage: **2 incidents**\n\n"
            f"Go to the **History page** to see the full timeline and trend charts.",
            "history",
        )

    # ── Healthy plants ────────────────────────────────────────────────────────
    if _match(r"healthy|good plants|how many healthy|how many ok", msg):
        return (
            f"🟢 **Farm Health Summary:**\n\n"
            f"• Healthy plants: **60%** (12 cells)\n"
            f"• Need attention: **20%** (4 cells)\n"
            f"• Diseased: **20%** (4 cells)\n\n"
            f"The majority of your farm is in good health!",
            "farm_summary",
        )

    # ── Default fallback ──────────────────────────────────────────────────────
    return (
        f"🤔 I didn't quite understand that. Here's what I know right now:\n\n"
        f"• **Disease:** {display_name} ({confidence}% confidence)\n"
        f"• **Severity:** {sev_cfg['label']}\n"
        f"• **Location:** Row {loc.row}, Section {loc.section}\n\n"
        f"Try asking:\n"
        f'• "What disease?"\n'
        f'• "How serious?"\n'
        f'• "Where is it?"\n'
        f'• "What should I do?"\n'
        f'• "How is the weather?"\n'
        f'• "How to prevent it?"',
        "fallback",
    )
