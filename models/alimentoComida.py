from pydantic import BaseModel

class alimentoComidaModel(BaseModel):
    id_alimento: str
    id_com: str
    nombre: str
    tipo: str 
    cantidad_gramos: int
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str