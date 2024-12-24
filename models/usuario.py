from pydantic import BaseModel, Field
from typing import Dict, Optional #para definir tipo de lista, util en model validation con pydantic

#modelo para lectura como get
class UsuarioModel(BaseModel):
    id_usuario: str = Field(alias="_id")#field para poder igualar/relacionar _id de bbdd a campo id_alimento
    hashed_password: str
    email: str
    email_verificado: bool
    objetivos: Dict[str, float]
    comidas: Dict[str, int]
    sexo: str
    altura: int
    peso: float
    edad: int
    nivel_actividad: int
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_usuario": "d12312da8da",
                "hashed_password": "hashed_password",
                "email": "example@example.com",
                "email_verificado": False,
                "objetivos": {"calorias": 2500, "proteinas": 150.0, "carbohidratos": 200.0, "grasas": 100.0},
                "comidas": {"Desayuno": 1, "Almuerzo": 2, "Cena": 3},
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }

#modelo para insercion inicial (id dada por mongodb), campos opcionales actuaran como default aqui en lugar de la app
class PostUsuarioModel(BaseModel):
    hashed_password: str
    email: str
    email_verificado: bool
    objetivos: Optional[Dict[str, float]] = {}
    comidas: Optional[Dict[str, int]] = {}
    sexo: Optional[str] = "Masculino"
    altura: Optional[int] = 175
    peso: Optional[float] = 75.5
    edad: Optional[int] = 30
    nivel_actividad: Optional[int] = 1
    
    class Config: 
        json_schema_extra = {
            "example": {
                "hashed_password": "pasS123.",
                "email": "juanpesca19@gmail.com",
                "email_verificado": False,
                "objetivos": {"calorias": 2500, "proteinas": 150.0, "carbohidratos": 200.0, "grasas": 100.0},
                "comidas": {"Desayuno": 1, "Almuerzo": 2, "Cena": 3},
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }
        
        
#modelo para updates
class UpdateUsuarioModel(BaseModel):
    objetivos: Optional[Dict[str, float]] = None
    comidas: Optional[Dict[str, int]] = None
    sexo: Optional[str] = None
    altura: Optional[int] = None
    peso: Optional[float] = None
    edad: Optional[int] = None
    nivel_actividad: Optional[int] = None
    
    class Config: 
        json_schema_extra = {
            "example": {
                "objetivos": {"calorias": 2500, "proteinas": 150.0, "carbohidratos": 200.0, "grasas": 100.0},
                "comidas": {"Desayuno": 1, "Almuerzo": 2, "Cena": 3},
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }

class UsuarioObjetivosComidasModel(BaseModel):
    objetivos: Dict[str, float]
    comidas: Dict[str, int]
    
    class Config: 
        json_schema_extra = {
            "usuario": {
                "objetivos": {
                    "calorias": 2500.0,
                    "proteinas": 150.0,
                    "carbohidratos": 200.0,
                    "grasas": 100.0
                },
                "comidas": {
                    "Desayuno": 1,
                    "Almuerzo": 2,
                    "Cena": 3
                },
        
            }
        }
   
class UsuarioDatosModel(BaseModel):
    sexo: str
    altura: int
    peso: float
    edad: int
    nivel_actividad: int
    
    class Config: 
        json_schema_extra = {
            "usuario": {
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }
   
