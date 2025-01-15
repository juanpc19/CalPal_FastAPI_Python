from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from models.alimentoBase import AlimentoBaseModel
from serializers.alimentoBase import serializar_alimentos_base, serializar_alimento_base
from bson import ObjectId

alimentos_base_root = APIRouter()

@alimentos_base_root.get("/alimentos-base", response_model=List[AlimentoBaseModel], response_description="Obtiene todos los alimentos base")
async def obtener_alimentos_base(request: Request):
   
    lista_alimentos = await request.app.mongodb["alimentos_base"].find().to_list(length=100)
    
    alimentos_base_serializados=serializar_alimentos_base(lista_alimentos)
    
    return alimentos_base_serializados

@alimentos_base_root.get("/alimentos-base/{_id}", response_model=AlimentoBaseModel, response_description="Devuelve el alimento base seleccionado")
async def alimento_base_seleccionado(_id: str, request: Request):
     
    alimento = await request.app.mongodb["alimentos_base"].find_one({"_id": ObjectId(_id)})
    
    if alimento is not None:
        alimentos_base_serializado = serializar_alimento_base(alimento)
        return alimentos_base_serializado   
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alimento no encontrado")

   
