import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header
import json
import jwt
import bcrypt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.token import TokenBasicModel, TokenModel

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
SENDGRID_API_KEY=os.getenv("SENDGRID_API_KEY")


#funcion que lee json
def leerFichero(nombreFichero):
    archivo = open(nombreFichero, "r", encoding="utf-8") 
    objetos = json.load(archivo)
    archivo.close()
    return objetos

#funcion que escribe un json
def escribeFichero(nombreFichero, objetos):
    archivo = open(nombreFichero, "w", encoding="utf-8")
    json.dump(objetos,archivo,ensure_ascii=False,indent=4)
    archivo.close()

#funcion para hacer hash a una contraseña
def hash_password(password: str) -> str:
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(password,salt)
    return hashed_password.decode('utf-8')
          
#funcion para verificar contraseña descodificando el hash, devuelve true si coninciden
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Funcion generalizada para crear un token con tiempo de expiración personalizado y devolverlo junto a un id usuario en un token model
def crear_token(id_usu: str, horas_expiracion: int) -> TokenBasicModel:
    fecha_creacion = datetime.now(timezone.utc)
    fecha_expiracion = fecha_creacion + timedelta(hours=horas_expiracion)
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

# Funcion para crear token de verificación de nuevo usuario (expiración de 24 horas)
def crear_token_verificacion(id_usu: str) -> TokenBasicModel:
    return crear_token(id_usu, 1)

# Funcion para crear token de verificación de usuario existente (expiración de 5 horas)
def crear_token_inicio_sesion(id_usu: str) -> TokenBasicModel:
    return crear_token(id_usu, 5)

# funcion que extrae el token JWT del Authorization del encabezado 
async def extraer_token_header(authorization: str = Header(...)):
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido.")
    return authorization.split(" ")[1]

#funcion para enviar email de verificacion
def enviar_email_verificacion(email: str, token: TokenModel):
    
    enlace_verificacion = f"http://127.0.0.1:8000/usuarios/verificar?token={token.token_jwt}"   
    
    message = Mail(
        from_email="calpalfit@gmail.com", 
        to_emails=email,
        subject="Verifica tu correo",
        html_content=f"""
            <p>Haz clic en el siguiente enlace para verificar tu correo:</p>
            <p><a href='{enlace_verificacion}'>Verificar correo</a></p>
            <p>Este enlace estará disponible durante 1 hora.</p>
        """
    )
    
    try:
        sg_api_key = SendGridAPIClient(SENDGRID_API_KEY)   
        sg_api_key.send(message)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")