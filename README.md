# Fraud Detection System

Real-time ML system that scores transactions and decides whether to approve, review, or block them.

**Demo:** http://fraud-detection-dashboard-sahil.s3-website.ap-south-1.amazonaws.com

## What it does

You submit a transaction → Lambda runs it through an XGBoost model → you get a risk score (0-100) and a decision.

High-risk transaction (large wire transfer, new payee, international, odd hours) gets blocked. Normal purchase goes through.

## How it works
```
Dashboard → API Gateway → Lambda (validation) → Lambda (ML inference) → DynamoDB
                                                        ↓
                                                   S3 (model file)
```

Two Lambda functions. First one validates the request. Second one loads the model from S3 and runs inference. Results get logged to DynamoDB.

## Tech

- Python, XGBoost, scikit-learn
- AWS Lambda, API Gateway, DynamoDB, S3
- Vanilla JS frontend, Chart.js
- Terraform for infrastructure

## Model stats

Trained on 10k synthetic transactions. 96% accuracy, 92% recall. Good enough for a demo, wouldn't trust it with real money.

Training takes about 2 minutes on a laptop. Most of the project time went into deployment, not the model.

## API

POST to `https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/prod/transactions`
```json
{
  "amount": 5000,
  "transaction_type": "wire_transfer",
  "user_id": "user_123",
  "is_international": true,
  "new_payee": true,
  "hour": 3,
  "day_of_week": 2
}
```

Returns:
```json
{
  "transaction_id": "tx_abc123",
  "risk_score": 85,
  "decision": "BLOCK"
}
```

Not all fields are required. The model uses 15 features total but has defaults for missing ones.

## Running locally
```bash
cd ml-training
pip install -r requirements.txt
python train_local.py
```

This spits out a model file. Upload it to S3 and point the Lambda at it.

## What's missing

- No authentication (API is open)
- No model retraining pipeline
- No monitoring beyond basic CloudWatch
- Cold starts are slow (~3s first request)

It's a portfolio project, not production software.

## Why I built this

Wanted to understand what goes into real-time fraud detection. Read about how Verafin does it at scale. Built a toy version to learn the basics.

The ML part was easy. The deployment part took 3 weeks.

## Structure
```
├── dashboard/        # frontend
├── lambda/           # lambda functions
├── ml-training/      # model training
├── infrastructure/   # terraform
```

## License

MIT

## Screenshots

### Live Dashboard
![Dashboard Demo](docs/screenshots/dashboard-demo.png)
*Real-time fraud detection with risk visualization*

### API Response
![API Response](docs/screenshots/api-response.png)
*JSON response showing fraud prediction*


