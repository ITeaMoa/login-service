from django.shortcuts import render, redirect
from .cognito_helper import signup_user, signin_user
from django.http import JsonResponse
from django.urls import reverse
from dotenv import load_dotenv
import boto3
import os

# Load environment variables from the .env file
load_dotenv()

# Now you can access the environment variables
AWS_CLIENT_ID = os.getenv('AWS_CLIENT_ID')
AWS_REGION = os.getenv('AWS_REGION')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        nickname = request.POST['nickname']  # Get the nickname
        full_name = request.POST['full_name']  # Get the full name
        result = signup_user(username, password, email, nickname, full_name)
        # return redirect(reverse('authentication:signin'))
        return redirect('authentication:verify')
    return render(request, 'signup.html')

def signin_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        result = signin_user(username, password)
        if 'AuthenticationResult' in result:
            jwt_token = result['AuthenticationResult']['AccessToken']
            return JsonResponse({'token': jwt_token})
        return JsonResponse(result)
    return render(request, 'signin.html')

def homepage_view(request):
    return render(request, 'homepage.html')

def confirm_signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        verification_code = request.POST['verification_code']
        
        client = boto3.client('cognito-idp', region_name='AWS_REGION')  # Replace with your region
        try:
            response = client.confirm_sign_up(
                ClientId='AWS_CLIENT_ID',  # Replace with your Cognito App Client ID
                Username=username,
                ConfirmationCode=verification_code
            )
            return redirect('authentication:signin')  # Redirect to sign-in page after confirmation
        except client.exceptions.CodeMismatchException:
            return render(request, 'verification.html', {'error': 'Invalid verification code.'})
        except client.exceptions.UserNotFoundException:
            return render(request, 'verification.html', {'error': 'User not found.'})
        except client.exceptions.NotAuthorizedException:
            return render(request, 'verification.html', {'error': 'User is already confirmed.'})
    
    return render(request, 'verification.html')