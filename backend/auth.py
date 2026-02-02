import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from py_models.signin_models import User

load_dotenv()

# ==================================================
# CONFIG
# ==================================================
SECRET_KEY = os.getenv("SECRET_KEY", "skillnest-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1 week (user requested long sessions)

# ==================================================
# 🔥 FIXED PASSWORD HASHING (NO BCRYPT)
# ==================================================
# pbkdf2_sha256 = NO 72 byte limit + Vercel safe
# schemes=["pbkdf2_sha256", "bcrypt"] = Supports both new and legacy hashes
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ==================================================
# PASSWORD FUNCTIONS
# ==================================================
def hash_password(password: str) -> str:
    """Hash plain password safely (NO length limit)."""
    return pwd_context.hash(password.strip())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    return pwd_context.verify(plain_password.strip(), hashed_password)


# ==================================================
# JWT TOKEN
# ==================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==================================================
# AUTH DEPENDENCY
# ==================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    def auth_error(msg: str):
        print(f"AUTH REJECTED: {msg}")
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auth error: {msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Debugging: Print first 10 chars of token
        print(f"Authenticating token starting with: {token[:10]}...")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise auth_error(f"Token decoded but 'sub' claim missing. Payload: {payload}")

    except JWTError as e:
        # Check if it's expired
        if "expired" in str(e).lower():
            raise auth_error("Token has expired. Please login again.")
        raise auth_error(f"JWT Decode failed: {str(e)}")
    except Exception as e:
        raise auth_error(f"Unexpected token error: {type(e).__name__}: {str(e)}")

    try:
        user_id_int = int(user_id)
        user = db.query(User).filter(User.user_id == user_id_int).first()
    except ValueError:
        raise auth_error(f"Invalid user ID format in token: {user_id}")
    except Exception as e:
        print(f"DB Error in Auth: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error during auth: {str(e)}")

    if not user:
        raise auth_error(f"User with ID {user_id} not found in database. Token is valid but user is gone.")

    print(f"AUTH SUCCESS for user: {user.user_email} (ID: {user.user_id})")
    return user
