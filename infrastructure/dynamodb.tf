# Main transactions table
resource "aws_dynamodb_table" "transactions" {
  name           = "${var.project_name}-transactions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "transaction_id"
  range_key      = "timestamp"
  
  attribute {
    name = "transaction_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  attribute {
    name = "risk_score"
    type = "N"
  }
  
  # Enable streams for real-time processing
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # TTL for old transactions (optional - keeps data for 90 days)
  ttl {
    enabled        = true
    attribute_name = "expiry_time"
  }
  
  # Global Secondary Index for user lookup
  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  # Global Secondary Index for risk score queries
  global_secondary_index {
    name            = "RiskScoreIndex"
    hash_key        = "risk_score"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  tags = {
    Name = "${var.project_name}-transactions"
  }
}

# Alerts table for fraud alerts
resource "aws_dynamodb_table" "alerts" {
  name           = "${var.project_name}-alerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "alert_id"
  range_key      = "created_at"
  
  attribute {
    name = "alert_id"
    type = "S"
  }
  
  attribute {
    name = "created_at"
    type = "S"
  }
  
  attribute {
    name = "transaction_id"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  
  # Global Secondary Index for transaction lookup
  global_secondary_index {
    name            = "TransactionIdIndex"
    hash_key        = "transaction_id"
    projection_type = "ALL"
  }
  
  # Global Secondary Index for status queries
  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
  }
  
  tags = {
    Name = "${var.project_name}-alerts"
  }
}

# Output the table names
output "transactions_table_name" {
  description = "Name of the transactions DynamoDB table"
  value       = aws_dynamodb_table.transactions.name
}

output "alerts_table_name" {
  description = "Name of the alerts DynamoDB table"
  value       = aws_dynamodb_table.alerts.name
}

output "transactions_table_arn" {
  description = "ARN of the transactions table"
  value       = aws_dynamodb_table.transactions.arn
}

output "alerts_table_arn" {
  description = "ARN of the alerts table"
  value       = aws_dynamodb_table.alerts.arn
}