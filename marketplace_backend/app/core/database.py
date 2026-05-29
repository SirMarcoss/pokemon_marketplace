from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import declerative_base
from app.core.config import settings

#Creo il motore di connessione al db
motore_database= create_engine(settings.DATABASE_URL)

#Creo la singola sessione per utente
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=motore_database)
#Rimuovendo l'autocommit si ha il pieno controllo del salvataggio delle operazioni
#Autoflush prepara le informazioni per l'autocommit, tenerlo attivo non ha senso
