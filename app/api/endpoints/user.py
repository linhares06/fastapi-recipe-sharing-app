from fastapi import APIRouter, HTTPException, status, Header
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError
from typing import Annotated

from app.api.models.user import User, Token
from app.api.dependencies import create_jwt_token, decode_token
from app.utils import convert_str_to_objectid
from app.database import RecipeDatabase


router = APIRouter()
recipes_db = RecipeDatabase()

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.post('/')
def add_user(user: User):
    """
    Register a new user.

    Parameters
    ----------
    user : User
        The user information including username and password.

    Returns
    -------
    dict
        User information excluding the password.

    Raises
    ------
    HTTPException
        If the username is already in use.
    """
    # Hash the user's password before storing it in the database
    user.password = password_context.hash(user.password)
    
    try:
        # Store the user in the database
        result = recipes_db.users_collection.insert_one(user.model_dump())
        return recipes_db.users_collection.find_one({'_id': result.inserted_id}, {'_id': 0, 'password': 0})

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail='Username already in use.')
    
@router.post('/login', response_model=Token)
def login(user: User):
    """
    Log in a user and return an access token.

    Parameters
    ----------
    user : User
        The user information including username and password.

    Returns
    -------
    dict
        The access token and token type.

    Raises
    ------
    HTTPException
        If the provided credentials are invalid.
    """
    user = recipes_db.users_collection.find_one({'username': user.username})

    if user and password_context.verify(user.password, user['password']):
        # Generate a JWT token
        token = create_jwt_token({'username': user['username']})

        return {"access_token": token, "token_type": "bearer"}

    # Return an error if credentials are invalid
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

@router.delete('/delete/{user_id}')
def delete_user(user_id: str, token: Annotated[str | None, Header()]):
    """
    Delete a user and associated data.

    Parameters
    ----------
    user_id : str
        The identifier of the user to be deleted.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        A message indicating the success of the operation.

    Raises
    ------
    HTTPException
        If the user is not found.
    """
    # Get logged in user from token
    user = decode_token(token)
    username = user['username']

    # Convert the str id to ObjectId
    user_id = convert_str_to_objectid(user_id)
    
    result = recipes_db.users_collection.delete_one({"_id": user_id, 'username': username})

    if result.deleted_count > 0:
        # If the user was deleted, remove their recipes
        recipes_db.recipes_collection.delete_many(
            {"author": username},
        )
        # If the user was deleted, remove their comments from recipes
        recipes_db.recipes_collection.update_many(
            {"comments.author": username},
            {"$pull": {"comments": {"author": username}}}
        )
    else:
        raise HTTPException(status_code=404, detail='User not found')
    
    return {"message": "User deleted successfully"}