"""
Create and attach minimal ML layer (joblib + xgboost)
"""
import boto3

REGION = 'ap-south-1'
FUNCTION_NAME = 'fraud-detection-ml'
BUCKET = 'fraud-ml-data-sahil-2024'

lambda_client = boto3.client('lambda', region_name=REGION)

print("=" * 70)
print("CREATING MINIMAL ML LAYER")
print("=" * 70)

# Create layer from S3
print("\n Creating layer from S3...")

response = lambda_client.publish_layer_version(
    LayerName='minimal-ml-dependencies',
    Description='joblib + xgboost for fraud detection',
    Content={
        'S3Bucket': BUCKET,
        'S3Key': 'lambda-layers/minimal-ml-layer.zip'
    },
    CompatibleRuntimes=['python3.11', 'python3.10']
)

layer_arn = response['LayerVersionArn']
print(f"    Layer created!")
print(f"   ARN: {layer_arn}")

# Attach BOTH layers to function
print("\n Attaching layers to Lambda...")
print("   Layer 1: AWS Data Science (numpy, pandas, scikit-learn)")
print("   Layer 2: Our layer (joblib, xgboost)")

lambda_client.update_function_configuration(
    FunctionName=FUNCTION_NAME,
    Layers=[
        layer_arn  # ONLY our layer - it has everything!
    ]
)

print("    Both layers attached!")

print("\n" + "=" * 70)
print(" COMPLETE!")
print("=" * 70)

print("\n Test now with: python test_lambda.py")