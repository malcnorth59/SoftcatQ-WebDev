# UKPC Membership Website - AWS Serverless Project Setup

## Architecture Overview
Based on the specifications in task.md, this project will use:

1. Frontend:
   - Static website hosted on Amazon S3
   - Bootstrap for styling and layout
   - TypeScript for API interactions and validation

2. Backend Services:
   - Amazon API Gateway
   - AWS Lambda (Python 3.10+)
   - Amazon DynamoDB
   - Amazon Cognito
   - Amazon SES (Simple Email Service)

## Initial Project Structure
```
ukpc_membership/
├── frontend/
│   ├── src/
│   │   ├── ts/
│   │   │   ├── validation.ts
│   │   │   └── api.ts
│   │   ├── css/
│   │   ├── html/
│   │   └── assets/
│   └── package.json
├── backend/
│   ├── lambda_functions/
│   │   ├── membership_validator/
│   │   │   └── handler.py
│   │   ├── cognito_updater/
│   │   │   └── handler.py
│   │   ├── dynamodb_handler/
│   │   │   └── handler.py
│   │   └── email_sender/
│   │       └── handler.py
│   └── requirements.txt
├── infrastructure/
│   └── cloudformation/
│       ├── cognito.yaml
│       ├── api_gateway.yaml
│       ├── dynamodb.yaml
│       └── lambda.yaml
└── README.md
```

## DynamoDB Schema
Based on requirements:

```javascript
{
  PK: "MEMBER#000001",  // Composite of record type and six-digit counter
  SK: "MEMBER#000001",  // Same as PK
  fullName: "String",   // Secondary index with record type
  email: "String",      // Secondary index with record type
  telephone: "String",  // Secondary index with record type
  postcode: "String",   // Secondary index with record type
  membershipType: "String",
  laaStatus: boolean,
  membershipStatus: "String", // Secondary index with record type
  recordType: "MEMBER"
}
```

## Next Steps

1. Set up the development environment:
   ```bash
   # Frontend setup
   cd frontend
   npm init
   npm install typescript bootstrap @aws-sdk/client-cognito-identity

   # Backend setup
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install boto3 aws-lambda-powertools
   pip freeze > requirements.txt
   ```

2. Key Lambda Functions to Implement:
   - Membership Application Validator
   - Cognito User Manager
   - DynamoDB Record Handler
   - Email Notification Sender

3. Core Features Flow:
   a. User submits membership application (Frontend -> API Gateway)
   b. Validation Lambda processes application
   c. Creates disabled Cognito user
   d. Stores member data in DynamoDB
   e. Sends payment instructions email
   f. Admin confirms payment
   g. Sends welcome email and enables Cognito user

4. Required IAM Roles:
   - Lambda execution roles with permissions for:
     - DynamoDB access
     - Cognito user management
     - SES email sending
   - S3 bucket policy for static website hosting

Would you like to proceed with this AWS serverless setup?