# Sombreando 🌊

**Um microSaaS moderno e seguro construído com Django REST Framework e React Native Expo**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![React Native](https://img.shields.io/badge/react--native-0.72+-blue.svg)](https://reactnative.dev/)
[![TypeScript](https://img.shields.io/badge/typescript-5.1+-blue.svg)](https://www.typescriptlang.org/)

## 📋 Visão Geral

Sombreando é uma plataforma microSaaS completa que combina um backend robusto em Django REST Framework com um frontend móvel em React Native Expo. O projeto foi desenvolvido com foco em **segurança**, **escalabilidade** e **facilidade de manutenção**.

### 🎯 Características Principais

- **Autenticação Segura**: JWT + 2FA via email
- **Backend Robusto**: Django REST Framework com PostgreSQL
- **Frontend Moderno**: React Native Expo com TypeScript
- **Pagamentos**: Integração com Mercado Pago
- **Mapas**: Integração com Mapbox
- **Deploy Simplificado**: Railway com Docker
- **Documentação Completa**: API docs, guias de instalação e segurança
- **Testes Automáticos**: Cobertura completa backend e frontend

## 🏗️ Arquitetura

```
sombreando/
├── backend/                 # Django REST API
│   ├── sombreando/         # Configurações principais
│   │   ├── settings/       # Configurações por ambiente
│   │   └── apps/          # Apps Django
│   │       ├── authentication/  # Sistema de auth
│   │       ├── payments/        # Mercado Pago
│   │       ├── maps/           # Mapbox
│   │       └── core/           # Funcionalidades core
│   └── requirements.txt    # Dependências Python
├── frontend/               # React Native Expo
│   ├── src/               # Código fonte
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── screens/       # Telas da aplicação
│   │   ├── services/      # Serviços de API
│   │   ├── store/         # Redux store
│   │   └── types/         # Tipos TypeScript
│   └── package.json       # Dependências Node.js
├── docker/                # Configurações Docker
├── scripts/               # Scripts de automação
└── docs/                  # Documentação
```

## 🚀 Início Rápido

### Pré-requisitos

- **Docker** e **Docker Compose**
- **Node.js** 18+ (para desenvolvimento frontend)
- **Python** 3.11+ (para desenvolvimento backend)
- **Git**

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/sombreando.git
cd sombreando
```

### 2. Configure o Ambiente

```bash
# Copie o arquivo de configuração
cp .env.example .env

# Edite as variáveis de ambiente
nano .env
```

### 3. Inicie o Ambiente de Desenvolvimento

```bash
# Torne os scripts executáveis
chmod +x scripts/*.sh

# Configure o ambiente
./scripts/dev.sh setup

# Inicie os serviços
./scripts/dev.sh start
```

### 4. Acesse a Aplicação

- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/api/docs
- **Admin Django**: http://localhost:8000/admin
- **Frontend Mobile**: Use o Expo Go app

## 🛠️ Desenvolvimento

### Backend (Django)

```bash
# Executar migrações
./scripts/dev.sh backend migrate

# Criar superusuário
./scripts/dev.sh backend createsuperuser

# Executar testes
./scripts/dev.sh backend test

# Shell Django
./scripts/dev.sh backend shell
```

### Frontend (React Native)

```bash
# Iniciar servidor Expo
./scripts/dev.sh frontend start

# Executar no Android
./scripts/dev.sh frontend android

# Executar no iOS
./scripts/dev.sh frontend ios

# Executar testes
./scripts/dev.sh frontend test
```

### Banco de Dados

```bash
# Backup do banco
./scripts/dev.sh db backup

# Reset do banco (CUIDADO!)
./scripts/dev.sh db reset

# Shell do banco
./scripts/dev.sh db shell
```

## 🔐 Segurança

O Sombreando implementa múltiplas camadas de segurança:

- **Autenticação JWT** com refresh tokens
- **2FA via email** para contas sensíveis
- **Rate limiting** em endpoints críticos
- **Validação rigorosa** de entrada
- **Headers de segurança** configurados
- **HTTPS** obrigatório em produção
- **Logs de auditoria** para ações importantes

Para mais detalhes, consulte o [Guia de Segurança](SECURITY_GUIDE.md).

## 💳 Integrações

### Mercado Pago

Configure as variáveis de ambiente:

```env
MERCADO_PAGO_ACCESS_TOKEN=your_access_token
MERCADO_PAGO_PUBLIC_KEY=your_public_key
MERCADO_PAGO_WEBHOOK_SECRET=your_webhook_secret
```

### Mapbox

Configure a variável de ambiente:

```env
MAPBOX_ACCESS_TOKEN=your_mapbox_token
```

## 🚀 Deploy

### Railway (Recomendado)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
./scripts/deploy.sh prod
```

### Docker Manual

```bash
# Build da imagem
docker build -t sombreando-backend ./backend

# Executar container
docker run -p 8000:8000 sombreando-backend
```

## 📊 Monitoramento

O projeto inclui:

- **Health checks** para todos os serviços
- **Logs estruturados** com diferentes níveis
- **Métricas de performance** via Django
- **Alertas de erro** via Sentry (produção)

## 🧪 Testes

### Backend

```bash
# Executar todos os testes
./scripts/dev.sh backend test

# Testes com cobertura
./scripts/dev.sh backend coverage

# Linting
./scripts/dev.sh backend lint
```

### Frontend

```bash
# Executar testes
./scripts/dev.sh frontend test

# Verificação de tipos
./scripts/dev.sh frontend type-check

# Linting
./scripts/dev.sh frontend lint
```

## 📚 Documentação

- [Guia de Instalação](INSTALLATION.md) - Setup detalhado
- [Guia de Segurança](SECURITY_GUIDE.md) - Práticas de segurança
- [Estrutura do Projeto](PROJECT_STRUCTURE.md) - Organização do código
- [API Documentation](http://localhost:8000/api/docs) - Documentação interativa

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/sombreando/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/sombreando/discussions)
- **Email**: suporte@sombreando.com

## 🙏 Agradecimentos

- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Native](https://reactnative.dev/)
- [Expo](https://expo.dev/)
- [Railway](https://railway.app/)
- [Mercado Pago](https://www.mercadopago.com.br/)
- [Mapbox](https://www.mapbox.com/)

---

**Desenvolvido com ❤️ pela equipe Sombreando**

