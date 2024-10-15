from fastapi import APIRouter
from models.alimentoBase import alimentoBaseModel
from config.config import alimentos_base_collection


alimento_base_root = APIRouter()

#post request

@alimento_base_root.post("/nuevo/alimentoBase")
def pruebaSubida(doc: alimentoBaseModel):
    #doc = doc.to_dict()
    doc = dict(doc)
    
    #tengo que subir los archivos desde el json aqui a traves de api 
    alimentos_base_collection.insert_one()
    #alimentos_base_collection.insert_many()
    
    
def pruebaSubida(doc: list[alimentoBaseModel]):  # Cambia a lista para recibir múltiples documentos
    # Convertir los objetos a diccionarios
    docs_dicts = [dict(d) for d in doc]  # Esto convierte cada objeto a un diccionario
    
    # Insertar múltiples documentos en la colección
    result = alimentos_base_collection.insert_many(docs_dicts)
    
    return {
        "status": "success",
        "inserted_ids": result.inserted_ids  # Retorna los IDs de los documentos insertados
    }