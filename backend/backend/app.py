# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import re
import numpy as np
import hashlib
import requests

# -------------------------------
# Load trained model
# -------------------------------
clf = joblib.load("model.pkl")

labels = {0: "Weak", 1: "Medium", 2: "Strong"}

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
# HIBP Check
# -------------------------------
def hibp_check(password: str) -> bool:
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)

    if res.status_code != 200:
        return False  # Fail-safe

    hashes = (line.split(":") for line in res.text.splitlines())
    return any(h[0] == suffix for h in hashes)

# -------------------------------
# FastAPI Setup
# -------------------------------
app = FastAPI(title="AI-Powered Password Strength API")

class PasswordRequest(BaseModel):
    password: str

@app.get("/")
def root():
    return {"message": "Welcome to the AI-Powered Password Strength API 🔐"}

@app.post("/predict")
def predict(req: PasswordRequest):
    pw = req.password
    features = [password_features(pw)]
    pred = clf.predict(features)[0]

    breached = hibp_check(pw)

    return {
        "password": pw,
        "strength": labels[pred],
        "strength_score": int(pred),
        "breached": breached,
        "message": (
            "⚠️ This password has been found in real breaches!"
            if breached else "✅ This password was not found in known breaches."
        ),
    }
