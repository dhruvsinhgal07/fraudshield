import pandas as pd
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv("../dataset/scam.csv", encoding="latin1")
df2 = pd.read_csv("../dataset/custom.csv")
df = pd.concat([df, df2])


# Keep only needed columns
df = df[["v1", "v2"]]

# Convert labels to numbers
df["v1"] = df["v1"].map({"spam": 1, "ham": 0})

# Clean text
def clean(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text

df["v2"] = df["v2"].apply(clean)

def enrich_text(text):
    keywords = [
        "urgent", "verify", "account", "blocked",
        "click", "login", "otp", "bank"
    ]
    for k in keywords:
        if k in text:
            text += f" {k}_flag"
    return text

df["v2"] = df["v2"].apply(enrich_text)


# Convert text to numbers
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),      # words + phrases
    max_features=5000,
    stop_words="english"
)

X = vectorizer.fit_transform(df["v2"])
y = df["v1"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train, y_train)

# Save trained model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ Model trained and saved successfully")
