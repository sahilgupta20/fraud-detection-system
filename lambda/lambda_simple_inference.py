import json
import boto3
import pickle

s3 = boto3.client('s3')
model = None

def load_model():
    global model
    if model is None:
        obj = s3.get_object(Bucket='fraud-ml-data-sahil-2024', Key='models/fraud_model.pkl')
        model = pickle.loads(obj['Body'].read())
    return model

def lambda_handler(event, context):
    try:
        ml_model = load_model()
        
        # Parse transaction
        transaction = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        # Simple feature extraction (adjust to your model's features)
        features = [[
            float(transaction.get('amount', 0)),
            1 if transaction.get('is_international', False) else 0,
            int(transaction.get('hour', 12)),
            float(transaction.get('velocity_score', 0)),
            1 if transaction.get('new_payee', False) else 0
        ]]
        
        # Predict
        fraud_prob = float(ml_model.predict_proba(features)[0][1])
        ml_score = int(fraud_prob * 100)
        
        decision = "BLOCK" if ml_score > 70 else "REVIEW" if ml_score > 40 else "APPROVE"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'transaction_id': transaction.get('transaction_id'),
                'ml_fraud_score': ml_score,
                'fraud_probability': round(fraud_prob, 4),
                'decision': decision,
                'model_version': 'local-trained-v1.0'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }