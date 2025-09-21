# backend/demo_streamlit.py
import streamlit as st
import joblib
import hashlib
import os
import re
import numpy as np
import requests
from functools import lru_cache

# -------------------------------
# Load model
# -------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    st.error(f"Failed to load model at {MODEL_PATH}: {e}")
    st.stop()

# -------------------------------
# Custom CSS for UI improvements
# -------------------------------
st.markdown(
    """
<style>
.big-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 12px;
    text-align: center;
}

label, .stCheckbox label {
    font-size: 18px !important;
}

input[type="password"] {
    font-size: 20px !important;
    padding: 14px 16px !important;
    height: 52px !important;
    line-height: 1.4 !important;
}

.stButton>button {
    height: 46px;
    font-size: 16px;
    width: 160px;
    margin: auto;
    display: block;
}

.stMarkdown, .stText, .stAlert {
    font-size: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------
# Helpers
# -------------------------------
def password_features(pw: str):
    length = len(pw)
    digits = len(re.findall(r"\d", pw))
    upper = len(re.findall(r"[A-Z]", pw))
    lower = len(re.findall(r"[a-z]", pw))
    symbols = len(re.findall(r"\W", pw))
    entropy = np.log2(len(set(pw))) * length if pw else 0
    return [[length, digits, upper, lower, symbols, entropy]]

@lru_cache(maxsize=256)
def hibp_check_cached(prefix: str, suffix: str):
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code != 200:
            return None
        hashes = (line.split(":") for line in res.text.splitlines())
        return any(h[0] == suffix for h in hashes)
    except requests.RequestException:
        return None

def hibp_check(password: str):
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    return hibp_check_cached(prefix, suffix)

# -------------------------------
# Session state
# -------------------------------
if "password_input" not in st.session_state:
    st.session_state.password_input = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# -------------------------------
# UI
# -------------------------------
st.markdown("<div class='big-title'>🔐 AI-Powered Password Strength Checker</div>", unsafe_allow_html=True)

# Clear callback
def clear_input():
    st.session_state.password_input = ""
    st.session_state.last_result = None

# Main input
password = st.text_input("Enter password (press Enter to analyze):", type="password", key="password_input")

# Clear button right below input
st.button("🗑️ Clear", on_click=clear_input)

# HIBP checkbox
check_breach = st.checkbox("Check against HaveIBeenPwned (HIBP)")

# -------------------------------
# Analysis
# -------------------------------
if password:
    try:
        features = password_features(password)
        score = model.predict(features)[0]
    except Exception as e:
        st.error(f"Model error: {e}")
        st.stop()

    labels = {0: "Weak", 1: "Medium", 2: "Strong"}
    strength = labels.get(int(score), "Unknown")
    percent = int((int(score) / 2) * 100)

    # Colored label
    color = "#0a8a0a" if strength == "Strong" else ("#ff8c00" if strength == "Medium" else "#b00020")
    st.markdown(f"<h2 style='color: {color}; text-align:center;'>{strength}</h2>", unsafe_allow_html=True)

    # Progress bar
    st.progress(percent)

    # Optional HIBP check
    if check_breach:
        if len(password) >= 6:
            with st.spinner("Checking HaveIBeenPwned..."):
                hibp_result = hibp_check(password)
            if hibp_result is True:
                st.error("⚠️ This password has appeared in breaches. DO NOT use it.")
            elif hibp_result is False:
                st.success("✅ Not found in HIBP.")
            else:
                st.warning("HIBP check unavailable.")
        else:
            st.info("HIBP skipped: too short.")

    # Save results
    st.session_state.last_result = {
        "Strength": strength,
        "Score": int(score),
        "Percent": percent,
        "Length": len(password),
        "HIBP_checked": bool(check_breach)
    }

    st.write("**Details**")
    st.json(st.session_state.last_result)

    if strength == "Weak":
        st.info(
            """
**Tips to improve your password:**
- Use at least 12–16 characters
- Mix upper/lowercase, numbers, and symbols
- Avoid dictionary words or common patterns
- Use a password manager
"""
        )
else:
    st.info("Enter a password and press Enter to analyze.")
