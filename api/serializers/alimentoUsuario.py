from typing import List
from api.models.alimentoUsuario import AlimentoUsuarioModel

def serializar_alimento_usuario(doc) -> AlimentoUsuarioModel:
    return AlimentoUsuarioModel(
        id_alimento=str(doc["_id"]),
        id_usu=doc["id_usu"],
        nombre=doc["nombre"],
        tipo=doc["tipo"], 
        cantidad_gramos=doc["cantidad_gramos"],
        calorias=doc["calorias"],
        proteinas=doc["proteinas"],
        carbohidratos=doc["carbohidratos"],
        grasas=doc["grasas"],
        info_adicional=doc["info_adicional"]
    )
    
def serializar_alimentos_usuario(docs) -> List[AlimentoUsuarioModel]:
    return [serializar_alimento_usuario(doc) for doc in docs]