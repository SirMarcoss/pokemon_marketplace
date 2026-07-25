from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importiamo gli schemi Pydantic
from app.schemas.user_sh import UserCreate, UserRead

# Importiamo il Service che abbiamo analizzato prima
from app.services.user_service import UserService

# Importiamo la funzione che ci fornisce la connessione al DB (ipotizziamo si trovi qui)
from app.core.database import get_db

# Creiamo il router
router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    try:
        # FastAPI "tenta" di eseguire la creazione
        user = await user_service.create_user(payload)
        return user

    except ValueError as e:
        # Se il Service lancia un ValueError, il codice salta immediatamente qui.
        # Catturiamo l'errore nella variabile 'e' e lo trasformiamo in un errore HTTP pulito.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)  # Questo stamperà esattamente la stringa definita nel Service
        )

