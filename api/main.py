from fastapi import FastAPI
from contextlib import asynccontextmanager# Para manejar la inicialización y cierre de recursos de forma asíncrona.
import uvicorn # Herramientas para testing local
from motor.motor_asyncio import AsyncIOMotorClient# Cliente asíncrono para MongoDB.
from pymongo.server_api import ServerApi
from api.routes.index import entry_root
from api.routes.alimentosBaseRoutes import alimentos_base_root
from api.routes.alimentosUsuarioRoutes import alimentos_usuario_root
from api.routes.usuariosRoutes import usuarios_root
from api.routes.registrosDiariosRoutes import registros_diarios_root
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
        
app = FastAPI(lifespan=lifespan)

app.include_router(entry_root)
app.include_router(alimentos_base_root)
app.include_router(usuarios_root)
app.include_router(alimentos_usuario_root)
app.include_router(registros_diarios_root)


if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
 

