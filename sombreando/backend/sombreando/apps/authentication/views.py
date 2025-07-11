from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from .models import User, LoginAttempt, EmailVerificationToken
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
    Toggle2FASerializer,
    UserStatsSerializer,
    EmailAvailabilitySerializer,
    UsernameAvailabilitySerializer,
)
from .utils import get_client_ip, send_verification_email

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Usuário criado com sucesso. Verifique seu email para ativar a conta.',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """User login endpoint with 2FA support"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Log failed login attempt
            self._log_login_attempt(
                request.data.get('email', ''),
                request,
                success=False,
                failure_reason=str(e)
            )
            raise e
        
        user = serializer.validated_data['user']
        
        # Log successful login
        self._log_login_attempt(
            user.email,
            request,
            success=True
        )
        
        # Update last login IP
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })
    
    def _log_login_attempt(self, email, request, success, failure_reason=''):
        """Log login attempt for security monitoring"""
        LoginAttempt.objects.create(
            email=email,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            failure_reason=failure_reason
        )


class UserLogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Logout realizado com sucesso.'})
        except Exception:
            return Response({'message': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """Password change endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Senha alterada com sucesso.'})


class EmailVerificationView(APIView):
    """Email verification endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Email verificado com sucesso.'})


class ResendVerificationEmailView(APIView):
    """Resend verification email endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.is_verified:
            return Response(
                {'message': 'Email já verificado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's a recent verification email
        recent_token = EmailVerificationToken.objects.filter(
            user=user,
            purpose='email_verification',
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()
        
        if recent_token:
            return Response(
                {'message': 'Email de verificação já enviado recentemente. Aguarde 5 minutos.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        send_verification_email(user, 'email_verification')
        
        return Response({'message': 'Email de verificação enviado.'})


class Toggle2FAView(APIView):
    """Enable/disable 2FA endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = Toggle2FASerializer(data=request.data, context={'request': request})
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # If requires verification, the exception contains the message
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                if e.detail.get('requires_verification'):
                    return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            raise e
        
        serializer.save()
        
        action = "ativado" if serializer.validated_data['enable'] else "desativado"
        return Response({'message': f'2FA {action} com sucesso.'})


class UserStatsView(APIView):
    """User statistics endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        
        # Calculate statistics
        login_attempts_today = LoginAttempt.objects.filter(
            email=user.email,
            timestamp__date=today
        ).count()
        
        total_login_attempts = LoginAttempt.objects.filter(
            email=user.email
        ).count()
        
        account_age = (timezone.now().date() - user.created_at.date()).days
        
        stats = {
            'login_attempts_today': login_attempts_today,
            'total_login_attempts': total_login_attempts,
            'account_age_days': account_age,
            'is_verified': user.is_verified,
            'is_2fa_enabled': user.is_2fa_enabled,
            'subscription_plan': user.subscription_plan,
            'is_subscription_active': user.is_subscription_active,
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_email_availability(request):
    """Check if email is available"""
    serializer = EmailAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    available = not User.objects.filter(email__iexact=email).exists()
    
    return Response({'available': available})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_username_availability(request):
    """Check if username is available"""
    serializer = UsernameAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    available = not User.objects.filter(username__iexact=username).exists()
    
    return Response({'available': available})


class RefreshTokenView(APIView):
    """Custom refresh token endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            
            return Response({
                'access': str(token.access_token),
            })
        except Exception:
            return Response(
                {'error': 'Token inválido ou expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserAvatarUploadView(APIView):
    """User avatar upload endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        user = request.user
        
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'Nenhum arquivo de avatar fornecido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        avatar_file = request.FILES['avatar']
        
        # Validate file size (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Arquivo muito grande. Máximo 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response(
                {'error': 'Tipo de arquivo não permitido. Use JPEG, PNG ou GIF.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.avatar = avatar_file
        user.save()
        
        return Response(UserProfileSerializer(user).data)


class DeleteAccountView(APIView):
    """Delete user account endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        
        # Soft delete - deactivate account
        user.is_active = False
        user.email = f"deleted_{user.id}@sombreando.com"
        user.username = f"deleted_{user.id}"
        user.save()
        
        return Response({'message': 'Conta deletada com sucesso.'})


class SecurityLogView(generics.ListAPIView):
    """User security log endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LoginAttempt.objects.filter(
            email=self.request.user.email
        ).order_by('-timestamp')[:50]  # Last 50 attempts
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        data = []
        for attempt in queryset:
            data.append({
                'timestamp': attempt.timestamp,
                'ip_address': attempt.ip_address,
                'success': attempt.success,
                'failure_reason': attempt.failure_reason,
                'country': attempt.country,
                'city': attempt.city,
            })
        
        return Response(data)

