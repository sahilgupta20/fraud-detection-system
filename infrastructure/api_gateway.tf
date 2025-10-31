# API Gateway REST API
resource "aws_api_gateway_rest_api" "fraud_detection_api" {
  name        = "${var.project_name}-api"
  description = "REST API for fraud detection system"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = "${var.project_name}-api"
  }
}

# API Resource (transactions endpoint)
resource "aws_api_gateway_resource" "transactions" {
  rest_api_id = aws_api_gateway_rest_api.fraud_detection_api.id
  parent_id   = aws_api_gateway_rest_api.fraud_detection_api.root_resource_id
  path_part   = "transactions"
}

# POST method on /transactions
resource "aws_api_gateway_method" "post_transaction" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id   = aws_api_gateway_resource.transactions.id
  http_method   = "POST"
  authorization = "NONE"
}

# OPTIONS method for CORS
resource "aws_api_gateway_method" "options_transaction" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id   = aws_api_gateway_resource.transactions.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# Lambda integration for POST
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id             = aws_api_gateway_resource.transactions.id
  http_method             = aws_api_gateway_method.post_transaction.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.transaction_validator.invoke_arn
}

# CORS integration for OPTIONS
resource "aws_api_gateway_integration" "cors_integration" {
  rest_api_id = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id = aws_api_gateway_resource.transactions.id
  http_method = aws_api_gateway_method.options_transaction.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# CORS response for OPTIONS
resource "aws_api_gateway_method_response" "cors_response" {
  rest_api_id = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id = aws_api_gateway_resource.transactions.id
  http_method = aws_api_gateway_method.options_transaction.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.fraud_detection_api.id
  resource_id = aws_api_gateway_resource.transactions.id
  http_method = aws_api_gateway_method.options_transaction.http_method
  status_code = aws_api_gateway_method_response.cors_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transaction_validator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fraud_detection_api.execution_arn}/*/*"
}

# API Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.fraud_detection_api.id

  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_integration.cors_integration
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# API Stage
resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.fraud_detection_api.id
  stage_name    = var.environment

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }
}

# Outputs
output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/transactions"
}

output "api_id" {
  description = "API Gateway ID"
  value       = aws_api_gateway_rest_api.fraud_detection_api.id
}