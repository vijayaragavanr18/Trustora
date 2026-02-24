from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User, UserSettings
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.utils.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# POST /api/auth/register
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        organization=user_data.organization or ""
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default settings
    new_settings = UserSettings(user_id=new_user.id)
    db.add(new_settings)
    db.commit()
    
    return _merge_user_settings(new_user, new_settings)

def _merge_user_settings(user, settings):
    # Create a dict from user
    u_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "organization": user.organization,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "language": settings.language if settings else "English (US)",
        "timezone": settings.timezone if settings else "UTC-05:00",
        "preferences": settings.preferences if settings else '{"analysis_complete": true, "security_alerts": true, "marketing": false}'
    }
    return u_dict

# POST /api/auth/login
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# POST /api/auth/logout
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless - client just deletes token
    return {"message": "Logged out successfully"}

# GET /api/auth/me
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        return _merge_user_settings(current_user, settings)
    except Exception:
        db.rollback()
        # Fallback to no settings if table doesn't exist
        return _merge_user_settings(current_user, None)

# PUT /api/auth/me
@router.put("/me")
def update_me(
    user_update: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.organization is not None:
        current_user.organization = user_update.organization
    
    if user_update.language is not None:
        settings.language = user_update.language
    if user_update.timezone is not None:
        settings.timezone = user_update.timezone
    if user_update.preferences is not None:
        settings.preferences = user_update.preferences
        
    if user_update.password is not None:
        current_user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    db.refresh(settings)
    return _merge_user_settings(current_user, settings)

# DELETE /api/auth/me
@router.delete("/me")
def delete_account(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

# POST /api/auth/refresh
@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": current_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}