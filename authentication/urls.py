from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('verify/verify-email', views.email_verification_view, name='verify-email'),
    path('verify/confirm-email', views.confirm_email_view, name='confirm-email'),
    path('verify/resend-code', views.resend_confirmation_view, name='resend-code'),
    path('signup', views.complete_signup_view, name='signup'),
    path('signin', views.signin_view, name='signin'),
    path('refresh', views.refresh_token_view, name='refresh-token'),
]
