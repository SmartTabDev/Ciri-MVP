from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash
from app.core.email import send_verification_code, send_password_reset_email
from app.crud.crud_user import user
from app.schemas.token import Token, RefreshRequest
from app.schemas.user import User, UserCreate
from app.schemas.email import (
    EmailVerificationRequest, EmailVerificationResponse, VerifyCodeRequest,
    ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
)
import secrets
import asyncio
import requests
import random
import string
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from app.services.outlook_auth_service import outlook_auth_service
from app.services.facebook_auth_service import facebook_auth_service
from app.services.instagram_auth_service import instagram_auth_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Register a new user and send verification code via email.
    """
    user_by_email = user.get_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    # user_by_username = user.get_by_username(db, username=user_in.username)
    # if user_by_username:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="A user with this username already exists",
    #     )
    
    # Create the user (verification code is generated in the create method)
    new_user = user.create(db, obj_in=user_in)
    
    # Send verification code in the background
    background_tasks.add_task(
        send_verification_code,
        email_to=new_user.email,
        code=new_user.verification_code,
        expires_in_minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES
    )
    
    return new_user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user_obj = user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Check if email is verified
    if not user_obj.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access your account.",
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=7)
    return {
        "access_token": create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(
            user_obj.id, expires_delta=refresh_token_expires
        ),
    }

@router.post("/refresh", response_model=Token)
def refresh_access_token(request: RefreshRequest) -> Any:
    """
    Exchange a refresh token for a new access token.
    """
    from fastapi import HTTPException, status
    from app.core.config import settings
    from datetime import timedelta
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=7)
    return {
        "access_token": create_access_token(user_id, expires_delta=access_token_expires),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(user_id, expires_delta=refresh_token_expires),
    }

@router.post("/verify-code", response_model=EmailVerificationResponse)
def verify_email_code(
    *,
    db: Session = Depends(get_db),
    verification_data: VerifyCodeRequest,
) -> Any:
    """
    Verify a user's email address using the verification code sent to their email.
    """
    user_obj = user.verify_email_with_code(
        db, 
        email=verification_data.email, 
        code=verification_data.code
    )
    
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification-code", response_model=EmailVerificationResponse)
async def resend_verification_code(
    *,
    db: Session = Depends(get_db),
    email_in: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Resend the verification code to the user's email.
    """
    user_obj = user.get_by_email(db, email=email_in.email)
    if not user_obj:
        # Return success even if user doesn't exist to prevent email enumeration
        return {"message": "If your email is registered, a verification code has been sent"}
    
    if user_obj.is_verified:
        return {"message": "Your email is already verified"}
    
    # Generate new verification code
    user_obj = user.generate_new_verification_code(db, email=email_in.email)
    
    # Send verification code in the background
    background_tasks.add_task(
        send_verification_code,
        email_to=user_obj.email,
        code=user_obj.verification_code,
        expires_in_minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES
    )
    
    return {"message": "If your email is registered, a verification code has been sent"}

import asyncio

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user_obj = user.get_by_email(db, email=request.email)
    if not user_obj:
        # Don't reveal if user exists
        return {"message": "If your email is registered, you will receive a password reset email."}
    # Generate a reset token (could be JWT or random string)
    reset_token = create_access_token(user_obj.id, expires_delta=timedelta(hours=1))
    # Send the password reset email
    await send_password_reset_email(user_obj.email, reset_token)
    return {"message": "If your email is registered, you will receive a password reset email."}

@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(request.token)
        user_id = payload.get("sub")
        if not user_id:
            raise Exception()
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User not found")
    user_obj.hashed_password = get_password_hash(request.new_password)
    db.add(user_obj)
    db.commit()
    return {"message": "Password has been reset successfully."}

@router.get("/google/login")
def google_login():
    # Redirect user to Google OAuth consent screen
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return RedirectResponse(url)

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_res = requests.post(token_url, data=data)
    if not token_res.ok:
        return JSONResponse(status_code=400, content={"detail": "Failed to get tokens from Google"})
    tokens = token_res.json()
    # Get user info
    userinfo_res = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    if not userinfo_res.ok:
        return JSONResponse(status_code=400, content={"detail": "Failed to get user info from Google"})
    userinfo = userinfo_res.json()
    # Find or create user in DB
    user_obj = user.get_by_email(db, email=userinfo["email"])
    if not user_obj:
        from app.schemas.user import UserCreate
        user_in = UserCreate(email=userinfo["email"], password="google-oauth", is_verified=True)
        user_obj = user.create(db, obj_in=user_in)
    # Issue JWT tokens
    access_token = create_access_token(user_obj.id)
    refresh_token = create_refresh_token(user_obj.id)
    redirect_url = f"{settings.FRONTEND_URL}/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)

@router.get("/calendar/login")
def calendar_login(redirect_to: str = "onboarding"):
    # Create state with redirect information
    state_data = {
        "random": ''.join(random.choices(string.digits, k=12)),
        "redirect_to": redirect_to
    }
    state = f"{state_data['random']}_{state_data['redirect_to']}"
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_CALENDAR_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.readonly",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
    return RedirectResponse(url)

@router.get("/calendar/callback")
def calendar_callback(code: str, state: str = None):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_CALENDAR_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_res = requests.post(token_url, data=data)
    if not token_res.ok:
        return HTMLResponse("<script>window.close();</script><p>Failed to connect Google Calendar. You may close this window.</p>")
    tokens = token_res.json()
    
    # Parse state to determine redirect location
    redirect_to = "onboarding"  # default
    if state and "_" in state:
        try:
            redirect_to = state.split("_")[-1]
        except:
            pass
    
    # Determine redirect URL based on redirect_to
    if redirect_to == "settings":
        redirect_url = f"{settings.FRONTEND_URL}/dashboard/pages/innstillinger/integrasjoner?onboarding_step=calendar&access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
    else:
        redirect_url = f"{settings.FRONTEND_URL}/onboarding?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&onboarding_step=calendar"
    
    return RedirectResponse(redirect_url)

@router.get("/gmail/login")
def gmail_login(redirect_to: str = "onboarding"):
    # Create state with redirect information
    state_data = {
        "random": ''.join(random.choices(string.digits, k=12)),
        "redirect_to": redirect_to
    }
    state = f"{state_data['random']}_{state_data['redirect_to']}"
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_GMAIL_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
    return RedirectResponse(url)

@router.get("/gmail/callback")
def gmail_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_GMAIL_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_res = requests.post(token_url, data=data)
    if not token_res.ok:
        return HTMLResponse("<script>window.close();</script><p>Failed to connect Gmail. You may close this window.</p>")
    tokens = token_res.json()
    # Fetch the user's Gmail address using the access token
    userinfo_res = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    if not userinfo_res.ok:
        return HTMLResponse("<script>window.close();</script><p>Failed to get Gmail user info. You may close this window.</p>")
    userinfo = userinfo_res.json()
    email = userinfo.get("email", "")
    username = userinfo.get("name", "")
    print(f"userinfo========>: {userinfo}")
    
    # Parse state to determine redirect location
    redirect_to = "onboarding"  # default
    if state and "_" in state:
        try:
            redirect_to = state.split("_")[-1]
        except:
            pass
    
    # Determine redirect URL based on redirect_to
    if redirect_to == "settings":
        redirect_url = f"{settings.FRONTEND_URL}/dashboard/pages/innstillinger/integrasjoner?onboarding_step=gmail-box&access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&gmail_address={email}&gmail_username={username}"
    else:
        redirect_url = f"{settings.FRONTEND_URL}/onboarding?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&onboarding_step=gmail-box&gmail_address={email}&gmail_username={username}"
    
    return RedirectResponse(redirect_url)

@router.get("/outlook/login")
def outlook_login(redirect_to: str = "onboarding"):
    # Create state with redirect information
    state_data = {
        "random": ''.join(random.choices(string.digits, k=12)),
        "redirect_to": redirect_to
    }
    state = f"{state_data['random']}_{state_data['redirect_to']}"
    
    auth_url = outlook_auth_service.get_auth_url(state)
    return RedirectResponse(auth_url)

@router.get("/outlook/callback")
def outlook_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    try:
        # Exchange code for tokens
        tokens = outlook_auth_service.exchange_code_for_tokens(code)
        
        # Get user info
        userinfo = outlook_auth_service.get_user_info(tokens['access_token'])
        email = userinfo.get("mail", userinfo.get("userPrincipalName", ""))
        username = userinfo.get("displayName", "")
        print(f"outlook userinfo========>: {userinfo}")
        
        # Parse state to determine redirect location
        redirect_to = "onboarding"  # default
        if state and "_" in state:
            try:
                redirect_to = state.split("_")[-1]
            except:
                pass
        
        # Determine redirect URL based on redirect_to
        if redirect_to == "settings":
            redirect_url = f"{settings.FRONTEND_URL}/dashboard/pages/innstillinger/integrasjoner?onboarding_step=outlook-box&access_token={tokens['access_token']}&refresh_token={tokens.get('refresh_token', '')}&outlook_address={email}&outlook_username={username}"
        else:
            redirect_url = f"{settings.FRONTEND_URL}/onboarding?access_token={tokens['access_token']}&refresh_token={tokens.get('refresh_token', '')}&onboarding_step=outlook-box&outlook_address={email}&outlook_username={username}"
        
        return RedirectResponse(redirect_url)
        
    except Exception as e:
        logger.error(f"Outlook callback error: {str(e)}", exc_info=True)
        error_message = f"Failed to connect Outlook: {str(e)}"
        return HTMLResponse(f"<script>window.close();</script><p>{error_message}</p><p>You may close this window.</p>")


@router.get("/facebook/login")
def facebook_login(redirect_to: str = "onboarding"):
    # Create state with redirect information
    state_data = {
        "random": ''.join(random.choices(string.digits, k=12)),
        "redirect_to": redirect_to
    }
    state = f"{state_data['random']}_{state_data['redirect_to']}"
    
    auth_url = facebook_auth_service.get_facebook_auth_url(state)
    return RedirectResponse(auth_url)

@router.get("/facebook/callback")
async def facebook_callback(
    code: str,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    # This is still sync; ok to call directly. (Or you can wrap in run_sync too.)
    tokens = await facebook_auth_service.exchange_facebook_code_for_token(code)
    if not tokens or "access_token" not in tokens:
        return JSONResponse(
            {"error": "oauth_exchange_failed", "detail": "No access token from Facebook"},
            status_code=HTTP_400_BAD_REQUEST,
        )

    access_token = tokens["access_token"]

    # NOW we await the async function
    userinfo = await facebook_auth_service.get_facebook_user_info(access_token)
    if not userinfo:
        return JSONResponse(
            {"error": "user_info_failed", "detail": "Could not fetch user info from Facebook"},
            status_code=HTTP_400_BAD_REQUEST,
        )

    email = userinfo.get("email", userinfo.get("userPrincipalName", "")) or ""
    username = userinfo.get("name", "") or ""

    # Get Facebook pages
    pages_data = await facebook_auth_service.get_facebook_pages(access_token)
    if not pages_data or not pages_data.get('data'):
        raise HTTPException(status_code=400, detail="No Facebook pages found")
    
    page = pages_data['data'][0]
    logging.info(f"User {username} is managing Facebook page: {page.get('name', '')} , Page Access Token: {page.get('access_token', '')}")
    # state parsing
    redirect_to = "onboarding"
    if state:
        try:
            redirect_to = state.split("_")[-1] if "_" in state else state
        except Exception:
            pass

    if redirect_to == "settings":
        
        redirect_url = (
            f"{settings.FRONTEND_URL}/dashboard/pages/innstillinger/integrasjoner"
            f"?onboarding_step=facebook-box"
            f"&access_token={access_token}"
            f"&refresh_token={tokens.get('access_token', '')}"
            f"&facebook_address={email}"
            f"&facebook_username={username}"
            f"&facebook_page_id={page.get('id', '')}"
            f"&facebook_page_name={page.get('name', '')}"
            f"&page_access_token={page.get('access_token', '')}"
            f"&facebook_user_id={userinfo.get('id', '')}"
            f"&category={page.get('category', '')}"
            f"&fan_count={page.get('fan_count', '')}"
        )
    else:
        redirect_url = (
            f"{settings.FRONTEND_URL}/onboarding"
             f"?onboarding_step=facebook-box"
           f"&access_token={access_token}"
             f"&refresh_token={tokens.get('access_token', '')}"
            f"&facebook_address={email}"
            f"&facebook_username={username}"
            f"&facebook_page_id={page.get('id', '')}"
            f"&facebook_page_name={page.get('name', '')}"
            f"&page_access_token={page.get('access_token', '')}"
            f"&facebook_user_id={userinfo.get('id', '')}"
            f"&category={page.get('category', '')}"
            f"&fan_count={page.get('fan_count', '')}"

        )

    return RedirectResponse(redirect_url, status_code=302)



@router.get("/instagram/login")
def instagram_login(redirect_to: str = "onboarding"):
    # Create state with redirect information
    state_data = {
        "random": ''.join(random.choices(string.digits, k=12)),
        "redirect_to": redirect_to
    }
    state = f"{state_data['random']}_{state_data['redirect_to']}"
    
    auth_url = instagram_auth_service.get_instagram_auth_url(state)
    return RedirectResponse(auth_url)

@router.get("/instagram/callback")
async def instagram_callback(
    code: str,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    # This is still sync; ok to call directly. (Or you can wrap in run_sync too.)
    tokens = await instagram_auth_service.exchange_instagram_code_for_token(code)
    if not tokens or "access_token" not in tokens:
        return JSONResponse(
            {"error": "oauth_exchange_failed", "detail": "No access token from instagram"},
            status_code=HTTP_400_BAD_REQUEST,
        )

    access_token = tokens["access_token"]

         # NOW we await the async function
    userinfo = await instagram_auth_service.get_instagram_user_info(access_token)
    if not userinfo:
        return JSONResponse(
            {"error": "user_info_failed", "detail": "Could not fetch user info from instagram"},
            status_code=HTTP_400_BAD_REQUEST,
        )

    instagram_user_id = userinfo.get("id", userinfo.get("user_id", "")) or ""
    instagram_username = userinfo.get("username", "") or ""
    instagram_page_access_token = access_token

    # Get instagram pages
    
    # state parsing
    redirect_to = "onboarding"
    if state:
        try:
            redirect_to = state.split("_")[-1] if "_" in state else state
        except Exception:
            pass

    if redirect_to == "settings":
        redirect_url = (
            f"{settings.FRONTEND_URL}/dashboard/pages/innstillinger/integrasjoner"
            f"?onboarding_step=instagram-box"
            f"&access_token={access_token}"
            f"&refresh_token={tokens.get('refresh_token', '')}"
            f"&instagram_account_id={instagram_user_id}"
            f"&instagram_username={instagram_username}"
            f"&instagram_tokens={instagram_page_access_token}"
        )
    else:
        redirect_url = (
            f"{settings.FRONTEND_URL}/onboarding"
            f"?access_token={access_token}"
            f"&refresh_token={tokens.get('refresh_token', '')}"
            f"&onboarding_step=instagram-box"
            f"&instagram_account_id={instagram_user_id}"
            f"&instagram_username={instagram_username}"
            f"&instagram_tokens={instagram_page_access_token}"
        )

    return RedirectResponse(redirect_url, status_code=302)


