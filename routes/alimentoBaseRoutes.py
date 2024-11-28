from typing import List
from fastapi import APIRouter, HTTPException, Request
from models.alimentoBase import AlimentoBaseModel
from serializers.alimentoBase import serializar_alimentos_base, serializar_alimento_base
from bson import ObjectId

alimento_base_root = APIRouter()

@alimento_base_root.get("/alimentosBase", response_model=List[AlimentoBaseModel], response_description="Obtiene todos los alimentos base")
async def obtener_alimentos_base(request: Request):
   
    respuesta = await request.app.mongodb["alimentos_base"].find().to_list(length=100)
    
    alimentos_base=serializar_alimentos_base(respuesta)
    
    return alimentos_base

#6710f557793494a80410b0a1     para testear el by id 
@alimento_base_root.get("/alimentosBase/{_id}", response_model=AlimentoBaseModel, response_description="Devuelve el alimento base seleccionado")
async def alimento_base_seleccionado(_id: str, request: Request):
     
    respuesta = await request.app.mongodb["alimentos_base"].find_one({"_id": ObjectId(_id)})
    
    if respuesta is not None:
        alimento_base = serializar_alimento_base(respuesta)
        return alimento_base   
    
    raise HTTPException(status_code=404, detail="Alimento no encontrado")

   
