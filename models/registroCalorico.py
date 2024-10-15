from datetime import date
from pydantic import BaseModel

class RegistroDiarioModel(BaseModel):
    id_registro: str
    id_usu: str
    fecha: date
    peso: float
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float