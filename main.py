from fastapi import FastAPI
from contextlib import asynccontextmanager#para iniciar y cerrar cliente
import uvicorn #para testing local
from motor.motor_asyncio import AsyncIOMotorClient#uso este para asincronia
#from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from routes.index import entry_root
from routes.alimentosBaseRoutes import alimentos_base_root
from routes.alimentosUsuarioRoutes import alimentos_usuario_root
from routes.usuariosRoutes import usuarios_root
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
        uri = os.getenv("MONGO_URI")
        client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
        app.mongodb=client.CalPal
        try:
                yield
        finally:
                client.close()
        
app = FastAPI(lifespan=lifespan)#la app tendra el lifespan dado por el yield de la funcion

app.include_router(entry_root)
app.include_router(alimentos_base_root)
app.include_router(usuarios_root)
app.include_router(alimentos_usuario_root) #TO DO


if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
 

