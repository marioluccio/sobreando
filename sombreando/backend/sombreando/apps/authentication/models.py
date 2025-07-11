from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class User(AbstractUser):
    """Custom User model with additional fields for Sombreando"""
    
    SUBSCRIPTION_CHOICES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Verification fields
    is_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    
    # Company information
    company_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Subscription information
    subscription_plan = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_CHOICES, 
        default='free'
    )
    subscription_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_subscription_active(self):
        if self.subscription_plan == 'free':
            return True
        if self.subscription_expires_at:
            return self.subscription_expires_at > timezone.now()
        return False


class UserProfile(models.Model):
    """Extended user profile information"""
    
    LANGUAGE_CHOICES = [
        ('pt-br', 'Português (Brasil)'),
        ('en', 'English'),
        ('es', 'Español'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Preferences
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='pt-br')
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Público'),
            ('private', 'Privado'),
            ('friends', 'Apenas Amigos'),
        ],
        default='public'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'
    
    def __str__(self):
        return f"{self.user.email} Profile"


class EmailVerificationToken(models.Model):
    """Email verification tokens for 2FA and account verification"""
    
    PURPOSE_CHOICES = [
        ('email_verification', 'Verificação de Email'),
        ('password_reset', 'Reset de Senha'),
        ('login_2fa', '2FA Login'),
        ('account_change', 'Mudança de Conta'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=6)  # 6-digit code
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'email_verification_token'
        verbose_name = 'Token de Verificação'
        verbose_name_plural = 'Tokens de Verificação'
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
            models.Index(fields=['token', 'purpose']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.token}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired and self.attempts < 3
    
    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save()


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring"""
    
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Geolocation data (optional)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'login_attempt'
        verbose_name = 'Tentativa de Login'
        verbose_name_plural = 'Tentativas de Login'
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.email} - {status} - {self.timestamp}"


class UserSession(models.Model):
    """Track active user sessions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict, blank=True)
    
    # Location data
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_session'
        verbose_name = 'Sessão do Usuário'
        verbose_name_plural = 'Sessões dos Usuários'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."
    
    @property
    def is_expired(self):
        return (timezone.now() - self.last_activity) > timedelta(days=30)

