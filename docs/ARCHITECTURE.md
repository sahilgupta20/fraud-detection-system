\# System Architecture



\## High-Level Overview



This document describes the architecture of the Real-Time Fraud Detection System.



\## Components



\### 1. Lambda Function (`fraud-detection-validator`)

\*\*Purpose:\*\* Core fraud detection logic

\*\*Runtime:\*\* Python 3.11

\*\*Memory:\*\* 256 MB

\*\*Timeout:\*\* 30 seconds



\*\*Responsibilities:\*\*

\- Parse incoming transaction data

\- Calculate risk score using multi-factor algorithm

\- Make approve/review/block decision

\- Store transaction in DynamoDB

\- Generate alerts for high-risk transactions



\### 2. DynamoDB Tables



\#### transactions Table

\*\*Purpose:\*\* Store all transaction records

\*\*Partition Key:\*\* transaction\_id

\*\*Sort Key:\*\* timestamp



\*\*Indexes:\*\*

\- UserIdIndex - Query by user

\- RiskScoreIndex - Query by risk level



\*\*Features:\*\*

\- Streams enabled (real-time processing)

\- Point-in-time recovery

\- TTL enabled (90-day retention)



\#### alerts Table

\*\*Purpose:\*\* Store fraud alerts

\*\*Partition Key:\*\* alert\_id

\*\*Sort Key:\*\* created\_at



\*\*Indexes:\*\*

\- TransactionIdIndex - Link to transaction

\- StatusIndex - Query by alert status



\### 3. IAM Roles \& Policies



\*\*lambda\_execution\_role:\*\*

\- Allows Lambda to write CloudWatch logs

\- Grants read/write access to DynamoDB tables

\- Follows least-privilege principle



\### 4. CloudWatch



\*\*Log Groups:\*\*

\- `/aws/lambda/fraud-detection-validator` - 7-day retention



\*\*Metrics:\*\*

\- Lambda invocations

\- Error rates

\- Duration

\- DynamoDB consumed capacity



\## Data Flow



1\. Transaction submitted to Lambda

2\. Lambda calculates risk score

3\. Decision made (Approve/Review/Block)

4\. Transaction saved to DynamoDB

5\. Alert created if risk >= 40

6\. Response returned to caller



\## Security



\- No public endpoints (yet - API Gateway coming)

\- IAM role-based access

\- Encryption at rest

\- CloudWatch logging for audit trail



\## Scalability



\- Lambda: Auto-scales to thousands of concurrent executions

\- DynamoDB: PAY\_PER\_REQUEST mode handles variable load

\- No manual capacity planning needed



\## Cost Optimization



\- Serverless = pay only for what you use

\- Free tier covers dev/demo usage

\- No idle resources



\## Future Enhancements



\- API Gateway for HTTP access

\- SNS for alert notifications

\- SageMaker for ML-based scoring

\- Kinesis for streaming analytics

