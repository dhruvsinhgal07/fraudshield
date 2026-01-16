import hashlib
import re
import pickle
import mysql.connector
from jose import jwt
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pickle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

model = pickle.load(open(MODEL_PATH, "rb"))
vectorizer = pickle.load(open(VECTORIZER_PATH, "rb"))

# ================= CONFIG =================
SECRET_KEY = os.getenv("SECRET_KEY", "dev_fraudshield_secret")
ALGORITHM = "HS256"

SHORT_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl",
    "ow.ly", "is.gd", "buff.ly"
]

SCAM_KEYWORDS = {
    "verify": 10,
    "urgent": 10,
    "account": 8,
    "blocked": 15,
    "suspended": 15,
    "click": 10,
    "login": 10,
    "password": 20,
    "otp": 25,
    "bank": 10,
    "reward": 8,
    "prize": 12
}

FAKE_BRANDS = [
    "paytm", "phonepe", "google", "amazon", "flipkart",
    "icici", "hdfc", "sbi", "axis", "upi"
]

SUSPICIOUS_TLDS = [
    ".xyz", ".click", ".top", ".online", ".site"
]

# ================= HELPERS =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def get_current_user(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def extract_urls(text):
    return re.findall(r"https?://\S+|www\.\S+", text)

def is_short_url(url):
    return any(domain in url for domain in SHORT_DOMAINS)

def suspicious_domain(url: str) -> bool:
    url = url.lower()
    for brand in FAKE_BRANDS:
        if brand in url and not url.endswith(".com"):
            return True
    for tld in SUSPICIOUS_TLDS:
        if tld in url:
            return True
    return False

def keyword_risk(text: str) -> int:
    text = text.lower()
    risk = 0
    for word, score in SCAM_KEYWORDS.items():
        if word in text:
            risk += score
    return risk

def clean(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text

# ================= APP =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DB =================
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        autocommit=True
    )


# ================= ML =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

model = pickle.load(open(MODEL_PATH, "rb"))
vectorizer = pickle.load(open(VECTORIZER_PATH, "rb"))


# ================= MODELS =================
class Message(BaseModel):
    text: str

class User(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

# ================= ROUTES =================

@app.post("/predict")
def predict(msg: Message, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")

    token = authorization.split(" ")[1]
    user = get_current_user(token)

    # ML score
    cleaned = clean(msg.text)
    vector = vectorizer.transform([cleaned])
    probs = model.predict_proba(vector)[0]
    ml_score = float(probs[1]) * 100

    # URL risk
    urls = extract_urls(msg.text)
    url_risk = 0
    for url in urls:
        if is_short_url(url):
            url_risk += 20
        if suspicious_domain(url):
            url_risk += 30
    if len(urls) > 1:
        url_risk += (len(urls) - 1) * 10

    # Keyword risk
    keyword_boost = keyword_risk(msg.text)

    # Final confidence
    final_confidence = min(
        100,
        ml_score + url_risk + keyword_boost
    )

    scam = final_confidence >= 55

    # Save report
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reports (message, scam, confidence, user_id) VALUES (%s,%s,%s,%s)",
        (msg.text, int(scam), final_confidence, user["user_id"])
    )
    cursor.close()
    db.close()

    return {
        "scam": scam,
        "confidence": round(final_confidence, 2),
        "ml_score": round(ml_score, 2),
        "url_risk": url_risk,
        "keyword_risk": keyword_boost,
        "urls_detected": urls
    }

@app.get("/history")
def history(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401)

    token = authorization.split(" ")[1]
    user = get_current_user(token)

    db = get_db()
    cursor = db.cursor()

    if user["role"] == "admin":
        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    else:
        cursor.execute(
            "SELECT * FROM reports WHERE user_id=%s ORDER BY created_at DESC",
            (user["user_id"],)
        )

    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

@app.get("/analytics")
def analytics(authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    user = get_current_user(token)

    if user["role"] != "admin":
        raise HTTPException(status_code=403)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM reports")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT scam, COUNT(*) FROM reports GROUP BY scam")
    data = cursor.fetchall()

    cursor.execute("""
        SELECT DATE(created_at), COUNT(*)
        FROM reports
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
    """)
    daily = cursor.fetchall()

    cursor.close()
    db.close()

    scam_count = sum(r[1] for r in data if r[0] == 1)
    safe_count = sum(r[1] for r in data if r[0] == 0)

    return {
        "total": total,
        "scam": scam_count,
        "safe": safe_count,
        "daily": daily
    }

@app.post("/signup")
def signup(user: User):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cursor.fetchone():
        cursor.close()
        db.close()
        return {"error": "Email already exists"}

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
        (user.name, user.email, hash_password(user.password))
    )

    cursor.close()
    db.close()
    return {"message": "User registered"}

@app.post("/login")
def login(data: Login):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, password, role FROM users WHERE email=%s",
        (data.email,)
    )
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if not user or not verify_password(data.password, user[1]):
        return {"error": "Invalid credentials"}

    token = jwt.encode(
        {"user_id": user[0], "role": user[2]},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"token": token}

@app.get("/admin/users")
def get_users(authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    user = get_current_user(token)

    if user["role"] != "admin":
        raise HTTPException(status_code=403)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, authorization: str = Header(None)):
    token = authorization.split(" ")[1]
    user = get_current_user(token)

    if user["role"] != "admin":
        raise HTTPException(status_code=403)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    cursor.close()
    db.close()
    return {"message": "User deleted"}
