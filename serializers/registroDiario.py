from typing import List
from models.alimentoComida import AlimentoComidaModel
from models.comidaRegistro import ComidaConAlimentosModel
from models.registroDiario import RegistroConComidasConAlimentosModel, RegistroDiarioModel

def serializar_registro(doc) -> RegistroDiarioModel:
    return RegistroDiarioModel(
        id_registro=str(doc["_id"]),
        id_usu=doc["id_usu"],
        fecha=doc["fecha"], 
        peso=doc["peso"],
        calorias=doc["calorias"],
        proteinas=doc["proteinas"],
        carbohidratos=doc["carbohidratos"],
        grasas=doc["grasas"]
    )

def serializar_registros(docs) -> List[RegistroDiarioModel]:
    return [serializar_registro(doc) for doc in docs]

def serializar_registro_completo(registro,comidas,alimentos_por_comida) -> RegistroConComidasConAlimentosModel:
    comidas_serializadas = []
    for comida in comidas:
        id_comida = str(comida["_id"])#paso id actual de comida a string porque me llega como objectid
        id_registro = str(registro["_id"])#paso id actual de registro a string porque me llega como objectid
        alimentos_por_comida_actual = alimentos_por_comida.get(id_comida, [])#obtiene alimentos asociados a comida segun id
        
        # serializo los alimentos creando lista de alimentos y los añado a la misma 
        # instanciando el modelo tantas veces como itera el bucle asignandoles el id de comida actual
        alimentos_serializados = []
        for alimento in alimentos_por_comida_actual:#itero sobre los alimentos de la comida actual
            alimentos_serializados.append(
                AlimentoComidaModel(
                id_alimento=str(alimento["_id"]),
                id_com=id_comida,
                nombre=alimento["nombre"],
                tipo=alimento["tipo"],
                cantidad_gramos=alimento["cantidad_gramos"],
                calorias=alimento["calorias"],
                proteinas=alimento["proteinas"],
                carbohidratos=alimento["carbohidratos"],
                grasas=alimento["grasas"],
                info_adicional=alimento.get("info_adicional", "")
                )
            )
             
        # Serializo la comida con sus alimentos a partir de lis previamente serializada
        comidas_serializadas.append(
            ComidaConAlimentosModel(
                id_comida=id_comida,
                id_reg=id_registro,
                orden=comida["orden"],
                nombre=comida["nombre"],
                calorias=comida["calorias"],
                proteinas=comida["proteinas"],
                carbohidratos=comida["carbohidratos"],
                grasas=comida["grasas"],
                alimentos=alimentos_serializados
            )
        )

    # Serializo el registro con sus comidas ya serializadas
    return RegistroConComidasConAlimentosModel(
        id_registro=str(registro["_id"]),
        id_usu=registro["id_usu"],
        fecha=registro["fecha"],
        peso=registro["peso"],
        calorias=registro["calorias"],
        proteinas=registro["proteinas"],
        carbohidratos=registro["carbohidratos"],
        grasas=registro["grasas"],
        comidas=comidas_serializadas
    )