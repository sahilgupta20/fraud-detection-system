"""
Generate synthetic fraud transaction data for ML training
Creates realistic transaction patterns with fraud indicators
"""
import json
import random
import csv
from datetime import datetime, timedelta
from decimal import Decimal

def generate_user_profile():
    """Generate a user with typical behavior patterns"""
    return {
        'user_id': f"user_{random.randint(1000, 9999)}",
        'avg_amount': random.choice([50, 100, 200, 500, 1000]),  # Typical spending
        'typical_hours': random.choice(['morning', 'afternoon', 'evening']),
        'usual_location': random.choice(['US', 'CA', 'UK', 'AU']),
        'account_age_days': random.randint(30, 3650),  # 1 month to 10 years
        'transactions_per_week': random.randint(1, 10)
    }

def generate_legitimate_transaction(user_profile):
    """Generate a normal, non-fraudulent transaction"""
    # Amount close to user's typical spending
    amount = user_profile['avg_amount'] * random.uniform(0.5, 2.0)
    
    # Transaction during typical hours
    hour = {
        'morning': random.randint(6, 11),
        'afternoon': random.randint(12, 17),
        'evening': random.randint(18, 22)
    }[user_profile['typical_hours']]
    
    transaction = {
        'user_id': user_profile['user_id'],
        'amount': round(amount, 2),
        'transaction_type': random.choice(['debit_card', 'debit_card', 'credit_card', 'ach']),
        'is_international': False if random.random() > 0.1 else True,  # 10% international
        'new_payee': False if random.random() > 0.2 else True,  # 20% new payees
        'hour': hour,
        'day_of_week': random.randint(0, 6),
        'location': user_profile['usual_location'],
        'merchant_category': random.choice(['groceries', 'gas', 'restaurant', 'retail', 'utilities']),
        'failed_login_attempts': 0,
        'account_age_days': user_profile['account_age_days'],
        'transactions_last_24h': random.randint(1, 3),
        'is_fraud': 0
    }
    
    return transaction

def generate_fraud_pattern_1(user_profile):
    """Pattern 1: Large amount + International + New payee"""
    amount = user_profile['avg_amount'] * random.uniform(10, 50)  # 10-50x normal!
    
    transaction = {
        'user_id': user_profile['user_id'],
        'amount': round(amount, 2),
        'transaction_type': 'wire_transfer',
        'is_international': True,  # International
        'new_payee': True,  # New recipient
        'hour': random.randint(0, 5),  # Late night
        'day_of_week': random.randint(0, 6),
        'location': random.choice(['CN', 'RU', 'NG', 'RO']),  # High-risk countries
        'merchant_category': 'wire_transfer',
        'failed_login_attempts': random.randint(2, 5),  # Multiple failed logins
        'account_age_days': user_profile['account_age_days'],
        'transactions_last_24h': random.randint(5, 15),  # High velocity
        'is_fraud': 1
    }
    
    return transaction

def generate_fraud_pattern_2(user_profile):
    """Pattern 2: Multiple transactions just below threshold"""
    amount = 9500 + random.uniform(0, 499)  # Just below $10k threshold
    
    transaction = {
        'user_id': user_profile['user_id'],
        'amount': round(amount, 2),
        'transaction_type': random.choice(['wire_transfer', 'cryptocurrency']),
        'is_international': True,
        'new_payee': True,
        'hour': random.randint(0, 23),
        'day_of_week': random.randint(0, 6),
        'location': user_profile['usual_location'],
        'merchant_category': 'cryptocurrency' if random.random() > 0.5 else 'wire_transfer',
        'failed_login_attempts': random.randint(1, 3),
        'account_age_days': user_profile['account_age_days'],
        'transactions_last_24h': random.randint(8, 20),  # Very high velocity
        'is_fraud': 1
    }
    
    return transaction

def generate_fraud_pattern_3(user_profile):
    """Pattern 3: Sudden behavior change (account takeover)"""
    # New device, new location, unusual amount
    amount = user_profile['avg_amount'] * random.uniform(5, 20)
    
    transaction = {
        'user_id': user_profile['user_id'],
        'amount': round(amount, 2),
        'transaction_type': random.choice(['debit_card', 'wire_transfer']),
        'is_international': True,
        'new_payee': True,
        'hour': random.randint(0, 5),  # Unusual time
        'day_of_week': random.randint(0, 6),
        'location': random.choice(['BR', 'PH', 'VN', 'ID']),  # Different location
        'merchant_category': random.choice(['electronics', 'jewelry', 'cash_withdrawal']),
        'failed_login_attempts': random.randint(3, 8),  # Many failed attempts
        'account_age_days': user_profile['account_age_days'],
        'transactions_last_24h': random.randint(10, 25),  # Burst of activity
        'is_fraud': 1
    }
    
    return transaction

def generate_dataset(num_transactions=10000, fraud_rate=0.05):
    """Generate complete dataset with mix of legitimate and fraud transactions"""
    print(f"Generating {num_transactions} transactions...")
    print(f"Fraud rate: {fraud_rate * 100}%")
    
    transactions = []
    num_fraud = int(num_transactions * fraud_rate)
    num_legitimate = num_transactions - num_fraud
    
    # Create user profiles
    num_users = 1000
    user_profiles = [generate_user_profile() for _ in range(num_users)]
    
    # Generate legitimate transactions
    print(f"\nGenerating {num_legitimate} legitimate transactions...")
    for i in range(num_legitimate):
        user = random.choice(user_profiles)
        transaction = generate_legitimate_transaction(user)
        transactions.append(transaction)
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1}/{num_legitimate} legitimate transactions")
    
    # Generate fraud transactions (mix of patterns)
    print(f"\nGenerating {num_fraud} fraud transactions...")
    fraud_patterns = [
        generate_fraud_pattern_1,
        generate_fraud_pattern_2,
        generate_fraud_pattern_3
    ]
    
    for i in range(num_fraud):
        user = random.choice(user_profiles)
        pattern = random.choice(fraud_patterns)
        transaction = pattern(user)
        transactions.append(transaction)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_fraud} fraud transactions")
    
    # Shuffle transactions
    random.shuffle(transactions)
    
    print(f"\n✅ Generated {len(transactions)} total transactions")
    print(f"   - Legitimate: {num_legitimate}")
    print(f"   - Fraud: {num_fraud}")
    
    return transactions

def calculate_features(transaction):
    """Calculate derived features for ML"""
    # Amount ratio (how much more than typical)
    typical_amounts = {'groceries': 100, 'gas': 50, 'restaurant': 40, 'retail': 150, 
                       'utilities': 80, 'wire_transfer': 500, 'cryptocurrency': 1000,
                       'electronics': 500, 'jewelry': 1000, 'cash_withdrawal': 200}
    
    typical = typical_amounts.get(transaction['merchant_category'], 100)
    transaction['amount_ratio'] = round(transaction['amount'] / typical, 2)
    
    # Time risk (0-10 scale, higher = riskier)
    hour = transaction['hour']
    if 0 <= hour <= 5:
        transaction['time_risk'] = 10  # Late night = high risk
    elif 6 <= hour <= 9:
        transaction['time_risk'] = 3
    elif 10 <= hour <= 17:
        transaction['time_risk'] = 1  # Business hours = low risk
    elif 18 <= hour <= 22:
        transaction['time_risk'] = 2
    else:
        transaction['time_risk'] = 7
    
    # Velocity score
    transaction['velocity_score'] = min(transaction['transactions_last_24h'], 20)
    
    # Account risk (newer = riskier)
    if transaction['account_age_days'] < 30:
        transaction['account_risk'] = 10
    elif transaction['account_age_days'] < 180:
        transaction['account_risk'] = 5
    else:
        transaction['account_risk'] = 1
    
    return transaction

def save_to_csv(transactions, filename='fraud_training_data.csv'):
    """Save transactions to CSV file"""
    print(f"\nSaving to {filename}...")
    
    # Calculate features for all transactions
    transactions_with_features = [calculate_features(t) for t in transactions]
    
    # Define field order
    fieldnames = [
        'user_id', 'amount', 'transaction_type', 'is_international', 'new_payee',
        'hour', 'day_of_week', 'location', 'merchant_category', 'failed_login_attempts',
        'account_age_days', 'transactions_last_24h', 'amount_ratio', 'time_risk',
        'velocity_score', 'account_risk', 'is_fraud'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions_with_features)
    
    print(f"✅ Saved {len(transactions)} transactions to {filename}")
    
    # Print statistics
    fraud_count = sum(1 for t in transactions if t['is_fraud'] == 1)
    print(f"\n Dataset Statistics:")
    print(f"   Total transactions: {len(transactions)}")
    print(f"   Legitimate: {len(transactions) - fraud_count} ({((len(transactions) - fraud_count) / len(transactions) * 100):.1f}%)")
    print(f"   Fraud: {fraud_count} ({(fraud_count / len(transactions) * 100):.1f}%)")
    print(f"   File size: {round(len(open(filename, 'rb').read()) / 1024 / 1024, 2)} MB")

def main():
    """Main execution"""
    print("=" * 60)
    print("FRAUD DETECTION ML - TRAINING DATA GENERATOR")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate dataset
    transactions = generate_dataset(
        num_transactions=10000,  # 10K transactions
        fraud_rate=0.05  # 5% fraud rate (realistic)
    )
    
    # Save to CSV
    save_to_csv(transactions)
    
    print("\n Data generation complete!")
    print("\nNext steps:")
    print("1. Review fraud_training_data.csv")
    print("2. Upload to S3")
    print("3. Train model in SageMaker")

if __name__ == "__main__":
    main()