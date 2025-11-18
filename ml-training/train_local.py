"""
Local XGBoost Fraud Detection Model Training
No SageMaker needed - trains on your computer
Cost: $0 | Time: ~2 minutes
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
import joblib
import boto3
import os
from datetime import datetime

print("=" * 70)
print("LOCAL ML TRAINING - FRAUD DETECTION MODEL")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Configuration
BUCKET_NAME = 'fraud-ml-data-sahil-2024'
REGION = 'ap-south-1'

# Download data from S3
print("\n Step 1: Downloading training data from S3...")
try:
    s3 = boto3.client('s3', region_name=REGION)
    s3.download_file(BUCKET_NAME, 'training/fraud_training_data.csv', 'data.csv')
    print("    Downloaded successfully")
except Exception as e:
    print(f"    Error downloading: {e}")
    print(f"   Make sure file exists at: s3://{BUCKET_NAME}/training/fraud_training_data.csv")
    exit(1)

# Load data
print("\n Step 2: Loading and analyzing data...")
df = pd.read_csv('data.csv')
print(f"   Total transactions: {len(df):,}")
print(f"   Fraud cases: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.1f}%)")
print(f"   Legitimate cases: {(~df['is_fraud']).sum():,} ({(~df['is_fraud']).mean()*100:.1f}%)")

# Display data info
print(f"\n   Columns: {list(df.columns)}")
print(f"   Data types:\n{df.dtypes}")

# Prepare features
print("\n🔧 Step 3: Engineering features...")
print("   Converting categorical variables to numeric...")

# Convert categorical to numeric codes
df['transaction_type'] = df['transaction_type'].astype('category').cat.codes
df['location'] = df['location'].astype('category').cat.codes
df['merchant_category'] = df['merchant_category'].astype('category').cat.codes
df['is_international'] = df['is_international'].astype(int)
df['new_payee'] = df['new_payee'].astype(int)

print("    Feature engineering complete")

# Prepare X and y
X = df.drop(['user_id', 'is_fraud'], axis=1)
y = df['is_fraud']

print(f"\n   Feature count: {len(X.columns)}")
print(f"   Features: {list(X.columns)}")

# Split data
print("\n  Step 4: Splitting data (80/20 train/test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Training samples: {len(X_train):,}")
print(f"   Test samples: {len(X_test):,}")
print(f"   Training fraud rate: {y_train.mean()*100:.1f}%")
print(f"   Test fraud rate: {y_test.mean()*100:.1f}%")

# Train model
print("\n  Step 5: Training XGBoost model...")
print("   Algorithm: XGBoost (Gradient Boosting Decision Trees)")
print("   Hyperparameters:")
print("   - Trees: 100")
print("   - Max depth: 5")
print("   - Learning rate: 0.2")
print("   - Subsample: 0.8")
print("   - Column sample: 0.8")
print("\n   Training in progress...")

model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=100,
    max_depth=5,
    learning_rate=0.2,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    eval_metric='auc',
    random_state=42,
    use_label_encoder=False,
    verbosity=0
)

# Train
model.fit(X_train, y_train)
print("    Training complete!")

# Evaluate
print("\n Step 6: Evaluating model performance...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print("\n" + "=" * 70)
print(" MODEL TRAINING COMPLETE!")
print("=" * 70)

print(f"\n PERFORMANCE METRICS:")
print(f"   Accuracy: {accuracy:.2%}")
print(f"   AUC Score: {auc:.4f}")

print(f"\n CONFUSION MATRIX:")
print(f"   True Negatives:  {tn:4d} (legitimate correctly identified)")
print(f"   False Positives: {fp:4d} (legitimate flagged as fraud)")
print(f"   False Negatives: {fn:4d} (fraud missed)")
print(f"   True Positives:  {tp:4d} (fraud correctly caught)")

print(f"\n DETAILED METRICS:")
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"   Precision: {precision:.2%} (of flagged transactions, % actually fraud)")
print(f"   Recall:    {recall:.2%} (of actual fraud, % we caught)")
print(f"   F1-Score:  {f1:.4f} (harmonic mean of precision and recall)")

print("\n CLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))

# Feature importance
print("\n TOP 10 MOST IMPORTANT FEATURES:")
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    bar_length = int(row['importance'] * 50)
    bar = '█' * bar_length
    print(f"   {row['feature']:25s} {bar} {row['importance']:.4f}")

# Save model
print("\n Step 7: Saving model...")
joblib.dump(model, 'fraud_model.pkl')
model_size = os.path.getsize('fraud_model.pkl') / 1024 / 1024
print(f"    Model saved: fraud_model.pkl ({model_size:.2f} MB)")

# Save feature names for later use
joblib.dump(list(X.columns), 'feature_names.pkl')
print(f"    Feature names saved: feature_names.pkl")

# Upload to S3
print("\n  Step 8: Uploading model to S3...")
try:
    s3.upload_file('fraud_model.pkl', BUCKET_NAME, 'models/fraud_model.pkl')
    print(f"    Uploaded to: s3://{BUCKET_NAME}/models/fraud_model.pkl")
    
    s3.upload_file('feature_names.pkl', BUCKET_NAME, 'models/feature_names.pkl')
    print(f"    Uploaded feature names to S3")
except Exception as e:
    print(f"     Upload failed: {e}")
    print("   Model is still saved locally and can be used!")

# Summary
print("\n" + "=" * 70)
print("🎉 SUCCESS! YOUR FRAUD DETECTION MODEL IS READY!")
print("=" * 70)

print(f"\n Files Created:")
print(f"   • fraud_model.pkl ({model_size:.2f} MB)")
print(f"   • feature_names.pkl")
print(f"   • data.csv (training data)")

print(f"\n  S3 Location:")
print(f"   • s3://{BUCKET_NAME}/models/fraud_model.pkl")

print(f"\n Model Performance Summary:")
print(f"   • Accuracy: {accuracy:.2%}")
print(f"   • AUC: {auc:.4f}")
print(f"   • Precision: {precision:.2%}")
print(f"   • Recall: {recall:.2%}")

print(f"\n Next Steps:")
print(f"   1. Test predictions with sample transactions")
print(f"   2. Deploy model to AWS Lambda")
print(f"   3. Integrate with your fraud detection API")
print(f"   4. Set up monitoring and alerts")

print(f"\n Cost: $0 (trained locally!)")
print(f"  Training time: ~2 minutes")
print(f" Ready for production deployment!")

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)