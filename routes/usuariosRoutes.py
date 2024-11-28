import os
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Header, Depends, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
from models.usuario import UsuarioModel, PostUsuarioModel, UpdateUsuarioModel, UsuarioRegistroResponseModel
from models.token import TokenModel
from serializers.usuario import serializar_usuario
from serializers.token import serializar_token
from utils.fileUtils import crear_token_verificacion, crear_token_inicio_sesion, enviar_email_verificacion, hash_password, verify_password

usuarios_root=APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#endpoint para comprobar si el email esta en uso, se usara cuando el usuario introduzca email 
# uso de post para poder enviar email de forma segura en el cuerpo de la peticion
@usuarios_root.post("/usuario/existente", response_model=dict, response_description="Verifica si el usuario existe en base a email")
async def comprobar_email_existente(data: dict, request: Request):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es requerido")
    
    # se comprueba si el email está registrado en la base de datos
    email_encontrado = await request.app.mongodb["usuarios"].find_one({"email": email})
    # Devuelve true si usuario no es none false en caso contrario
    email_existente = email_encontrado is not None
    
    return {"email_existente": email_existente}     
 
#endpoint que registrara al usuario con email sin verificar
@usuarios_root.post("/registro", response_model=UsuarioRegistroResponseModel, response_description="Registra al usuario")
async def registrar_usuario(usuario: PostUsuarioModel, request: Request):
    try:
        #paso a formato json el usuario y hago hash a su pass antes de insertarlo en bbdd
        usuario=jsonable_encoder(usuario)
        password=usuario["hashed_password"]
        nueva_password=hash_password(password)
        usuario["hashed_password"]=nueva_password
        
        #inserto documento usuario en su coleccion y obtengo la referencia del documento recien creado
        ref_nuevo_usuario = await request.app.mongodb["usuarios"].insert_one(usuario)
        usuario_registrado = await request.app.mongodb["usuarios"].find_one({"_id": ref_nuevo_usuario.inserted_id})
        
        id_usu = str(ref_nuevo_usuario.inserted_id)
        
        #creo un token para el usuario y lo inserto usando el id del documento extraido a partir de referencia
        token=crear_token_verificacion(id_usu)
        token_data=jsonable_encoder(token)
        
        ref_nuevo_token = await request.app.mongodb["tokens"].insert_one(token_data)
        token_insertado = await request.app.mongodb["tokens"].find_one({"_id": ref_nuevo_token.inserted_id})
        
        #para JSONResponse
        usuario_model=serializar_usuario(usuario_registrado)
        token_model=serializar_token(token_insertado)
        
        #envio email de verificacion al email del usuario junto al token_data con formato TokenModel para verificacion
        try:
            enviar_email_verificacion(usuario_model.email, token_model)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al enviar el email: {str(e)}")

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=UsuarioRegistroResponseModel(usuario=usuario_model, token=token_model).model_dump())
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")
    
#endpoint que verificara usuario en base a token recibido, uso de get porque la seguridad del token permite su uso en url
@usuarios_root.get("/usuario/verificar", response_model=TokenModel, response_description="Verifica email de usuario")
async def verificar_usuario(request: Request, token: str = Query(..., description="Token JWT de verificación")):
    try:
        # Verifico y descodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]

        #verifico el email del usuario en la bbdd
        resultado_update = await request.app.mongodb["usuarios"].update_one(
            {"_id": ObjectId(id_usuario)},   
            {"$set": {"email_verificado": True}}
        )
        #en caso de que no se de la update genero excepcion
        if resultado_update.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado o ya verificado.")

        # elimino el token de verificacion y creo otro para inicio de sesion por seguridad
        resultado_delete = await request.app.mongodb["tokens"].find_one_and_delete({"token_jwt": token})
        #si no se da el delete genero excepcion
        if not resultado_delete:
            raise HTTPException(status_code=400, detail="Token inválido o ya eliminado.")

        nuevo_token=crear_token_inicio_sesion(id_usuario)
        nuevo_token_json=jsonable_encoder(nuevo_token)
        ref_nuevo_token = await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
        token_insertado = await request.app.mongodb["tokens"].find_one({"_id": ref_nuevo_token.inserted_id})
        
        #para JSONResponse
        token_model=serializar_token(token_insertado)
        #CAMBIAR LA RESPONSE MODEL A DICT Y EL RETURN A UN DICT CON LA URL
        deep_link = f"myapp://login?token={token_insertado['token_jwt']}"
        #return {"deep_link": deep_link}
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=token_model.model_dump())
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
#end point que comprobara estado de verificacion de usuario tras registro NO LO USO SI DEEP LINK 
@usuarios_root.post("/usuario/estado", response_model=dict, response_description="Verifica si el usuario esta verificado en base a email")
async def comprobar_estado_usuario(data: dict, request: Request):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es requerido")
    
    # se comprueba si el email está registrado en la base de datos
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
    
    email_verificado = usuario.get("email_verificado", False)   
         
    return {"email_verificado": email_verificado} 
 
#end point que creara nuevo token tras validar los datos recibidos mediante comprobaciones 
@usuarios_root.post("/usuario/login", response_model=dict, response_description="Crea nuevo token para el usuario")
#recibo email y pass, encuentro email contrasto con pass, si correcto
async def iniciar_sesion(data: dict, request: Request):
    email=data.get("email")
    password=data.get("password")
    
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe ese usuario")

    usuario_serializado=serializar_usuario(usuario)
    
    if not usuario.get("email_verificado", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email no verificado")

    if not verify_password(password, usuario_serializado.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")

    try:
        resultado_delete = await request.app.mongodb["tokens"].find_one_and_delete({"id_usu": usuario_serializado.id_usuario})
        
        if not resultado_delete:
            raise HTTPException(status_code=400, detail="Token inválido o ya eliminado.")

        nuevo_token=crear_token_inicio_sesion(usuario_serializado.id_usuario)
        nuevo_token_json=jsonable_encoder(nuevo_token)
        
        await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": nuevo_token.token_jwt})
      
    
    