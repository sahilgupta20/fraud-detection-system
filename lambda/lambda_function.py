"""
AWS Lambda Function - ML-Based Fraud Detection
Uses trained XGBoost model for predictions
"""
import json
import boto3
import joblib
import numpy as np
from io import BytesIO
from decimal import Decimal

# Initialize S3 client
s3_client = boto3.client('s3')

# Global variables for model (loaded once, reused across invocations)
model = None
feature_names = None
BUCKET_NAME = 'fraud-ml-data-sahil-2024'

def load_model():
    """Load model from S3 (only once per container)"""
    global model, feature_names
    
    if model is None:
        print("Loading model from S3...")
        
        # Download model
        model_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key='models/fraud_model.pkl')
        model = joblib.load(BytesIO(model_obj['Body'].read()))
        
        # Download feature names
        features_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key='models/feature_names.pkl')
        feature_names = joblib.load(BytesIO(features_obj['Body'].read()))
        
        print(f"Model loaded! Features: {feature_names}")
    
    return model, feature_names

def prepare_features(transaction):
    """Convert transaction to model input format - MATCHES TRAINING DATA"""
    
    # Map transaction type to codes
    type_mapping = {
        'purchase': 0,
        'transfer': 1,
        'withdrawal': 2,
        'deposit': 3,
        'payment': 4
    }
    
    # Map location to codes
    location_mapping = {
        'domestic': 0,
        'international': 1,
        'US': 0,
        'UK': 1,
        'CA': 2,
        'EU': 3,
        'AS': 4
    }
    
    # Map merchant category to codes
    merchant_mapping = {
        'retail': 0,
        'online': 1,
        'restaurant': 2,
        'gas': 3,
        'grocery': 4,
        'entertainment': 5,
        'travel': 6,
        'other': 7
    }
    
    # Extract features in EXACT order model expects
    features = {
        'amount': float(transaction.get('amount', 0)),
        'transaction_type': type_mapping.get(transaction.get('transaction_type', 'purchase').lower(), 0),
        'is_international': 1 if transaction.get('is_international', False) else 0,
        'new_payee': 1 if transaction.get('new_payee', False) else 0,
        'hour': int(transaction.get('hour', 12)),
        'day_of_week': int(transaction.get('day_of_week', 1)),
        'location': location_mapping.get(transaction.get('location', 'domestic').upper(), 0),
        'merchant_category': merchant_mapping.get(transaction.get('merchant_category', 'other').lower(), 0),
        'failed_login_attempts': int(transaction.get('failed_login_attempts', 0)),  # Changed from failed_attempts
        'account_age_days': int(transaction.get('account_age_days', 30)),  # New field
        'transactions_last_24h': int(transaction.get('transactions_last_24h', 5)),  # New field
        'amount_ratio': float(transaction.get('amount_ratio', 1.0)),
        'time_risk': float(transaction.get('time_risk', 0.5)),  # New field
        'velocity_score': float(transaction.get('velocity_score', 0)),
        'account_risk': float(transaction.get('account_risk', 0.5))  # New field
    }
    
    return features

def calculate_risk_score_ml(transaction, model, feature_names):
    """Use ML model to predict fraud probability"""
    
    # Prepare features
    features = prepare_features(transaction)
    
    # Create feature array in correct order
    feature_array = np.array([[features[name] for name in feature_names]])
    
    # Get prediction probability
    fraud_probability = float(model.predict_proba(feature_array)[0][1])  # Convert to Python float
    
    # Convert to 0-100 score
    ml_score = int(fraud_probability * 100)
    
    return ml_score, fraud_probability

def make_decision(ml_score):
    """Determine action based on ML score"""
    if ml_score < 30:
        return "APPROVE", "Low risk - transaction approved"
    elif ml_score < 60:
        return "REVIEW", "Medium risk - manual review required"
    else:
        return "BLOCK", "High risk - transaction blocked"

def lambda_handler(event, context):
    """Main Lambda handler"""
    
    try:
        # Load model (cached after first invocation)
        model, feature_names = load_model()
        
        # Parse request
        if isinstance(event.get('body'), str):
            transaction = json.loads(event['body'])
        else:
            transaction = event.get('body', event)
        
        print(f"Processing transaction: {transaction.get('transaction_id', 'unknown')}")
        
        # Get ML prediction
        ml_score, fraud_probability = calculate_risk_score_ml(transaction, model, feature_names)
        
        # Make decision
        decision, reason = make_decision(ml_score)
        
        # Prepare response
        response = {
    'transaction_id': transaction.get('transaction_id', 'unknown'),
    'ml_fraud_score': ml_score,
    'fraud_probability': float(round(fraud_probability, 4)),  # Keep as float for JSON
    'decision': decision,
    'reason': reason,
    'model_version': 'xgboost-v1.0',
    'timestamp': transaction.get('timestamp', ''),
    'details': {
        'amount': float(transaction.get('amount', 0)),  # Convert to float
        'type': transaction.get('transaction_type'),
        'is_international': transaction.get('is_international', False)
    }
}
        
        print(f"Decision: {decision} (ML Score: {ml_score})")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error during fraud detection'
            })
        }