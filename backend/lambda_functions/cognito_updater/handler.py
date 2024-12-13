import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()
cognito = boto3.client('cognito-idp')

def create_disabled_user(user_data: dict) -> tuple[bool, str, str]:
    """
    Creates a disabled Cognito user and returns success status, message, and user sub if successful
    """
    try:
        # Generate a temporary password
        temp_password = os.urandom(16).hex()
        
        response = cognito.admin_create_user(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=user_data['email'],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user_data['email']
                },
                {
                    'Name': 'name',
                    'Value': user_data['fullName']
                },
                {
                    'Name': 'custom:membershipType',
                    'Value': user_data['membershipType']
                },
                {
                    'Name': 'custom:laaStatus',
                    'Value': str(user_data['laaStatus']).lower()
                }
            ],
            TemporaryPassword=temp_password,
            MessageAction='SUPPRESS'  # Don't send automatic welcome email
        )
        
        # Disable the user until payment is confirmed
        cognito.admin_disable_user(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=user_data['email']
        )
        
        return True, "Cognito user created successfully", response['User']['Username']
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'UsernameExistsException':
            return False, "An account with this email already exists", ""
        
        logger.exception("Error creating Cognito user")
        return False, f"Error creating user account: {str(e)}", ""

@logger.inject_lambda_context
def handler(event, context):
    try:
        # Event should contain validated user data from previous Lambda
        user_data = json.loads(event['body'])
        
        success, message, user_sub = create_disabled_user(user_data)
        
        if not success:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': message
                })
            }
            
        # Add the Cognito username to the user data for the next Lambda
        user_data['cognitoUsername'] = user_sub
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': message,
                'data': user_data
            })
        }
        
    except Exception as e:
        logger.exception("Error in Cognito updater Lambda")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error while creating user account'
            })
        }