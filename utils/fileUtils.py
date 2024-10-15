import json

#funcion lee json
def leerFichero(nombreFichero):
    archivo = open(nombreFichero, "r", encoding="utf-8") 
    objetos = json.load(archivo)
    archivo.close()
    return objetos

#funcion escribe un json
def escribeFichero(nombreFichero, objetos):
    archivo = open(nombreFichero, "w", encoding="utf-8")
    json.dump(objetos,archivo,ensure_ascii=False,indent=4)
    archivo.close()