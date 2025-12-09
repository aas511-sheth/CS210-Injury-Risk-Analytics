import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
import pickle
import json

# ---------- PATHS ----------
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FEATURES_PATH = os.path.join(PROJECT_ROOT, "data", "features_for_ml.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "code", "injury_model.pkl")
METRICS_PATH = os.path.join(PROJECT_ROOT, "data", "model_metrics.json")

# ---------- LOAD DATA ----------
df = pd.read_csv(FEATURES_PATH)

X = df[['training_load_hours', 'workload_ratio', 'intensity_avg',
        'recovery_score', 'fatigue_level']]
y = df['injury_occurred']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------- TRAIN MODEL ----------
print("Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'
)
rf.fit(X_train, y_train)

# ---------- EVALUATE ----------
y_pred = rf.predict(X_test)
y_pred_proba = rf.predict_proba(X_test)[:, 1]

train_acc = rf.score(X_train, y_train)
test_acc = rf.score(X_test, y_test)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("\n=== MODEL PERFORMANCE ===")
print(f"Training Accuracy: {train_acc:.4f}")
print(f"Testing Accuracy:  {test_acc:.4f}")
print(f"ROC-AUC Score:     {roc_auc:.4f}")

cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='roc_auc')
print(f"Cross-validation:  {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(y_test, y_pred, target_names=['No Injury', 'Injury']))

importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("\n=== FEATURE IMPORTANCE ===")
print(importance_df)

# ---------- SAVE ARTIFACTS ----------
metrics = {
    'train_accuracy': float(train_acc),
    'test_accuracy': float(test_acc),
    'roc_auc': float(roc_auc),
    'cv_mean': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'feature_importance': importance_df.to_dict('records')
}

# use the absolute paths defined at the top
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(rf, f)

with open(METRICS_PATH, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\n✓ Model saved to {MODEL_PATH}")
print(f"✓ Metrics saved to {METRICS_PATH}")
