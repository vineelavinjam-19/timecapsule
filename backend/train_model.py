import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Load dataset
df = pd.read_csv("email.csv", encoding="latin-1")

print("COLUMNS FOUND:", df.columns)

# Safer explicit mapping (your dataset)
df = df.rename(columns={
    "Category": "label",
    "Message": "text"
})

# Remove missing values (VERY important)
df = df.dropna()

X = df["text"]
y = df["label"]

# Model pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("clf", MultinomialNB())
])

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "spam_model.pkl")

print("✅ Model trained and saved!")