from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.company_context import CompanyContext
from app.schemas.company_context import CompanyContextCreate, CompanyContextUpdate
from app.services.flow_analyzer_service import FlowAnalyzerService

class CRUDCompanyContext(CRUDBase[CompanyContext, CompanyContextCreate, CompanyContextUpdate]):
    def __init__(self):
        super().__init__(CompanyContext)
        self.flow_analyzer = FlowAnalyzerService()
    
    def get_by_company_id(self, db: Session, *, company_id: int) -> Optional[CompanyContext]:
        return db.query(CompanyContext).filter(CompanyContext.company_id == company_id).first()
    
    def get_multi_by_company_id(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[CompanyContext]:
        return db.query(CompanyContext).filter(CompanyContext.company_id == company_id).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CompanyContextCreate) -> CompanyContext:
        # If flow_builder_data is provided, analyze it with AI
        if obj_in.flow_builder_data:
            flow_context = self.flow_analyzer.update_flow_context(
                obj_in.company_id, 
                obj_in.flow_builder_data
            )
            if flow_context:
                obj_in.flow_context = flow_context
        
        return super().create(db, obj_in=obj_in)
    
    def update(self, db: Session, *, db_obj: CompanyContext, obj_in: Union[CompanyContextUpdate, Dict[str, Any]]) -> CompanyContext:
        # If flow_builder_data is being updated, re-analyze with AI
        if isinstance(obj_in, dict):
            flow_builder_data = obj_in.get('flow_builder_data')
        else:
            flow_builder_data = obj_in.flow_builder_data
        
        if flow_builder_data:
            flow_context = self.flow_analyzer.update_flow_context(
                db_obj.company_id, 
                flow_builder_data
            )
            if flow_context:
                if isinstance(obj_in, dict):
                    obj_in['flow_context'] = flow_context
                else:
                    obj_in.flow_context = flow_context
        
        return super().update(db, db_obj=db_obj, obj_in=obj_in)
    
    def update_flow_builder_data(self, db: Session, *, company_id: int, flow_builder_data: str) -> Optional[CompanyContext]:
        """
        Update flow_builder_data and automatically generate flow_context using AI.
        Creates company context if it doesn't exist.
        
        Args:
            db: Database session
            company_id: Company ID
            flow_builder_data: JSON string containing flow builder data
            
        Returns:
            Updated CompanyContext object
        """
        company_context = self.get_by_company_id(db, company_id=company_id)
        
        # Create company context if it doesn't exist
        if not company_context:
            from app.schemas.company_context import CompanyContextCreate
            company_context_create = CompanyContextCreate(company_id=company_id)
            company_context = self.create(db, obj_in=company_context_create)
        
        # Generate AI analysis
        flow_context = self.flow_analyzer.update_flow_context(company_id, flow_builder_data)
        
        # Update the record
        update_data = {
            'flow_builder_data': flow_builder_data,
            'flow_context': flow_context
        }
        
        return self.update(db, db_obj=company_context, obj_in=update_data)

    def update_text_context(self, db: Session, *, company_id: int, text_context: str) -> CompanyContext:
        """
        Update text_context for a company.
        Creates company context if it doesn't exist.
        
        Args:
            db: Database session
            company_id: Company ID
            text_context: Text context string
            
        Returns:
            Updated CompanyContext object
        """
        company_context = self.get_by_company_id(db, company_id=company_id)
        
        # Create company context if it doesn't exist
        if not company_context:
            from app.schemas.company_context import CompanyContextCreate
            company_context_create = CompanyContextCreate(
                company_id=company_id,
                text_context=text_context
            )
            company_context = self.create(db, obj_in=company_context_create)
        else:
            # Update existing company context
            update_data = {
                'text_context': text_context
            }
            company_context = self.update(db, db_obj=company_context, obj_in=update_data)
        
        return company_context

company_context = CRUDCompanyContext() 