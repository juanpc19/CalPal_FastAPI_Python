from datetime import date
from typing import List
from pydantic import BaseModel, Field
from models.comidaRegistro import ComidaRegistroModel

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
        json_schema_extra = {
            "example": {
                "id_registro": "1abc45452sf57...",  
                "id_usu": "xr23x2xsf5dada7...",  
                "fecha": "2024-12-24",
                "peso": 70.0,
                "calorias": 3490.0,
                "proteinas": 200.1,
                "carbohidratos": 970.8,
                "grasas": 69.3
            }
        }
        
class PostRegistroDiarioModel(BaseModel):
    id_usu: str
    fecha: date
    peso: float
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_usu": "xr23x2xsf5dada7...",  
                "fecha": "2024-12-24",
                "peso": 70.0,
                "calorias": 3490.0,
                "proteinas": 200.1,
                "carbohidratos": 970.8,
                "grasas": 69.3
            }
        }
        
class UpdateRegistroDiarioModel(BaseModel):
    peso: float
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "peso": 70.0,
                "calorias": 3490.0,
                "proteinas": 200.1,
                "carbohidratos": 970.8,
                "grasas": 69.3
            }
        }
        
class RegistroDiarioComidasModel(BaseModel):
    registro: RegistroDiarioModel
    comidas: List[ComidaRegistroModel]
    
    class Config: 
        json_schema_extra = {
            "example": {
                "registro": {
                    "_id": "reg123",
                    "id_usu": "user456",
                    "fecha": "2024-12-24",   
                    "peso": 70.5,
                    "calorias": 2200,
                    "proteinas": 150,
                    "carbohidratos": 250,
                    "grasas": 70
                },
                "comidas": [
                    {
                        "_id": "com123",
                        "nombre": "Desayuno",
                        "calorias": 500,
                        "proteinas": 30,
                        "carbohidratos": 50,
                        "grasas": 15
                    },
                    {
                        "_id": "com124",
                        "nombre": "Cena",
                        "calorias": 700,
                        "proteinas": 40,
                        "carbohidratos": 60,
                        "grasas": 25
                    }
                ]
            }
        }