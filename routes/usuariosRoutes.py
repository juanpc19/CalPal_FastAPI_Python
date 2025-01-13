import os
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Header, Query, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
from models.usuario import UsuarioModel, PostUsuarioModel, UpdateUsuarioModel, UsuarioObjetivosComidasModel, UsuarioDatosModel
from serializers.usuario import serializar_usuario, serializar_usuario_objetivos_comidas, serializar_usuario_datos
from serializers.token import serializar_token
from utils.fileUtils import crear_token_verificacion, crear_token_inicio_sesion, enviar_email_verificacion, enviar_email_cambiar_contrasena, hash_password, verify_password, extraer_token_header_authorization

usuarios_root=APIRouter()
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#endpoint para comprobar existencia de usuario e base a email, se usara cuando el usuario introduzca email, en registro o nuevo inicio sesion
# uso de post para poder enviar email de forma segura en el cuerpo de la peticion
@usuarios_root.post("/usuarios/existe", response_model=dict, response_description="Verifica si el usuario existe en base a email")
async def comprobar_email_existente(data: dict, request: Request):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es requerido")
    
    # se comprueba si el email está registrado en la base de datos
    email_encontrado = await request.app.mongodb["usuarios"].find_one({"email": email})
    # Devuelve true si usuario no es none false en caso contrario
    email_existente = email_encontrado is not None
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"email_existente": email_existente})     
 
#endpoint que registrara al usuario con email sin verificar, 
# uso de post para poder enviar datos de forma segura en el cuerpo de la peticion
@usuarios_root.post("/usuarios/registro", response_model=dict, response_description="Registra al usuario")
async def registrar_usuario(usuario: PostUsuarioModel, request: Request):
#paso a formato json el usuario y hago hash a su pass antes de insertarlo en bbdd
    usuario_json=jsonable_encoder(usuario)
    password=usuario_json["hashed_password"]
    nueva_password=hash_password(password)
    usuario_json["hashed_password"]=nueva_password
    
    #inserto documento usuario en su coleccion y obtengo la referencia del documento recien creado
    ref_nuevo_usuario = await request.app.mongodb["usuarios"].insert_one(usuario_json)
    usuario_registrado = await request.app.mongodb["usuarios"].find_one({"_id": ref_nuevo_usuario.inserted_id})
    
    id_usu = str(ref_nuevo_usuario.inserted_id)
    
    #creo un token para el usuario y lo inserto usando el id del documento extraido a partir de referencia
    token=crear_token_verificacion(id_usu)
    token_data=jsonable_encoder(token)
    
    ref_nuevo_token = await request.app.mongodb["tokens"].insert_one(token_data)
    token_insertado = await request.app.mongodb["tokens"].find_one({"_id": ref_nuevo_token.inserted_id})
    
    #serializo para JSONResponse
    usuario_model=serializar_usuario(usuario_registrado)
    token_model=serializar_token(token_insertado)
    
    #envio email de verificacion al email del usuario junto al token para verificacion
    try:
        enviar_email_verificacion(usuario_model.email, token_model.token_jwt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al enviar el email: {str(e)}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"mensaje": "Revisa tu email para completar el registro"})    
        
#endpoint que verificara usuario en base a token recibido,
# uso de get porque la seguridad del token permite su uso en url, datos como params
@usuarios_root.get("/usuarios/verificacion", response_model=dict, response_description="Verifica email de usuario")
async def verificar_usuario(request: Request, token: str = Query(..., description="Token JWT de verificación")):
    try:
        # Verifico y descodifico el token, de estar caducado generara excepcion ExpiredSignatureError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    #verifico el email del usuario en la bbdd
    resultado_update = await request.app.mongodb["usuarios"].update_one(
        {"_id": ObjectId(id_usuario)},   
        {"$set": {"email_verificado": True}}
    )
    #en caso de que no se de la update genero excepcion
    if resultado_update.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado o ya verificado.")

    # elimino el token de verificacion y creo otro para inicio de sesion por seguridad
    resultado_delete = await request.app.mongodb["tokens"].find_one_and_delete({"token_jwt": token})
    #si no se da el delete genero excepcion
    if not resultado_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya eliminado.")

    nuevo_token=crear_token_inicio_sesion(id_usuario)
    nuevo_token_json=jsonable_encoder(nuevo_token)
    ref_nuevo_token = await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
    token_insertado = await request.app.mongodb["tokens"].find_one({"_id": ref_nuevo_token.inserted_id})
    
    deep_link = f"myapp://login?token={token_insertado['token_jwt']}"
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "deep_link": deep_link
        }
    )

#end point que comprobara estado de verificacion de usuario tras registro NO LO USO SI DEEP LINK 
@usuarios_root.post("/usuarios/estado", response_model=dict, response_description="Verifica si el usuario esta verificado en base a email")
async def comprobar_estado_usuario(data: dict, request: Request):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es requerido")
    
    # se comprueba si el email está registrado en la base de datos
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
    if not usuario:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    email_verificado = usuario.get("email_verificado", False)   
         
    return JSONResponse(status_code=status.HTTP_200_OK, content={"email_verificado": email_verificado}) 
 
#end point que creara nuevo token para el usuario tras validar los datos recibidos mediante comprobaciones 
# uso de post para poder enviar datos de forma segura en el cuerpo de la peticion
@usuarios_root.post("/usuarios/login", response_model=dict, response_description="Crea nuevo token para el usuario")
async def crear_nueva_sesion(data: dict, request: Request):
    email=data.get("email")
    password=data.get("password")
    
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe ese usuario")

    usuario_serializado=serializar_usuario(usuario)
    if not usuario.get("email_verificado", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email no verificado")

    hash_pass_cadena=str(usuario_serializado.hashed_password)
    if not verify_password(password, hash_pass_cadena):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")
    
    resultado_delete = await request.app.mongodb["tokens"].delete_many({"id_usu": usuario_serializado.id_usuario})
    if not resultado_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya eliminado.")

    nuevo_token=crear_token_inicio_sesion(usuario_serializado.id_usuario)
    nuevo_token_json=jsonable_encoder(nuevo_token)
    
    await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
 
    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": nuevo_token.token_jwt})

#endpoint para reenviar email de verificacion en caso de caducar el token, se usara tras comprobar existencia usuario y estado verificacion = false desde app
# uso de post para poder enviar datos de forma segura en el cuerpo de la peticion
@usuarios_root.post("/usuarios/reenvio-email", response_model=dict, response_description="Reenvia email con link para verificacion")
async def reenviar_link_email(data: dict, request: Request):

    email=data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es obligatorio.")
    
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe.")
    
    usuario_serializado=serializar_usuario(usuario)
    
    if usuario_serializado.email_verificado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está verificado.")

    resultado_delete = await request.app.mongodb["tokens"].find_one_and_delete({"id_usu": usuario_serializado.id_usuario})
    if not resultado_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya eliminado.")
    
    nuevo_token=crear_token_verificacion(usuario_serializado.id_usuario)
    nuevo_token_json=jsonable_encoder(nuevo_token)
    ref_nuevo_token = await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
    token_insertado = await request.app.mongodb["tokens"].find_one({"_id": ref_nuevo_token.inserted_id})
    
    #para JSONResponse
    token_model=serializar_token(token_insertado)
    
    #envio email de verificacion al email del usuario junto al token_data con formato TokenModel para verificacion
    try:
        enviar_email_verificacion(email, token_model.token_jwt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al enviar el email: {str(e)}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Revisa tu email para completar el registro"})
    
#endpoint que genera un token de verificación y lo envía por correo al usuario, para permitirle cambiar su contraseña 
@usuarios_root.post("/usuarios/cambio-contrasena", response_model=dict, response_description="Envia correo con link para cambio de contraseña")
async def cambiar_contrasena(data: dict, request: Request):
    email=data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email es obligatorio.")
        
    usuario = await request.app.mongodb["usuarios"].find_one({"email": email})
        
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe.")
            
    usuario_model=serializar_usuario(usuario)
                
    if not usuario_model.email_verificado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email no está verificado.")
    
    nuevo_token=crear_token_verificacion(usuario_model.id_usuario)  
    nuevo_token_json=jsonable_encoder(nuevo_token)
    await request.app.mongodb["tokens"].insert_one(nuevo_token_json)
    
    try:
        enviar_email_cambiar_contrasena(email, nuevo_token.token_jwt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al enviar el correo:{e}")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Correo de cambio de contraseña enviado."})

#endpoint que verifica el token recibido y genera un deep link para redirigir a la aplicación.
@usuarios_root.get("/usuarios/redireccion-cambio-contrasena", response_model=dict, response_description="Redirige a ventana de cambio de contraseña")
async def redirigir_cambio_contrasena(request: Request, token: str = Query(..., description="Token JWT para cambio de contraseña")):
    try:
        # Verifico y decodifico el token
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    # Generar un deep link para la app
    deep_link = f"myapp://nueva-contrasena?token={token}"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "deep_link": deep_link
        }
    )
        
   

#endpoint que cambiara la contraseña del usuario
@usuarios_root.patch("/usuarios/nueva-contrasena", response_model=dict, response_description="Cambia la contraseña del usuario")
async def establecer_nueva_contrasena(data: dict, request: Request):
    token_jwt= data.get("token")
    password = data.get("password")
    
    if not token_jwt or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token y contraseña son obligatorios.")
    
    # Verifico y descodifico el token, de estar caducado generara excepcion ExpiredSignatureError
    try:
        payload = jwt.decode(token_jwt, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.") 
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token_jwt})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
        
    hashed_password=hash_password(password)
    resultado=await request.app.mongodb["usuarios"].update_one({"_id": ObjectId(id_usuario)}, {"$set": {"hashed_password": hashed_password}})
    if resultado.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario especificado no existe.")
   
    resultado_delete = await request.app.mongodb["tokens"].find_one_and_delete({"token_jwt": token_jwt})
    if not resultado_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o ya eliminado.")
     
    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "contraseña cambiada con exito"})

#endpoint que devolvera los datos del usuario asociado al token recibido
@usuarios_root.get("/usuarios/perfil-completo", response_model=UsuarioModel, response_description="Obtiene los datos del perfil usuario")
async def obtener_datos_usuario(request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    try:
        token=extraer_token_header_authorization(authorization)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]#extraigo el id del usuario del token    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")

    usuario = await request.app.mongodb["usuarios"].find_one({"_id":ObjectId(id_usuario)})
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    usuario_serializado=serializar_usuario(usuario)
    
    return usuario_serializado

#endpoint que devolvera los datos del usuario asociado al token recibido
@usuarios_root.get("/usuarios/perfil-objetivos-comidas", response_model=UsuarioObjetivosComidasModel, response_description="Obtiene los datos del perfil usuario")
async def obtener_datos_usuario(request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    token=extraer_token_header_authorization(authorization)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]#extraigo el id del usuario del token    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")

    usuario = await request.app.mongodb["usuarios"].find_one({"_id":ObjectId(id_usuario)})
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    usuario_serializado=serializar_usuario_objetivos_comidas(usuario)
    
    return usuario_serializado

#endpoint que devolvera los datos del usuario asociado al token recibido
@usuarios_root.get("/usuarios/perfil-datos", response_model=UsuarioDatosModel, response_description="Obtiene los datos del perfil usuario")
async def obtener_datos_usuario(request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    token=extraer_token_header_authorization(authorization)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]#extraigo el id del usuario del token    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")

    usuario = await request.app.mongodb["usuarios"].find_one({"_id":ObjectId(id_usuario)})
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    usuario_serializado=serializar_usuario_datos(usuario)
    
    return usuario_serializado

#endpoint que actualiza datos del perfil del usuario, recibe datos a insertar en usuario e id para localizarlo en bbdd
@usuarios_root.patch("/usuarios/actualizacion-perfil", response_model=dict, response_description="Actualiza los datos del usuario")
async def actualizar_datos_usuario(usuario: UpdateUsuarioModel, request: Request, authorization: str = Header(..., description="Token JWT para autorización")):
    token=extraer_token_header_authorization(authorization)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload["sub"]#extraigo el id del usuario del token    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido.")
    
    token_encontrado = await request.app.mongodb["tokens"].find_one({"token_jwt": token})
    if not token_encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token no encontrado.")
    
    usuario_dict = usuario.model_dump(exclude_unset=True)#quita campos vacios de la actualizacion
 
    # Compruebo si el usuario existe antes de actualizar
    usuario_existente = await request.app.mongodb["usuarios"].find_one({"_id": ObjectId(id_usuario)})
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    resultado_update = await request.app.mongodb["usuarios"].update_one({"_id": ObjectId(id_usuario)}, {"$set": usuario_dict})
    
    # si no hubo modificaciones pero el usuario existe
    if resultado_update.modified_count == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Cambios no realizados, los datos no son diferentes."})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mensaje": "Perfil actualizado correctamente"})
