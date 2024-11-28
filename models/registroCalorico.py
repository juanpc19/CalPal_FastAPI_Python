from datetime import date
from pydantic import BaseModel, Field

class RegistroDiarioModel(BaseModel):
    id_registro: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    id_usu: str
    fecha: date
    peso: float
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True