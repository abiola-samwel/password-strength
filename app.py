from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib, re, numpy as np, hashlib, requests, os

# -------------------------------
# FastAPI Setup
# -------------------------------
app = FastAPI(title="AI-Powered Password Strength API")

# Enable CORS BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS, etc.
    allow_headers=["*"]
)

# -------------------------------
# Load or Train model
# -------------------------------
if not os.path.exists("model.pkl"):
    print("model.pkl not found. Training model...")
    from train_model import train_model
    train_model()
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
# HaveIBeenPwned Check
# -------------------------------
def hibp_check(password: str) -> bool:
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)
    if res.status_code != 200:
        return False
    hashes = (line.split(":") for line in res.text.splitlines())
    return any(h[0] == suffix for h in hashes)

# -------------------------------
# Request model
# -------------------------------
class PasswordRequest(BaseModel):
    password: str

# -------------------------------
# Routes
# -------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the AI-Powered Password Strength API 🔐"}

@app.options("/predict")
def options_handler():
    return {
        "message": "Preflight OK",
        "allowed_methods": ["POST", "OPTIONS"]
    }

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
        )
    }
