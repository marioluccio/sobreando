# 📁 Estrutura do Projeto Sombreando

Este documento descreve a organização completa do projeto Sombreando, explicando a função de cada diretório e arquivo.

## 🏗️ Visão Geral da Arquitetura

```
sombreando/
├── 🐍 backend/                 # Django REST API
├── 📱 frontend/                # React Native Expo
├── 🐳 docker/                  # Configurações Docker
├── 📜 scripts/                 # Scripts de automação
├── 📚 docs/                    # Documentação adicional
├── 🧪 tests/                   # Testes integrados
├── 🔧 .env.example             # Exemplo de configuração
├── 🐳 docker-compose.yml       # Orquestração de containers
├── 🚀 railway.json             # Configuração Railway
├── 📖 README.md                # Documentação principal
├── 📦 INSTALLATION.md          # Guia de instalação
├── 🔒 SECURITY_GUIDE.md        # Guia de segurança
└── 📄 LICENSE                  # Licença MIT
```

## 🐍 Backend (Django REST Framework)

### Estrutura Principal

```
backend/
├── manage.py                   # Script de gerenciamento Django
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Container do backend
├── pytest.ini                  # Configuração de testes
└── sombreando/                 # Projeto Django principal
    ├── __init__.py
    ├── urls.py                 # URLs principais
    ├── wsgi.py                 # WSGI para produção
    ├── settings/               # Configurações por ambiente
    │   ├── __init__.py
    │   ├── base.py             # Configurações base
    │   ├── local.py            # Desenvolvimento
    │   └── production.py       # Produção
    └── apps/                   # Aplicações Django
        ├── __init__.py
        ├── authentication/     # Sistema de autenticação
        ├── payments/           # Integração Mercado Pago
        ├── maps/              # Integração Mapbox
        └── core/              # Funcionalidades centrais
```

### App de Autenticação

```
authentication/
├── __init__.py
├── apps.py                     # Configuração do app
├── models.py                   # Modelos de usuário e tokens
├── serializers.py              # Serializers da API
├── views.py                    # Views da API REST
├── urls.py                     # URLs do app
├── utils.py                    # Funções utilitárias
├── permissions.py              # Permissões customizadas
├── tests.py                    # Testes unitários
├── admin.py                    # Interface admin
└── migrations/                 # Migrações do banco
    └── __init__.py
```

#### Principais Funcionalidades:

- **Modelos**:
  - `User`: Usuário customizado com 2FA
  - `UserProfile`: Perfil estendido
  - `EmailVerificationToken`: Tokens de verificação
  - `LoginAttempt`: Log de tentativas de login
  - `UserSession`: Sessões ativas

- **APIs**:
  - Registro e login com JWT
  - 2FA via email
  - Gerenciamento de perfil
  - Verificação de email
  - Logs de segurança

### App de Pagamentos

```
payments/
├── models.py                   # Modelos de pagamento
├── serializers.py              # Serializers Mercado Pago
├── views.py                    # APIs de pagamento
├── utils.py                    # Integração MP
└── webhooks.py                 # Webhooks MP
```

#### Funcionalidades:

- Integração completa com Mercado Pago
- Processamento de pagamentos
- Webhooks para atualizações
- Gestão de assinaturas
- Histórico de transações

### App de Mapas

```
maps/
├── models.py                   # Modelos de localização
├── serializers.py              # Serializers Mapbox
├── views.py                    # APIs de mapas
└── utils.py                    # Integração Mapbox
```

#### Funcionalidades:

- Integração com Mapbox
- Geolocalização
- Marcadores personalizados
- Busca por proximidade
- Rotas e direções

### App Core

```
core/
├── models.py                   # Modelos centrais
├── views.py                    # APIs gerais
├── utils.py                    # Utilitários globais
└── middleware.py               # Middlewares customizados
```

#### Funcionalidades:

- Health checks
- Configurações globais
- Middlewares de segurança
- APIs de sistema

## 📱 Frontend (React Native Expo)

### Estrutura Principal

```
frontend/
├── App.tsx                     # Componente principal
├── package.json                # Dependências Node.js
├── tsconfig.json               # Configuração TypeScript
├── app.json                    # Configuração Expo
├── babel.config.js             # Configuração Babel
├── jest.config.js              # Configuração Jest
├── metro.config.js             # Configuração Metro
├── assets/                     # Assets estáticos
│   ├── images/
│   └── icons/
└── src/                        # Código fonte
    ├── components/             # Componentes reutilizáveis
    ├── screens/                # Telas da aplicação
    ├── navigation/             # Navegação
    ├── services/               # Serviços de API
    ├── store/                  # Redux store
    ├── types/                  # Tipos TypeScript
    ├── utils/                  # Utilitários
    ├── hooks/                  # Hooks customizados
    └── constants/              # Constantes
```

### Componentes

```
components/
├── common/                     # Componentes comuns
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   ├── LoadingScreen.tsx
│   └── ErrorBoundary.tsx
├── auth/                       # Componentes de auth
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── TwoFactorForm.tsx
├── maps/                       # Componentes de mapas
│   ├── MapView.tsx
│   ├── MarkerComponent.tsx
│   └── LocationPicker.tsx
└── payments/                   # Componentes de pagamento
    ├── PaymentForm.tsx
    ├── SubscriptionCard.tsx
    └── PaymentHistory.tsx
```

### Telas

```
screens/
├── auth/                       # Telas de autenticação
│   ├── LoginScreen.tsx
│   ├── RegisterScreen.tsx
│   ├── ForgotPasswordScreen.tsx
│   └── EmailVerificationScreen.tsx
├── main/                       # Telas principais
│   ├── HomeScreen.tsx
│   ├── DashboardScreen.tsx
│   └── SearchScreen.tsx
├── profile/                    # Telas de perfil
│   ├── ProfileScreen.tsx
│   ├── EditProfileScreen.tsx
│   ├── SettingsScreen.tsx
│   └── SecurityScreen.tsx
├── maps/                       # Telas de mapas
│   ├── MapScreen.tsx
│   ├── LocationDetailsScreen.tsx
│   └── DirectionsScreen.tsx
└── payments/                   # Telas de pagamento
    ├── PaymentScreen.tsx
    ├── SubscriptionScreen.tsx
    └── BillingScreen.tsx
```

### Serviços

```
services/
├── apiClient.ts                # Cliente HTTP base
├── authService.ts              # Serviços de autenticação
├── paymentService.ts           # Serviços de pagamento
├── mapService.ts               # Serviços de mapas
└── notificationService.ts      # Serviços de notificação
```

### Store Redux

```
store/
├── index.ts                    # Configuração do store
├── slices/                     # Redux slices
│   ├── authSlice.ts
│   ├── appSlice.ts
│   ├── mapSlice.ts
│   └── paymentSlice.ts
└── middleware/                 # Middlewares Redux
    ├── authMiddleware.ts
    └── errorMiddleware.ts
```

### Tipos TypeScript

```
types/
├── index.ts                    # Tipos principais
├── auth.ts                     # Tipos de autenticação
├── payment.ts                  # Tipos de pagamento
├── map.ts                      # Tipos de mapas
└── navigation.ts               # Tipos de navegação
```

## 🐳 Docker e Deploy

### Configurações Docker

```
docker/
├── nginx/                      # Configuração Nginx
│   ├── default.conf
│   └── ssl.conf
├── postgres/                   # Configuração PostgreSQL
│   ├── init.sql
│   └── postgresql.conf
└── railway/                    # Configuração Railway
    ├── Dockerfile.railway
    └── railway.toml
```

### Scripts de Automação

```
scripts/
├── dev.sh                      # Script de desenvolvimento
├── deploy.sh                   # Script de deploy
├── entrypoint.sh               # Entrypoint Docker
├── backup.sh                   # Script de backup
└── migrate.sh                  # Script de migração
```

#### Comandos Disponíveis:

**Desenvolvimento:**
```bash
./scripts/dev.sh setup          # Configurar ambiente
./scripts/dev.sh start          # Iniciar serviços
./scripts/dev.sh backend test   # Executar testes backend
./scripts/dev.sh frontend start # Iniciar Expo
./scripts/dev.sh db backup      # Backup do banco
```

**Deploy:**
```bash
./scripts/deploy.sh dev         # Deploy desenvolvimento
./scripts/deploy.sh prod        # Deploy produção
./scripts/deploy.sh test        # Executar testes
./scripts/deploy.sh logs        # Ver logs
```

## 📚 Documentação

### Arquivos de Documentação

```
docs/
├── api/                        # Documentação da API
│   ├── authentication.md
│   ├── payments.md
│   └── maps.md
├── deployment/                 # Guias de deploy
│   ├── railway.md
│   ├── docker.md
│   └── vps.md
├── development/                # Guias de desenvolvimento
│   ├── setup.md
│   ├── testing.md
│   └── contributing.md
└── architecture/               # Documentação de arquitetura
    ├── database.md
    ├── security.md
    └── performance.md
```

### Documentação Principal

- **README.md**: Visão geral e início rápido
- **INSTALLATION.md**: Guia detalhado de instalação
- **SECURITY_GUIDE.md**: Práticas de segurança
- **PROJECT_STRUCTURE.md**: Este documento

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── backend/                    # Testes backend
│   ├── unit/                   # Testes unitários
│   ├── integration/            # Testes de integração
│   └── e2e/                    # Testes end-to-end
├── frontend/                   # Testes frontend
│   ├── components/             # Testes de componentes
│   ├── screens/                # Testes de telas
│   └── services/               # Testes de serviços
└── fixtures/                   # Dados de teste
    ├── users.json
    ├── payments.json
    └── locations.json
```

### Tipos de Teste

**Backend (Django):**
- Testes unitários com pytest
- Testes de API com DRF
- Testes de integração
- Testes de performance
- Testes de segurança

**Frontend (React Native):**
- Testes de componentes com Jest
- Testes de hooks
- Testes de navegação
- Testes de Redux
- Testes de serviços

## 🔧 Configuração

### Variáveis de Ambiente

```
.env.example                    # Exemplo de configuração
```

#### Principais Variáveis:

**Django:**
- `SECRET_KEY`: Chave secreta Django
- `DEBUG`: Modo debug
- `DATABASE_URL`: URL do banco PostgreSQL
- `REDIS_URL`: URL do Redis

**Integrações:**
- `MERCADO_PAGO_ACCESS_TOKEN`: Token Mercado Pago
- `MAPBOX_ACCESS_TOKEN`: Token Mapbox
- `SENTRY_DSN`: DSN do Sentry

**Email:**
- `EMAIL_HOST`: Servidor SMTP
- `EMAIL_HOST_USER`: Usuário SMTP
- `EMAIL_HOST_PASSWORD`: Senha SMTP

### Arquivos de Configuração

- **docker-compose.yml**: Orquestração local
- **railway.json**: Deploy Railway
- **nginx.conf**: Configuração web server
- **requirements.txt**: Dependências Python
- **package.json**: Dependências Node.js

## 📊 Monitoramento

### Logs

```
logs/
├── django.log                  # Logs Django
├── nginx.log                   # Logs Nginx
├── postgres.log                # Logs PostgreSQL
└── security.log                # Logs de segurança
```

### Métricas

- Health checks automáticos
- Monitoramento de performance
- Alertas de segurança
- Backup automático
- Logs estruturados

## 🔒 Segurança

### Implementações de Segurança

**Autenticação:**
- JWT com refresh tokens
- 2FA via email
- Rate limiting
- Logs de tentativas

**Proteção de Dados:**
- Criptografia em trânsito (HTTPS)
- Hash seguro de senhas
- Sanitização de entrada
- Headers de segurança

**Monitoramento:**
- Logs de auditoria
- Detecção de intrusão
- Alertas automáticos
- Backup criptografado

## 🚀 Deploy

### Ambientes

**Desenvolvimento:**
- Docker Compose local
- Hot reload habilitado
- Debug mode ativo
- Banco local PostgreSQL

**Produção:**
- Railway deployment
- HTTPS obrigatório
- Banco PostgreSQL gerenciado
- Redis para cache
- Nginx como proxy

### CI/CD

- Testes automáticos
- Build automático
- Deploy automático
- Rollback automático

## 📈 Performance

### Otimizações

**Backend:**
- Cache Redis
- Conexões persistentes
- Query optimization
- Compressão gzip

**Frontend:**
- Bundle optimization
- Image optimization
- Lazy loading
- Offline support

**Banco de Dados:**
- Índices otimizados
- Queries eficientes
- Connection pooling
- Backup incremental

## 🔄 Manutenção

### Tarefas Regulares

**Diárias:**
- Verificar logs de erro
- Monitorar performance
- Backup automático

**Semanais:**
- Atualizar dependências
- Revisar logs de segurança
- Testar backups

**Mensais:**
- Auditoria de segurança
- Limpeza de logs antigos
- Otimização de banco

## 📞 Suporte

### Contatos

- **Desenvolvimento**: dev@sombreando.com
- **Segurança**: security@sombreando.com
- **Suporte**: suporte@sombreando.com

### Recursos

- **Documentação**: Neste repositório
- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Wiki**: GitHub Wiki

---

**Este documento é atualizado automaticamente com mudanças na estrutura do projeto.**

*Última atualização: Dezembro 2024*

