from pydantic import BaseModel, Field

class AlimentoUsuarioModel(BaseModel):
    id_alimento: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    id_usu: str
    nombre: str
    tipo: str 
    cantidad_gramos: int
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_alimento": "6710f557...",   
                "id_usu": "121212sf57...",  
                "nombre": "Plátano",
                "tipo": "Fruta",
                "cantidad_gramos": 100,
                "calorias": 89.0,
                "proteinas": 1.1,
                "carbohidratos": 22.8,
                "grasas": 0.3,
                "info_adicional": "Proporciona energía rápida, mejora la digestión y ayuda a regular la presión arterial. Rico en potasio, vitamina B6, vitamina C y fibra."
            }
        }
        
class PostAlimentoUsuarioModel(BaseModel):
    id_usu: str
    nombre: str
    tipo: str 
    cantidad_gramos: int
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str
    
    class Config: 
        json_schema_extra = {
            "example": {
                "id_usu": "121212sf57...",  
                "nombre": "Plátano",
                "tipo": "Fruta",
                "cantidad_gramos": 100,
                "calorias": 89.0,
                "proteinas": 1.1,
                "carbohidratos": 22.8,
                "grasas": 0.3,
                "info_adicional": "Proporciona energía rápida, mejora la digestión y ayuda a regular la presión arterial. Rico en potasio, vitamina B6, vitamina C y fibra."
            }
        }