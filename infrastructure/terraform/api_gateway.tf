# API Gateway
resource "aws_api_gateway_rest_api" "ukpc_api" {
  name        = "ukpc-api-${var.environment}"
  description = "API for UKPC membership management"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Cognito Authorizer
resource "aws_api_gateway_authorizer" "cognito" {
  name          = "ukpc-cognito-authorizer-${var.environment}"
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.ukpc_api.id
  provider_arns = [data.aws_cloudformation_export.cognito_user_pool_arn.value]
}

# API Resources
resource "aws_api_gateway_resource" "membership" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  parent_id   = aws_api_gateway_rest_api.ukpc_api.root_resource_id
  path_part   = "membership"
}

resource "aws_api_gateway_resource" "apply" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  parent_id   = aws_api_gateway_resource.membership.id
  path_part   = "apply"
}

resource "aws_api_gateway_resource" "payment_confirm" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  parent_id   = aws_api_gateway_resource.membership.id
  path_part   = "confirm-payment"
}

# Methods
resource "aws_api_gateway_method" "apply" {
  rest_api_id   = aws_api_gateway_rest_api.ukpc_api.id
  resource_id   = aws_api_gateway_resource.apply.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "apply" {
  rest_api_id             = aws_api_gateway_rest_api.ukpc_api.id
  resource_id             = aws_api_gateway_resource.apply.id
  http_method             = aws_api_gateway_method.apply.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${data.aws_cloudformation_export.membership_validator_function_arn.value}/invocations"
}

resource "aws_api_gateway_method" "payment_confirm" {
  rest_api_id          = aws_api_gateway_rest_api.ukpc_api.id
  resource_id          = aws_api_gateway_resource.payment_confirm.id
  http_method          = "POST"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
}

resource "aws_api_gateway_integration" "payment_confirm" {
  rest_api_id             = aws_api_gateway_rest_api.ukpc_api.id
  resource_id             = aws_api_gateway_resource.payment_confirm.id
  http_method             = aws_api_gateway_method.payment_confirm.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${data.aws_cloudformation_export.payment_confirm_function_arn.value}/invocations"
}

# CORS
resource "aws_api_gateway_method" "apply_options" {
  rest_api_id   = aws_api_gateway_rest_api.ukpc_api.id
  resource_id   = aws_api_gateway_resource.apply.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "apply_options" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  resource_id = aws_api_gateway_resource.apply.id
  http_method = aws_api_gateway_method.apply_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_integration_response" "apply_options" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  resource_id = aws_api_gateway_resource.apply.id
  http_method = aws_api_gateway_method.apply_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [aws_api_gateway_integration.apply_options]
}

resource "aws_api_gateway_method_response" "apply_options" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id
  resource_id = aws_api_gateway_resource.apply.id
  http_method = aws_api_gateway_method.apply_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

# Deployment and Stage
resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.ukpc_api.id

  depends_on = [
    aws_api_gateway_method.apply,
    aws_api_gateway_method.payment_confirm,
    aws_api_gateway_method.apply_options,
    aws_api_gateway_integration.apply,
    aws_api_gateway_integration.payment_confirm,
    aws_api_gateway_integration.apply_options
  ]
}

resource "aws_api_gateway_stage" "api" {
  deployment_id = aws_api_gateway_deployment.api.id
  rest_api_id  = aws_api_gateway_rest_api.ukpc_api.id
  stage_name   = var.environment
}

# Lambda Permissions
resource "aws_lambda_permission" "membership_validator" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_cloudformation_export.membership_validator_function_arn.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ukpc_api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "payment_confirm" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_cloudformation_export.payment_confirm_function_arn.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ukpc_api.execution_arn}/*/*/*"
}

# Data sources for external values
data "aws_region" "current" {}

data "aws_cloudformation_export" "cognito_user_pool_arn" {
  name = "cognito-stack-UserPoolArn"
}

data "aws_cloudformation_export" "membership_validator_function_arn" {
  name = "membership-validator-function-arn"
}

data "aws_cloudformation_export" "payment_confirm_function_arn" {
  name = "payment-confirm-function-arn"
}

# Variables
variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "dev"
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either dev or prod"
  }
}