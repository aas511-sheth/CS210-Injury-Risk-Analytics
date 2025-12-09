import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.model_selection import train_test_split
import pickle

# paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FEATURES_PATH = os.path.join(PROJECT_ROOT, "data", "features_for_ml.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "code", "injury_model.pkl")
VIS_PATH = os.path.join(PROJECT_ROOT, "visualizations")
os.makedirs(VIS_PATH, exist_ok=True)

# Load data and model
df = pd.read_csv(FEATURES_PATH)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Load data and model
X = df[['training_load_hours', 'workload_ratio', 'intensity_avg', 'recovery_score', 'fatigue_level']]
y = df['injury_occurred']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

with open(MODEL_PATH, 'rb') as f:
    rf = pickle.load(f)

y_pred = rf.predict(X_test)
y_pred_proba = rf.predict_proba(X_test)[:, 1]

# 1. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve - Injury Risk Prediction', fontsize=14, fontweight='bold')
plt.legend(loc="lower right", fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(VIS_PATH, 'roc_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: roc_curve.png")

# 2. Feature Importance
importance = rf.feature_importances_
features = X.columns
sorted_idx = np.argsort(importance)[::-1]

plt.figure(figsize=(10, 6))
colors = plt.cm.viridis(np.linspace(0, 1, len(features)))
bars = plt.barh(range(len(features)), importance[sorted_idx], color=colors)
plt.yticks(range(len(features)), [features[i] for i in sorted_idx], fontsize=11)
plt.xlabel('Importance Score', fontsize=12)
plt.title('Feature Importance in Injury Risk Prediction', fontsize=14, fontweight='bold')
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2, f'{width:.3f}', 
             ha='left', va='center', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(VIS_PATH, 'roc_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: feature_importance.png")

# 3. Confusion Matrix
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Injury', 'Injury'],
            yticklabels=['No Injury', 'Injury'],
            cbar_kws={'label': 'Count'})
plt.title('Confusion Matrix - Injury Predictions', fontsize=14, fontweight='bold')
plt.ylabel('Actual', fontsize=12)
plt.xlabel('Predicted', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(VIS_PATH, 'roc_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: confusion_matrix.png")

# 4. Risk Distribution Analysis (4-panel)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel 1: Risk score distribution
ax = axes[0, 0]
ax.hist(y_pred_proba, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
ax.set_title('Distribution of Risk Scores', fontsize=12, fontweight='bold')
ax.set_xlabel('Risk Score')
ax.set_ylabel('Frequency')
ax.grid(alpha=0.3)

# Panel 2: Risk vs Workload Ratio
ax = axes[0, 1]
scatter = ax.scatter(X_test['workload_ratio'], y_pred_proba, 
                     c=y_test, cmap='RdYlGn_r', alpha=0.6, s=50)
ax.set_title('Risk Score vs Workload Ratio', fontsize=12, fontweight='bold')
ax.set_xlabel('Workload Ratio')
ax.set_ylabel('Predicted Risk Score')
ax.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Injury (1=Yes)')

# Panel 3: Risk vs Fatigue Level
ax = axes[1, 0]
scatter = ax.scatter(X_test['fatigue_level'], y_pred_proba, 
                     c=y_test, cmap='RdYlGn_r', alpha=0.6, s=50)
ax.set_title('Risk Score vs Fatigue Level', fontsize=12, fontweight='bold')
ax.set_xlabel('Fatigue Level')
ax.set_ylabel('Predicted Risk Score')
ax.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Injury (1=Yes)')

# Panel 4: Risk vs Recovery Score
ax = axes[1, 1]
scatter = ax.scatter(X_test['recovery_score'], y_pred_proba, 
                     c=y_test, cmap='RdYlGn_r', alpha=0.6, s=50)
ax.set_title('Risk Score vs Recovery Score', fontsize=12, fontweight='bold')
ax.set_xlabel('Recovery Score')
ax.set_ylabel('Predicted Risk Score')
ax.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Injury (1=Yes)')

plt.tight_layout()
plt.savefig(os.path.join(VIS_PATH, 'roc_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: risk_analysis.png")

print("\n✅ ALL VISUALIZATIONS COMPLETE!")
