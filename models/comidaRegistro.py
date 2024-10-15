from pydantic import BaseModel

class ComidaRegistroModel(BaseModel):
    id_comida: str
    id_reg: str
    idOrden: int
    nombre: str
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    info_adicional: str