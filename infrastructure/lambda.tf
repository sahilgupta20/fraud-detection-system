# Lambda IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-role"
  }
}

# Lambda IAM Policy
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.transactions.arn,
          aws_dynamodb_table.alerts.arn,
          "${aws_dynamodb_table.transactions.arn}/index/*",
          "${aws_dynamodb_table.alerts.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Package Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/transaction-validator"
  output_path = "${path.module}/../lambdas/transaction-validator/lambda.zip"
  excludes = [
    "tests",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "requirements-dev.txt",
    "lambda.zip"
  ]
}

# Lambda Function
resource "aws_lambda_function" "transaction_validator" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-validator"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      TRANSACTIONS_TABLE = aws_dynamodb_table.transactions.name
      ALERTS_TABLE      = aws_dynamodb_table.alerts.name
    }
  }

  tags = {
    Name = "${var.project_name}-validator"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.transaction_validator.function_name}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-lambda-logs"
  }
}

# Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.transaction_validator.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.transaction_validator.arn
}