# 🔒 Guia de Segurança - Sombreando

Este documento detalha as práticas de segurança implementadas no Sombreando e fornece diretrizes para manter a aplicação segura em produção.

## 📋 Índice

1. [Visão Geral de Segurança](#visão-geral-de-segurança)
2. [Autenticação e Autorização](#autenticação-e-autorização)
3. [Proteção de Dados](#proteção-de-dados)
4. [Segurança de Rede](#segurança-de-rede)
5. [Configurações de Produção](#configurações-de-produção)
6. [Monitoramento e Auditoria](#monitoramento-e-auditoria)
7. [Resposta a Incidentes](#resposta-a-incidentes)
8. [Checklist de Segurança](#checklist-de-segurança)

## 🛡️ Visão Geral de Segurança

O Sombreando implementa uma arquitetura de segurança em camadas (Defense in Depth) que inclui:

- **Autenticação robusta** com JWT e 2FA
- **Autorização granular** baseada em permissões
- **Criptografia** de dados sensíveis
- **Validação rigorosa** de entrada
- **Rate limiting** para prevenir ataques
- **Logs de auditoria** para rastreabilidade
- **Headers de segurança** configurados
- **Proteção CSRF** e XSS

### Princípios de Segurança

1. **Princípio do Menor Privilégio**: Usuários e sistemas têm apenas as permissões mínimas necessárias
2. **Defesa em Profundidade**: Múltiplas camadas de proteção
3. **Falha Segura**: Em caso de erro, o sistema falha de forma segura
4. **Segurança por Design**: Segurança considerada desde o início do desenvolvimento

## 🔐 Autenticação e Autorização

### Sistema JWT

O Sombreando utiliza JSON Web Tokens (JWT) para autenticação stateless:

```python
# Configuração JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
}
```

#### Características de Segurança:

- **Tokens de curta duração**: Access tokens expiram em 60 minutos
- **Rotação de tokens**: Refresh tokens são rotacionados a cada uso
- **Blacklist**: Tokens antigos são invalidados
- **Assinatura segura**: Tokens assinados com chave secreta forte

### Autenticação de Dois Fatores (2FA)

O 2FA via email adiciona uma camada extra de segurança:

```python
class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)  # 6-digit code
    purpose = models.CharField(max_length=20)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired and self.attempts < 3
```

#### Características:

- **Códigos temporários**: Expiram em 24 horas
- **Limite de tentativas**: Máximo 3 tentativas por token
- **Propósito específico**: Tokens vinculados a ações específicas
- **Rate limiting**: Prevenção de spam de emails

### Políticas de Senha

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

#### Requisitos de Senha:

- **Mínimo 12 caracteres**
- **Não pode ser similar ao nome de usuário**
- **Não pode ser uma senha comum**
- **Não pode ser apenas numérica**
- **Deve conter maiúsculas, minúsculas, números e símbolos**

### Controle de Acesso

```python
class UserPermissions:
    """Permissões granulares por funcionalidade"""
    
    # Perfil
    CAN_VIEW_PROFILE = 'auth.view_profile'
    CAN_EDIT_PROFILE = 'auth.change_profile'
    CAN_DELETE_ACCOUNT = 'auth.delete_account'
    
    # Pagamentos
    CAN_VIEW_PAYMENTS = 'payments.view_payment'
    CAN_CREATE_PAYMENT = 'payments.add_payment'
    
    # Mapas
    CAN_VIEW_MAPS = 'maps.view_map'
    CAN_EDIT_MARKERS = 'maps.change_marker'
```

## 🔒 Proteção de Dados

### Criptografia

#### Dados em Trânsito

- **HTTPS obrigatório** em produção
- **TLS 1.2+** para todas as conexões
- **HSTS** configurado para forçar HTTPS
- **Certificate pinning** no app móvel

```python
# Configurações HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### Dados em Repouso

- **Senhas hasheadas** com bcrypt
- **Tokens sensíveis** criptografados
- **Dados PII** criptografados quando necessário
- **Backup criptografado** do banco de dados

```python
# Configuração de hash de senha
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### Proteção de Dados Pessoais (LGPD/GDPR)

```python
class DataProtectionMixin:
    """Mixin para proteção de dados pessoais"""
    
    def anonymize_user_data(self, user):
        """Anonimiza dados do usuário"""
        user.email = f"deleted_{user.id}@sombreando.com"
        user.first_name = "Usuário"
        user.last_name = "Removido"
        user.phone = ""
        user.is_active = False
        user.save()
    
    def export_user_data(self, user):
        """Exporta dados do usuário (direito à portabilidade)"""
        return {
            'profile': UserSerializer(user).data,
            'payments': PaymentSerializer(user.payments.all(), many=True).data,
            'login_history': LoginAttemptSerializer(user.login_attempts.all(), many=True).data,
        }
```

### Validação de Entrada

```python
class SecureSerializer(serializers.Serializer):
    """Serializer base com validações de segurança"""
    
    def validate(self, attrs):
        # Sanitização de entrada
        for field, value in attrs.items():
            if isinstance(value, str):
                # Remove caracteres perigosos
                attrs[field] = bleach.clean(value)
                
                # Valida tamanho máximo
                if len(value) > 1000:
                    raise ValidationError(f"{field} muito longo")
        
        return attrs
```

## 🌐 Segurança de Rede

### Rate Limiting

```python
# Configuração de rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
        'register': '3/minute',
    }
}
```

#### Limites por Endpoint:

- **Login**: 5 tentativas por minuto
- **Registro**: 3 tentativas por minuto
- **API geral**: 1000 requests/hora para usuários autenticados
- **API pública**: 100 requests/hora para anônimos

### CORS (Cross-Origin Resource Sharing)

```python
# Configuração CORS restritiva
CORS_ALLOWED_ORIGINS = [
    "https://sombreando.com",
    "https://www.sombreando.com",
    "https://app.sombreando.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Nunca True em produção
```

### Headers de Segurança

```python
# Headers de segurança obrigatórios
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSP (Content Security Policy)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

### Proteção CSRF

```python
# Configuração CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://sombreando.com',
    'https://www.sombreando.com',
]
```

## ⚙️ Configurações de Produção

### Variáveis de Ambiente Seguras

```bash
# Chaves e segredos
SECRET_KEY=sua-chave-super-secreta-de-50-caracteres-ou-mais
JWT_SECRET_KEY=sua-chave-jwt-diferente-da-secret-key

# Banco de dados
DATABASE_URL=postgresql://user:senha_forte@host:5432/db

# Email
EMAIL_HOST_PASSWORD=senha_do_email_provider

# Integrações
MERCADO_PAGO_ACCESS_TOKEN=seu_token_mercado_pago
MAPBOX_ACCESS_TOKEN=seu_token_mapbox

# Monitoramento
SENTRY_DSN=sua_dsn_sentry
```

### Configuração do Banco de Dados

```python
# Configurações seguras do PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',  # SSL obrigatório
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=serializable'
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}
```

### Configuração do Redis

```python
# Redis com autenticação
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://username:password@host:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': 'required',
                'ssl_ca_certs': '/path/to/ca.crt',
            }
        }
    }
}
```

### Configuração do Nginx

```nginx
# Configuração segura do Nginx
server {
    listen 443 ssl http2;
    server_name sombreando.com;
    
    # SSL/TLS
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    
    location /api/v1/auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://backend;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

## 📊 Monitoramento e Auditoria

### Logs de Segurança

```python
# Configuração de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/sombreando/security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Eventos Auditados

```python
class SecurityLogger:
    """Logger para eventos de segurança"""
    
    @staticmethod
    def log_login_attempt(user_email, ip_address, success, failure_reason=None):
        logger = logging.getLogger('security')
        logger.info(f"LOGIN_ATTEMPT: {user_email} from {ip_address} - {'SUCCESS' if success else 'FAILED'} {failure_reason or ''}")
    
    @staticmethod
    def log_password_change(user_email, ip_address):
        logger = logging.getLogger('security')
        logger.info(f"PASSWORD_CHANGE: {user_email} from {ip_address}")
    
    @staticmethod
    def log_2fa_toggle(user_email, enabled, ip_address):
        logger = logging.getLogger('security')
        action = "ENABLED" if enabled else "DISABLED"
        logger.info(f"2FA_{action}: {user_email} from {ip_address}")
    
    @staticmethod
    def log_suspicious_activity(user_email, activity, ip_address):
        logger = logging.getLogger('security')
        logger.warning(f"SUSPICIOUS_ACTIVITY: {activity} - {user_email} from {ip_address}")
```

### Monitoramento de Intrusão

```python
class SecurityMiddleware:
    """Middleware para detecção de atividades suspeitas"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar tentativas de SQL injection
        if self.detect_sql_injection(request):
            SecurityLogger.log_suspicious_activity(
                getattr(request.user, 'email', 'anonymous'),
                'SQL_INJECTION_ATTEMPT',
                self.get_client_ip(request)
            )
            return HttpResponseForbidden("Acesso negado")
        
        # Verificar tentativas de XSS
        if self.detect_xss_attempt(request):
            SecurityLogger.log_suspicious_activity(
                getattr(request.user, 'email', 'anonymous'),
                'XSS_ATTEMPT',
                self.get_client_ip(request)
            )
            return HttpResponseForbidden("Acesso negado")
        
        response = self.get_response(request)
        return response
```

### Alertas Automáticos

```python
class SecurityAlerts:
    """Sistema de alertas de segurança"""
    
    @staticmethod
    def check_failed_logins():
        """Verifica tentativas de login falhadas"""
        threshold = 10
        time_window = timedelta(minutes=15)
        
        failed_attempts = LoginAttempt.objects.filter(
            success=False,
            timestamp__gte=timezone.now() - time_window
        ).values('ip_address').annotate(
            count=Count('id')
        ).filter(count__gte=threshold)
        
        for attempt in failed_attempts:
            send_security_alert(
                f"Múltiplas tentativas de login falhadas do IP {attempt['ip_address']}"
            )
    
    @staticmethod
    def check_unusual_activity():
        """Verifica atividades incomuns"""
        # Login de localizações diferentes
        # Múltiplas sessões simultâneas
        # Alterações de perfil suspeitas
        pass
```

## 🚨 Resposta a Incidentes

### Plano de Resposta

1. **Detecção**: Monitoramento contínuo e alertas automáticos
2. **Análise**: Investigação do escopo e impacto
3. **Contenção**: Isolamento da ameaça
4. **Erradicação**: Remoção da vulnerabilidade
5. **Recuperação**: Restauração dos serviços
6. **Lições Aprendidas**: Melhoria dos processos

### Procedimentos de Emergência

#### Comprometimento de Conta

```python
def emergency_account_lockdown(user_email):
    """Bloqueio emergencial de conta"""
    user = User.objects.get(email=user_email)
    
    # Desativar conta
    user.is_active = False
    user.save()
    
    # Invalidar todas as sessões
    user.sessions.all().delete()
    
    # Revogar tokens JWT
    outstanding_tokens = OutstandingToken.objects.filter(user=user)
    for token in outstanding_tokens:
        BlacklistedToken.objects.get_or_create(token=token)
    
    # Notificar usuário
    send_security_notification(user, "Conta temporariamente suspensa por atividade suspeita")
    
    # Log do incidente
    SecurityLogger.log_suspicious_activity(user.email, "EMERGENCY_LOCKDOWN", "system")
```

#### Vazamento de Dados

```python
def data_breach_response():
    """Resposta a vazamento de dados"""
    
    # 1. Contenção imediata
    # - Isolar sistemas afetados
    # - Revogar credenciais comprometidas
    
    # 2. Avaliação do impacto
    # - Identificar dados afetados
    # - Determinar número de usuários impactados
    
    # 3. Notificação
    # - Autoridades competentes (ANPD)
    # - Usuários afetados
    # - Stakeholders internos
    
    # 4. Documentação
    # - Cronologia do incidente
    # - Ações tomadas
    # - Impacto avaliado
    
    pass
```

### Contatos de Emergência

- **Equipe de Segurança**: security@sombreando.com
- **Administrador de Sistema**: admin@sombreando.com
- **ANPD**: https://www.gov.br/anpd/pt-br
- **CERT.br**: https://www.cert.br/

## ✅ Checklist de Segurança

### Desenvolvimento

- [ ] Validação de entrada implementada
- [ ] Sanitização de saída configurada
- [ ] Autenticação e autorização testadas
- [ ] Logs de segurança implementados
- [ ] Testes de segurança executados
- [ ] Revisão de código realizada

### Deploy

- [ ] HTTPS configurado e funcionando
- [ ] Headers de segurança configurados
- [ ] Rate limiting ativado
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Monitoramento ativo

### Produção

- [ ] Certificados SSL válidos
- [ ] Logs de segurança monitorados
- [ ] Alertas configurados
- [ ] Backup testado
- [ ] Plano de resposta a incidentes atualizado
- [ ] Treinamento da equipe realizado

### Manutenção

- [ ] Atualizações de segurança aplicadas
- [ ] Revisão de logs realizada
- [ ] Testes de penetração executados
- [ ] Auditoria de permissões realizada
- [ ] Documentação atualizada
- [ ] Treinamento contínuo da equipe

## 📚 Recursos Adicionais

### Ferramentas de Segurança

- **OWASP ZAP**: Scanner de vulnerabilidades
- **Bandit**: Análise estática de código Python
- **Safety**: Verificação de vulnerabilidades em dependências
- **Semgrep**: Análise de código para padrões de segurança

### Padrões e Frameworks

- **OWASP Top 10**: Principais riscos de segurança web
- **NIST Cybersecurity Framework**: Framework de cibersegurança
- **ISO 27001**: Padrão de gestão de segurança da informação
- **LGPD**: Lei Geral de Proteção de Dados

### Treinamento

- **OWASP WebGoat**: Aplicação para aprender segurança web
- **PortSwigger Web Security Academy**: Curso gratuito de segurança web
- **SANS**: Cursos de segurança cibernética
- **Coursera/edX**: Cursos online de segurança

## 🔄 Atualizações de Segurança

Este documento deve ser revisado e atualizado:

- **Mensalmente**: Revisão de logs e métricas
- **Trimestralmente**: Atualização de procedimentos
- **Anualmente**: Auditoria completa de segurança
- **Após incidentes**: Incorporação de lições aprendidas

---

**A segurança é responsabilidade de todos. Mantenha-se vigilante! 🛡️**

*Última atualização: [Data atual]*
*Próxima revisão: [Data + 3 meses]*

