import json
from django.shortcuts import render, redirect
from .cognito_helper import signup_user, signin_user
from django.http import JsonResponse
from django.urls import reverse
from dotenv import load_dotenv
import boto3
import os
from django.views.decorators.csrf import csrf_exempt

# Load environment variables from the .env file
load_dotenv()

# Now you can access the environment variables
AWS_CLIENT_ID = os.getenv('AWS_CLIENT_ID')
AWS_REGION = os.getenv('AWS_REGION')

@csrf_exempt
def signup_view(request):   # auth/signup
    if request.method == 'POST':
        data = json.loads(request.body)  # Load JSON data from request body
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        nickname = data.get('nickname')
        full_name = data.get('full_name')

        result = signup_user(username, password, email, nickname, full_name)
        
        if result:  # Check if signup_user succeeded
            return JsonResponse({'message': 'User signed up successfully!'}, status=201)
        else:
            return JsonResponse({'error': 'Signup failed.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def signin_view(request):   # auth/signin
    if request.method == 'POST':
        data = json.loads(request.body)  # Load JSON data from request body
        username = data.get('username')
        password = data.get('password')
        

        client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))
        
        try:
            response = client.initiate_auth(
                ClientId=os.getenv('AWS_CLIENT_ID'),  # Your App Client ID
                AuthFlow='USER_PASSWORD_AUTH',  # Use USER_SRP_AUTH for SRP flow
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                }
            )
            
            # Retrieve the tokens from the response
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']
            
            return JsonResponse({
                'access_token': access_token,
                'id_token': id_token,
                'refresh_token': refresh_token,
            }, status=200)
        
        except client.exceptions.NotAuthorizedException:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
        except client.exceptions.UserNotFoundException:
            return JsonResponse({'error': 'User does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def homepage_view(request):
    return render(request, 'homepage.html')

@csrf_exempt  # Only use this for testing, better to handle CSRF properly in production
def confirm_signup_view(request):   # auth/verify
    if request.method == 'POST':    
        try:
            data = json.loads(request.body)  # Load JSON data from request body
            username = data['username']
            verification_code = data['verification_code']

            client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))  # Use environment variable for region
            response = client.confirm_sign_up(
                ClientId=os.getenv('AWS_CLIENT_ID'),  # Use environment variable for Client ID
                Username=username,
                ConfirmationCode=verification_code
            )
            return JsonResponse({'message': 'User confirmed successfully!'}, status=200)
        except client.exceptions.CodeMismatchException:
            return JsonResponse({'error': 'Invalid verification code.'}, status=400)
        except client.exceptions.UserNotFoundException:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except client.exceptions.NotAuthorizedException:
            return JsonResponse({'error': 'User is already confirmed.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def refresh_token_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')

        client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))

        try:
            response = client.initiate_auth(
                ClientId=os.getenv('AWS_CLIENT_ID'),
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            # Extract the new tokens from the response
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            new_refresh_token = response['AuthenticationResult'].get('RefreshToken')  # May receive a new refresh token

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
