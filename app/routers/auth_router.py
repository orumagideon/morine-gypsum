# app/routers/auth_router.py
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select, Session
from sqlalchemy import or_
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.db.session import get_session
from app.models.models import AdminUser
from app.config import get_settings
from app.services.email_service import send_otp_email

try:
    import bcrypt as _bcrypt

    if not hasattr(_bcrypt, "__about__"):
        class _About:
            __version__ = getattr(_bcrypt, "__version__", "4.0.1")

        _bcrypt.__about__ = _About()
except Exception:
    pass

router = APIRouter(prefix="/auth", tags=["Authentication"])

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should be in environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Password hashing - use bcrypt with proper configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"  # Use bcrypt 2b format
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory token blacklist for logout (development use). Tokens added here
# will be rejected by get_current_user. This is not persisted across restarts.
token_blacklist: set[str] = set()

class LoginRequest(BaseModel):
    # The frontend sends an `email` field; we treat this as a login identifier
    # which may be either an email or username for backward compatibility.
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None


class OtpVerificationRequest(BaseModel):
    email: str
    otp: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str


def _generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _find_admin(session: Session, identifier: str):
    return session.exec(
        select(AdminUser).where(or_(AdminUser.username == identifier, AdminUser.email == identifier))
    ).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if not plain_password or not hashed_password:
        return False
    
    try:
        # Try passlib first
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Fallback for bcrypt version issues
        try:
            import bcrypt
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # Handle both string and bytes for hashed_password
            if isinstance(hashed_password, str):
                hash_bytes = hashed_password.encode('utf-8')
            else:
                hash_bytes = hashed_password
            
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e2:
            print(f"Password verification failed: {e}, {e2}")
            return False


def get_password_hash(password: str) -> str:
    """Hash a password. Handle bcrypt version compatibility."""
    try:
        return pwd_context.hash(password)
    except (ValueError, AttributeError) as e:
        # Fallback for bcrypt version issues
        import bcrypt
        password_bytes = password.encode('utf-8')
        # Bcrypt has 72 byte limit
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # reject blacklisted tokens
        if token in token_blacklist:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = session.exec(
        select(AdminUser).where(or_(AdminUser.username == username, AdminUser.email == username))
    ).first()
    if admin is None:
        raise credentials_exception
    if not getattr(admin, "is_verified", True):
        raise credentials_exception
    return admin


@router.post("/register")
async def register_admin(payload: RegisterRequest, session: Session = Depends(get_session)):
    """Admin signup is disabled; access is login-only."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin signup is disabled.",
    )


@router.post("/verify-otp")
async def verify_admin_otp(payload: OtpVerificationRequest, session: Session = Depends(get_session)):
    """Verify the OTP sent during registration."""
    email = payload.email.strip().lower()
    admin = _find_admin(session, email)
    if not admin or not admin.otp_hash:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification code not found")

    if admin.otp_expires_at and admin.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")

    if not verify_password(payload.otp.strip(), admin.otp_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    admin.is_verified = True
    admin.otp_hash = None
    admin.otp_expires_at = None
    session.add(admin)
    session.commit()

    return {"message": "Account verified successfully"}


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, session: Session = Depends(get_session)):
    """Send a password reset OTP to the admin email address."""
    email = payload.email.strip().lower()
    admin = _find_admin(session, email)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin account not found")

    otp_code = _generate_otp()
    admin.reset_token_hash = get_password_hash(otp_code)
    admin.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
    session.add(admin)
    session.commit()

    email_sent = send_otp_email(email, otp_code, purpose="reset")
    if email_sent:
        return {"message": "Password reset code sent to your email"}

    return {
        "message": "Password reset code generated. SMTP is not configured, so use the code shown here.",
        "dev_reset_code": otp_code,
    }


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, session: Session = Depends(get_session)):
    """Reset the admin password using the emailed OTP."""
    email = payload.email.strip().lower()
    admin = _find_admin(session, email)
    if not admin or not admin.reset_token_hash:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reset code not found")

    if admin.reset_token_expires_at and admin.reset_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset code expired")

    if not verify_password(payload.otp.strip(), admin.reset_token_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset code")

    admin.password_hash = get_password_hash(payload.new_password)
    admin.reset_token_hash = None
    admin.reset_token_expires_at = None
    admin.is_verified = True
    session.add(admin)
    session.commit()

    return {"message": "Password reset successfully"}


@router.post("/login")
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Admin login endpoint."""
    # Get settings for default admin credentials
    settings = get_settings()
    default_email = settings.get("admin", {}).get("email", "orumagideon535@gmail.com")
    # Support legacy plaintext password in settings (deprecated) and new hashed
    default_password = settings.get("admin", {}).get("password", "@Kisumu254")
    settings_password_hash = settings.get("admin", {}).get("password_hash")
    
    email = login_data.email
    password = login_data.password
    
    # Check if admin exists (match either username or email)
    admin = _find_admin(session, email)
    
    # If admin doesn't exist, create it if credentials match settings defaults
    if not admin:
        created = False
        # First try hashed settings password if available
        if settings_password_hash and verify_password(password, settings_password_hash) and email == default_email:
            admin = AdminUser(username=default_email, email=default_email, password_hash=settings_password_hash, is_verified=True)
            session.add(admin)
            session.commit()
            session.refresh(admin)
            created = True
        # Fallback: legacy plaintext default password
        if not created and email == default_email and password == default_password:
            admin = AdminUser(username=default_email, email=default_email, password_hash=get_password_hash(default_password), is_verified=True)
            session.add(admin)
            session.commit()
            session.refresh(admin)
            created = True

        if not created:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Verify password
    password_valid = False
    
    # If admin has no password hash, try to validate against settings password hash or legacy plaintext
    if not admin.password_hash or admin.password_hash.strip() == "":
        # If settings contains a hashed password, verify against it
        if settings_password_hash and verify_password(password, settings_password_hash):
            password_valid = True
            admin.password_hash = settings_password_hash
            session.add(admin)
            session.commit()
        else:
            # Fallback: legacy plaintext default password
            settings_password = settings.get("admin", {}).get("password")
            if settings_password and password == settings_password:
                password_valid = True
                admin.password_hash = get_password_hash(password)
                session.add(admin)
                session.commit()
    else:
        # Admin has a password hash, try to verify
        try:
            password_valid = verify_password(password, admin.password_hash)
        except Exception as e:
            print(f"Password verification error: {e}")
            password_valid = False
        
        # If hash verification failed, check against default credentials as fallback
        if not password_valid:
            if email == default_email and password == default_password:
                password_valid = True
                # Update password hash to ensure it's properly stored
                admin.password_hash = get_password_hash(default_password)
                session.add(admin)
                session.commit()
            else:
                # Also check if password matches legacy plaintext settings
                settings_password = settings.get("admin", {}).get("password")
                if settings_password and password == settings_password:
                    password_valid = True
                    # Update password hash
                    admin.password_hash = get_password_hash(password)
                    session.add(admin)
                    session.commit()
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not getattr(admin, "is_verified", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please check your email for the OTP code.",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin.id,
            "email": admin.email or admin.username,
            "role": "admin"
        }
    }


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout by blacklisting the provided token (development use)."""
    token_blacklist.add(token)
    return {"message": "Logged out"}


@router.get("/me")
async def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "email": current_user.email or current_user.username,
        "role": "admin"
    }


@router.post("/reset-admin")
async def reset_admin(session: Session = Depends(get_session)):
    """Utility endpoint to reset/create default admin user. For development only."""
    settings = get_settings()
    default_email = settings.get("admin", {}).get("email", "orumagideon535@gmail.com")
    default_password = settings.get("admin", {}).get("password", "@Kisumu254")
    
    # Check if admin exists
    admin = session.exec(
        select(AdminUser).where(or_(AdminUser.username == default_email, AdminUser.email == default_email))
    ).first()
    
    if admin:
        # Update existing admin
        admin.password_hash = get_password_hash(default_password)
        admin.is_verified = True
        admin.otp_hash = None
        admin.otp_expires_at = None
        admin.reset_token_hash = None
        admin.reset_token_expires_at = None
        session.add(admin)
        session.commit()
        return {"message": f"Admin user '{default_email}' password reset successfully"}
    else:
        # Create new admin
        admin = AdminUser(
            username=default_email,
            email=default_email,
            password_hash=get_password_hash(default_password),
            is_verified=True,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return {"message": f"Admin user '{default_email}' created successfully"}

