from models.usuario import UsuarioModel

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