from fastapi import APIRouter, Header, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from models.alimentoUsuario import AlimentoUsuarioModel, PostAlimentoUsuarioModel
import jwt
import os
from dotenv import load_dotenv
from utils.fileUtils import extraer_token_header_authorization

alimentos_usuario_root = APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

@alimentos_usuario_root.post("/alimentos-usuarios", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: PostAlimentoUsuarioModel, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]#extraigo el id del usuario del token    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("usuario no existente."))
    
    alimento_usuario_json=jsonable_encoder(alimento_usuario)
    await request.app.mongodb["alimentos_usuarios"].insert_one(alimento_usuario_json)
     
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "alimento insertado correctamente."})

@alimentos_usuario_root.get("/alimentos-usuarios", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: AlimentoUsuarioModel, request: Request):
    pass
@alimentos_usuario_root.get("/alimentos-usuarios/{_id}", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: AlimentoUsuarioModel, request: Request):
    pass
@alimentos_usuario_root.patch("/alimentos-usuarios/{_id}", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: AlimentoUsuarioModel, request: Request):
    pass
@alimentos_usuario_root.delete("/alimentos-usuarios/{_id}", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: AlimentoUsuarioModel, request: Request):
    pass