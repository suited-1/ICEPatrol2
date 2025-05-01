import pandas as pd
import joblib
import os

DATA_DIR = "data/training"
ROLE_PATH = f"{DATA_DIR}/role_training.csv"
MIS_PATH = f"{DATA_DIR}/misconduct_training.csv"
EXAMPLE_PATH = "training_profiles.csv"

role_model = joblib.load("models/role_classifier.pkl")
mis_model = joblib.load("models/misconduct_classifier.pkl")

def get_class_probs(model, text):
    if pd.isna(text):
        text = ""
    proba = model.predict_proba([text])[0]
    labels = model.classes_
    return dict(zip(labels, proba))

def review_profile(row):
    name = row.get("Name", "")
    title = row.get("Title", "")
    snippet = row.get("Snippet", title)  # fallback to Title
    location = row.get("Location", "")
    education = row.get("Education", "")
    connections = row.get("Connections", "")

    full_text = f"{name} {title}"

    print(f"\n=== Reviewing: {name} ===")
    if location:
        print(f"📍 Location: {location}")
    if education:
        print(f"🎓 Education: {education}")
    if connections:
        print(f"🔗 Connections: {connections}")

    # === MISCONDUCT FIRST ===
    misconduct_score = 0.0
    mis_label = None
    mis_choice = None

    if snippet:
        mis_probs = get_class_probs(mis_model, snippet)
        misconduct_score = round(float(mis_probs.get("Misconduct", 0.0)), 2)
        mis_probs = {k: round(float(v), 2) for k, v in mis_probs.items()}

        print("\n🔶 MISCONDUCT CLASSIFIER")
        print(f"📝 Snippet: {snippet}")
        print(f"🤖 Misconduct Score: {misconduct_score} (Probs: {mis_probs})")
        print("How should this be labeled?")
        print("[0] Clean")
        print("[1] Misconduct")
        print("[2] ✅ Good (accept model's prediction)")
        print("[3] ❌ Discard")

        mis_choice = input("Your choice [0/1/2/3]: ").strip()
        if mis_choice == "2":
            mis_label = "Misconduct" if misconduct_score >= 0.7 else "Clean"
        elif mis_choice == "1":
            mis_label = "Misconduct"
        elif mis_choice == "0":
            mis_label = "Clean"
        else:
            print("❌ Skipping misconduct entry...")

    # === ROLE CLASSIFICATION ===
    role_label = None
    if mis_label == "Misconduct":
        role_label = "Agent"
        print("⚠️  Auto-assuming Agent due to confirmed Misconduct label.")
    else:
        role_probs = get_class_probs(role_model, full_text)
        role_score = round(float(role_probs.get("Agent", 0.0)), 2)
        role_probs = {k: round(float(v), 2) for k, v in role_probs.items()}

        print("\n🔷 ROLE CLASSIFIER")
        print(f"👤 Name: {name}")
        print(f"🏷️  Title: {title}")
        print(f"🤖 Agent Score: {role_score} (Probs: {role_probs})")
        print("How would you rate this prediction?")
        print("[1] ✅ Good (auto-label by highest score)")
        print("[2] ⚠️  Needs correction (manual entry)")
        print("[3] ❌ Discard")

        role_choice = input("Your choice [1/2/3]: ").strip()
        if role_choice == "1":
            role_label = max(role_probs, key=role_probs.get)
        elif role_choice == "2":
            role_label = input("Enter correct label (Agent/Lawyer/Other): ").strip()
        else:
            print("❌ Skipping role entry...")

    # === Append to files ===
    if role_label:
        df = pd.read_csv(ROLE_PATH)
        new_row = pd.DataFrame([[name, title, role_label]], columns=["Name", "Title", "Label"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(ROLE_PATH, index=False)
        print(f"✅ Appended to {ROLE_PATH}")

    if snippet and mis_label:
        df = pd.read_csv(MIS_PATH)
        new_row = pd.DataFrame([[snippet, mis_label]], columns=["Snippet", "Label"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(MIS_PATH, index=False)
        print(f"✅ Appended to {MIS_PATH}")

def batch_review():
    if not os.path.exists(EXAMPLE_PATH):
        print(f"❌ ERROR: {EXAMPLE_PATH} not found.")
        return

    try:
        df = pd.read_csv(EXAMPLE_PATH)
    except pd.errors.EmptyDataError:
        print(f"⚠️  {EXAMPLE_PATH} is empty or has no valid rows.")
        return

    required_fields = {"Name", "Title"}
    if df.empty or not required_fields.issubset(df.columns):
        print("⚠️  training_profiles.csv missing required columns.")
        return

    for index, row in df.iterrows():
        if pd.isna(row.get("Snippet")) and pd.isna(row.get("Title")):
            print(f"⚠️ Skipping profile {index + 1}: no valid snippet or title.")
            continue

        print(f"\n📄 Reviewing profile {index + 1}/{len(df)}")
        review_profile(row)
        input("➡️ Press Enter to continue to the next profile...")

if __name__ == "__main__":
    batch_review()
