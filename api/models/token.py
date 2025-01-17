from pydantic import BaseModel, Field

#model usado por funcion que creara el token se usara en peticiones post
class TokenBasicModel(BaseModel):
    id_usu: str
    token_jwt: str 
    
    class Config: 
        json_schema_extra = {
            "example": {
                "id_usu": "605c72e9f7f9f2051c5f8b77",  
                "token_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

#model que se usara en peticiones get
class TokenModel(BaseModel):
    id_token: str = Field(alias="_id")
    id_usu: str
    token_jwt: str 
    
    class Config: 
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_token": "d12312da8da",
                "id_usu": "605c72e9f7f9f2051c5f8b77",  
                "token_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    

