from pydantic import BaseModel, Field

class ConsejoModel(BaseModel):
    id_consejo: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    tema: str
    titulo: str
    contenido: str
    
    class Config: 
        populate_by_name = True
    