from fastapi import FastAPI

from app.api.routes import router
from app.db.session import Base, engine

app = FastAPI(title="RR Control Panel API", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
