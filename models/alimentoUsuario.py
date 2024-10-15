from pydantic import BaseModel

class alimentoUsuarioModel(BaseModel):
    id_alimento: str
    id_usu: str
    nombre: str
    tipo: str 
    cantidad_gramos: int
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str