"""
Unit tests for fraud detection Lambda function
"""
import json
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock AWS services before importing lambda_function
from moto import mock_dynamodb
import boto3
import pytest

# Import your Lambda function
from lambda_function import calculate_risk_score, lambda_handler


class TestRiskScoring:
    """Test risk score calculation logic"""
    
    def test_low_risk_transaction(self):
        """Test that small transactions get low risk scores"""
        transaction = {
            'amount': 100,
            'transaction_type': 'debit_card',
            'is_international': False,
            'new_payee': False
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score < 40, "Small local transaction should be low risk"
    
    def test_high_amount_risk(self):
        """Test that large amounts increase risk"""
        transaction = {
            'amount': 15000,
            'transaction_type': 'debit_card',
            'is_international': False,
            'new_payee': False
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score >= 40, "Large amount should increase risk"
    
    def test_international_risk(self):
        """Test that international transfers increase risk"""
        transaction = {
            'amount': 5000,
            'transaction_type': 'wire_transfer',
            'is_international': True,
            'new_payee': False
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score >= 40, "International wire should be medium risk"
    
    def test_high_risk_transaction(self):
        """Test that multiple risk factors add up correctly"""
        transaction = {
            'amount': 15000,
            'transaction_type': 'wire_transfer',
            'is_international': True,
            'new_payee': True
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score >= 70, "Multiple risk factors should result in high risk"
    
    def test_risk_score_capped_at_100(self):
        """Test that risk score never exceeds 100"""
        transaction = {
            'amount': 999999,
            'transaction_type': 'cryptocurrency',
            'is_international': True,
            'new_payee': True
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score <= 100, "Risk score should be capped at 100"
    
    def test_wire_transfer_risk(self):
        """Test that wire transfers are considered risky"""
        transaction = {
            'amount': 5000,
            'transaction_type': 'wire_transfer',
            'is_international': False,
            'new_payee': False
        }
        
        risk_score = calculate_risk_score(transaction)
        assert risk_score > 0, "Wire transfer should add risk points"
    
    def test_new_payee_risk(self):
        """Test that new payees increase risk"""
        transaction1 = {
            'amount': 1000,
            'transaction_type': 'debit_card',
            'is_international': False,
            'new_payee': False
        }
        
        transaction2 = {
            'amount': 1000,
            'transaction_type': 'debit_card',
            'is_international': False,
            'new_payee': True
        }
        
        score1 = calculate_risk_score(transaction1)
        score2 = calculate_risk_score(transaction2)
        
        assert score2 > score1, "New payee should increase risk score"


@mock_dynamodb
class TestLambdaHandler:
    """Test the Lambda handler function"""
    
    def setup_method(self):
        """Set up mock DynamoDB tables before each test"""
        # Create mock DynamoDB resource
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        # Create mock tables
        self.transactions_table = self.dynamodb.create_table(
            TableName='fraud-detection-transactions',
            KeySchema=[
                {'AttributeName': 'transaction_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'transaction_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'risk_score', 'AttributeType': 'N'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        self.alerts_table = self.dynamodb.create_table(
            TableName='fraud-detection-alerts',
            KeySchema=[
                {'AttributeName': 'alert_id', 'KeyType': 'HASH'},
                {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'alert_id', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'S'},
                {'AttributeName': 'transaction_id', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'TransactionIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'transaction_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Set environment variables
        os.environ['TRANSACTIONS_TABLE'] = 'fraud-detection-transactions'
        os.environ['ALERTS_TABLE'] = 'fraud-detection-alerts'
    
    def test_lambda_handler_approved(self):
        """Test Lambda handler with low-risk transaction"""
        event = {
            'amount': 500,
            'transaction_type': 'debit_card',
            'user_id': 'test_user_123',
            'is_international': False,
            'new_payee': False
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'APPROVED'
        assert body['risk_score'] < 40
    
    def test_lambda_handler_blocked(self):
        """Test Lambda handler with high-risk transaction"""
        event = {
            'amount': 15000,
            'transaction_type': 'wire_transfer',
            'user_id': 'test_user_456',
            'is_international': True,
            'new_payee': True
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'BLOCKED'
        assert body['risk_score'] >= 70
    
    def test_lambda_handler_creates_alert(self):
        """Test that high-risk transactions create alerts"""
        event = {
            'amount': 8000,
            'transaction_type': 'wire_transfer',
            'user_id': 'test_user_789',
            'is_international': False,
            'new_payee': True
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        # Should create alert for medium/high risk
        if body['risk_score'] >= 40:
            # Check that alert was created in mock DynamoDB
            alerts_table = self.dynamodb.Table('fraud-detection-alerts')
            response = alerts_table.scan()
            assert response['Count'] >= 1, "Alert should be created for medium/high risk"
    
    def test_lambda_handler_error_handling(self):
        """Test Lambda handler error handling"""
        event = {
            'amount': 'invalid',  # Invalid amount
            'transaction_type': 'debit_card'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body


if __name__ == '__main__':
    pytest.main([__file__, '-v'])