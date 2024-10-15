from pydantic import BaseModel
from models.token import TokenModel
from typing import List, Dict #para definir tipo de lista, util en model validation con pydantic


class UsuarioModel(BaseModel):
    id_usuario: str
    password_hash: str
    email: str
    objetivos: Dict[str, float]
    comidas: Dict[int, str]
    sexo: str
    altura: int
    peso: float
    edad: int
    nivel_actividad: int
    