import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()
ses = boto3.client('ses')

def send_payment_instructions(user_data: dict) -> tuple[bool, str]:
    """
    Sends payment instructions email to new member
    """
    try:
        subject = 'UKPC Membership - Payment Instructions'
        
        bank_details = {
            'account_name': os.environ['BANK_ACCOUNT_NAME'],
            'sort_code': os.environ['BANK_SORT_CODE'],
            'account_number': os.environ['BANK_ACCOUNT_NUMBER']
        }
        
        membership_fees = {
            'full': '£50',
            'associate': '£25'
        }
        
        body_html = f"""
        <html>
        <body>
            <h2>Thank you for your UKPC membership application</h2>
            <p>Dear {user_data['fullName']},</p>
            <p>Thank you for applying for UKPC membership. To complete your application, please make a payment of {membership_fees[user_data['membershipType']]} using the following bank details:</p>
            <ul>
                <li>Account Name: {bank_details['account_name']}</li>
                <li>Sort Code: {bank_details['sort_code']}</li>
                <li>Account Number: {bank_details['account_number']}</li>
                <li>Reference: {user_data['memberId']}</li>
            </ul>
            <p>Your membership will be activated once payment is confirmed.</p>
            <p>Best regards,<br>UKPC Membership Team</p>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=os.environ['FROM_EMAIL'],
            Destination={
                'ToAddresses': [user_data['email']]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': body_html
                    }
                }
            }
        )
        
        return True, "Payment instructions email sent successfully"
        
    except ClientError as e:
        logger.exception("Error sending payment instructions email")
        return False, f"Error sending email: {str(e)}"

def send_welcome_email(user_data: dict, temp_password: str) -> tuple[bool, str]:
    """
    Sends welcome email with login credentials after payment confirmation
    """
    try:
        subject = 'Welcome to UKPC - Account Activated'
        
        body_html = f"""
        <html>
        <body>
            <h2>Welcome to UKPC</h2>
            <p>Dear {user_data['fullName']},</p>
            <p>Your UKPC membership has been activated. You can now log in to your account using:</p>
            <ul>
                <li>Username: {user_data['email']}</li>
                <li>Temporary Password: {temp_password}</li>
            </ul>
            <p>Please change your password when you first log in.</p>
            <p>Best regards,<br>UKPC Membership Team</p>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=os.environ['FROM_EMAIL'],
            Destination={
                'ToAddresses': [user_data['email']]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': body_html
                    }
                }
            }
        )
        
        return True, "Welcome email sent successfully"
        
    except ClientError as e:
        logger.exception("Error sending welcome email")
        return False, f"Error sending email: {str(e)}"

@logger.inject_lambda_context
def handler(event, context):
    try:
        # Event should contain user data and email type
        body = json.loads(event['body'])
        email_type = body.get('emailType')
        user_data = body.get('userData')
        
        if not email_type or not user_data:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'Missing email type or user data'
                })
            }
            
        if email_type == 'payment_instructions':
            success, message = send_payment_instructions(user_data)
        elif email_type == 'welcome':
            temp_password = body.get('tempPassword')
            if not temp_password:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Missing temporary password for welcome email'
                    })
                }
            success, message = send_welcome_email(user_data, temp_password)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': f'Invalid email type: {email_type}'
                })
            }
        
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'message': message
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': message
            })
        }
        
    except Exception as e:
        logger.exception("Error in email sender Lambda")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error while sending email'
            })
        }