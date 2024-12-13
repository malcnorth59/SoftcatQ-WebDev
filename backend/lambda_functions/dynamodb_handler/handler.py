import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key

logger = Logger()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MEMBERS_TABLE_NAME'])

def get_next_counter() -> str:
    """
    Gets the next available 6-digit counter for the member ID
    """
    try:
        # Scan the table to find the highest counter
        response = table.query(
            IndexName='RecordTypeIndex',
            KeyConditionExpression=Key('recordType').eq('MEMBER'),
            ProjectionExpression='PK',
            ScanIndexForward=False,  # Sort in descending order
            Limit=1
        )
        
        if not response['Items']:
            return '000001'
            
        last_pk = response['Items'][0]['PK']
        last_counter = int(last_pk.split('#')[1])
        new_counter = str(last_counter + 1).zfill(6)
        
        return new_counter
        
    except ClientError as e:
        logger.exception("Error getting next counter")
        raise

def store_member_data(user_data: dict) -> tuple[bool, str]:
    """
    Stores the member data in DynamoDB
    """
    try:
        counter = get_next_counter()
        pk = f"MEMBER#{counter}"
        
        # Prepare the DynamoDB item
        item = {
            'PK': pk,
            'SK': pk,
            'fullName': user_data['fullName'],
            'email': user_data['email'],
            'telephone': user_data['telephone'],
            'postcode': user_data['postcode'],
            'membershipType': user_data['membershipType'],
            'laaStatus': user_data['laaStatus'],
            'membershipStatus': 'PENDING',  # Initial status before payment
            'recordType': 'MEMBER'
        }
        
        # Store in DynamoDB
        table.put_item(Item=item)
        
        # Add the member ID to the user data for the next Lambda
        user_data['memberId'] = pk
        
        return True, "Member data stored successfully"
        
    except ClientError as e:
        logger.exception("Error storing member data")
        return False, f"Error storing member data: {str(e)}"

@logger.inject_lambda_context
def handler(event, context):
    try:
        # Event should contain user data from previous Lambdas
        user_data = json.loads(event['body'])
        
        success, message = store_member_data(user_data)
        
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
                'message': message,
                'data': user_data
            })
        }
        
    except Exception as e:
        logger.exception("Error in DynamoDB handler Lambda")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': 'Internal server error while storing member data'
            })
        }