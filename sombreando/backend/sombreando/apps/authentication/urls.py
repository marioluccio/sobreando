from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    EmailVerificationView,
    ResendVerificationEmailView,
    Toggle2FAView,
    UserStatsView,
    RefreshTokenView,
    UserAvatarUploadView,
    DeleteAccountView,
    SecurityLogView,
    check_email_availability,
    check_username_availability,
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Token management
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('avatar/upload/', UserAvatarUploadView.as_view(), name='avatar_upload'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Email verification
    path('email/verify/', EmailVerificationView.as_view(), name='email_verify'),
    path('email/resend/', ResendVerificationEmailView.as_view(), name='email_resend'),
    
    # 2FA management
    path('2fa/toggle/', Toggle2FAView.as_view(), name='toggle_2fa'),
    
    # User statistics and security
    path('stats/', UserStatsView.as_view(), name='user_stats'),
    path('security/log/', SecurityLogView.as_view(), name='security_log'),
    
    # Account management
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
    
    # Availability checks
    path('email/check/', check_email_availability, name='email_check'),
    path('username/check/', check_username_availability, name='username_check'),
]

