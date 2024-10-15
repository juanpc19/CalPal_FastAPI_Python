from pydantic import BaseModel

class ConsejoModel(BaseModel):
    id_consejo: str
    tema: str
    titulo: str
    contenido: str
    