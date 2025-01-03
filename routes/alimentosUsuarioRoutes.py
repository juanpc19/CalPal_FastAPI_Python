from typing import List
from fastapi import APIRouter, Header, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from models.alimentoUsuario import AlimentoUsuarioModel, PostAlimentoUsuarioModel, UpdateAlimentoUsuarioModel
import jwt
import os
from dotenv import load_dotenv
from utils.fileUtils import extraer_token_header_authorization
from serializers.alimentoUsuario import serializar_alimento_usuario, serializar_alimentos_usuario

alimentos_usuario_root = APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

@alimentos_usuario_root.post("/alimentos-usuarios", response_model=dict, response_description="Añade un nuevo alimento de usuario")
async def insertar_nuevo_alimento(alimento_usuario: PostAlimentoUsuarioModel, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Usuario no existente."))
    
    alimento_usuario_json=jsonable_encoder(alimento_usuario)
    await request.app.mongodb["alimentos_usuarios"].insert_one(alimento_usuario_json)
     
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "Alimento insertado correctamente."})

@alimentos_usuario_root.get("/alimentos-usuarios", response_model=List[AlimentoUsuarioModel], response_description="Obtiene todos los alimentos del usuario")
async def obtener_alimentos_usuario(request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"] 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Usuario no existente."))
    
    alimentos_usuario = await request.app.mongodb["alimentos_usuarios"].find({"id_usu": id_usuario}).to_list()
    if not alimentos_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("No se encontraron alimentos asociados al usuario"))
    alimentos_usuario_serializados = serializar_alimentos_usuario(alimentos_usuario)
    
    return alimentos_usuario_serializados

@alimentos_usuario_root.get("/alimentos-usuarios/{_id}", response_model=AlimentoUsuarioModel, response_description="Obtiene alimento de usuario seleccionado")
async def obtener_alimento_usuario_por_id(_id: str, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"] 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Usuario no existente."))
    
    alimento_usuario = await request.app.mongodb["alimentos_usuarios"].find_one({"_id":ObjectId(_id)})
    if not alimento_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("No se encontro el alimento especificado"))
    alimento_usuario_serializado = serializar_alimento_usuario(alimento_usuario)
    
    return alimento_usuario_serializado

@alimentos_usuario_root.patch("/alimentos-usuarios/{_id}", response_model=dict, response_description="modifica alimento de usuario seleccionado")
async def modificar_alimento_usuario(_id: str, alimento_usuario: UpdateAlimentoUsuarioModel, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Usuario no existente."))
    
    alimento_encontrado = await request.app.mongodb["alimentos_usuarios"].find_one({"_id": ObjectId(_id)})
    if not alimento_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alimento no encontrado")

    alimento_usuario_dict = alimento_usuario.model_dump(exclude_unset=True)
    resultado_update = await request.app.mongodb["alimentos_usuarios"].update_one({"_id": ObjectId(_id)}, {"$set": alimento_usuario_dict})
    if resultado_update.modified_count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Cambios no realizados, los datos no son diferentes."})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Alimento actualizado correctamente"})
    
     
@alimentos_usuario_root.delete("/alimentos-usuarios/{_id}", response_model=dict, response_description="Elimina alimento de usuario seleccionado")
async def eliminar_alimento_usuario(_id: str, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    usuario_encontrado=await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Usuario no existente."))
    
    alimento_encontrado = await request.app.mongodb["alimentos_usuarios"].find_one({"_id": ObjectId(_id)})
    if not alimento_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alimento no encontrado")

    resultado_delete=await request.app.mongodb["alimentos_usuarios"].find_one_and_delete({"_id":ObjectId(_id)})
    if not resultado_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error en la eliminacion del alimento.")
     
    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Alimento eliminado correctamente."})