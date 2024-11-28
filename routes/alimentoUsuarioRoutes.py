from fastapi import APIRouter, Request
from models.alimentoUsuario import AlimentoUsuarioModel

alimento_usuario_root = APIRouter()

@alimento_usuario_root.post("/nuevo/alimentoUsuario", response_description="Añade un nuevo alimento de usuario")

def pruebaSubida(doc: AlimentoUsuarioModel, request: Request):
    alimentos_usuarios_collection=request.app.mongodb["alimentos_base"]

    #doc = doc.to_dict()
    doc = dict(doc)
    
    #tengo que subir los archivos desde el json aqui a traves de api 
    alimentos_usuarios_collection.insert_one()
    #alimentos_base_collection.insert_many()
    
    
def pruebaSubida(doc: list[AlimentoUsuarioModel], request: Request):  # Cambia a lista para recibir múltiples documentos
    alimentos_usuarios_collection=request.app.mongodb["alimentos_base"]

    # Convertir los objetos a diccionarios
    docs_dicts = [dict(d) for d in doc]  # Esto convierte cada objeto a un diccionario
    
    # Insertar múltiples documentos en la colección
    result = alimentos_usuarios_collection.insert_many(docs_dicts)
    
    return {
        "status": "success",
        "inserted_ids": result.inserted_ids  # Retorna los IDs de los documentos insertados
    }