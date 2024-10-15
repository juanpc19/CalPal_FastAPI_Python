from fastapi import FastAPI
from routes.index import entry_root
from routes.alimentoBaseRoutes import alimento_base_root

app = FastAPI()

app.include_router(entry_root)
app.include_router(alimento_base_root)
