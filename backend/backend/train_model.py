# train_model.py
import pandas as pd
import sqlite3
import re
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib

# -------------------------------
# Feature extraction
# -------------------------------
def password_features(pw: str):
    length = len(pw)
    digits = len(re.findall(r"\d", pw))
    upper = len(re.findall(r"[A-Z]", pw))
    lower = len(re.findall(r"[a-z]", pw))
    symbols = len(re.findall(r"\W", pw))
    entropy = np.log2(len(set(pw))) * length if pw else 0
    return [length, digits, upper, lower, symbols, entropy]

# -------------------------------
# Load dataset
# -------------------------------
conn = sqlite3.connect("password_data.sqlite")
df = pd.read_sql_query("SELECT password, strength FROM users", conn)
conn.close()

# Drop NA
df = df.dropna()

# Features + Labels
X = [password_features(p) for p in df["password"]]
y = df["strength"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train DecisionTree
clf = DecisionTreeClassifier(max_depth=10, random_state=42)
clf.fit(X_train, y_train)

# Save model
joblib.dump(clf, "model.pkl")
print("✅ Model trained and saved as model.pkl")
