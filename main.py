from fastapi import FastAPI

app = FastAPI(title="StockClothing API")

from product_routes import product_router
from sale_routes import sale_router

app.include_router(product_router)
app.include_router(sale_router)


# Para rodar: uvicorn main:app --reload
