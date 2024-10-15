from pydantic import BaseModel

class alimentoBaseModel(BaseModel):
    id_alimento: str
    nombre: str
    tipo: str 
    cantidad_gramos: int
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str