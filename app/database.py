from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
#Configuro la conexión con PostgreSQL
#DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hospital_db" #Para usar localmente
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/hospital_db") #Para usar Docker


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

#Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()