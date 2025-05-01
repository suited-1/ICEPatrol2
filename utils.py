import joblib
import re

role_model = joblib.load("models/role_classifier.pkl")
misconduct_model = joblib.load("models/misconduct_classifier.pkl")

def get_class_probs(model, text):
    proba = model.predict_proba([text])[0]
    labels = model.classes_
    return dict(zip(labels, proba))

def score_profile(name, title, snippet=None):
    text = f"{name} {title}"
    role_probs_raw = get_class_probs(role_model, text)
    role_score = role_probs_raw.get("Agent", 0.0)

    role_probs = {k: round(float(v), 2) for k, v in role_probs_raw.items()}

    misconduct_score = 0.0
    if snippet:
        misconduct_probs = get_class_probs(misconduct_model, snippet)
        misconduct_score = misconduct_probs.get("Misconduct", 0.0)

    misconduct_score = round(float(misconduct_score), 2)

    # 🔥 Override logic: high misconduct implies agent
    if misconduct_score >= 0.70:
        role_score = 1.0
        role_probs["Agent"] = 1.0
        role_probs["Lawyer"] = 0.0
        role_probs["Other"] = 0.0

    return {
        "AgentScore": round(float(role_score), 2),
        "RoleProbs": role_probs,
        "MisconductScore": misconduct_score,
    }

def extract_name(raw_name):
    return raw_name.split('-')[0].strip()

def extract_title(snippet):
    parts = re.split(r'·|Experience:', snippet)
    return parts[0].strip().strip(',').strip('-') if parts else ''

def extract_location(snippet):
    match = re.search(r'Location:\s*([^·,\n]+)', snippet)
    return match.group(1).strip() if match else ''

def extract_education(snippet):
    match = re.search(r'Education:\s*([^·,\n]+)', snippet)
    return match.group(1).strip() if match else ''

def extract_connections(snippet):
    match = re.search(r'(\d+\+?) connections', snippet)
    return match.group(1) if match else ''

MISCONDUCT_SEARCH_TERMS = [
    "ICE misconduct", "ICE abuse", "ICE lawsuit", "ICE charges",
    "ICE arrest", "ICE complaint", "ICE violation", "ICE brutality", "ICE allegations"
]
