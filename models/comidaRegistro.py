from pydantic import BaseModel, Field

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