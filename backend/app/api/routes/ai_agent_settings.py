from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.ai_agent_settings import AIAgentSettingsCreate, AIAgentSettingsUpdate, AIAgentSettingsInDB
from app.crud.crud_ai_agent_settings import ai_agent_settings
from app.crud.crud_company import company

router = APIRouter()

@router.post("", response_model=AIAgentSettingsInDB)
def create_ai_agent_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    settings_in: AIAgentSettingsCreate,
) -> Any:
    """
    Create AI agent settings for a company.
    Only company users can create settings for their company.
    Company ID is taken from the user's context.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    # Verify company exists
    db_company = company.get(db=db, id=current_user.company_id)
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    
    # Check if settings already exist
    existing_settings = ai_agent_settings.get_by_company_id(db=db, company_id=current_user.company_id)
    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI agent settings already exist for this company",
        )
    
    # Create settings using company_id from user context
    settings = ai_agent_settings.create_for_company(
        db=db,
        company_id=current_user.company_id,
        obj_in=settings_in
    )
    return settings

@router.get("", response_model=AIAgentSettingsInDB)
def get_ai_agent_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get AI agent settings for the current user's company.
    Company ID is taken from the user's context.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    settings = ai_agent_settings.get_by_company_id(db=db, company_id=current_user.company_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent settings not found",
        )
    
    return settings

@router.put("", response_model=AIAgentSettingsInDB)
def update_ai_agent_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    settings_in: AIAgentSettingsUpdate,
) -> Any:
    """
    Update AI agent settings for the current user's company.
    Company ID is taken from the user's context.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    settings = ai_agent_settings.update_for_company(
        db=db,
        company_id=current_user.company_id,
        obj_in=settings_in
    )
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent settings not found",
        )
    
    return settings 