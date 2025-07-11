from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, EmailVerificationToken
from .utils import send_verification_email, generate_verification_token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone', 'company_name', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value.lower()
    
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value.lower()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Send verification email
        send_verification_email(user, 'email_verification')
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    verification_code = serializers.CharField(max_length=6, required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        verification_code = attrs.get('verification_code')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError("Credenciais inválidas.")
            
            if not user.is_verified:
                raise serializers.ValidationError("Email não verificado. Verifique sua caixa de entrada.")
            
            if not user.is_active:
                raise serializers.ValidationError("Conta desativada.")
            
            # Check if 2FA is enabled
            if user.is_2fa_enabled:
                if not verification_code:
                    # Send 2FA code
                    send_verification_email(user, 'login_2fa')
                    raise serializers.ValidationError({
                        'requires_2fa': True,
                        'message': 'Código de verificação enviado para seu email.'
                    })
                else:
                    # Validate 2FA code
                    token = EmailVerificationToken.objects.filter(
                        user=user,
                        token=verification_code,
                        purpose='login_2fa',
                        is_used=False
                    ).first()
                    
                    if not token or not token.is_valid:
                        raise serializers.ValidationError("Código de verificação inválido ou expirado.")
                    
                    token.mark_as_used()
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Email e senha são obrigatórios.")


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    full_name = serializers.ReadOnlyField()
    is_subscription_active = serializers.ReadOnlyField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'company_name', 'is_verified', 'is_2fa_enabled',
            'subscription_plan', 'is_subscription_active', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return UserProfileDetailSerializer(obj.profile).data
        return None


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'location', 'website', 'birth_date', 'language', 'timezone',
            'email_notifications', 'push_notifications', 'marketing_emails',
            'profile_visibility'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    token = serializers.CharField(max_length=6)
    
    def validate_token(self, value):
        user = self.context['request'].user
        
        token = EmailVerificationToken.objects.filter(
            user=user,
            token=value,
            purpose='email_verification',
            is_used=False
        ).first()
        
        if not token:
            raise serializers.ValidationError("Token inválido.")
        
        if not token.is_valid:
            raise serializers.ValidationError("Token expirado ou inválido.")
        
        return value
    
    def save(self):
        user = self.context['request'].user
        token = EmailVerificationToken.objects.get(
            user=user,
            token=self.validated_data['token'],
            purpose='email_verification',
            is_used=False
        )
        
        token.mark_as_used()
        user.is_verified = True
        user.save()
        
        return user


class Toggle2FASerializer(serializers.Serializer):
    """Serializer for enabling/disabling 2FA"""
    
    enable = serializers.BooleanField()
    verification_code = serializers.CharField(max_length=6, required=False)
    
    def validate(self, attrs):
        user = self.context['request'].user
        enable = attrs.get('enable')
        verification_code = attrs.get('verification_code')
        
        if enable and not user.is_2fa_enabled:
            # Enabling 2FA requires verification
            if not verification_code:
                # Send verification code
                send_verification_email(user, 'account_change')
                raise serializers.ValidationError({
                    'requires_verification': True,
                    'message': 'Código de verificação enviado para seu email.'
                })
            else:
                # Validate verification code
                token = EmailVerificationToken.objects.filter(
                    user=user,
                    token=verification_code,
                    purpose='account_change',
                    is_used=False
                ).first()
                
                if not token or not token.is_valid:
                    raise serializers.ValidationError("Código de verificação inválido ou expirado.")
                
                attrs['token'] = token
        
        return attrs
    
    def save(self):
        user = self.context['request'].user
        enable = self.validated_data['enable']
        
        if enable and 'token' in self.validated_data:
            self.validated_data['token'].mark_as_used()
        
        user.is_2fa_enabled = enable
        user.save()
        
        return user


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    login_attempts_today = serializers.IntegerField()
    total_login_attempts = serializers.IntegerField()
    account_age_days = serializers.IntegerField()
    is_verified = serializers.BooleanField()
    is_2fa_enabled = serializers.BooleanField()
    subscription_plan = serializers.CharField()
    is_subscription_active = serializers.BooleanField()


class EmailAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking email availability"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        return value.lower()


class UsernameAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking username availability"""
    
    username = serializers.CharField(max_length=150)
    
    def validate_username(self, value):
        return value.lower()

