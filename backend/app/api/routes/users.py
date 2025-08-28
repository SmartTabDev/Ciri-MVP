from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.crud_user import user
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    user_dict = current_user.__dict__.copy()
    user_dict["company_gmail_box_email"] = (
        current_user.company.gmail_box_email if current_user.company else None
    )
    user_dict["company_outlook_box_email"] = (
        current_user.company.outlook_box_email if current_user.company else None
    )
    from app.schemas.user import User as UserSchema
    return UserSchema(**user_dict)

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    if user_in.email and user_in.email != current_user.email:
        if user.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    return user.update(db, db_obj=current_user, obj_in=user_in)
