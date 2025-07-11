#!/bin/bash

# Sombreando - Deploy Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sombreando"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="docker-compose.prod.yml"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  🚀 Sombreando Deploy Script"
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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Railway CLI is installed
check_railway() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Installing..."
        npm install -g @railway/cli
    fi
    
    print_success "Railway CLI is available"
}

# Build and start development environment
dev_deploy() {
    print_step "Starting development environment..."
    
    # Stop existing containers
    docker-compose down
    
    # Build and start containers
    docker-compose up --build -d
    
    # Wait for services to be ready
    print_step "Waiting for services to be ready..."
    sleep 30
    
    # Check if backend is healthy
    if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
        print_success "Development environment is running!"
        echo -e "${GREEN}🌐 Backend: http://localhost:8000${NC}"
        echo -e "${GREEN}📊 Admin: http://localhost:8000/admin${NC}"
        echo -e "${GREEN}📖 API Docs: http://localhost:8000/api/docs${NC}"
    else
        print_error "Backend health check failed"
        docker-compose logs backend
        exit 1
    fi
}

# Deploy to production (Railway)
prod_deploy() {
    print_step "Deploying to Railway..."
    
    # Check if logged in to Railway
    if ! railway whoami > /dev/null 2>&1; then
        print_step "Please login to Railway..."
        railway login
    fi
    
    # Deploy to Railway
    railway up
    
    print_success "Deployed to Railway!"
    
    # Get the deployment URL
    RAILWAY_URL=$(railway domain)
    if [ ! -z "$RAILWAY_URL" ]; then
        echo -e "${GREEN}🌐 Production URL: https://$RAILWAY_URL${NC}"
    fi
}

# Run tests
run_tests() {
    print_step "Running tests..."
    
    # Backend tests
    docker-compose exec backend python manage.py test
    
    # Frontend tests (if container exists)
    if docker-compose ps frontend > /dev/null 2>&1; then
        docker-compose exec frontend npm test
    fi
    
    print_success "All tests passed!"
}

# Database operations
db_migrate() {
    print_step "Running database migrations..."
    docker-compose exec backend python manage.py migrate
    print_success "Database migrations completed!"
}

db_backup() {
    print_step "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec db pg_dump -U sombreando sombreando_dev > "backups/$BACKUP_FILE"
    print_success "Database backup created: backups/$BACKUP_FILE"
}

db_restore() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    print_step "Restoring database from $1..."
    docker-compose exec -T db psql -U sombreando sombreando_dev < "$1"
    print_success "Database restored successfully!"
}

# Cleanup
cleanup() {
    print_step "Cleaning up..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Cleanup completed!"
}

# Show logs
show_logs() {
    SERVICE=${1:-backend}
    print_step "Showing logs for $SERVICE..."
    docker-compose logs -f "$SERVICE"
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment"
    echo "  prod        Deploy to production (Railway)"
    echo "  test        Run tests"
    echo "  migrate     Run database migrations"
    echo "  backup      Create database backup"
    echo "  restore     Restore database from backup"
    echo "  logs        Show service logs"
    echo "  cleanup     Clean up Docker resources"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Start development"
    echo "  $0 prod                   # Deploy to production"
    echo "  $0 logs backend           # Show backend logs"
    echo "  $0 restore backup.sql     # Restore from backup"
}

# Main script
main() {
    print_header
    
    case "${1:-help}" in
        "dev")
            check_docker
            dev_deploy
            ;;
        "prod")
            check_docker
            check_railway
            prod_deploy
            ;;
        "test")
            check_docker
            run_tests
            ;;
        "migrate")
            check_docker
            db_migrate
            ;;
        "backup")
            check_docker
            mkdir -p backups
            db_backup
            ;;
        "restore")
            check_docker
            db_restore "$2"
            ;;
        "logs")
            check_docker
            show_logs "$2"
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"

