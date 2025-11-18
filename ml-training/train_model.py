"""
Train XGBoost fraud detection model using AWS SageMaker
"""
import boto3
import sagemaker
from sagemaker.xgboost import XGBoost
from sagemaker.inputs import TrainingInput
import pandas as pd
import time

# Configuration
BUCKET_NAME = 'fraud-ml-data-sahil-2024'  # Change if you used different name
REGION = 'ap-south-1'

print("=" * 70)
print("FRAUD DETECTION ML - SAGEMAKER TRAINING")
print("=" * 70)

# Initialize
boto_session = boto3.Session(region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto_session)
sts = boto3.client('sts', region_name=REGION)
account_id = sts.get_caller_identity()['Account']

print(f"\n AWS Account: {account_id}")
print(f" Region: {REGION}")
print(f" S3 Bucket: {BUCKET_NAME}")

# Create IAM role for SageMaker
def create_sagemaker_role():
    """Create IAM role for SageMaker training"""
    iam = boto3.client('iam', region_name=REGION)
    role_name = 'SageMakerFraudDetectionRole'
    
    try:
        role = iam.get_role(RoleName=role_name)
        print(f"\n✅ Using existing IAM role: {role_name}")
        return role['Role']['Arn']
    except:
        print(f"\n⏳ Creating IAM role: {role_name}...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        import json
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='SageMaker fraud detection role'
        )
        
        # Attach policies
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
        )
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        
        print(f" IAM role created")
        print(" Waiting 15 seconds for role to propagate...")
        time.sleep(15)
        
        return role['Role']['Arn']

# Prepare data
def prepare_data():
    """Convert data to XGBoost format"""
    print("\n Preparing training data...")
    
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        # Download from S3
        s3.download_file(BUCKET_NAME, 'training/fraud_training_data.csv', 'data.csv')
    except Exception as e:
        print(f" Error downloading data: {e}")
        print(f"   Make sure file exists at: s3://{BUCKET_NAME}/training/fraud_training_data.csv")
        raise
    
    # Load and process
    df = pd.read_csv('data.csv')
    print(f"   Loaded {len(df)} transactions")
    
    # Convert categorical to numeric
    df['transaction_type'] = df['transaction_type'].astype('category').cat.codes
    df['location'] = df['location'].astype('category').cat.codes  
    df['merchant_category'] = df['merchant_category'].astype('category').cat.codes
    df['is_international'] = df['is_international'].astype(int)
    df['new_payee'] = df['new_payee'].astype(int)
    
    # Remove non-feature columns
    df = df.drop('user_id', axis=1)
    
    # XGBoost format: label first
    cols = ['is_fraud'] + [c for c in df.columns if c != 'is_fraud']
    df = df[cols]
    
    # Split 80/20
    train_size = int(0.8 * len(df))
    train_df = df[:train_size]
    val_df = df[train_size:]
    
    print(f"   Training: {len(train_df)}")
    print(f"   Validation: {len(val_df)}")
    
    # Save as CSV (no headers for XGBoost)
    train_df.to_csv('train.csv', index=False, header=False)
    val_df.to_csv('validation.csv', index=False, header=False)
    
    # Upload to S3
    s3.upload_file('train.csv', BUCKET_NAME, 'training/xgboost/train.csv')
    s3.upload_file('validation.csv', BUCKET_NAME, 'training/xgboost/validation.csv')
    
    print(f" Data prepared and uploaded to S3")

def train_model(role_arn):
    """Start SageMaker training job"""
    print("\n Starting SageMaker training job...")
    print("   Instance: ml.m5.xlarge")
    print("   Cost: ~$0.23/hour (runs ~15 min = $0.06)")
    print("   Algorithm: XGBoost")
    
    # Use built-in XGBoost algorithm
    from sagemaker import image_uris
    container = image_uris.retrieve('xgboost', REGION, '1.7-1')
    
    # Create estimator
    xgb = sagemaker.estimator.Estimator(
        container,
        role=role_arn,
        instance_count=1,
        instance_type='ml.t3.medium',
        output_path=f's3://{BUCKET_NAME}/output',
        sagemaker_session=sagemaker_session
    )
    
    # Set hyperparameters
    xgb.set_hyperparameters(
        objective='binary:logistic',
        num_round=100,
        max_depth=5,
        eta=0.2,
        eval_metric='auc',
    )
    
    # Training data channels
    train_input = TrainingInput(
        f's3://{BUCKET_NAME}/training/xgboost/train.csv',
        content_type='text/csv'
    )
    val_input = TrainingInput(
        f's3://{BUCKET_NAME}/training/xgboost/validation.csv',
        content_type='text/csv'
    )
    
    print("\nTraining started (takes ~15 minutes)...")
    print("\n   Watch progress at:")
    print(f"   https://console.aws.amazon.com/sagemaker/home?region={REGION}#/jobs")
    
    # Start training
    xgb.fit({'train': train_input, 'validation': val_input}, wait=True)
    
    return xgb

# Main
try:
    role_arn = create_sagemaker_role()
    prepare_data()
    xgb_model = train_model(role_arn)
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\nModel saved to:")
    print(f"s3://{BUCKET_NAME}/output/{xgb_model.latest_training_job.name}/output/model.tar.gz")
    print("\n📊 Next: Download model and deploy to Lambda!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()