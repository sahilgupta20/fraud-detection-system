import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB connection
dynamodb = boto3.resource('dynamodb')
transactions_table = dynamodb.Table(os.environ.get('TRANSACTIONS_TABLE', 'fraud-detection-transactions'))
alerts_table = dynamodb.Table(os.environ.get('ALERTS_TABLE', 'fraud-detection-alerts'))

def calculate_risk_score(transaction):
    """
    Calculate fraud risk score (0-100) based on transaction characteristics
    Higher score = Higher fraud risk
    """
    risk_score = 0
    
    # Factor 1: Transaction Amount
    amount = float(transaction.get('amount', 0))
    if amount > 10000:
        risk_score += 40  # Very high amount
    elif amount > 5000:
        risk_score += 25  # High amount
    elif amount > 1000:
        risk_score += 10  # Medium amount
    
    # Factor 2: International Transfer
    if transaction.get('is_international', False):
        risk_score += 20  # Cross-border transactions are riskier
    
    # Factor 3: Transaction Type
    high_risk_types = ['wire_transfer', 'cryptocurrency', 'cash_withdrawal']
    if transaction.get('transaction_type') in high_risk_types:
        risk_score += 15  # These types are commonly used in fraud
    
    # Factor 4: Time of Day (Off-hours transactions)
    hour = datetime.now().hour
    if hour >= 21 or hour <= 6:  # Between 9 PM and 6 AM
        risk_score += 10  # Fraudsters often work at night
    
    # Factor 5: New Payee
    if transaction.get('new_payee', False):
        risk_score += 15  # First-time recipients are riskier
    
    return min(risk_score, 100)  # Cap at 100

def lambda_handler(event, context):
    """
    Main function that AWS Lambda calls
    This processes each transaction and determines if it's fraudulent
    """
    
    try:
        # Parse incoming transaction data
        if isinstance(event.get('body'), str):
            transaction = json.loads(event['body'])
        else:
            transaction = event
        
        # Generate unique transaction ID
        if 'transaction_id' not in transaction:
            transaction['transaction_id'] = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Add timestamp
        transaction['timestamp'] = datetime.now().isoformat()
        
        # Calculate fraud risk score
        risk_score = calculate_risk_score(transaction)
        transaction['risk_score'] = risk_score
        
        # Decide what to do based on risk score
        if risk_score >= 70:
            transaction['status'] = 'BLOCKED'
            alert_severity = 'HIGH'
        elif risk_score >= 40:
            transaction['status'] = 'REVIEW_REQUIRED'
            alert_severity = 'MEDIUM'
        else:
            transaction['status'] = 'APPROVED'
            alert_severity = 'LOW'
        
        # Convert numbers to Decimal (required by DynamoDB)
        transaction['amount'] = Decimal(str(transaction.get('amount', 0)))
        transaction['risk_score'] = Decimal(str(risk_score))
        
        # Set expiry time (90 days from now)
        expiry_timestamp = int(datetime.now().timestamp()) + (90 * 24 * 60 * 60)
        transaction['expiry_time'] = expiry_timestamp
        
        # Save transaction to DynamoDB
        transactions_table.put_item(Item=transaction)
        
        # Create alert if risk score is high or medium
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
            alerts_table.put_item(Item=alert)
        
        # Return success response
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
        # Handle errors gracefully
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