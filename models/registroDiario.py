from datetime import date
from typing import List
from pydantic import BaseModel, Field
from models.comidaRegistro import ComidaConAlimentosModel

#model para peticiones get
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
        
#model para peticiones post
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
        
#model para peticiones patch
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
 
#model para peticion get de un registroDiario con sus comidas y sus alimentos anidados
class RegistroConComidasConAlimentosModel(BaseModel):
    id_registro: str = Field(alias="_id")  # Identificador único del registro
    id_usu: str
    fecha: date
    peso: float
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    comidas: List[ComidaConAlimentosModel]  # Lista de comidas relacionadas con el registro
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_registro": "reg123",
                "id_usu": "user456",
                "fecha": "2024-12-24",
                "peso": 70.5,
                "calorias": 2200,
                "proteinas": 150,
                "carbohidratos": 250,
                "grasas": 70,
                "comidas": [
                    {
                        "id_comida": "1abc45452sf57...",
                        "orden": 1,
                        "nombre": "Desayuno",
                        "calorias": 349.0,
                        "proteinas": 36.1,
                        "carbohidratos": 220.8,
                        "grasas": 6.3,
                        "alimentos": [
                            {
                                "id_alimento": "6710f557...",
                                "nombre": "Plátano",
                                "tipo": "Fruta",
                                "cantidad_gramos": 100,
                                "calorias": 89.0,
                                "proteinas": 1.1,
                                "carbohidratos": 22.8,
                                "grasas": 0.3,
                                "info_adicional": "Proporciona energía rápida..."
                            },
                            {
                                "id_alimento": "6720f558...",
                                "nombre": "Huevo",
                                "tipo": "Proteína",
                                "cantidad_gramos": 50,
                                "calorias": 70.0,
                                "proteinas": 6.3,
                                "carbohidratos": 0.6,
                                "grasas": 5.0,
                                "info_adicional": "Rico en proteínas, vitamina D y colina..."
                            }
                        ]
                    }
                ]
            }
        }
        
               