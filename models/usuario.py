from pydantic import BaseModel, Field
from typing import Dict, Optional #para definir tipo de lista, util en model validation con pydantic
from models.token import TokenModel

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
                "email": "example@example.com",
                "email_verificado": False,
                "hashed_password": "hashed_password",
                "objetivos": {"calorias": 2500, "proteinas": 150.0, "carbohidratos": 200.0, "grasas": 100.0},
                "comidas": {"Desayuno": 1, "Almuerzo": 2, "Cena": 3},
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }

#modelo para insercion inicial (id dada por mongodb)
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
                "email": "example@example.com",
                "email_verificado": False,
                "hashed_password": "pasS123.",
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
    email_verificado: bool = None
    hashed_password: Optional[str] = None
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
                "email_verificado": False,
                "hashed_password": "hashed_password",
                "objetivos": {"calorias": 2500, "proteinas": 150.0, "carbohidratos": 200.0, "grasas": 100.0},
                "comidas": {"Desayuno": 1, "Almuerzo": 2, "Cena": 3},
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            }
        }

#modelo para usar en content de JSONResponse al registrar usuario        
class UsuarioRegistroResponseModel(BaseModel):
    usuario: UsuarioModel
    token: TokenModel
    
    class Config: 
        json_schema_extra = {
            "usuario": {
                "id_usuario": "67277c51ae7c0124f4494dbb",
                "hashed_password": "$2b$12$YzhHDpaU0syeubGQIMLyQuVe3zoa.zp1H3AniVAyAKvnCf1HDDBC.",
                "email": "example@example.com",
                "email_verificado": False,
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
                "sexo": "Masculino",
                "altura": 175,
                "peso": 75.5,
                "edad": 30,
                "nivel_actividad": 1
            },
            "token": {
                "id_token": "d12312da8da",
                "id_usu": "67277c51ae7c0124f4494dbb",
                "token_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzI3N2M1MWFlN2MwMTI0ZjQ0OTRkYmIiLCJpYXQiOjE3MzA2NDA5NzcsImV4cCI6MTczMDcyNzM3N30.Vais0nOw2JjEyf2Vzs17Lrykb5QhCV34Zod-CcnNMgY"
            }
        }
        
