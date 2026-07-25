from passlib.context import CryptContext
from jose import jwt, ExpiredSignatureError
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.database import get_db
from app.services.user_service import UserService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "sub": str(data.get("sub")), # User ID
        "iat": datetime.now(timezone.utc),   # Quando è stato emesse issued at
        "exp": expire               # Quando scade
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str)-> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None or sub == "None":
            raise ValueError("Token missing 'sub' claim")
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")




# Questo è il "segugio" di FastAPI.
# tokenUrl indica a FastAPI dove si trova la porta d'ingresso.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    """
    Dipendenza che legge il token, lo verifica e restituisce l'utente autenticato.
    """
    
    # Centralizziamo l'errore per rispettare il principio DRY (Don't Repeat Yourself)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o token scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_service = UserService(db)

    try:
        verified_token = verify_access_token(token)
        user_id = verified_token.get("sub")
        if user_id is None:
                raise credentials_exception

    except ValueError:  # Cattura l'errore che lancia la tua verify_access_token
        raise credentials_exception

    # 3. Cerca l'utente nel database tramite l'ID (user_id)
    # Suggerimento: dovrai creare un metodo get_user_by_id nel UserService
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise credentials_exception
    return user