from models.usuario import UsuarioModel, UsuarioObjetivosComidasModel, UsuarioDatosModel

def serializar_usuario(doc) -> UsuarioModel:
    return UsuarioModel(
        id_usuario=str(doc["_id"]),
        hashed_password=doc["hashed_password"],
        email=doc["email"], 
        email_verificado= doc["email_verificado"],
        objetivos=doc.get("objetivos", {}),   
        comidas=doc.get("comidas", {}),
        sexo=doc["sexo"],
        altura=doc["altura"],
        peso=doc["peso"],
        edad=doc["edad"],
        nivel_actividad=doc["nivel_actividad"]
    )
    
def serializar_usuario_objetivos_comidas(doc) -> UsuarioObjetivosComidasModel:
    return UsuarioObjetivosComidasModel(
        objetivos=doc.get("objetivos", {}),   
        comidas=doc.get("comidas", {}),
    )
    
def serializar_usuario_datos(doc) -> UsuarioDatosModel:
    return UsuarioDatosModel(
        sexo=doc["sexo"],
        altura=doc["altura"],
        peso=doc["peso"],
        edad=doc["edad"],
        nivel_actividad=doc["nivel_actividad"]
    )