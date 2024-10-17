import boto3
import logging
from dotenv import load_dotenv
import boto3
import os

# Load environment variables from the .env file
load_dotenv()

# Now you can access the environment variables
AWS_CLIENT_ID = os.getenv('AWS_CLIENT_ID')
AWS_REGION = os.getenv('AWS_REGION')

def signup_user(username, password, email,nickname, full_name):
    client = boto3.client('cognito-idp', region_name='AWS_REGION')
    try:
        response = client.sign_up(
            ClientId='AWS_CLIENT_ID',
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'nickname', 'Value': nickname},  # Include required attributes
                {'Name': 'name', 'Value': full_name},
            ]
        )
        return response
    except client.exceptions.UsernameExistsException:
        return 'User already exists'

def signin_user(username, password):
    client = boto3.client('cognito-idp', region_name='AWS_REGION')
    try:
        response = client.initiate_auth(
            ClientId='AWS_CLIENT_ID',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': username, 'PASSWORD': password}
        )
        return response
    except client.exceptions.NotAuthorizedException:
        return 'Invalid credentials'
    except client.exceptions.NotAuthorizedException:
        print("Invalid credentials provided.")
        return {'error': 'Invalid credentials'}
    except client.exceptions.UserNotConfirmedException:
        print("User is not confirmed.")
        return {'error': 'User not confirmed. Please check your email for verification.'}
    except client.exceptions.PasswordResetRequiredException:
        print("Password reset required for this user.")
        return {'error': 'Password reset required. Please reset your password.'}
    except client.exceptions.UserNotFoundException:
        print("User not found.")
        return {'error': 'User not found.'}
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return {'error': 'An unexpected error occurred.'}