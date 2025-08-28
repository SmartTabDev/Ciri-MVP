from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate

class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name).first()
    
    def get_by_business_email(self, db: Session, *, email: str) -> Optional[Company]:
        return db.query(Company).filter(Company.business_email == email).first()

    def create(self, db: Session, obj_in: CompanyCreate) -> Company:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[CRUD_COMPANY] Starting company creation in CRUD")
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        logger.info(f"[CRUD_COMPANY] Input data: {obj_in_data}")
        
        try:
            logger.info(f"[CRUD_COMPANY] Creating Company model instance")
            db_obj = self.model(
                name=obj_in_data["name"],
                follow_up_cycle=obj_in_data.get("follow_up_cycle"),
                business_email=obj_in_data["business_email"],
                business_category=obj_in_data["business_category"],
                terms_of_service=obj_in_data["terms_of_service"],
                phone_numbers=obj_in_data.get("phone_numbers"),
                logo_url=obj_in_data.get("logo_url"),
                goal=obj_in_data["goal"],
                gmail_box_credentials=obj_in_data.get("gmail_box_credentials"),
                calendar_credentials=obj_in_data.get("calendar_credentials"),
                gmail_box_email=obj_in_data.get("gmail_box_email"),
                gmail_box_app_password=obj_in_data.get("gmail_box_app_password"),
                gmail_box_username=obj_in_data.get("gmail_box_username"),
                outlook_box_credentials=obj_in_data.get("outlook_box_credentials"),
                outlook_box_email=obj_in_data.get("outlook_box_email"),
                outlook_box_username=obj_in_data.get("outlook_box_username"),
                instagram_credentials=obj_in_data.get("instagram_credentials"),
                instagram_username=obj_in_data.get("instagram_username"),
                instagram_account_id=obj_in_data.get("instagram_account_id"),
                instagram_page_id=obj_in_data.get("instagram_page_id"),
                facebook_box_credentials=obj_in_data.get("facebook_box_credentials"),
                facebook_box_page_id=obj_in_data.get("facebook_box_page_id"),
                facebook_box_page_name=obj_in_data.get("facebook_box_page_name"),
            )
            logger.info(f"[CRUD_COMPANY] Company model instance created successfully")
            
            logger.info(f"[CRUD_COMPANY] Adding to database session")
            db.add(db_obj)
            logger.info(f"[CRUD_COMPANY] Committing to database")
            db.commit()
            logger.info(f"[CRUD_COMPANY] Refreshing object")
            db.refresh(db_obj)
            logger.info(f"[CRUD_COMPANY] Company created successfully with ID: {db_obj.id}")
            return db_obj
            
        except Exception as e:
            logger.error(f"[CRUD_COMPANY] Error in create method: {str(e)}")
            logger.error(f"[CRUD_COMPANY] Error type: {type(e).__name__}")
            import traceback
            logger.error(f"[CRUD_COMPANY] Full traceback: {traceback.format_exc()}")
            raise e

company = CRUDCompany(Company)
