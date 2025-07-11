# 📦 Guia de Instalação - Sombreando

Este guia fornece instruções detalhadas para configurar o ambiente de desenvolvimento e produção do Sombreando.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação para Desenvolvimento](#instalação-para-desenvolvimento)
3. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
4. [Configuração de Variáveis de Ambiente](#configuração-de-variáveis-de-ambiente)
5. [Instalação do Backend](#instalação-do-backend)
6. [Instalação do Frontend](#instalação-do-frontend)
7. [Deploy em Produção](#deploy-em-produção)
8. [Solução de Problemas](#solução-de-problemas)

## 🔧 Pré-requisitos

### Sistema Operacional

O Sombreando é compatível com:
- **Linux** (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **macOS** (10.15+)
- **Windows** (10/11 com WSL2)

### Software Necessário

#### Docker (Recomendado)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
brew install docker docker-compose

# Windows
# Baixe Docker Desktop do site oficial
```

#### Node.js (Para desenvolvimento frontend)

```bash
# Usando Node Version Manager (recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Ou via package manager
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@18

# Windows
# Baixe do site oficial nodejs.org
```

#### Python (Para desenvolvimento backend)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip

# macOS
brew install python@3.11

# Windows (WSL2)
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip
```

#### Git

```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows
# Baixe do site oficial git-scm.com
```

## 🚀 Instalação para Desenvolvimento

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/sombreando.git
cd sombreando
```

### 2. Configuração Inicial

```bash
# Torne os scripts executáveis
chmod +x scripts/*.sh

# Execute o setup automático
./scripts/dev.sh setup
```

O script de setup irá:
- Verificar dependências
- Criar ambiente virtual Python
- Instalar dependências do backend
- Instalar dependências do frontend
- Criar arquivo .env base

### 3. Configuração Manual (Alternativa)

Se preferir configurar manualmente:

#### Backend

```bash
cd backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

cd ..
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Ou usando yarn
yarn install

cd ..
```

## 🗄️ Configuração do Banco de Dados

### Usando Docker (Recomendado)

O docker-compose já inclui PostgreSQL configurado:

```bash
# Iniciar apenas o banco de dados
docker-compose up -d db

# Verificar se está funcionando
docker-compose exec db psql -U sombreando -d sombreando_dev -c "SELECT version();"
```

### Instalação Manual do PostgreSQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Configurar usuário e banco
sudo -u postgres psql
```

```sql
CREATE USER sombreando WITH PASSWORD 'password';
CREATE DATABASE sombreando_dev OWNER sombreando;
GRANT ALL PRIVILEGES ON DATABASE sombreando_dev TO sombreando;
\q
```

#### macOS

```bash
brew install postgresql
brew services start postgresql

# Configurar usuário e banco
psql postgres
```

```sql
CREATE USER sombreando WITH PASSWORD 'password';
CREATE DATABASE sombreando_dev OWNER sombreando;
GRANT ALL PRIVILEGES ON DATABASE sombreando_dev TO sombreando;
\q
```

### Redis (Para Cache e Celery)

#### Usando Docker

```bash
docker-compose up -d redis
```

#### Instalação Manual

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis
brew services start redis

# Testar conexão
redis-cli ping
```

## ⚙️ Configuração de Variáveis de Ambiente

### 1. Arquivo .env Principal

Copie e edite o arquivo de configuração:

```bash
cp .env.example .env
nano .env  # ou seu editor preferido
```

### 2. Variáveis Essenciais

```env
# Django
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Banco de Dados
DATABASE_URL=postgresql://sombreando:password@localhost:5432/sombreando_dev
DB_NAME=sombreando_dev
DB_USER=sombreando
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (Desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@sombreando.com

# JWT
JWT_SECRET_KEY=sua-chave-jwt-secreta
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Variáveis de Integração (Opcional)

```env
# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=your_access_token
MERCADO_PAGO_PUBLIC_KEY=your_public_key
MERCADO_PAGO_WEBHOOK_SECRET=your_webhook_secret

# Mapbox
MAPBOX_ACCESS_TOKEN=your_mapbox_token

# Sentry (Produção)
SENTRY_DSN=your_sentry_dsn
```

### 4. Gerar Chave Secreta

```bash
# Gerar SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Gerar JWT_SECRET_KEY
openssl rand -base64 64
```

## 🔧 Instalação do Backend

### 1. Usando Docker (Recomendado)

```bash
# Iniciar todos os serviços
./scripts/dev.sh start

# Ou manualmente
docker-compose up -d
```

### 2. Instalação Manual

```bash
cd backend

# Ativar ambiente virtual
source venv/bin/activate

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar servidor de desenvolvimento
python manage.py runserver 0.0.0.0:8000
```

### 3. Verificar Instalação

```bash
# Testar API
curl http://localhost:8000/api/v1/health/

# Acessar documentação
# http://localhost:8000/api/docs
```

## 📱 Instalação do Frontend

### 1. Instalar Expo CLI

```bash
npm install -g @expo/cli
```

### 2. Configurar Projeto

```bash
cd frontend

# Instalar dependências (se não foi feito no setup)
npm install

# Iniciar servidor de desenvolvimento
npm start
```

### 3. Configurar Dispositivo

#### Expo Go App

1. Instale o Expo Go no seu dispositivo móvel
2. Escaneie o QR code exibido no terminal
3. O app será carregado automaticamente

#### Simulador iOS (macOS)

```bash
# Instalar Xcode Command Line Tools
xcode-select --install

# Iniciar no simulador
npm run ios
```

#### Emulador Android

```bash
# Instalar Android Studio
# Configurar emulador Android

# Iniciar no emulador
npm run android
```

### 4. Configurar API Base URL

Edite `frontend/src/services/apiClient.ts`:

```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://SEU_IP_LOCAL:8000/api/v1'  // Substitua pelo seu IP
  : 'https://sua-api-producao.com/api/v1';
```

Para encontrar seu IP local:

```bash
# Linux/macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"
```

## 🚀 Deploy em Produção

### Railway (Recomendado)

#### 1. Instalar Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Login e Deploy

```bash
# Login
railway login

# Deploy
./scripts/deploy.sh prod
```

#### 3. Configurar Variáveis de Ambiente

No painel do Railway, configure:

```env
DJANGO_SETTINGS_MODULE=sombreando.settings.production
DEBUG=False
ALLOWED_HOSTS=$RAILWAY_PUBLIC_DOMAIN
DATABASE_URL=$DATABASE_URL  # Automaticamente configurado
REDIS_URL=$REDIS_URL        # Automaticamente configurado
SECRET_KEY=sua-chave-secreta-producao
```

### Docker Manual

#### 1. Build da Imagem

```bash
docker build -t sombreando-backend ./backend
```

#### 2. Executar Container

```bash
docker run -d \
  --name sombreando-prod \
  -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=sombreando.settings.production \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  sombreando-backend
```

### VPS/Servidor Dedicado

#### 1. Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install python3.11 python3.11-venv nginx postgresql redis-server

# Configurar firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### 2. Deploy da Aplicação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/sombreando.git
cd sombreando

# Configurar ambiente
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configurar banco de dados
sudo -u postgres createuser sombreando
sudo -u postgres createdb sombreando_prod -O sombreando

# Executar migrações
cd backend
python manage.py migrate
python manage.py collectstatic --noinput

# Configurar Gunicorn
pip install gunicorn
```

#### 3. Configurar Nginx

```nginx
# /etc/nginx/sites-available/sombreando
server {
    listen 80;
    server_name seu-dominio.com;
    
    location /static/ {
        alias /path/to/sombreando/backend/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/sombreando/backend/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/sombreando /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Configurar Systemd

```ini
# /etc/systemd/system/sombreando.service
[Unit]
Description=Sombreando Django App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/sombreando/backend
Environment="PATH=/path/to/sombreando/venv/bin"
ExecStart=/path/to/sombreando/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sombreando.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable sombreando
sudo systemctl start sombreando
```

## 🔍 Solução de Problemas

### Problemas Comuns

#### 1. Erro de Conexão com Banco de Dados

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar conexão
psql -h localhost -U sombreando -d sombreando_dev

# Verificar configurações no .env
cat .env | grep DB_
```

#### 2. Erro de Permissão Docker

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar
newgrp docker
```

#### 3. Porta já em Uso

```bash
# Verificar processos na porta 8000
sudo lsof -i :8000

# Matar processo
sudo kill -9 PID
```

#### 4. Erro de Migração Django

```bash
# Reset das migrações (CUIDADO!)
./scripts/dev.sh db reset

# Ou manualmente
python manage.py migrate --fake-initial
```

#### 5. Erro no Frontend React Native

```bash
# Limpar cache do Metro
npx react-native start --reset-cache

# Limpar cache do npm
npm start -- --clear
```

### Logs e Debugging

#### Backend

```bash
# Logs do Django
./scripts/dev.sh logs backend

# Logs detalhados
docker-compose logs -f backend

# Debug no shell
./scripts/dev.sh backend shell
```

#### Frontend

```bash
# Logs do Expo
npm start

# Debug no navegador
npm run web
```

#### Banco de Dados

```bash
# Logs do PostgreSQL
./scripts/dev.sh logs db

# Shell do banco
./scripts/dev.sh db shell
```

### Performance

#### 1. Otimização do Backend

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Conexões persistentes
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### 2. Otimização do Frontend

```bash
# Build otimizado
expo build:android --release-channel production
expo build:ios --release-channel production
```

### Monitoramento

#### 1. Health Checks

```bash
# Backend
curl http://localhost:8000/api/v1/health/

# Banco de dados
docker-compose exec db pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

#### 2. Métricas

```bash
# Uso de recursos
docker stats

# Logs de sistema
journalctl -u sombreando -f
```

## 📞 Suporte

Se você encontrar problemas não cobertos neste guia:

1. **Verifique os logs** primeiro
2. **Consulte a documentação** da API
3. **Abra uma issue** no GitHub
4. **Entre em contato** via email: suporte@sombreando.com

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. Leia o [Guia de Segurança](SECURITY_GUIDE.md)
2. Explore a [documentação da API](http://localhost:8000/api/docs)
3. Configure as integrações (Mercado Pago, Mapbox)
4. Personalize o frontend conforme suas necessidades

---

**Instalação concluída com sucesso! 🎉**

