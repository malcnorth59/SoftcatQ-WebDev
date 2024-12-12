# UKPC MemberShip Website

## Site Description

The webite is constructed as a static site in Amazon S3 with a backend built using Amazon SES, Amazon Cognito, Amazon API Gateway, and Lambda (Python 3.10+) and DynamoDB.

The frontend uses bootstrap for styling and layout. Calling the APIs and input validation will use Typescript

## Membership data

The membership data is stored in a dynamo DB table and will be used for managining entitlement to other website features.

A primary key is required comprising a six counter, incremented every time a record is added and a record type field of member.

The member full name is a string field and along with the record type forms a secondary key

The member email address is a string field and along with the record type forms a secondary key

The member telephone number is a string field and and along with the record type forms a secondary key

The member postcode is a string field and and along with the record type forms a secondary key

The membership type field is a string field

The LAA membership field is a boolean flag

The password field must not be stored in the database

The membership status field is a string field and along with the record type forms a secondary key

## User Stories

As a user I want to be able to apply for membership via the website

As a membership secretary I want user's to be able to submit their membership details to the website and receive and email with payment instructions and the UKPC bank details

As an API I want to validate users when I've received a membership application

As an API I want to update Amazon Cognito with cognito details, but keep disable their account when I've validated the user.

As an API I want to store the membership details in DynamoDB when i've validated the user

As an API I want to send an email with joining instructions when I've validated the user

As membership secretary I want to be able to confirm payment when I receive it.

As an API I want to send a welcome email when payment confirmation is received.