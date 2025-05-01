import pandas as pd
import joblib
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DATA_DIR = "data/training"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


# === ROLE CLASSIFIER ===
def train_role_classifier():
    print("🔵 Training agent role probability model...")

    df = pd.read_csv(f"{DATA_DIR}/role_training.csv")
    df['Text'] = df['Name'].fillna('') + ' ' + df['Title'].fillna('')
    X = df['Text']
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)

    print(classification_report(y_test, pipeline.predict(X_test)))

    joblib.dump(pipeline, f"{MODEL_DIR}/role_classifier.pkl")
    print("✅ Saved role classifier to models/role_classifier.pkl")


# === MISCONDUCT CLASSIFIER ===
def train_misconduct_classifier():
    print("🔵 Training misconduct classifier...")

    df = pd.read_csv(f"{DATA_DIR}/misconduct_training.csv")
    X = df['Snippet'].fillna('')
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)

    print(classification_report(y_test, pipeline.predict(X_test)))

    joblib.dump(pipeline, f"{MODEL_DIR}/misconduct_classifier.pkl")
    print("✅ Saved misconduct classifier to models/misconduct_classifier.pkl")


if __name__ == "__main__":
    train_role_classifier()
    train_misconduct_classifier()
