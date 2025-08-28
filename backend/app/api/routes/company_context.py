import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import crud, schemas
from app.api import deps

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

class FlowBuilderDataRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]

class TextContextRequest(BaseModel):
    text_context: str

@router.get("/", response_model=List[schemas.CompanyContext])
def read_company_contexts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve company contexts.
    """
    company_contexts = crud.company_context.get_multi(db, skip=skip, limit=limit)
    return company_contexts

@router.post("/", response_model=schemas.CompanyContext, status_code=status.HTTP_201_CREATED)
def create_company_context(
    *,
    db: Session = Depends(deps.get_db),
    company_context_in: schemas.CompanyContextCreate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new company context.
    """
    # Check if company exists
    company = crud.company.get(db, id=company_context_in.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    
    # Check if company context already exists for this company
    existing_context = crud.company_context.get_by_company_id(db, company_id=company_context_in.company_id)
    if existing_context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company context already exists for this company",
        )
    
    company_context = crud.company_context.create(db=db, obj_in=company_context_in)
    return company_context

@router.get("/{company_context_id}", response_model=schemas.CompanyContext)
def read_company_context(
    *,
    db: Session = Depends(deps.get_db),
    company_context_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get company context by ID.
    """
    company_context = crud.company_context.get(db=db, id=company_context_id)
    if not company_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company context not found",
        )
    return company_context

@router.get("/company/{company_id}", response_model=schemas.CompanyContext)
def read_company_context_by_company_id(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get company context by company ID.
    """
    company_context = crud.company_context.get_by_company_id(db=db, company_id=company_id)
    if not company_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company context not found for this company",
        )
    return company_context

@router.put("/{company_context_id}", response_model=schemas.CompanyContext)
def update_company_context(
    *,
    db: Session = Depends(deps.get_db),
    company_context_id: int,
    company_context_in: schemas.CompanyContextUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update company context.
    """
    company_context = crud.company_context.get(db=db, id=company_context_id)
    if not company_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company context not found",
        )
    
    # If company_id is being updated, check if the new company exists
    if company_context_in.company_id is not None:
        company = crud.company.get(db, id=company_context_in.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
    
    company_context = crud.company_context.update(db=db, db_obj=company_context, obj_in=company_context_in)
    return company_context

@router.put("/company/{company_id}/text-context", response_model=schemas.CompanyContext)
def update_text_context(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    text_context_data: TextContextRequest,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update text context for a company.
    Creates company context if it doesn't exist.
    """
    logger.info(f"API: update_text_context called for company_id: {company_id}")
    logger.debug(f"API: Received text_context length: {len(text_context_data.text_context)} characters")
    
    company_context = crud.company_context.update_text_context(
        db=db, 
        company_id=company_id, 
        text_context=text_context_data.text_context
    )
    
    logger.info(f"API: Successfully updated company context id: {company_context.id}")
    logger.debug(f"API: Final result - text_context: {bool(company_context.text_context)}")
    return company_context

@router.put("/company/{company_id}/flow-builder-data", response_model=schemas.CompanyContext)
def update_flow_builder_data(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    flow_data: FlowBuilderDataRequest,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update flow builder data and automatically generate flow context using AI.
    Creates company context if it doesn't exist.
    """
    logger.info(f"API: update_flow_builder_data called for company_id: {company_id}")
    logger.info(f"API: Received {len(flow_data.nodes)} nodes and {len(flow_data.edges)} edges")
    logger.debug(f"API: Flow data: {flow_data.dict()}")
    
    import json
    flow_builder_data_json = json.dumps(flow_data.dict())
    logger.debug(f"API: Converted to JSON string, length: {len(flow_builder_data_json)} characters")
    
    company_context = crud.company_context.update_flow_builder_data(
        db=db, 
        company_id=company_id, 
        flow_builder_data=flow_builder_data_json
    )
    
    logger.info(f"API: Successfully updated company context id: {company_context.id}")
    logger.debug(f"API: Final result - flow_builder_data: {bool(company_context.flow_builder_data)}, flow_context: {bool(company_context.flow_context)}")
    
    return company_context

@router.delete("/{company_context_id}", response_model=schemas.CompanyContext)
def delete_company_context(
    *,
    db: Session = Depends(deps.get_db),
    company_context_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete company context.
    """
    company_context = crud.company_context.get(db=db, id=company_context_id)
    if not company_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company context not found",
        )
    company_context = crud.company_context.remove(db=db, id=company_context_id)
    return company_context 