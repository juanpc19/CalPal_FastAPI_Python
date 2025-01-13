from datetime import datetime
import os
from typing import List
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Header, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
from utils.fileUtils import extraer_token_header_authorization
from models.registroDiario import RegistroDiarioModel, PostRegistroDiarioModel, UpdateRegistroDiarioModel, RegistroConComidasConAlimentosModel
from models.usuario import UsuarioObjetivosComidasModel
from models.comidaRegistro import PostComidaRegistroModel
from models.alimentoComida import AlimentoComidaModel, PostAlimentoComidaModel
from serializers.registroDiario import serializar_registro_completo, serializar_registros

registros_diarios_root=APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#endpoint que recibe un registro recien creado desde app y lo inserta en la bbdd creando sus comidas partir de datos_usuario
@registros_diarios_root.post("/registros-diarios", response_model=dict, response_description="Inserta nuevo registro diario del usuario")
async def nuevo_registro_diario(registro_diario: PostRegistroDiarioModel, datos_usuario: UsuarioObjetivosComidasModel, 
    request: Request, authorization: str = Header(..., description="Token JWT de verificación")):
    token=extraer_token_header_authorization(authorization)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    registro_diario_json=jsonable_encoder(registro_diario)
    ref_registro=await request.app.mongodb["registros_diarios"].insert_one(registro_diario_json)
    
    #Registro viene de app y se puede insertar tal cual, con datos de usuario creo comidas default y las inserto
    comidas_usuario=datos_usuario.comidas
    lista_comidas=[]
    
    for k,v in comidas_usuario.items():
        comida = PostComidaRegistroModel(   
        id_reg=str(ref_registro.inserted_id),
        orden=v,
        nombre=k,
        calorias=0.0,
        proteinas=0.0,
        carbohidratos=0.0,
        grasas=0.0
    )
        lista_comidas.append(jsonable_encoder(comida))
    
    await request.app.mongodb["comidas_registro"].insert_many(lista_comidas)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "Registro con comidas creado con exito"})
        
#endpoint que actualiza campo peso de un usuario
@registros_diarios_root.patch("/registros-diarios/{id_registro}", response_model=dict, response_description="Actualiza peso en un registro diario del usuario")
async def actualizar_peso_registro_diario(id_registro: str, data: dict, request: Request, authorization: str = Header(..., description="Token JWT de verificación")):
    token=extraer_token_header_authorization(authorization)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
 
    peso=data.get("peso")
    if peso is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo 'peso' es requerido.")
    
    resultado=await request.app.mongodb["registros_diarios"].update_one({"_id": ObjectId(id_registro)}, {"$set": {"peso": peso}})
    if resultado.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el registro para actualizar.")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Peso actualizado correctamente"})

@registros_diarios_root.get("/registros-diarios/registro-actual", response_model=RegistroConComidasConAlimentosModel, response_description="Obtiene un registro con sus comidas asociadas y los alimentos asociados a las comidas")
async def obtener_registro_completo_actual(request: Request, authorization: str = Header(..., description="Token JWT de verificacion")):
    token=extraer_token_header_authorization(authorization)
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    id_usuario=payload["sub"]
    fecha_actual_string=str(datetime.now().date())
    
    registro = await request.app.mongodb["registros_diarios"].find_one({"id_usu": id_usuario, "fecha": fecha_actual_string})
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado para la fecha actual.")
    
    id_registro=registro["_id"]
    comidas=await request.app.mongodb["comidas_registro"].find({"id_reg": str(id_registro)}).to_list()
    comida_object_ids = [comida["_id"] for comida in comidas]#para consulta unica almaceno todos los ids en una lista
    
    alimentos = await request.app.mongodb["alimentos_comida"].find({"id_com": {"$in": [str(_id) for _id in comida_object_ids]}}).to_list()
    alimentos_por_comida = {}#guardara la relacion entre comida y sus alimentos (k,v) para facilitar serializacion
    for alimento in alimentos:
        alimentos_por_comida.setdefault(alimento["id_com"], []).append(alimento)
        
    registro_completo_model=serializar_registro_completo(registro,comidas,alimentos_por_comida)
    
    return registro_completo_model

#endpoint que retorna los registros de un usuario
@registros_diarios_root.get("/registros-diarios", response_model=List[RegistroDiarioModel], response_description="Obtiene todos los registros de un usuario")
async def obtener_registros_usuario(request: Request, authorization: str = Header(..., description="Token JWT de verificacion")):
    token=extraer_token_header_authorization(authorization)
    try: 
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")        
    
    token_encontrado=await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    id_usuario=payload["sub"]
    
    lista_registros=await request.app.mongodb["registros_diarios"].find({"id_usu": id_usuario}).to_list()
    if not lista_registros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("No se encontraron registros asociados al usuario"))
    registros_serializados=serializar_registros(lista_registros)
    
    return registros_serializados
    
#endpoint que añade un alimento y actualiza valores en cascada en comidas y registro
@registros_diarios_root.patch("/registros-diarios/{id_registro}/comidas/{id_comida}/alimentos", response_model=dict, response_description="Inserta nuevo alimento actualiza datos de comidas y registro")
async def nuevo_alimento_comida_registro(id_registro: str, id_comida: str, alimento_comida: PostAlimentoComidaModel, 
    request: Request, authorization: str = Header(..., description="Token JWT de verificación")):
    token=extraer_token_header_authorization(authorization)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    id_registro=ObjectId(id_registro)
    id_comida=ObjectId(id_comida)
    
    registro = await request.app.mongodb["registros_diarios"].find_one({"_id": id_registro})
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado.")
    
    comida = await request.app.mongodb["comidas_registro"].find_one({"_id": id_comida})
    if not comida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada.")
    
    
    valores_incrementar = {
        "calorias": alimento_comida.calorias,
        "proteinas": alimento_comida.proteinas,
        "carbohidratos": alimento_comida.carbohidratos,
        "grasas": alimento_comida.grasas
    }
    
    alimento_comida_json=jsonable_encoder(alimento_comida)
    
    # Actualizar en cascada con sesion como transaccion para asegurar actualizacion completa
    async with await request.app.mongodb.client.start_session() as session:
        async with session.start_transaction():
         
            await request.app.mongodb["alimentos_comida"].insert_one(alimento_comida_json, session=session)
            
            await request.app.mongodb["comidas_registro"].update_one(
                {"_id": id_comida},
                {"$inc": valores_incrementar},
                session=session
            )
            
            await request.app.mongodb["registros_diarios"].update_one(
                {"_id": id_registro},
                {"$inc": valores_incrementar},
                session=session
            )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "Alimento añadido correctamente"})

    
#endpoint que Borra un alimento y actualiza valores en cascada en comidas y registro
@registros_diarios_root.delete("/registros-diarios/{id_registro}/comidas/{id_comida}/alimentos", response_model=dict, response_description="Borra alimento y actualiza datos de comidas y registro")
async def eliminar_alimento_comida_registro(id_registro: str, id_comida: str, alimento_comida: AlimentoComidaModel, 
    request: Request, authorization: str = Header(..., description="Token JWT de verificación")):
    token=extraer_token_header_authorization(authorization)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    id_registro=ObjectId(id_registro)
    id_comida=ObjectId(id_comida)
    id_alimento=ObjectId(alimento_comida.id_alimento)
    
    registro = await request.app.mongodb["registros_diarios"].find_one({"_id": id_registro})
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado.")
    
    comida = await request.app.mongodb["comidas_registro"].find_one({"_id": id_comida})
    if not comida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comida no encontrada.")
    
    alimento = await request.app.mongodb["alimentos_comida"].find_one({"_id": id_alimento})
    if not alimento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alimento no encontrado.")
    
    
    valores_decrementar = {
        "calorias": alimento_comida.calorias,
        "proteinas": alimento_comida.proteinas,
        "carbohidratos": alimento_comida.carbohidratos,
        "grasas": alimento_comida.grasas
    }
    
    # Actualizar en cascada con sesion como transaccion para asegurar actualizacion completa
    async with await request.app.mongodb.client.start_session() as session:
        async with session.start_transaction():
         
            await request.app.mongodb["alimentos_comida"].delete_one({"_id": id_alimento}, session=session)

            await request.app.mongodb["comidas_registro"].update_one(
                {"_id": id_comida},
                #recorre el dict extrayendo el value como negativo de cada key "restando" su valor al hacer el incremento
                {"$inc": {k: -v for k, v in valores_decrementar.items()}},
                session=session
            )
            
            await request.app.mongodb["registros_diarios"].update_one(
                {"_id": id_registro},
                {"$inc": {k: -v for k, v in valores_decrementar.items()}},
                session=session
            )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Alimento eliminado correctamente"})
