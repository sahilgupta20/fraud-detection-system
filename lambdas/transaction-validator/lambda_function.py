import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

from decimal import Decimal

def convert_floats_to_decimal(obj):

    if isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

dynamodb = boto3.resource('dynamodb')
transactions_table = dynamodb.Table(os.environ.get('TRANSACTIONS_TABLE', 'fraud-detection-transactions'))
alerts_table = dynamodb.Table(os.environ.get('ALERTS_TABLE', 'fraud-detection-alerts'))

def calculate_risk_score(transaction):

    risk_score = 0

    amount = float(transaction.get('amount', 0))
    if amount > 10000:
        risk_score += 40  # Very high amount
    elif amount > 5000:
        risk_score += 25  # High amount
    elif amount > 1000:
        risk_score += 10  # Medium amount

    if transaction.get('is_international', False):
        risk_score += 20  

    high_risk_types = ['wire_transfer', 'cryptocurrency', 'cash_withdrawal']
    if transaction.get('transaction_type') in high_risk_types:
        risk_score += 15  

    hour = datetime.now().hour
    if hour >= 21 or hour <= 6:  # Between 9 PM and 6 AM
        risk_score += 10 

    if transaction.get('new_payee', False):
        risk_score += 15 
    
    return min(risk_score, 100)  # Cap at 100

def lambda_handler(event, context):
   
    
    try:
        if isinstance(event.get('body'), str):
            transaction = json.loads(event['body'])
        else:
            transaction = event

        if 'transaction_id' not in transaction:
            transaction['transaction_id'] = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        

        transaction['timestamp'] = datetime.now().isoformat()

        risk_score = calculate_risk_score(transaction)
        transaction['risk_score'] = risk_score

        if risk_score >= 70:
            transaction['status'] = 'BLOCKED'
            alert_severity = 'HIGH'
        elif risk_score >= 40:
            transaction['status'] = 'REVIEW_REQUIRED'
            alert_severity = 'MEDIUM'
        else:
            transaction['status'] = 'APPROVED'
            alert_severity = 'LOW'

        transaction['amount'] = Decimal(str(transaction.get('amount', 0)))
        transaction['risk_score'] = Decimal(str(risk_score))
 
        expiry_timestamp = int(datetime.now().timestamp()) + (90 * 24 * 60 * 60)
        transaction['expiry_time'] = expiry_timestamp

        transactions_table.put_item(Item=convert_floats_to_decimal(transaction))

        if risk_score >= 40:
            alert = {
                'alert_id': f"ALERT-{transaction['transaction_id']}",
                'transaction_id': transaction['transaction_id'],
                'created_at': datetime.now().isoformat(),
                'severity': alert_severity,
                'risk_score': Decimal(str(risk_score)),
                'status': 'OPEN',
                'alert_type': 'HIGH_RISK_TRANSACTION',
                'description': f"Transaction flagged with risk score of {risk_score}"
            }
            alerts_table.put_item(Item=convert_floats_to_decimal(alert))

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'transaction_id': transaction['transaction_id'],
                'status': transaction['status'],
                'risk_score': risk_score,
                'message': f'Transaction processed with risk score: {risk_score}'
            })
        }
    
    except Exception as e:
        print(f"Error processing transaction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process transaction'
            })
        }