from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.models.user import User
from app.schemas.lead import Lead, LeadCreate, LeadUpdate, LeadBulkCreate
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[Lead])
def read_leads(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve leads for the current user's company.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with any company")
    
    leads = crud.lead.get_by_company(
        db=db, company_id=current_user.company_id, skip=skip, limit=limit
    )
    return leads

@router.post("/", response_model=Lead)
def create_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_in: LeadCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new lead.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with any company")
    
    # Check if lead with same email already exists
    lead = crud.lead.get_by_email(
        db=db, email=lead_in.email, company_id=current_user.company_id
    )
    if lead:
        raise HTTPException(
            status_code=400,
            detail="A lead with this email already exists for this company",
        )
    
    lead = crud.lead.create(db=db, obj_in=lead_in, company_id=current_user.company_id)
    return lead

@router.post("/bulk", response_model=List[Lead])
def create_leads_bulk(
    *,
    db: Session = Depends(deps.get_db),
    leads_in: LeadBulkCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create multiple leads in bulk.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with any company")
    
    leads = crud.lead.create_bulk(db=db, leads=leads_in.leads, company_id=current_user.company_id)
    return leads

@router.put("/{lead_id}", response_model=Lead)
def update_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    lead_in: LeadUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a lead.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with any company")
    
    lead = crud.lead.get(db=db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    lead = crud.lead.update(db=db, db_obj=lead, obj_in=lead_in)
    return lead

@router.delete("/{lead_id}", response_model=Lead)
def delete_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a lead.
    """
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with any company")
    
    lead = crud.lead.get(db=db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    lead = crud.lead.remove(db=db, id=lead_id)
    return lead 