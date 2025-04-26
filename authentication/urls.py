from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('verify/email', views.email_verification_view, name='verify-email'),
    path('confirm/email', views.confirm_email_view, name='confirm-email'),
    path('verify/resend', views.resend_confirmation_view, name='resend-code'),
    path('verify/nickname', views.nickname_verification_view, name='verify-nickname'),
    path('confirm/signup', views.complete_signup_view, name='signup'),
    path('confirm/signin', views.signin_view, name='signin'),
    path('verify/refresh', views.refresh_token_view, name='refresh-token'),
    path('/test', views.test_return, name='test_return'),
]
