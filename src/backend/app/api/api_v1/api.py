"""
API router for version 1 endpoints
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth
from app.api.v1.endpoints import accounts

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include account routes
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# TODO: Add other endpoint routers as they are created
# api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
# api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
# api_router.include_router(csv_import.router, prefix="/csv", tags=["csv-import"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
