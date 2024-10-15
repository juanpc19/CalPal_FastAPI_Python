from fastapi import APIRouter

entry_root = APIRouter()

#endpoint
@entry_root.get("/")
def apiRunning():
    response = {
        "status" : "ok",
        "message" : "API its working"
    }
    return response