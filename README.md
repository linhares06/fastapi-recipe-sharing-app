# Recipe Sharing App API Project
This is a Python-based RESTful API with FastAPI that provides information for a Recipe Sharing App.
It uses FastAPI and pymongo for integration with a noSQL database(MongoDB).

## Running 
1. Clone repository.
2. pip install requirements.txt
3. Create a new .env file at the base of the project with these values:<br/>
	SECRET_KEY="Generate a random 32-byte (256-bit) secret key"<br/>
	ALGORITHM=HS256<br/>
	obs.: for the SECRET_KEY the following python code can be used:<br/>
		import secrets<br/>
		secret_key = secrets.token_urlsafe(32)<br/>
		print(secret_key)<br/>
4. Start server by running uvicorn app.main:app 

## API Documentation
Swagger UI documentation at [http://localhost:8000/docs/](http://localhost:8000/docs/) to interactively explore and test the API endpoints.

## Endpoints
- **recipes**
- **GET /api/v1/recipes/:** Retrieve a list of all recipes.
- **POST /api/v1/recipes/:** Add a new recipe.
- **GET /api/v1/recipes/{recipe_id}:** Retrieve details for a specific recipe.
- **PUT PUT /api/v1/recipes/{recipe_id}:** Edit an existing recipe.
- **DELETE /api/v1/recipes/{recipe_id}:** Delete a specific recipe.
- **POST /api/v1/recipes/comments/{recipe_id}:** Add a comment to a specific recipe.
- **GET /api/v1/recipes/comments/{recipe_id}:** Retrieve all comments for a specific recipe.
- **DELETE /api/v1/recipes/comments/{recipe_id}/{comment_id}:** Retrieve all comments for a specific recipe.
- **users**
- **POST /api/v1/users/:** Add a new user.
- **POST /api/v1/users/login/:** User login.
- **DELETE /api/v1/users/delete/{user_id}:** Delete a user.
