from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings


key = settings.SECRETE_KEY
pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password (password):
    secrete_pwd = pwd_context.hash(password) #funzione di hashing della password
    return secrete_pwd


def verify_password(plain_password, hash_password):
    return pwd_context.verify(plain_password, hash_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

#riceve un dizionario
#ne fa una copia
#calcola il tempo di expire prendendo il tempo attuale UTC + 30 min (deciso da noi)
#aggiunge al dizionario expire
#jason wek token encoda il dizionario in una stringa utilizzando head, payload, stringa SECRET KEY, algoritmo di encode