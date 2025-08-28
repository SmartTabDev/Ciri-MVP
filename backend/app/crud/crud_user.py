from typing import Any, Optional, Union, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, generate_verification_code, get_verification_code_expiry
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.datetime_utils import is_expired

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    # def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
    #     return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # Generate verification code
        verification_code = generate_verification_code(settings.VERIFICATION_CODE_LENGTH)
        verification_code_expires_at = get_verification_code_expiry()
        db_obj = User(
            email=obj_in.email,
            # username=obj_in.username,  # Removed
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
            is_verified=obj_in.is_verified if obj_in.is_verified is not None else False,
            verification_code=verification_code,
            verification_code_expires_at=verification_code_expires_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user_obj = self.get_by_email(db, email=email)
        if not user_obj:
            return None
        if not verify_password(password, user_obj.hashed_password):
            return None
        return user_obj

    def verify_email_with_code(self, db: Session, *, email: str, code: str) -> Optional[User]:
        user_obj = self.get_by_email(db, email=email)
        if not user_obj:
            return None
            
        # Check if user is already verified
        if user_obj.is_verified:
            return user_obj
            
        # Check if code is valid and not expired
        if (user_obj.verification_code != code or 
            not user_obj.verification_code_expires_at or 
            is_expired(user_obj.verification_code_expires_at)):
            return None
            
        # Mark user as verified and clear verification code
        user_obj.is_verified = True
        user_obj.verification_code = None
        user_obj.verification_code_expires_at = None
        
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj
    
    def generate_new_verification_code(self, db: Session, *, email: str) -> Optional[User]:
        user_obj = self.get_by_email(db, email=email)
        if not user_obj:
            return None
            
        # Check if user is already verified
        if user_obj.is_verified:
            return user_obj
            
        # Generate new verification code
        verification_code = generate_verification_code(settings.VERIFICATION_CODE_LENGTH)
        verification_code_expires_at = get_verification_code_expiry()
        
        user_obj.verification_code = verification_code
        user_obj.verification_code_expires_at = verification_code_expires_at
        
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj

user = CRUDUser(User)

# Import settings at the end to avoid circular imports
from app.core.config import settings
