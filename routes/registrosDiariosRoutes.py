import os
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Header, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
from utils.fileUtils import crear_token_verificacion, crear_token_inicio_sesion, enviar_email_verificacion, enviar_email_cambiar_contrasena, hash_password, verify_password, extraer_token_header_authorization
from models.registroDiario import RegistroDiarioModel, PostRegistroDiarioModel, UpdateRegistroDiarioModel
from models.usuario import UsuarioObjetivosComidasModel
from models.comidaRegistro import PostComidaRegistroModel

registros_diarios_root=APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#endpoint que recibe un registro recien creado desde app y lo inserta en la bbdd
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
    ref_registro=await request.app.mongodb["registrosDiarios"].insert_one(registro_diario_json)
    
    #Registro viene de app y se puede insertar tal cual, con datos de usuario creo comidas default y las inserto
    comidas_usuario=datos_usuario.comidas
    print(comidas_usuario)
    lista_comidas=[]
    
    for k,v in comidas_usuario.items():
        comida = PostComidaRegistroModel(  # Crear una nueva instancia en cada iteración
        id_reg=str(ref_registro.inserted_id),
        orden=v,
        nombre=k,
        calorias=0.0,
        proteinas=0.0,
        carbohidratos=0.0,
        grasas=0.0
    )
        lista_comidas.append(jsonable_encoder(comida))
    
    await request.app.mongodb["comidasRegistro"].insert_many(lista_comidas)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "Registro con comidas creado con exito"})
        
    
    

