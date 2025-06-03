"""
Monitoring and logging configuration for BudgetManager Pro
"""
import logging
import logging.handlers
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest

from app.core.config import settings


# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table', 'status']
)

USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations'
)

CSV_IMPORTS = Counter(
    'csv_imports_total',
    'Total CSV imports',
    ['status']
)

AUTHENTICATION_ATTEMPTS = Counter(
    'authentication_attempts_total',
    'Total authentication attempts',
    ['status']
)


class MonitoringManager:
    """Centralized monitoring and metrics management"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = structlog.get_logger(__name__)
    
    def setup_logging(self):
        """Configure structured logging"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        logging.basicConfig(
            format=settings.LOG_FORMAT,
            level=getattr(logging, settings.LOG_LEVEL),
            handlers=[
                logging.handlers.RotatingFileHandler(
                    "logs/app.log",
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5
                ),
                logging.StreamHandler()
            ]
        )
        
        # Security logging
        security_logger = logging.getLogger("security")
        security_handler = logging.handlers.RotatingFileHandler(
            "logs/security.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        security_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Log request
        self.logger.info(
            "HTTP request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration
        )
    
    def record_database_operation(self, operation: str, table: str, success: bool):
        """Record database operation metrics"""
        status = "success" if success else "error"
        DATABASE_OPERATIONS.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
        
        self.logger.info(
            "Database operation",
            operation=operation,
            table=table,
            status=status
        )
    
    def record_authentication_attempt(self, email: str, success: bool, ip_address: str):
        """Record authentication attempt for security monitoring"""
        status = "success" if success else "failed"
        AUTHENTICATION_ATTEMPTS.labels(status=status).inc()
        
        # Security logging
        security_logger = logging.getLogger("security")
        security_logger.info(
            f"Authentication {status}",
            extra={
                "email": email,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "authentication"
            }
        )
        
        if not success:
            self.logger.warning(
                "Failed authentication attempt",
                email=email,
                ip_address=ip_address
            )
    
    def record_user_registration(self, email: str, ip_address: str):
        """Record user registration"""
        USER_REGISTRATIONS.inc()
        
        self.logger.info(
            "User registration",
            email=email,
            ip_address=ip_address
        )
    
    def record_csv_import(self, user_id: int, filename: str, records_count: int, success: bool):
        """Record CSV import attempt"""
        status = "success" if success else "error"
        CSV_IMPORTS.labels(status=status).inc()
        
        self.logger.info(
            "CSV import",
            user_id=user_id,
            filename=filename,
            records_count=records_count,
            status=status
        )
    
    def record_error(self, error: Exception, context: Dict[str, Any]):
        """Record application error"""
        self.logger.error(
            "Application error",
            error=str(error),
            error_type=type(error).__name__,
            **context
        )
    
    def record_security_event(self, event_type: str, details: Dict[str, Any]):
        """Record security event"""
        security_logger = logging.getLogger("security")
        security_logger.warning(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                **details
            }
        )
        
        self.logger.warning(
            "Security event",
            event_type=event_type,
            **details
        )
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics"""
        return generate_latest()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get application health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": self._check_database_health(),
            "uptime": self._get_uptime()
        }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from app.core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    def _get_uptime(self) -> float:
        """Get application uptime in seconds"""
        if not hasattr(self, '_start_time'):
            self._start_time = time.time()
        return time.time() - self._start_time


# Global monitoring instance
monitoring = MonitoringManager()


# Monitoring middleware
class MonitoringMiddleware:
    """FastAPI middleware for monitoring"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Increment active connections
            ACTIVE_CONNECTIONS.inc()
            
            try:
                await self.app(scope, receive, send)
            finally:
                # Record metrics
                duration = time.time() - start_time
                method = scope["method"]
                path = scope["path"]
                
                # Decrement active connections
                ACTIVE_CONNECTIONS.dec()
                
                # Note: We can't easily get status code here without modifying send
                # This would require a more complex implementation
        else:
            await self.app(scope, receive, send)


# Health check utilities
class HealthChecker:
    """Application health checking"""
    
    @staticmethod
    def check_all() -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            "database": HealthChecker._check_database(),
            "disk_space": HealthChecker._check_disk_space(),
            "memory": HealthChecker._check_memory()
        }
        
        overall_status = "healthy" if all(
            check["status"] == "healthy" for check in checks.values()
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    
    @staticmethod
    def _check_database() -> Dict[str, Any]:
        """Check database health"""
        try:
            from app.core.database import engine
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                return {"status": "healthy", "message": "Database accessible"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    @staticmethod
    def _check_disk_space() -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            
            if free_percent > 10:
                return {
                    "status": "healthy",
                    "free_space_percent": round(free_percent, 2)
                }
            else:
                return {
                    "status": "warning",
                    "free_space_percent": round(free_percent, 2),
                    "message": "Low disk space"
                }
        except Exception as e:
            return {"status": "unknown", "message": str(e)}
    
    @staticmethod
    def _check_memory() -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent < 80:
                return {
                    "status": "healthy",
                    "memory_usage_percent": memory.percent
                }
            else:
                return {
                    "status": "warning",
                    "memory_usage_percent": memory.percent,
                    "message": "High memory usage"
                }
        except ImportError:
            return {"status": "unknown", "message": "psutil not available"}
        except Exception as e:
            return {"status": "unknown", "message": str(e)}
