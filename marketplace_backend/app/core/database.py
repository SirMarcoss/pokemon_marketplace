from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import declarative_base
from app.core.config import settings

#Creo il motore di connessione al db
motore_database= create_engine(settings.DATABASE_URL)

#Creo la singola sessione per utente
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=motore_database)
#Rimuovendo l'autocommit si ha il pieno controllo del salvataggio delle operazioni
#Autoflush prepara le informazioni per l'autocommit, tenerlo attivo non ha senso
Base= declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db  #indipendentemente dal fatto che la funzione sia finita o meno(crash), il db si chiude
    finally:
        db.close()