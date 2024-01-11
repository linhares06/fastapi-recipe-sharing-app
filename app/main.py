from fastapi import FastAPI
from app.api.endpoints import recipe, user

app = FastAPI()

# Include API routers
app.include_router(recipe.router, prefix="/api/v1/recipes", tags=["recipes"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])