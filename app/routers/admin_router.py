# app/routers/admin_router.py
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session, engine
from app.config import get_settings
import json
import os
from pydantic import BaseModel
from typing import Optional

# models & helpers
from app.models.models import AdminUser
from app.routers.auth_router import get_password_hash, verify_password, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.services.email_service import send_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/admin", tags=["Admin"])


class Credentials(BaseModel):
    email: str
    password: str

@router.post("/update-credentials", status_code=200)
async def update_credentials(
    payload: Credentials = Body(...),
    session: Session = Depends(get_session)
):
    """Update admin credentials (no authentication required)."""
    # Accept a JSON body containing { "email": ..., "password": ... }
    # Update settings file
    settings_file = os.getenv("SETTINGS_FILE", "app_settings.json")
    settings = get_settings()
    email = payload.email
    password = payload.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password fields are required")
    settings["admin"]["email"] = email
    # Hash the password before saving to settings to avoid storing plaintext
    password_hash = get_password_hash(password)
    settings["admin"]["password_hash"] = password_hash

    # Also persist to DB AdminUser row for consistency
    try:
        # use direct engine-backed session for this DB update
        with Session(engine) as session:
            admin = session.exec(select(AdminUser).where((AdminUser.username == email) | (AdminUser.email == email))).first()
            if admin:
                admin.password_hash = password_hash
                admin.email = email
                admin.username = email
                session.add(admin)
                session.commit()
            else:
                admin = AdminUser(username=email, email=email, password_hash=password_hash)
                session.add(admin)
                session.commit()
    except Exception:
        # If DB update fails, continue but log (do not expose internals)
        print("Warning: failed to update AdminUser DB row")

    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)

    return {"message": "Credentials updated successfully"}


class TempAdminCreate(BaseModel):
    email: Optional[str] = None



@router.post("/create-temp")
async def create_temp_admin(payload: TempAdminCreate = Body(...), session: Session = Depends(get_session)):
    """Create a temporary admin user with a random password and return it.

    Development-only: returns the temporary password so you can log in and then change it.
    """
    import secrets

    email = payload.email or "temp_admin@example.com"
    temp_password = secrets.token_urlsafe(10)
    password_hash = get_password_hash(temp_password)

    # Update settings file (store hash only)
    settings_file = os.getenv("SETTINGS_FILE", "app_settings.json")
    settings = get_settings()
    settings["admin"]["email"] = email
    settings["admin"]["password_hash"] = password_hash
    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        print("Warning: failed to write settings file for temp admin")

    # Update or create DB AdminUser
    admin = session.exec(select(AdminUser).where((AdminUser.username == email) | (AdminUser.email == email))).first()
    if admin:
        admin.password_hash = password_hash
        admin.email = email
        admin.username = email
        session.add(admin)
        session.commit()
    else:
        admin = AdminUser(username=email, email=email, password_hash=password_hash)
        session.add(admin)
        session.commit()
        session.refresh(admin)

    return {"email": email, "temp_password": temp_password, "message": "Temporary admin created. Change password after login."}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    payload: PasswordChange,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Change the current admin's password. Requires a valid admin token."""
    try:
        payload_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload_jwt.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin = session.exec(select(AdminUser).where((AdminUser.username == username) | (AdminUser.email == username))).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")

    # Verify current password
    if not verify_password(payload.current_password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current password is incorrect")

    admin.password_hash = get_password_hash(payload.new_password)
    session.add(admin)
    session.commit()
    return {"message": "Password changed successfully"}


@router.get("/settings")
async def get_admin_settings():
    """Get current admin settings (no authentication required)."""
    return get_settings()


@router.put("/settings")
async def update_admin_settings(settings: dict):
    """Update admin settings (no authentication required)."""
    settings_file = os.getenv("SETTINGS_FILE", "app_settings.json")
    current_settings = get_settings()
    
    # Merge with new settings
    updated_settings = {**current_settings, **settings}
    
    with open(settings_file, "w") as f:
        json.dump(updated_settings, f, indent=2)
    
    return {"message": "Settings updated successfully", "settings": updated_settings}


@router.post("/test-email")
async def test_email(payload: dict = Body(...)):
    """Send a test email using configured SMTP settings. Payload: {to_email, subject, body}.

    This is useful to verify SMTP configuration when enabling admin notifications.
    """
    to_email = payload.get("to_email")
    subject = payload.get("subject", "Test Email from Morine Gypsum")
    body = payload.get("body", "This is a test email.")

    if not to_email:
        raise HTTPException(status_code=400, detail="to_email is required")

    success = send_email(to_email, subject, body)
    if success:
        return {"sent": True, "to": to_email}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email. Check SMTP settings.")

