from fastapi import FastAPI
from app.routers import auth_routes, user_routes
from app.database import Base, engine
from app.routers import cita_routes
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware



#Aqui creo las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app =FastAPI(title="API de Gestión de Citas Medicas")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o usa ["*"] para pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Aqui incluyo las rutas de autenticación y usuario
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(cita_routes.router)