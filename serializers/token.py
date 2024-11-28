from models.token import TokenModel 

def serializar_token(doc) -> TokenModel:
    return TokenModel(
        id_token=str(doc["_id"]),
        id_usu=doc["id_usu"],
        token_jwt=doc["token_jwt"]
    )