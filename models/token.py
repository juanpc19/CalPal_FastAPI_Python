import datetime
from pydantic import BaseModel

class TokenModel(BaseModel):
    id_usu: str
    token: str 
    fecha_creacion: datetime   
    fecha_expiracion: datetime   