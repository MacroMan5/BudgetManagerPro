#!/bin/bash

# BudgetManager Pro Deployment Script
# This script handles production deployment tasks

set -e

# Configuration
DEPLOY_USER="deploy"
PROD_HOST="budgetmanager.example.com"
STAGING_HOST="staging.budgetmanager.example.com"
APP_DIR="/opt/budgetmanager"
BACKUP_DIR="/opt/budgetmanager-backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! command_exists git; then
        log_error "Git is not installed"
        exit 1
    fi
    
    log_info "Prerequisites validated successfully"
}

# Create backup
create_backup() {
    local environment=$1
    log_info "Creating backup for $environment environment..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/backup_${environment}_${timestamp}.tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database and configuration
    tar -czf "$backup_file" \
        -C "$APP_DIR-$environment" \
        docker-compose.prod.yml \
        .env \
        data/ 2>/dev/null || true
    
    log_info "Backup created: $backup_file"
    
    # Keep only last 10 backups
    find "$BACKUP_DIR" -name "backup_${environment}_*.tar.gz" -type f | sort -r | tail -n +11 | xargs -r rm -f
}

# Health check
health_check() {
    local host=$1
    local max_attempts=30
    local attempt=1
    
    log_info "Performing health check for $host..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://$host:8000/health" > /dev/null; then
            log_info "Health check passed"
            return 0
        fi
        
        log_warn "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Deploy to environment
deploy() {
    local environment=$1
    local tag=${2:-latest}
    
    log_info "Deploying to $environment environment with tag: $tag"
    
    # Set environment-specific variables
    case $environment in
        "staging")
            local host=$STAGING_HOST
            local app_path="$APP_DIR-staging"
            ;;
        "production")
            local host=$PROD_HOST
            local app_path="$APP_DIR-prod"
            ;;
        *)
            log_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
    
    # Create backup before deployment
    create_backup "$environment"
    
    # Update docker-compose file with new image tags
    log_info "Updating docker-compose configuration..."
    cd "$app_path"
    
    # Update image tags in docker-compose.prod.yml
    sed -i "s|image: ghcr.io/.*/budgetmanager-backend:.*|image: ghcr.io/username/budgetmanager-backend:$tag|g" docker-compose.prod.yml
    sed -i "s|image: ghcr.io/.*/budgetmanager-frontend:.*|image: ghcr.io/username/budgetmanager-frontend:$tag|g" docker-compose.prod.yml
    
    # Pull new images
    log_info "Pulling new Docker images..."
    docker-compose -f docker-compose.prod.yml pull
    
    # Start services
    log_info "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Perform health check
    if ! health_check "localhost"; then
        log_error "Deployment failed - health check failed"
        rollback "$environment"
        exit 1
    fi
    
    log_info "Deployment to $environment completed successfully"
}

# Rollback to previous version
rollback() {
    local environment=$1
    
    log_warn "Rolling back $environment environment..."
    
    case $environment in
        "staging")
            local app_path="$APP_DIR-staging"
            ;;
        "production")
            local app_path="$APP_DIR-prod"
            ;;
        *)
            log_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
    
    cd "$app_path"
    
    # Stop current services
    docker-compose -f docker-compose.prod.yml down
    
    # Restore from backup
    if [ -f docker-compose.prod.yml.backup ]; then
        cp docker-compose.prod.yml.backup docker-compose.prod.yml
        log_info "Configuration restored from backup"
    else
        log_error "No backup configuration found"
        exit 1
    fi
    
    # Start services with previous configuration
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait and check health
    sleep 30
    if health_check "localhost"; then
        log_info "Rollback completed successfully"
    else
        log_error "Rollback failed - manual intervention required"
        exit 1
    fi
}

# Cleanup old images and containers
cleanup() {
    log_info "Cleaning up old Docker images and containers..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this in production)
    # docker volume prune -f
    
    log_info "Cleanup completed"
}

# Main function
main() {
    case "$1" in
        "deploy")
            validate_prerequisites
            deploy "$2" "$3"
            ;;
        "rollback")
            validate_prerequisites
            rollback "$2"
            ;;
        "health-check")
            health_check "$2"
            ;;
        "backup")
            create_backup "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health-check|backup|cleanup} [environment] [tag]"
            echo ""
            echo "Commands:"
            echo "  deploy <environment> [tag]    - Deploy to staging or production"
            echo "  rollback <environment>        - Rollback to previous version"
            echo "  health-check <host>          - Perform health check"
            echo "  backup <environment>         - Create backup"
            echo "  cleanup                      - Clean up old Docker resources"
            echo ""
            echo "Examples:"
            echo "  $0 deploy staging v1.2.0"
            echo "  $0 deploy production v1.2.0"
            echo "  $0 rollback production"
            echo "  $0 health-check localhost"
            echo "  $0 backup production"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
