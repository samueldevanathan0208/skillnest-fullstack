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
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# ==================================================
# 🔥 FIXED PASSWORD HASHING (NO BCRYPT)
# ==================================================
# pbkdf2_sha256 = NO 72 byte limit + Vercel safe
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
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
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auth error: {msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise auth_error("Token missing 'sub' claim")

    except JWTError as e:
        raise auth_error(f"JWT Decode failed: {str(e)}")
    except Exception as e:
        raise auth_error(f"Unexpected token error: {str(e)}")

    try:
        user = db.query(User).filter(User.user_id == int(user_id)).first()
    except ValueError:
        raise auth_error("Invalid user ID format in token")
    except Exception as e:
        # This might be a DB connection error, but let's check it
        raise HTTPException(status_code=500, detail=f"Database error during auth: {str(e)}")

    if not user:
        raise auth_error(f"User with ID {user_id} not found in database")

    return user
