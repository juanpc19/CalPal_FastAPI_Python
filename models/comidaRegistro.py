from pydantic import BaseModel, Field

class ComidaRegistroModel(BaseModel):
    id_comida: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    id_reg: str
    idOrden: int
    nombre: str
    calorias: float
    proteinas: float
    carbohidratos: float
    grasas: float
    
    class Config: 
        populate_by_name = True