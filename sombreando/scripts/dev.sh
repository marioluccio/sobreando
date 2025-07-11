#!/bin/bash

# Sombreando - Development Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sombreando"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  🛠️  Sombreando Development Tools"
    echo "=================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Setup development environment
setup() {
    print_step "Setting up development environment..."
    
    # Create virtual environment for backend
    if [ ! -d "$BACKEND_DIR/venv" ]; then
        print_step "Creating Python virtual environment..."
        cd $BACKEND_DIR
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        cd ..
        print_success "Python environment created!"
    fi
    
    # Install frontend dependencies
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_step "Installing frontend dependencies..."
        cd $FRONTEND_DIR
        npm install
        cd ..
        print_success "Frontend dependencies installed!"
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_step "Creating .env file..."
        cp .env.example .env
        print_success ".env file created! Please update it with your settings."
    fi
    
    print_success "Development environment setup complete!"
}

# Start development servers
start() {
    print_step "Starting development servers..."
    
    # Start with Docker Compose
    docker-compose up -d
    
    print_success "Development servers started!"
    echo -e "${GREEN}🌐 Backend: http://localhost:8000${NC}"
    echo -e "${GREEN}📱 Frontend: Use Expo Go app${NC}"
    echo -e "${GREEN}📊 Admin: http://localhost:8000/admin${NC}"
    echo -e "${GREEN}📖 API Docs: http://localhost:8000/api/docs${NC}"
}

# Stop development servers
stop() {
    print_step "Stopping development servers..."
    docker-compose down
    print_success "Development servers stopped!"
}

# Restart development servers
restart() {
    print_step "Restarting development servers..."
    docker-compose restart
    print_success "Development servers restarted!"
}

# Show status
status() {
    print_step "Checking service status..."
    docker-compose ps
}

# Run backend commands
backend() {
    case "$1" in
        "shell")
            docker-compose exec backend python manage.py shell
            ;;
        "migrate")
            docker-compose exec backend python manage.py migrate
            ;;
        "makemigrations")
            docker-compose exec backend python manage.py makemigrations
            ;;
        "createsuperuser")
            docker-compose exec backend python manage.py createsuperuser
            ;;
        "collectstatic")
            docker-compose exec backend python manage.py collectstatic --noinput
            ;;
        "test")
            docker-compose exec backend python manage.py test
            ;;
        "coverage")
            docker-compose exec backend coverage run --source='.' manage.py test
            docker-compose exec backend coverage report
            ;;
        "lint")
            docker-compose exec backend flake8 .
            docker-compose exec backend black --check .
            docker-compose exec backend isort --check-only .
            ;;
        "format")
            docker-compose exec backend black .
            docker-compose exec backend isort .
            ;;
        *)
            echo "Backend commands:"
            echo "  shell           - Django shell"
            echo "  migrate         - Run migrations"
            echo "  makemigrations  - Create migrations"
            echo "  createsuperuser - Create superuser"
            echo "  collectstatic   - Collect static files"
            echo "  test            - Run tests"
            echo "  coverage        - Run tests with coverage"
            echo "  lint            - Check code style"
            echo "  format          - Format code"
            ;;
    esac
}

# Run frontend commands
frontend() {
    case "$1" in
        "start")
            cd $FRONTEND_DIR && npm start
            ;;
        "android")
            cd $FRONTEND_DIR && npm run android
            ;;
        "ios")
            cd $FRONTEND_DIR && npm run ios
            ;;
        "web")
            cd $FRONTEND_DIR && npm run web
            ;;
        "test")
            cd $FRONTEND_DIR && npm test
            ;;
        "lint")
            cd $FRONTEND_DIR && npm run lint
            ;;
        "type-check")
            cd $FRONTEND_DIR && npm run type-check
            ;;
        *)
            echo "Frontend commands:"
            echo "  start      - Start Expo development server"
            echo "  android    - Start on Android"
            echo "  ios        - Start on iOS"
            echo "  web        - Start on web"
            echo "  test       - Run tests"
            echo "  lint       - Check code style"
            echo "  type-check - Check TypeScript types"
            ;;
    esac
}

# Database operations
db() {
    case "$1" in
        "reset")
            print_step "Resetting database..."
            docker-compose down
            docker volume rm sombreando_postgres_data 2>/dev/null || true
            docker-compose up -d db
            sleep 5
            docker-compose up -d backend
            print_success "Database reset complete!"
            ;;
        "backup")
            print_step "Creating database backup..."
            mkdir -p backups
            BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
            docker-compose exec db pg_dump -U sombreando sombreando_dev > "$BACKUP_FILE"
            print_success "Database backup created: $BACKUP_FILE"
            ;;
        "shell")
            docker-compose exec db psql -U sombreando sombreando_dev
            ;;
        *)
            echo "Database commands:"
            echo "  reset   - Reset database (WARNING: destroys all data)"
            echo "  backup  - Create database backup"
            echo "  shell   - Open database shell"
            ;;
    esac
}

# Show logs
logs() {
    SERVICE=${1:-backend}
    docker-compose logs -f "$SERVICE"
}

# Clean up
clean() {
    print_step "Cleaning up development environment..."
    
    # Stop containers
    docker-compose down
    
    # Remove volumes
    docker volume prune -f
    
    # Remove images
    docker image prune -f
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean Node modules (optional)
    read -p "Remove node_modules? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf $FRONTEND_DIR/node_modules
    fi
    
    print_success "Cleanup complete!"
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND] [ARGS...]"
    echo ""
    echo "Commands:"
    echo "  setup           Setup development environment"
    echo "  start           Start development servers"
    echo "  stop            Stop development servers"
    echo "  restart         Restart development servers"
    echo "  status          Show service status"
    echo "  logs [service]  Show service logs"
    echo "  backend [cmd]   Run backend commands"
    echo "  frontend [cmd]  Run frontend commands"
    echo "  db [cmd]        Database operations"
    echo "  clean           Clean up environment"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup                    # Setup environment"
    echo "  $0 start                    # Start all services"
    echo "  $0 backend migrate          # Run migrations"
    echo "  $0 frontend start           # Start Expo server"
    echo "  $0 logs backend             # Show backend logs"
    echo "  $0 db backup                # Backup database"
}

# Main script
main() {
    print_header
    
    case "${1:-help}" in
        "setup")
            setup
            ;;
        "start")
            start
            ;;
        "stop")
            stop
            ;;
        "restart")
            restart
            ;;
        "status")
            status
            ;;
        "logs")
            logs "$2"
            ;;
        "backend")
            backend "$2"
            ;;
        "frontend")
            frontend "$2"
            ;;
        "db")
            db "$2"
            ;;
        "clean")
            clean
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"

