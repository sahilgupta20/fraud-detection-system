\# Real-Time Fraud Detection System



A cloud-native, serverless fraud detection platform built with AWS, inspired by Nasdaq Verafin's mission to combat financial crime. This system processes transactions in real-time, calculates risk scores and automatically blocks suspicious activity.



\[!\[AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB-orange)](https://aws.amazon.com/)

\[!\[Terraform](https://img.shields.io/badge/IaC-Terraform-purple)](https://www.terraform.io/)

\[!\[Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)



\## Project Overview



This fraud detection system demonstrates enterprise-grade architecture patterns used by financial institutions to prevent fraud before money moves. The system analyzes transaction patterns, calculates risk scores using multiple factors and makes real-time decisions to approve, flag for review or block transactions.



\### Key Features



\- \*\*Real-Time Processing\*\* - Sub-100ms transaction validation

\- \*\*Multi-Factor Risk Scoring\*\* - Analyzes 5+ fraud indicators

\- \*\*Automated Decision Engine\*\* - Approve, Review, or Block logic

\- \*\*Alert Generation\*\* - Automatic flagging of suspicious activity

\- \*\*Serverless Architecture\*\* - Auto-scaling, high availability

\- \*\*Infrastructure as Code\*\* - Fully automated deployment

\- \*\*Cost Optimized\*\* - 100% within AWS Free Tier



\## Architecture



\### System Components

```

┌─────────────────┐

│   Transaction   │

│     Input       │

└────────┬────────┘

&nbsp;        │

&nbsp;        ▼

┌─────────────────────────────────────┐

│      AWS Lambda Function            │

│  ┌──────────────────────────────┐   │

│  │   Risk Scoring Algorithm     │   │

│  │   • Amount Analysis          │   │

│  │   • Transaction Type         │   │

│  │   • Geographic Risk          │   │

│  │   • Time-based Patterns      │   │

│  │   • Payee Analysis           │   │

│  └──────────────────────────────┘   │

└───────────┬─────────────────────────┘

&nbsp;           │

&nbsp;           ▼

&nbsp;   ┌───────────────┐

&nbsp;   │   Decision    │

&nbsp;   │    Engine     │

&nbsp;   └───────┬───────┘

&nbsp;           │

&nbsp;   ┌───────┴────────┐

&nbsp;   │                │

&nbsp;   ▼                ▼

┌────────┐      ┌─────────┐

│Approve │      │ Block/  │

│        │      │ Review  │

└───┬────┘      └────┬────┘

&nbsp;   │                │

&nbsp;   └────────┬───────┘

&nbsp;            │

&nbsp;            ▼

&nbsp;   ┌────────────────┐

&nbsp;   │   DynamoDB     │

&nbsp;   │  • Transactions│

&nbsp;   │  • Alerts      │

&nbsp;   └────────────────┘

```



\### Technology Stack



\*\*Cloud Infrastructure:\*\*

\- AWS Lambda - Serverless compute

\- Amazon DynamoDB - NoSQL database

\- Amazon CloudWatch - Monitoring \& logging

\- Amazon S3 - Terraform state management



\*\*Development:\*\*

\- Python 3.11 - Core logic

\- Terraform - Infrastructure as Code

\- AWS CLI - Deployment \& testing

\- Git - Version control



\## Risk Scoring Algorithm



The system calculates fraud risk on a 0-100 scale using multiple weighted factors:



| Factor | Threshold | Risk Points | Rationale |

|--------|-----------|-------------|-----------|

| \*\*Transaction Amount\*\* | >$10,000 | +40 | Large amounts are high-risk |

| | >$5,000 | +25 | Medium-high risk threshold |

| | >$1,000 | +10 | Elevated risk monitoring |

| \*\*International Transfer\*\* | Yes | +20 | Cross-border = higher fraud |

| \*\*Payment Type\*\* | Wire/Crypto/Cash | +15 | High-risk payment methods |

| \*\*Time of Transaction\*\* | 9PM - 6AM | +10 | Off-hours activity |

| \*\*New Payee\*\* | First-time recipient | +15 | Unknown recipient risk |



\### Decision Logic



\- \*\*0-39 points\*\*: APPROVED - Transaction proceeds

\- \*\*40-69 points\*\*: REVIEW REQUIRED - Manual investigation

\- \*\*70-100 points\*\*: BLOCKED - Transaction denied



\## Test Results



\### Test Case 1: Low-Risk Transaction

```json

Input: {

&nbsp; "amount": 500,

&nbsp; "transaction\_type": "debit\_card",

&nbsp; "is\_international": false

}



Output: {

&nbsp; "status": "APPROVED",

&nbsp; "risk\_score": 0

}

```



\### Test Case 2: Medium-Risk Transaction

```json

Input: {

&nbsp; "amount": 6000,

&nbsp; "transaction\_type": "wire\_transfer",

&nbsp; "new\_payee": true

}



Output: {

&nbsp; "status": "REVIEW\_REQUIRED",

&nbsp; "risk\_score": 55

}

```



\### Test Case 3: High-Risk Transaction

```json

Input: {

&nbsp; "amount": 15000,

&nbsp; "transaction\_type": "wire\_transfer",

&nbsp; "is\_international": true,

&nbsp; "new\_payee": true

}



Output: {

&nbsp; "status": "BLOCKED",

&nbsp; "risk\_score": 90

}

```



\## Deployment Guide



\### Prerequisites



\- AWS Account with Free Tier

\- AWS CLI configured

\- Terraform >= 1.0

\- Python >= 3.9



\### Step 1: Clone Repository

```bash

git clone https://github.com/sahilgupta20/fraud-detection-system.git

cd fraud-detection-system

```



\### Step 2: Configure AWS

```bash

aws configure

\# Enter your AWS Access Key, Secret Key, and region (ap-south-1)

```



\### Step 3: Create S3 Bucket for Terraform State

```bash

aws s3 mb s3://your-unique-bucket-name --region ap-south-1

```



Update `infrastructure/backend.tf` with your bucket name.



\### Step 4: Package Lambda Function

```bash

cd lambdas/transaction-validator

powershell Compress-Archive -Path lambda\_function.py -DestinationPath lambda.zip -Force

cd ../../infrastructure

```



\### Step 5: Deploy Infrastructure

```bash

terraform init

terraform plan

terraform apply -auto-approve

```



\### Step 6: Test the System

```bash

aws lambda invoke \\

&nbsp; --function-name fraud-detection-validator \\

&nbsp; --payload file://test1.json \\

&nbsp; --region ap-south-1 \\

&nbsp; response.json

```



##  API Documentation

### Live API Endpoint
```
POST https://[your-api-id].execute-api.ap-south-1.amazonaws.com/development/transactions
```

### Request Format

**Example Request:**
```json
{
  "amount": 5000,
  "transaction_type": "wire_transfer",
  "user_id": "user123",
  "is_international": false,
  "new_payee": true
}
```

### Response Format

**Success Response:**
```json
{
  "statusCode": 200,
  "body": {
    "transaction_id": "TXN-20251028163136",
    "status": "REVIEW_REQUIRED",
    "risk_score": 55,
    "message": "Transaction processed with risk score: 55"
  }
}
```

### Decision Logic

| Risk Score | Status | Action |
|------------|--------|--------|
| 0-39 | APPROVED  | Transaction proceeds |
| 40-69 | REVIEW_REQUIRED  | Manual investigation |
| 70-100 | BLOCKED  | Transaction denied |

### Testing the API

**cURL Example:**
```bash
curl -X POST "YOUR-API-ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"amount": 15000, "transaction_type": "wire_transfer", "is_international": true, "new_payee": true}'
```

**PowerShell Example:**
```powershell
$body = @{
    amount = 5000
    transaction_type = "wire_transfer"
    user_id = "user123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR-API-ENDPOINT" -Method POST -Body $body -ContentType "application/json"
```


\##  Roadmap



\### Phase 2: API Layer (In Progress)

\- \[ ] API Gateway REST API

\- \[ ] Authentication (API Keys)

\- \[ ] Rate limiting

\- \[ ] CORS configuration



\### Phase 3: Advanced Analytics

\- \[ ] Machine Learning model (SageMaker)

\- \[ ] Historical pattern analysis

\- \[ ] User behavior profiling

\- \[ ] Anomaly detection



\### Phase 4: Visualization Dashboard

\- \[ ] React frontend

\- \[ ] Real-time transaction monitoring

\- \[ ] Alert management interface

\- \[ ] Analytics dashboards



\### Phase 5: Enhanced Features

\- \[ ] Kinesis data streaming

\- \[ ] SNS notifications

\- \[ ] Multi-region deployment

\- \[ ] CI/CD pipeline



\## Project Structure

```

fraud-detection-system/

├── infrastructure/           # Terraform IaC

│   ├── main.tf              # Provider configuration

│   ├── variables.tf         # Input variables

│   ├── dynamodb.tf          # Database resources

│   ├── lambda.tf            # Lambda function

│   └── backend.tf           # Remote state config

├── lambdas/

│   └── transaction-validator/

│       ├── lambda\_function.py   # Core fraud detection logic

│       └── lambda.zip           # Deployment package

├── tests/                   # Test cases

│   ├── test1.json          # Low-risk test

│   ├── test2.json          # Medium-risk test

│   └── test3.json          # High-risk test

└── README.md               # This file

```



\## 🤝 Contributing



This is a portfolio/learning project. Suggestions and improvements are welcome!



\## 👤 Author



\*\*Sahil Gupta\*\*

\- GitHub: \[@sahilgupta20](https://github.com/sahilgupta20)

\- LinkedIn: \[Your Profile](https://www.linkedin.com/in/sahil-gupta-050336153/)

\- Email: sahilg@mun.ca



\## Acknowledgments



Inspired by \[Nasdaq Verafin](https://verafin.com/)'s mission to combat financial crime and protect vulnerable populations.



