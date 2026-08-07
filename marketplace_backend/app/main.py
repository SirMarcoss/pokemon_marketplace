from fastapi import FastAPI
from app.api.v1.endpoints import cart, products, auth, orders

app = FastAPI(
    title='MarketPlace API',
    version="0.1.0"
)

#Semantic versioning: 0 -> not in production project (instable project)
#                     1 -> first version that works
#                     0: no patch realized


# 2. AGGANCIA I ROUTER ALL'APP
# Il 'prefix' indica la rotta base, i 'tags' servono per ordinare l'interfaccia di Swagger
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(products.router, prefix="/products", tags=["Products"])

app.include_router(orders.router, prefix="/orders", tags=["Orders"])

@app.get("/") # the function right below is in charge of handling requests that go to: the path (/)
async def root(): #async function
    return {"message": "Tutto ok"}

# @(decorator) tells FastAPI that the function below corresponds to the path / with an operation get


# GET: to read a data
# POST: to create a data
# PUT: to update a data
# DELETE: to delete a data
