from typing import List
from pydantic import BaseModel, Field
from models.alimentoComida import AlimentoComidaModel

#model para peticiones get
class ComidaRegistroModel(BaseModel):
    id_comida: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    id_reg: str
    orden: int
    nombre: str
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_comida": "1abc45452sf57...",  
                "id_reg": "xr23x2xsf57...",  
                "orden": 1,
                "nombre": "Desayuno",
                "calorias": 349.0,
                "proteinas": 36.1,
                "carbohidratos": 220.8,
                "grasas": 6.3
            }
        }
        
#model para peticiones post
class PostComidaRegistroModel(BaseModel):
    id_reg: str
    orden: int
    nombre: str
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_reg": "xr23x2xsf57...",  
                "orden": 1,
                "nombre": "Desayuno",
                "calorias": 349.0,
                "proteinas": 36.1,
                "carbohidratos": 220.8,
                "grasas": 6.3
            }
        }
        
#model para peticiones patch
class UpdateComidaRegistroModel(BaseModel):
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
            json_schema_extra = {
            "example": {
                "calorias": 349.0,
                "proteinas": 36.1,
                "carbohidratos": 220.8,
                "grasas": 6.3
            }
        }
            
#model usado como parte de un modelo de registroDiario usado en peticion get         
class ComidaConAlimentosModel(BaseModel):
    id_comida: str = Field(alias="_id")  
    id_reg: str
    orden: int
    nombre: str
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    alimentos: List[AlimentoComidaModel]  
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_comida": "1abc45452sf57...",  
                "id_reg": "xr23x2xsf57...",  
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
        }