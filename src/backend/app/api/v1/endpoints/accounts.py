"""
Account API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.account import AccountType
from app.schemas.user import UserInDB
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountSummary,
    AccountStats
)
from app.services.account_service import AccountService

router = APIRouter()


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    service = AccountService(db)
    account = service.create_account(account_data, current_user.id)
    return account


@router.get("/", response_model=List[AccountSummary])
def get_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in account name, bank name, or description"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts for the current user"""
    service = AccountService(db)
    accounts = service.get_accounts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        account_type=account_type,
        is_active=is_active,
        search=search
    )
    return accounts


@router.get("/count")
def get_accounts_count(
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in account name, bank name, or description"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total count of accounts for the current user"""
    service = AccountService(db)
    count = service.get_accounts_count(
        user_id=current_user.id,
        account_type=account_type,
        is_active=is_active,
        search=search
    )
    return {"count": count}


@router.get("/types")
def get_account_types(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available account types"""
    service = AccountService(db)
    types = service.get_account_types()
    return types


@router.get("/stats", response_model=List[AccountStats])
def get_account_stats(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for all accounts"""
    service = AccountService(db)
    stats = service.get_account_stats(current_user.id)
    return stats


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account by ID"""
    service = AccountService(db)
    account = service.get_account(account_id, current_user.id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update account"""
    service = AccountService(db)
    account = service.update_account(account_id, account_data, current_user.id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    hard_delete: bool = Query(False, description="Permanently delete account and all data"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete account (soft delete by default, hard delete if specified)"""
    service = AccountService(db)
    
    if hard_delete:
        success = service.hard_delete_account(account_id, current_user.id)
        message = "Account permanently deleted"
    else:
        success = service.delete_account(account_id, current_user.id)
        message = "Account deactivated successfully"
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return {"message": message, "success": True}


@router.patch("/{account_id}/activate")
def activate_account(
    account_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate a deactivated account"""
    service = AccountService(db)
    account_data = AccountUpdate(is_active=True)
    account = service.update_account(account_id, account_data, current_user.id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return {"message": "Account activated successfully", "success": True}
