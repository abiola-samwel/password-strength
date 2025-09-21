"""
 AI-Powered Password Strength Predictor
-----------------------------------------
This tool predicts password strength (Weak / Medium / Strong) 
using a machine learning model trained on real password data.

Features:
- Trains a Decision Tree Classifier
- Visualizes performance via a Confusion Matrix
- Interactive password tester (type your own)
- Saves trained model for reuse

Author: Samuel Abiola
"""

import pandas as pd
import re
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

# -------------------------
# Feature Engineering
# -------------------------
def password_features(password: str):
    """Extract simple statistical features from a password string."""
    length = len(password)
    digits = len(re.findall(r"\d", password))
    upper = len(re.findall(r"[A-Z]", password))
    lower = len(re.findall(r"[a-z]", password))
    special = len(re.findall(r"[^A-Za-z0-9]", password))
    return [length, digits, upper, lower, special]

# -------------------------
# Load Dataset
# -------------------------
print("📂 Loading dataset...")
df = pd.read_csv("dataset.csv")

X = df["password"].apply(password_features).tolist()
y = df["strength"]

# -------------------------
# Train/Test Split
# -------------------------
print("⚙️ Training model...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------
# Model Training
# -------------------------
clf = DecisionTreeClassifier(max_depth=8, random_state=42)
clf.fit(X_train, y_train)

# Save model for future use
joblib.dump(clf, "password_model.pkl")

# -------------------------
# Evaluation
# -------------------------
y_pred = clf.predict(X_test)
print("\n📊 Classification Report:\n", classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Weak", "Medium", "Strong"],
            yticklabels=["Weak", "Medium", "Strong"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Password Strength Confusion Matrix")
plt.tight_layout()

# Save and show plot (non-blocking)
plt.savefig("confusion_matrix.png")
plt.show(block=False)
print("📸 Confusion matrix saved as 'confusion_matrix.png'")

# -------------------------
# Interactive Prediction
# -------------------------
labels = {0: "Weak", 1: "Medium", 2: "Strong"}

print("\n🔐 Interactive Password Tester")
print("Type a password to check its strength (or 'exit' to quit):")

while True:
    pwd = input("\nEnter password: ")
    if pwd.lower() == "exit":
        print("👋 Exiting. Stay secure!")
        break
    features = [password_features(pwd)]
    pred = clf.predict(features)[0]
    print(f"👉 Predicted Strength: {labels[pred]}")
