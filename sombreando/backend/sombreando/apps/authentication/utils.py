import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailVerificationToken


def generate_verification_token(length=6):
    """Generate a random verification token"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(user, purpose):
    """Send verification email to user"""
    
    # Delete old unused tokens for this purpose
    EmailVerificationToken.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False
    ).delete()
    
    # Generate new token
    token_code = generate_verification_token()
    expires_at = timezone.now() + timedelta(hours=24)
    
    # Create token record
    token = EmailVerificationToken.objects.create(
        user=user,
        token=token_code,
        purpose=purpose,
        expires_at=expires_at
    )
    
    # Email content based on purpose
    email_templates = {
        'email_verification': {
            'subject': 'Verificação de Email - Sombreando',
            'template': 'emails/email_verification.html',
        },
        'password_reset': {
            'subject': 'Reset de Senha - Sombreando',
            'template': 'emails/password_reset.html',
        },
        'login_2fa': {
            'subject': 'Código de Verificação - Sombreando',
            'template': 'emails/login_2fa.html',
        },
        'account_change': {
            'subject': 'Verificação de Mudança de Conta - Sombreando',
            'template': 'emails/account_change.html',
        },
    }
    
    email_config = email_templates.get(purpose)
    if not email_config:
        raise ValueError(f"Unknown email purpose: {purpose}")
    
    # Prepare email context
    context = {
        'user': user,
        'token': token_code,
        'expires_at': expires_at,
        'site_name': 'Sombreando',
        'site_url': getattr(settings, 'SITE_URL', 'https://sombreando.com'),
    }
    
    # Render email content
    try:
        html_message = render_to_string(email_config['template'], context)
        plain_message = f"""
        Olá {user.first_name},
        
        Seu código de verificação é: {token_code}
        
        Este código expira em 24 horas.
        
        Se você não solicitou este código, ignore este email.
        
        Atenciosamente,
        Equipe Sombreando
        """
    except:
        # Fallback to plain text if template doesn't exist
        html_message = None
        plain_message = f"""
        Olá {user.first_name},
        
        Seu código de verificação é: {token_code}
        
        Este código expira em 24 horas.
        
        Se você não solicitou este código, ignore este email.
        
        Atenciosamente,
        Equipe Sombreando
        """
    
    # Send email
    try:
        send_mail(
            subject=email_config['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_password_strength(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 12:
        errors.append("A senha deve ter pelo menos 12 caracteres.")
    
    if not any(c.isupper() for c in password):
        errors.append("A senha deve conter pelo menos uma letra maiúscula.")
    
    if not any(c.islower() for c in password):
        errors.append("A senha deve conter pelo menos uma letra minúscula.")
    
    if not any(c.isdigit() for c in password):
        errors.append("A senha deve conter pelo menos um número.")
    
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        errors.append("A senha deve conter pelo menos um caractere especial.")
    
    # Check for common patterns
    common_patterns = ['123456', 'password', 'qwerty', 'abc123']
    if any(pattern in password.lower() for pattern in common_patterns):
        errors.append("A senha não pode conter padrões comuns.")
    
    return errors


def is_email_domain_allowed(email):
    """Check if email domain is allowed"""
    blocked_domains = getattr(settings, 'BLOCKED_EMAIL_DOMAINS', [])
    domain = email.split('@')[1].lower()
    return domain not in blocked_domains


def generate_username_suggestions(base_username, count=5):
    """Generate username suggestions based on a base username"""
    from .models import User
    
    suggestions = []
    
    # Try base username with numbers
    for i in range(1, count + 1):
        suggestion = f"{base_username}{i}"
        if not User.objects.filter(username__iexact=suggestion).exists():
            suggestions.append(suggestion)
    
    # Try base username with random suffixes
    while len(suggestions) < count:
        suffix = ''.join(random.choices(string.digits, k=3))
        suggestion = f"{base_username}_{suffix}"
        if (not User.objects.filter(username__iexact=suggestion).exists() and 
            suggestion not in suggestions):
            suggestions.append(suggestion)
    
    return suggestions[:count]


def cleanup_expired_tokens():
    """Clean up expired verification tokens"""
    expired_tokens = EmailVerificationToken.objects.filter(
        expires_at__lt=timezone.now()
    )
    count = expired_tokens.count()
    expired_tokens.delete()
    return count


def get_user_device_info(request):
    """Extract device information from request"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    device_info = {
        'user_agent': user_agent,
        'is_mobile': False,
        'is_tablet': False,
        'is_desktop': True,
        'browser': 'Unknown',
        'os': 'Unknown',
    }
    
    # Simple device detection
    user_agent_lower = user_agent.lower()
    
    if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone']):
        device_info['is_mobile'] = True
        device_info['is_desktop'] = False
    elif any(tablet in user_agent_lower for tablet in ['tablet', 'ipad']):
        device_info['is_tablet'] = True
        device_info['is_desktop'] = False
    
    # Browser detection
    if 'chrome' in user_agent_lower:
        device_info['browser'] = 'Chrome'
    elif 'firefox' in user_agent_lower:
        device_info['browser'] = 'Firefox'
    elif 'safari' in user_agent_lower:
        device_info['browser'] = 'Safari'
    elif 'edge' in user_agent_lower:
        device_info['browser'] = 'Edge'
    
    # OS detection
    if 'windows' in user_agent_lower:
        device_info['os'] = 'Windows'
    elif 'mac' in user_agent_lower:
        device_info['os'] = 'macOS'
    elif 'linux' in user_agent_lower:
        device_info['os'] = 'Linux'
    elif 'android' in user_agent_lower:
        device_info['os'] = 'Android'
    elif 'ios' in user_agent_lower:
        device_info['os'] = 'iOS'
    
    return device_info


def rate_limit_check(user_or_ip, action, limit=5, window_minutes=60):
    """Check if action is rate limited"""
    from django.core.cache import cache
    
    if hasattr(user_or_ip, 'email'):
        key = f"rate_limit:{action}:{user_or_ip.email}"
    else:
        key = f"rate_limit:{action}:{user_or_ip}"
    
    current_count = cache.get(key, 0)
    
    if current_count >= limit:
        return False, limit - current_count
    
    # Increment counter
    cache.set(key, current_count + 1, window_minutes * 60)
    
    return True, limit - (current_count + 1)

