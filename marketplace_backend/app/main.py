from fastapi import FastAPI

app = FastAPI(
    title='MarketPlace API',
    version="0.1.0"
)

#Semantic versioning: 0 -> not in production project (instable project)
#                     1 -> first version that works
#                     0: no patch realized

@app.get("/") # the function right below is in charge of handling requests that go to: the path (/)
async def root(): #async function
    return {"message": "Tutto ok"}

# @(decorator) tells FastAPI that the function below corresponds to the path / with an operation get


# GET: to read a data
# POST: to create a data
# PUT: to update a data
# DELETE: to delete a data
