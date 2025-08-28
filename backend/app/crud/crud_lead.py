from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate

class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def get_by_company(
        self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lead]:
        return (
            db.query(self.model)
            .filter(Lead.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_bulk(
        self, db: Session, *, leads: List[LeadCreate], company_id: int
    ) -> List[Lead]:
        db_leads = [Lead(**lead.dict(), company_id=company_id) for lead in leads]
        db.add_all(db_leads)
        db.commit()
        for lead in db_leads:
            db.refresh(lead)
        return db_leads

    def get_by_email(
        self, db: Session, *, email: str, company_id: int
    ) -> Optional[Lead]:
        return (
            db.query(self.model)
            .filter(Lead.email == email, Lead.company_id == company_id)
            .first()
        )

    def create(
        self, db: Session, *, obj_in: LeadCreate, company_id: int
    ) -> Lead:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, company_id=company_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

lead = CRUDLead(Lead) 