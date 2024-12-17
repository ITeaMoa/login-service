import json
from django.shortcuts import render, redirect
from .cognito_helper import signup_user, signin_user
from django.http import JsonResponse
from django.urls import reverse
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key
import os
import hmac
import hashlib
import base64
import string
import random
import bcrypt
from django.views.decorators.csrf import csrf_exempt

# Now you can access the environment variables
AWS_CLIENT_ID = os.getenv('AWS_CLIENT_ID')
AWS_CLIENT_SECRET =os.getenv('AWS_CLIENT_SECRET')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_USER_POOL_ID = os.getenv('AWS_USER_POOL_ID')

# Validation
if not all([AWS_CLIENT_ID, AWS_CLIENT_SECRET, AWS_REGION, AWS_USER_POOL_ID]):
    raise ValueError("One or more required environment variables are missing")

# cb_client = boto3.client('codebuild', region_name=AWS_REGION)
# response = cb_client.start_build(
#     projectName="iteamoa-loginpage",
#     environmentVariablesOverride=[
#         {
#             "name": "AWS_CLIENT_ID",
#             "type": "PLAINTEXT",
#             "value": AWS_CLIENT_ID  # Dynamically fetched value
#         },
#         {
#             "name": "AWS_CLIENT_SECRET",
#             "type": "PLAINTEXT",
#             "value": AWS_CLIENT_SECRET  # Dynamically fetched value
#         },
#         {
#             "name": "AWS_REGION",
#             "type": "PLAINTEXT",
#             "value": AWS_REGION
#         },
#         {
#             "name": "AWS_USER_POOL_ID",
#             "type": "PLAINTEXT",
#             "value": AWS_USER_POOL_ID
#         }
#     ]
# )

def calculate_secret_hash(client_id, client_secret, username):
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def generate_valid_password(length=12):
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    # Ensure the password has at least one of each required character type
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?/")  # Define your special characters
    remaining = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/", k=length - 4))
    
    # Combine and shuffle to ensure randomness
    password = upper + lower + digit + special + remaining
    return ''.join(random.sample(password, len(password)))

@csrf_exempt
def email_verification_view(request):  # verify/email
    client = boto3.client('cognito-idp', region_name=AWS_REGION)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            if not email:
                return JsonResponse({'error': 'Email is required.'}, status=400)
            
            try:
                client.admin_get_user(
                    UserPoolId=AWS_USER_POOL_ID,
                    Username=email
                )
                return JsonResponse({'error': 'Email is already registered.'}, status=409)
            except client.exceptions.UserNotFoundException:
                pass

            client_id = os.getenv('AWS_CLIENT_ID')
            client_secret = os.getenv('AWS_CLIENT_SECRET')
            if not client_secret:
                return JsonResponse({'error': 'AWS_CLIENT_SECRET is not set.'}, status=500)
            
            # Calculate the SECRET_HASH
            secret_hash = calculate_secret_hash(client_id, client_secret, email)
            
            client = boto3.client('cognito-idp', region_name=AWS_REGION)
            
            response = client.sign_up(
                ClientId=client_id,
                SecretHash=secret_hash,  # Include SECRET_HASH
                Username=email,
                Password=generate_valid_password(),  # Generate a random password for initial sign-up
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                ]
            )
            
            return JsonResponse({'message': 'Verification code sent to email!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def resend_confirmation_view(request):  # verify/resend
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required.'}, status=400)
            
            client = boto3.client('cognito-idp', region_name=AWS_REGION)
            secret_hash = calculate_secret_hash(AWS_CLIENT_ID, AWS_CLIENT_SECRET, email)
            
            # Resend the confirmation code
            response = client.resend_confirmation_code(
                ClientId=os.getenv('AWS_CLIENT_ID'),
                Username=email,
                SecretHash=secret_hash,
            )
            
            return JsonResponse({'message': 'Confirmation code resent successfully!'}, status=200)
        except client.exceptions.UserNotFoundException:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def confirm_email_view(request):  # confirm/email
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            verification_code = data['verification_code']
            
            client = boto3.client('cognito-idp', region_name=AWS_REGION)
            secret_hash = calculate_secret_hash(AWS_CLIENT_ID, AWS_CLIENT_SECRET, email)

            response = client.confirm_sign_up(
                ClientId=os.getenv('AWS_CLIENT_ID'),
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=verification_code
            )
            
            return JsonResponse({'message': 'Email verified successfully!'}, status=200)
        
        except client.exceptions.CodeMismatchException:
            return JsonResponse({'error': 'Invalid verification code.'}, status=400)
        except client.exceptions.UserNotFoundException:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except client.exceptions.NotAuthorizedException as e:
            if 'User is already confirmed' in str(e):
                return JsonResponse({'error': 'User is already confirmed.'}, status=409)
            return JsonResponse({'error': 'Not authorized for this action.'}, status=403)
        except Exception as e:
            # Log unexpected errors for debugging
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

@csrf_exempt
def nickname_verification_view(request):  # verify/nickname
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Request body: {data}")
            nickname = data['nickname']
 
            if not nickname:
                return JsonResponse({'error': 'Nickname are required.'}, status=400)
            
            # client = boto3.client('cognito-idp', region_name=AWS_REGION)
            # response = client.list_users(
            #     UserPoolId=AWS_USER_POOL_ID,
            #     Filter=f'custom:nickname = "{nickname}"'
            # )
            # if response['Users']:
            #     return JsonResponse({'error': 'Nickname is already taken.'}, status=409)
            
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table('IM_MAIN_TB')
            response = table.query(
                IndexName='Nickname-index',  # Ensure a DynamoDB index exists for nickname
                KeyConditionExpression=Key('nickname').eq(nickname)
            )
            if response['Items']:
                return JsonResponse({'error': 'Nickname is already taken.'}, status=409)
            
            return JsonResponse({'message': 'Nickname is available.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def complete_signup_view(request):  # confirm/signup
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            nickname = data['nickname']
            password = data['password']
            
            if not email or not password or not nickname:
                return JsonResponse({'error': 'Email, password, and nickname are required.'}, status=400)

            client = boto3.client('cognito-idp', region_name=AWS_REGION)
            # Update the user's attributes
            try:
                client.admin_update_user_attributes(
                    UserPoolId=AWS_USER_POOL_ID,
                    Username=email,
                    UserAttributes=[
                        {'Name': 'nickname', 'Value': nickname},
                    ]
                )
            except client.exceptions.UserNotFoundException:
                return JsonResponse({'error': 'User not found in Cognito.'}, status=404)
            except Exception as e:
                return JsonResponse({'error': f'Failed to update user attributes: {str(e)}'}, status=500)

            # Set the new password
            client.admin_set_user_password(
                UserPoolId=AWS_USER_POOL_ID,
                Username=email,
                Password=password,
                Permanent=True
            )

            # Retrieve Cognito user ID (sub)
            client = boto3.client('cognito-idp', region_name=AWS_REGION)
            user_response = client.admin_get_user(
                UserPoolId=AWS_USER_POOL_ID,
                Username=email
            )
            sub = next(attr['Value'] for attr in user_response['UserAttributes'] if attr['Name'] == 'sub')

            hashed_password = hash_password(password)

            # Save user profile to DynamoDB
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table('IM_MAIN_TB')

            # Insert user info
            try:
                table.put_item(
                    Item={
                        'Pk': f"USER#{sub}",
                        'Sk': f"INFO#",
                        'email': email,
                        'password': hashed_password,
                        'nickname': nickname,
                    }
                )
            except Exception as e:
                return JsonResponse({'error': f'Failed to save user profile to DynamoDB: {str(e)}'}, status=500)

            return JsonResponse({'message': 'Signup completed successfully, profile added to DynamoDB!'}, status=201)
        
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def signin_view(request):   # confirm/signin
    if request.method == 'POST':
        data = json.loads(request.body)  # Load JSON data from request body
        email = data.get('email')
        password = data.get('password')
        secret_hash = calculate_secret_hash(AWS_CLIENT_ID, AWS_CLIENT_SECRET, email)
        # secret hash 꼭 포함하기 !! > 포함안하면 로그인 오류남 (cognito 업데이트 이후 그런듯/한달전만해도 안그럼)
        # 지금은 secret이 필수로 포함되어서 모든 cognito와 소통하는 항목에는 포함해줘야함 (다른 함수도 다 포함되어 있음)
        # 얘는 sub 하면 오류나고 email 해야함 (이유가 뭐지 .. )
        
        client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))
        
        try:
            response = client.initiate_auth(
                ClientId=AWS_CLIENT_ID,  
                AuthFlow='USER_PASSWORD_AUTH',  # Use USER_SRP_AUTH for SRP flow
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash
                }
            )
            
            # Retrieve the tokens from the response
            authentication_result = response['AuthenticationResult']
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']
            
            return JsonResponse({
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': refresh_token,
            }, status=200)
        
        except client.exceptions.NotAuthorizedException as e:
            error_message = str(e)
            if "User is disabled" in error_message:
                return JsonResponse({'error': 'User is disabled.'}, status=403)
            elif "User is not confirmed" in error_message:
                return JsonResponse({'error': 'User is not confirmed.'}, status=402)
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)
            
        except client.exceptions.UserNotFoundException:
            return JsonResponse({'error': 'User does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def homepage_view(request):
    return render(request, 'homepage.html')

@csrf_exempt
def refresh_token_view(request):    # verify/refresh
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        refresh_token = data.get('refresh_token')
        print(f"Refresh Token: {refresh_token}")

        client = boto3.client('cognito-idp', region_name=AWS_REGION)
        
        user_response = client.admin_get_user(
            UserPoolId=AWS_USER_POOL_ID,
            Username=email
        )
        sub = next(attr['Value'] for attr in user_response['UserAttributes'] if attr['Name'] == 'sub')
        secret_hash = calculate_secret_hash(AWS_CLIENT_ID, AWS_CLIENT_SECRET, sub)
        # sub 말고 email 넣으면 cognito에서 반환안해줌 
        # Refer to https://stackoverflow.com/questions/50337252/aws-cognito-refresh-token-fails-on-secret-hash
        
        try:
            response = client.initiate_auth(
                ClientId=AWS_CLIENT_ID,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token,
                    'SECRET_HASH': secret_hash
                }
            )
            
            # Extract the new tokens from the response
            authentication_result = response['AuthenticationResult']
            access_token = authentication_result['AccessToken']
            id_token = authentication_result['IdToken']
            new_refresh_token = authentication_result.get('RefreshToken')   # may be null

            return JsonResponse({
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': new_refresh_token,
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except client.exceptions.NotAuthorizedException:
            return JsonResponse({'error': 'Refresh token is invalid or has expired.'}, status=401)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")  # Log the exception
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
