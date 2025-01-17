import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header
import json
import jwt
import bcrypt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from api.models.token import TokenBasicModel

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
SENDGRID_API_KEY=os.getenv("SENDGRID_API_KEY")

#funcion que devuelve la contraseña con el hash realizado
def hash_password(password: str) -> str:
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(password,salt)
    return hashed_password.decode('utf-8')
          
#funcion para verificar contraseña decodificando el hash, devuelve true si coinciden
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Funcion generalizada para crear un token con tiempo de expiración personalizado y devolverlo junto a un id usuario en un token model
def crear_token(id_usu: str, minutos_expiracion: int) -> TokenBasicModel:
    fecha_creacion = datetime.now(timezone.utc)
    fecha_expiracion = fecha_creacion + timedelta(minutes=minutos_expiracion)
    payload = {
        "sub": id_usu,  
        "iat": fecha_creacion,  
        "exp": fecha_expiracion  
    }  
    token_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    token = TokenBasicModel(
        id_usu=id_usu,
        token_jwt=token_jwt,
    )

    return token

# Funcion para crear token de verificación de nuevo usuario o restablecer contraseña (expiración de 15 minutos)
def crear_token_verificacion(id_usu: str) -> TokenBasicModel:
    return crear_token(id_usu, 15)

# Funcion para crear token de inicio de sesion de usuario existente (expiración de 120 minutos)
def crear_token_inicio_sesion(id_usu: str) -> TokenBasicModel:
    return crear_token(id_usu, 120)

# funcion que extrae el token del Authorization del header 
def extraer_token_header_authorization(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")
    
    token=authorization.split(" ")[1]
    return token

#funcion para enviar email de verificacion, redirigira a app mediante implementacion de deep link
def enviar_email_verificacion(email: str, token_jwt: str):
    
    enlace_verificacion = f"http://127.0.0.1:8000/usuarios/verificacion?token={token_jwt}"#cambiar cuando suba API a servicio en nube   
    
    message = Mail(
        from_email="calpalfit@gmail.com", 
        to_emails=email,
        subject="Verifica tu correo",
        html_content=f"""
            <p>Haz clic en el siguiente enlace para verificar tu correo:</p>
            <p><a href='{enlace_verificacion}'>Verificar correo</a></p>
            <p>Este enlace estará disponible durante 15 minutos.</p>
        """
    )
    
    try:
        sg_api_key = SendGridAPIClient(SENDGRID_API_KEY)   
        sg_api_key.send(message)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        
        
#funcion para enviar link de cambio de contraseña, redirigira a app mediante implementacion de deep link
def enviar_email_cambiar_contrasena(email:str, token_jwt: str):
    
    enlace_cambio_pass = f"http://127.0.0.1:8000/usuarios/redireccion-cambio-contrasena?token={token_jwt}"#cambiar cuando suba API a servicio en nube
    
    message = Mail(
        from_email="calpalfit@gmail.com", 
        to_emails=email,
        subject="Cambio de contraseña",
        html_content=f"""
            <p>Haz clic en el siguiente enlace para confirmar tu identidad y te redigiremos a la app para cambiar tu contraseña:</p>
            <p><a href='{enlace_cambio_pass}'>Cambiar contraseña</a></p>
            <p>Este enlace estará disponible durante 15 minutos.</p>
        """
    )
    
    try:
        sg_api_key = SendGridAPIClient(SENDGRID_API_KEY)   
        sg_api_key.send(message)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    