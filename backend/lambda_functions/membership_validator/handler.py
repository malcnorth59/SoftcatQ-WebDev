import json
import re
from typing import Dict, Tuple
from aws_lambda_powertools import Logger

logger = Logger()

def validate_full_name(name: str) -> bool:
    return bool(name and len(name.strip()) >= 2)

def validate_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def validate_telephone(phone: str) -> bool:
    phone_regex = r'^[\d\s\-+()]{10,}$'
    return bool(re.match(phone_regex, phone))

def validate_postcode(postcode: str) -> bool:
    uk_postcode_regex = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'
    return bool(re.match(uk_postcode_regex, postcode, re.IGNORECASE))

def validate_membership_application(event_body: Dict) -> Tuple[bool, str]:
    required_fields = ['fullName', 'email', 'telephone', 'postcode', 'membershipType']
    
    # Check for missing fields
    for field in required_fields:
        if field not in event_body:
            return False, f"Missing required field: {field}"
    
    # Validate each field
    if not validate_full_name(event_body['fullName']):
        return False, "Invalid full name"
    
    if not validate_email(event_body['email']):
        return False, "Invalid email address"
    
    if not validate_telephone(event_body['telephone']):
        return False, "Invalid telephone number"
    
    if not validate_postcode(event_body['postcode']):
        return False, "Invalid UK postcode"
    
    if event_body['membershipType'] not in ['full', 'associate']:
        return False, "Invalid membership type"
    
    return True, "Validation successful"

@logger.inject_lambda_context
def handler(event, context):
    try:
        body = json.loads(event['body'])
        is_valid, message = validate_membership_application(body)
        
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': message
                })
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': message,
                'data': body
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Invalid JSON in request body'
            })
        }
    except Exception as e:
        logger.exception('Error processing membership application')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error'
            })
        }