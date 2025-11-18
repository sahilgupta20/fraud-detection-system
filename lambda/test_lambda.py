"""
Test Lambda function with sample transaction
"""
import boto3
import json

REGION = 'ap-south-1'
FUNCTION_NAME = 'fraud-detection-ml'

lambda_client = boto3.client('lambda', region_name=REGION)

print("=" * 70)
print("TESTING ML FRAUD DETECTION LAMBDA")
print("=" * 70)

# Test transaction (high risk)
test_transaction = {
    "transaction_id": "tx_test_001",
    "user_id": "user_12345",
    "amount": 15000,
    "transaction_type": "transfer",
    "is_international": True,
    "hour": 3,
    "day_of_week": 2,
    "location": "international",
    "merchant_category": "online",
    "new_payee": True,
    "amount_ratio": 5.0,
    "velocity_score": 8,
    "failed_attempts": 0,
    "unusual_location": True,
    "device_change": False,
    "high_risk_country": True,
    "weekend_transaction": False,
    "timestamp": "2025-11-11T19:30:00Z"
}

print("\n Sending test transaction:")
print(json.dumps(test_transaction, indent=2))

print("\n Invoking Lambda function...")

response = lambda_client.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType='RequestResponse',
    Payload=json.dumps(test_transaction)
)

print(f"   Status Code: {response['StatusCode']}")

result = json.loads(response['Payload'].read())

print("\n Response:")
print(json.dumps(result, indent=2))

if response['StatusCode'] == 200:
    print("\n" + "=" * 70)
    print(" TEST SUCCESSFUL!")
    print("=" * 70)
    
    if 'body' in result:
        body = json.loads(result['body'])
        print(f"\n Decision: {body.get('decision')}")
        print(f" ML Fraud Score: {body.get('ml_fraud_score')}")
        print(f" Probability: {body.get('fraud_probability')}")
        print(f" Reason: {body.get('reason')}")
else:
    print("\n TEST FAILED")