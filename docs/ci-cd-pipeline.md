# BudgetManager Pro CI/CD Pipeline Configuration

This document explains the CI/CD pipeline configuration for BudgetManager Pro, including workflows, deployment strategies, and security measures.

## 🚀 Pipeline Overview

Our CI/CD pipeline consists of four main workflows:

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
- **Triggers**: Push to `main`/`develop`, Pull Requests
- **Jobs**:
  - Backend Tests (Python/FastAPI)
  - Frontend Tests (React/TypeScript)
  - Security Scanning
  - Docker Build & Test
  - Integration Tests

### 2. **Deployment Pipeline** (`.github/workflows/deploy.yml`)
- **Triggers**: Push to `main`, Tags, Releases
- **Jobs**:
  - Build & Push Docker Images
  - Deploy to Staging (main branch)
  - Deploy to Production (tags only)
  - Rollback capability

### 3. **Code Quality** (`.github/workflows/code-quality.yml`)
- **Triggers**: Push, Pull Requests, Weekly schedule
- **Jobs**:
  - Code Quality Analysis
  - SonarQube Integration
  - License Compliance
  - Documentation Checks
  - Performance Baseline

### 4. **Dependency Management** (`.github/workflows/dependency-updates.yml`)
- **Triggers**: Weekly schedule, Manual dispatch
- **Jobs**:
  - Update Python Dependencies
  - Update Node.js Dependencies
  - Security Audits
  - Automated PR Creation

## 🔧 Setup Instructions

### 1. Repository Secrets

Configure the following secrets in your GitHub repository settings:

```bash
# Production Deployment
PROD_HOST=your-production-server.com
PROD_USER=deploy
PROD_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...

# Staging Deployment
STAGING_HOST=staging.budgetmanager.example.com
STAGING_USER=deploy
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...

# Container Registry
GITHUB_TOKEN=ghp_... (automatically provided)

# Monitoring & Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SONAR_TOKEN=your-sonarqube-token
```

### 2. Environment Configuration

#### Staging Environment
```bash
# Create .env file on staging server
cp .env.prod.example .env
# Edit with staging-specific values
```

#### Production Environment
```bash
# Create .env file on production server
cp .env.prod.example .env
# Edit with production values
```

### 3. Server Setup

#### Prerequisites on Deployment Servers
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment directories
sudo mkdir -p /opt/budgetmanager-staging
sudo mkdir -p /opt/budgetmanager-prod
sudo chown -R deploy:deploy /opt/budgetmanager-*
```

#### SSH Key Setup
```bash
# On deployment servers, add the SSH public key to authorized_keys
mkdir -p ~/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2E... deploy-key" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

## 🌊 Workflow Details

### Branch Strategy
- **`develop`**: Development branch, triggers staging deployment
- **`main`**: Production-ready code, triggers staging deployment
- **`tags/v*`**: Version tags, triggers production deployment
- **Feature branches**: Trigger CI tests only

### Quality Gates

#### Backend Quality Requirements
- ✅ Python code formatted with Black
- ✅ Imports sorted with isort
- ✅ Linting passes (flake8)
- ✅ Type checking passes (mypy)
- ✅ Test coverage ≥ 80%
- ✅ Security scan passes (bandit, safety)

#### Frontend Quality Requirements
- ✅ Code formatted with Prettier
- ✅ Linting passes (ESLint)
- ✅ Type checking passes (TypeScript)
- ✅ Tests pass (Jest/Vitest)
- ✅ Build succeeds

### Security Measures

#### Automated Security Scanning
- **Trivy**: Vulnerability scanning for containers and filesystems
- **Bandit**: Python security analysis
- **Safety**: Python dependency vulnerability checking
- **npm audit**: Node.js dependency security audit
- **License compliance**: Automated license checking

#### Security Best Practices
- Container images built from scratch for production
- Secrets managed through GitHub Secrets
- SSH key-based authentication for deployments
- SSL/TLS certificates automated with Let's Encrypt
- Security headers enforced via Traefik

## 🚀 Deployment Process

### Staging Deployment
1. **Trigger**: Push to `main` or `develop`
2. **Process**:
   - Build and test Docker images
   - Push to container registry
   - Deploy to staging environment
   - Run smoke tests
   - Notify team of deployment status

### Production Deployment
1. **Trigger**: Git tag creation (`v1.0.0`, `v1.1.0`, etc.)
2. **Process**:
   - Require staging deployment success
   - Build production-optimized images
   - Create backup of current production state
   - Deploy with zero-downtime strategy
   - Run comprehensive health checks
   - Rollback automatically if health checks fail
   - Notify team of deployment status

### Rollback Process
1. **Manual Trigger**: Workflow dispatch or emergency procedure
2. **Process**:
   - Stop current services
   - Restore previous configuration
   - Restart services with previous version
   - Verify system health
   - Notify team of rollback

## 📊 Monitoring & Observability

### Metrics Collection
- **Prometheus**: Application and infrastructure metrics
- **Grafana**: Metrics visualization and alerting
- **Health Checks**: Automated endpoint monitoring
- **Log Aggregation**: Structured logging with JSON format

### Performance Monitoring
- **Load Testing**: Automated performance baseline tests
- **Database Performance**: Query performance monitoring
- **API Response Times**: Endpoint performance tracking
- **Resource Usage**: CPU, memory, and disk monitoring

## 🔄 Dependency Management

### Automated Updates
- **Schedule**: Every Monday at 9 AM UTC
- **Process**:
  - Check for dependency updates
  - Run tests with new dependencies
  - Create pull request if tests pass
  - Include security audit results

### Security Audits
- **Frequency**: Weekly + on-demand
- **Tools**: Safety, pip-audit, npm audit, Bandit
- **Actions**: Create GitHub issues for critical vulnerabilities

## 📋 Manual Procedures

### Emergency Deployment
```bash
# Quick production deployment (use with caution)
git tag -a v1.0.1 -m "Emergency fix for critical issue"
git push origin v1.0.1
```

### Manual Rollback
```bash
# Trigger rollback workflow
gh workflow run deploy.yml --ref main -f rollback=true
```

### Database Backup
```bash
# Run backup service
docker-compose --profile backup run backup
```

### Log Access
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View Traefik logs
docker-compose logs -f traefik
```

## 🚨 Troubleshooting

### Common Issues

#### Deployment Failures
1. Check GitHub Actions logs
2. Verify server connectivity
3. Check disk space on deployment servers
4. Verify environment variables are set

#### Health Check Failures
1. Check application logs
2. Verify database connectivity
3. Check Redis connectivity
4. Verify external service dependencies

#### Performance Issues
1. Check Grafana dashboards
2. Review application metrics
3. Check database query performance
4. Monitor resource usage

### Emergency Contacts
- **DevOps Lead**: devops@budgetmanager.example.com
- **Security Team**: security@budgetmanager.example.com
- **On-call Engineer**: +1-XXX-XXX-XXXX

---

## 📚 Additional Resources

- [Docker Compose Production Guide](../docs/deployment/docker-production.md)
- [Security Best Practices](../docs/security/security-guidelines.md)
- [Monitoring Setup Guide](../docs/monitoring/monitoring-setup.md)
- [Troubleshooting Guide](../docs/troubleshooting/common-issues.md)
