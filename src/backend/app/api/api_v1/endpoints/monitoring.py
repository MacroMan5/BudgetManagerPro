"""
Monitoring and health check endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.core.monitoring import monitoring, HealthChecker
from app.core.deps import get_current_superuser
from app.schemas.user import UserInDB

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return monitoring.get_health_status()


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all subsystems"""
    return HealthChecker.check_all()


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics(
    current_user: UserInDB = Depends(get_current_superuser)
):
    """
    Get Prometheus metrics (admin only)
    """
    return monitoring.get_metrics()


@router.get("/status")
async def get_application_status():
    """Get application status information"""
    return {
        "status": "running",
        "environment": "development",  # Should come from settings
        "version": "0.1.0",  # Should come from settings
        "features": {
            "authentication": True,
            "csv_import": True,
            "transaction_management": True,
            "reporting": True
        }
    }


@router.get("/logs/recent")
async def get_recent_logs(
    lines: int = 100,
    current_user: UserInDB = Depends(get_current_superuser)
):
    """
    Get recent log entries (admin only)
    """
    try:
        with open("logs/app.log", "r") as f:
            log_lines = f.readlines()
            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
        return {
            "total_lines": len(log_lines),
            "returned_lines": len(recent_lines),
            "logs": [line.strip() for line in recent_lines]
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading logs: {str(e)}"
        )
