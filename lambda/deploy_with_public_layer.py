"""
Deploy Lambda with AWS Data Wrangler Layer (has ML libraries)
"""
import boto3
import zipfile
import time

REGION = 'ap-south-1'
FUNCTION_NAME = 'fraud-detection-ml'
BUCKET_NAME = 'fraud-ml-data-sahil-2024'

lambda_client = boto3.client('lambda', region_name=REGION)
sts = boto3.client('sts', region_name=REGION)

account_id = sts.get_caller_identity()['Account']
role_arn = f"arn:aws:iam::{account_id}:role/FraudDetectionLambdaRole"

# AWS Data Wrangler layer (has numpy, pandas, etc)
# We'll add scikit-learn and xgboost manually
PUBLIC_LAYER_ARN = 'arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python311:13'

print("=" * 70)
print("DEPLOYING LAMBDA WITH ML LIBRARIES")
print("=" * 70)

# Create deployment package with just your code
print("\n Creating deployment package...")

with zipfile.ZipFile('lambda_deployment.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('lambda_ml_inference.py', 'lambda_function.py')

print("    Package created")

# Delete old function
print("\n  Removing old function...")
try:
    lambda_client.delete_function(FunctionName=FUNCTION_NAME)
    print("    Deleted")
    time.sleep(5)
except:
    print("     No function to delete")

# Create function
print("\n Creating Lambda function...")

with open('lambda_deployment.zip', 'rb') as f:
    response = lambda_client.create_function(
        FunctionName=FUNCTION_NAME,
        Runtime='python3.11',
        Role=role_arn,
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': f.read()},
        Layers=[PUBLIC_LAYER_ARN],  # AWS layer with some libraries
        Timeout=30,
        MemorySize=1024,
        Environment={
            'Variables': {
                'BUCKET_NAME': BUCKET_NAME
            }
        }
    )

print(f"    Function created!")
print(f"   ARN: {response['FunctionArn']}")

print("\n" + "=" * 70)
print(" DEPLOYMENT COMPLETE!")
print("=" * 70)

print("\n  NOTE: Testing if xgboost/joblib are available...")
print("   If test fails, we'll add a custom layer")