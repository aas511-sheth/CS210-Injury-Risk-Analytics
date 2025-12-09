import os
import psycopg2
import pickle
import pandas as pd
from config import DB_CONFIG
from datetime import date

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(PROJECT_ROOT, "code", "injury_model.pkl")
FEATURES_PATH = os.path.join(PROJECT_ROOT, "data", "features_for_ml.csv")

# Load model and features
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

df = pd.read_csv(FEATURES_PATH)

# Make predictions
X = df[['training_load_hours', 'workload_ratio', 'intensity_avg', 'recovery_score', 'fatigue_level']]
risk_scores = model.predict_proba(X)[:, 1]

# Categorize risk
df['risk_score'] = risk_scores
df['risk_category'] = pd.cut(risk_scores, 
                              bins=[0, 0.33, 0.67, 1.0],
                              labels=['Low', 'Medium', 'High'])

# Insert into database
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

for idx, row in df.iterrows():
    cur.execute("""
        INSERT INTO injury_predictions 
        (player_id, prediction_date, risk_score, risk_category, model_version)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        int(row['player_id']),
        date.today(),                      # <‑‑ replace week_start_date
        float(row['risk_score']),
        row['risk_category'],
        'v1.0'
    ))

conn.commit()
cur.close()
conn.close()

print(f"✓ Stored {len(df)} predictions in database")