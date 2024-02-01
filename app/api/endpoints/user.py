from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError
from typing import Annotated

from app.api.models.user import User
from app.api.dependencies import authenticate_user, get_current_user
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

@router.delete('/delete/{user_id}')
def delete_user(user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Delete a user and associated data.

    Parameters
    ----------
    user_id : str
        The user ID to be deleted.
    current_user : User
        The currently logged-in user.

    Raises
    ------
    HTTPException
        If the user is not found.

    Returns
    -------
    dict
        A message indicating the success of the deletion.
    """
    # Get logged in user
    username = current_user.username

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

@router.post('/token')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Generate an access token for the given user credentials.

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm
        User credentials.

    Returns
    -------
    dict
        Access token response.
    """
    return authenticate_user(form_data.username, form_data.password)

@router.get('/me')
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Retrieve information about the currently logged-in user.

    Parameters
    ----------
    current_user : User
        The currently logged-in user.

    Returns
    -------
    User
        User information.
    """
    return current_user