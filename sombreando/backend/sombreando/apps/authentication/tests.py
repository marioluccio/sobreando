import json
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerificationToken, LoginAttempt, UserProfile
from .utils import generate_verification_token, send_verification_email

User = get_user_model()


class UserModelTest(TestCase):
    """Testes para o modelo User"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@sombreando.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!@#'
        }
    
    def test_create_user(self):
        """Teste criação de usuário"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_2fa_enabled)
        self.assertEqual(user.subscription_plan, 'free')
    
    def test_create_superuser(self):
        """Teste criação de superusuário"""
        user = User.objects.create_superuser(
            email='admin@sombreando.com',
            username='admin',
            password='AdminPassword123!@#'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)
    
    def test_user_full_name(self):
        """Teste propriedade full_name"""
        user = User.objects.create_user(**self.user_data)
        expected_name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.full_name, expected_name)
    
    def test_subscription_active(self):
        """Teste propriedade is_subscription_active"""
        user = User.objects.create_user(**self.user_data)
        
        # Free plan sempre ativo
        self.assertTrue(user.is_subscription_active)
        
        # Premium plan sem data de expiração
        user.subscription_plan = 'premium'
        user.save()
        self.assertFalse(user.is_subscription_active)
        
        # Premium plan com data futura
        user.subscription_expires_at = timezone.now() + timedelta(days=30)
        user.save()
        self.assertTrue(user.is_subscription_active)
        
        # Premium plan expirado
        user.subscription_expires_at = timezone.now() - timedelta(days=1)
        user.save()
        self.assertFalse(user.is_subscription_active)


class UserProfileModelTest(TestCase):
    """Testes para o modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@sombreando.com',
            username='testuser',
            password='TestPassword123!@#'
        )
    
    def test_profile_creation(self):
        """Teste criação automática de perfil"""
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.language, 'pt-br')
        self.assertEqual(profile.timezone, 'America/Sao_Paulo')
        self.assertTrue(profile.email_notifications)
        self.assertTrue(profile.push_notifications)
        self.assertFalse(profile.marketing_emails)


class EmailVerificationTokenTest(TestCase):
    """Testes para o modelo EmailVerificationToken"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@sombreando.com',
            username='testuser',
            password='TestPassword123!@#'
        )
    
    def test_token_creation(self):
        """Teste criação de token"""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, '123456')
        self.assertFalse(token.is_used)
        self.assertEqual(token.attempts, 0)
    
    def test_token_validity(self):
        """Teste validade do token"""
        # Token válido
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        self.assertTrue(token.is_valid)
        
        # Token usado
        token.is_used = True
        token.save()
        self.assertFalse(token.is_valid)
        
        # Token expirado
        token.is_used = False
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        self.assertFalse(token.is_valid)
        
        # Muitas tentativas
        token.expires_at = timezone.now() + timedelta(hours=24)
        token.attempts = 3
        token.save()
        self.assertFalse(token.is_valid)
    
    def test_mark_as_used(self):
        """Teste marcar token como usado"""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        token.mark_as_used()
        
        self.assertTrue(token.is_used)
        self.assertIsNotNone(token.used_at)


class AuthenticationAPITest(APITestCase):
    """Testes para as APIs de autenticação"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.profile_url = reverse('authentication:profile')
        
        self.user_data = {
            'email': 'test@sombreando.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!@#',
            'password_confirm': 'TestPassword123!@#'
        }
        
        self.user = User.objects.create_user(
            email='existing@sombreando.com',
            username='existing',
            password='ExistingPassword123!@#',
            is_verified=True
        )
    
    def test_user_registration(self):
        """Teste registro de usuário"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        
        # Verificar se usuário foi criado
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertFalse(user.is_verified)
    
    def test_registration_duplicate_email(self):
        """Teste registro com email duplicado"""
        self.user_data['email'] = 'existing@sombreando.com'
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_password_mismatch(self):
        """Teste registro com senhas diferentes"""
        self.user_data['password_confirm'] = 'DifferentPassword123!@#'
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Teste login de usuário"""
        login_data = {
            'email': 'existing@sombreando.com',
            'password': 'ExistingPassword123!@#'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Teste login com credenciais inválidas"""
        login_data = {
            'email': 'existing@sombreando.com',
            'password': 'WrongPassword123!@#'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verificar se tentativa foi logada
        attempt = LoginAttempt.objects.filter(email=login_data['email']).first()
        self.assertIsNotNone(attempt)
        self.assertFalse(attempt.success)
    
    def test_login_unverified_user(self):
        """Teste login com usuário não verificado"""
        unverified_user = User.objects.create_user(
            email='unverified@sombreando.com',
            username='unverified',
            password='UnverifiedPassword123!@#',
            is_verified=False
        )
        
        login_data = {
            'email': 'unverified@sombreando.com',
            'password': 'UnverifiedPassword123!@#'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_2fa(self):
        """Teste login com 2FA habilitado"""
        self.user.is_2fa_enabled = True
        self.user.save()
        
        login_data = {
            'email': 'existing@sombreando.com',
            'password': 'ExistingPassword123!@#'
        }
        
        # Primeiro login sem código 2FA
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Criar token 2FA
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='login_2fa',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Login com código 2FA
        login_data['verification_code'] = '123456'
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Verificar se token foi marcado como usado
        token.refresh_from_db()
        self.assertTrue(token.is_used)
    
    def test_user_logout(self):
        """Teste logout de usuário"""
        # Fazer login primeiro
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        logout_data = {'refresh': str(refresh)}
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_profile(self):
        """Teste obter perfil do usuário"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_update_user_profile(self):
        """Teste atualizar perfil do usuário"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+5511999999999'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        
        # Verificar se foi salvo no banco
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')


class EmailVerificationAPITest(APITestCase):
    """Testes para verificação de email"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@sombreando.com',
            username='testuser',
            password='TestPassword123!@#',
            is_verified=False
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.verify_url = reverse('authentication:email_verify')
        self.resend_url = reverse('authentication:email_resend')
    
    def test_email_verification(self):
        """Teste verificação de email"""
        # Criar token de verificação
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        verify_data = {'token': '123456'}
        response = self.client.post(self.verify_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se usuário foi marcado como verificado
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        
        # Verificar se token foi marcado como usado
        token.refresh_from_db()
        self.assertTrue(token.is_used)
    
    def test_email_verification_invalid_token(self):
        """Teste verificação com token inválido"""
        verify_data = {'token': '999999'}
        response = self.client.post(self.verify_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resend_verification_email(self):
        """Teste reenvio de email de verificação"""
        response = self.client.post(self.resend_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se token foi criado
        token = EmailVerificationToken.objects.filter(
            user=self.user,
            purpose='email_verification'
        ).first()
        self.assertIsNotNone(token)
    
    def test_resend_verification_already_verified(self):
        """Teste reenvio para usuário já verificado"""
        self.user.is_verified = True
        self.user.save()
        
        response = self.client.post(self.resend_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TwoFactorAuthTest(APITestCase):
    """Testes para autenticação de dois fatores"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@sombreando.com',
            username='testuser',
            password='TestPassword123!@#',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.toggle_2fa_url = reverse('authentication:toggle_2fa')
    
    def test_enable_2fa(self):
        """Teste habilitar 2FA"""
        # Criar token de verificação
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='123456',
            purpose='account_change',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        toggle_data = {
            'enable': True,
            'verification_code': '123456'
        }
        
        response = self.client.post(self.toggle_2fa_url, toggle_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se 2FA foi habilitado
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)
    
    def test_disable_2fa(self):
        """Teste desabilitar 2FA"""
        self.user.is_2fa_enabled = True
        self.user.save()
        
        toggle_data = {'enable': False}
        response = self.client.post(self.toggle_2fa_url, toggle_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se 2FA foi desabilitado
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_2fa_enabled)


class UtilsTest(TestCase):
    """Testes para funções utilitárias"""
    
    def test_generate_verification_token(self):
        """Teste geração de token de verificação"""
        token = generate_verification_token()
        
        self.assertEqual(len(token), 6)
        self.assertTrue(token.isdigit())
    
    def test_generate_verification_token_custom_length(self):
        """Teste geração de token com tamanho customizado"""
        token = generate_verification_token(8)
        
        self.assertEqual(len(token), 8)
        self.assertTrue(token.isdigit())


class SecurityTest(APITestCase):
    """Testes de segurança"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@sombreando.com',
            username='testuser',
            password='TestPassword123!@#',
            is_verified=True
        )
    
    def test_rate_limiting_login(self):
        """Teste rate limiting no login"""
        login_url = reverse('authentication:login')
        login_data = {
            'email': 'test@sombreando.com',
            'password': 'WrongPassword123!@#'
        }
        
        # Fazer múltiplas tentativas de login
        for i in range(6):  # Limite é 5 por minuto
            response = self.client.post(login_url, login_data)
        
        # A 6ª tentativa deve ser bloqueada
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_password_validation(self):
        """Teste validação de senha"""
        register_url = reverse('authentication:register')
        
        # Senha muito simples
        weak_passwords = [
            '123456',
            'password',
            'abc123',
            'qwerty',
            'TestPassword',  # Sem símbolos
            'testpassword123!@#',  # Sem maiúsculas
            'TESTPASSWORD123!@#',  # Sem minúsculas
            'TestPassword!@#',  # Sem números
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                'email': f'test{weak_password}@sombreando.com',
                'username': f'test{weak_password}',
                'first_name': 'Test',
                'last_name': 'User',
                'password': weak_password,
                'password_confirm': weak_password
            }
            
            response = self.client.post(register_url, user_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_sql_injection_protection(self):
        """Teste proteção contra SQL injection"""
        login_url = reverse('authentication:login')
        
        # Tentativas de SQL injection
        malicious_inputs = [
            "'; DROP TABLE auth_user; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM auth_user --"
        ]
        
        for malicious_input in malicious_inputs:
            login_data = {
                'email': malicious_input,
                'password': 'TestPassword123!@#'
            }
            
            response = self.client.post(login_url, login_data)
            # Deve retornar erro de validação, não erro de servidor
            self.assertIn(response.status_code, [400, 401])
    
    def test_xss_protection(self):
        """Teste proteção contra XSS"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_url = reverse('authentication:profile')
        
        # Tentativas de XSS
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            update_data = {
                'first_name': payload,
                'last_name': 'Test'
            }
            
            response = self.client.patch(profile_url, update_data)
            
            # Verificar se payload foi sanitizado
            if response.status_code == 200:
                self.assertNotIn('<script>', response.data.get('first_name', ''))
                self.assertNotIn('javascript:', response.data.get('first_name', ''))


class PerformanceTest(APITestCase):
    """Testes de performance"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_login_performance(self):
        """Teste performance do login"""
        # Criar usuário
        user = User.objects.create_user(
            email='perf@sombreando.com',
            username='perfuser',
            password='PerfPassword123!@#',
            is_verified=True
        )
        
        login_url = reverse('authentication:login')
        login_data = {
            'email': 'perf@sombreando.com',
            'password': 'PerfPassword123!@#'
        }
        
        import time
        start_time = time.time()
        
        response = self.client.post(login_url, login_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 1.0)  # Login deve ser < 1 segundo
    
    def test_bulk_user_creation(self):
        """Teste criação em massa de usuários"""
        import time
        start_time = time.time()
        
        users = []
        for i in range(100):
            users.append(User(
                email=f'bulk{i}@sombreando.com',
                username=f'bulk{i}',
                first_name='Bulk',
                last_name='User'
            ))
        
        User.objects.bulk_create(users)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        self.assertEqual(User.objects.filter(email__startswith='bulk').count(), 100)
        self.assertLess(creation_time, 5.0)  # Criação deve ser < 5 segundos

