from typing import List
from models.alimentoBase import AlimentoBaseModel

def serializar_alimento_base(doc) -> AlimentoBaseModel:
    return AlimentoBaseModel(
        id_alimento=str(doc["_id"]),
        nombre=doc["nombre"],
        tipo=doc["tipo"], 
        cantidad_gramos=doc["cantidad_gramos"],
        calorias=doc["calorias"],
        proteinas=doc["proteinas"],
        carbohidratos=doc["carbohidratos"],
        grasas=doc["grasas"],
        info_adicional=doc["info_adicional"]
    )
    
def serializar_alimentos_base(docs) -> List[AlimentoBaseModel]:
    return [serializar_alimento_base(doc) for doc in docs]