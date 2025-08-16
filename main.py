from fastapi import FastAPI

from api.routes.eval_router import router 

app = FastAPI(
    title="Evaluation Service",
    description="The evaluation service module",
    version="1.0.0",
)


app.include_router(router)
