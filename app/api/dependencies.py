import os
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from passlib.context import CryptContext

from app.api.models.user import TokenData, Token, User
from app.database import RecipeDatabase

recipes_db = RecipeDatabase()

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Load environment variables from .env file
load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
algorithm = os.environ.get('ALGORITHM')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")

# Function to create a JWT token
def create_jwt_token(data: dict) -> str:
    """
    Create a JWT token with the given data.

    Parameters
    ----------
    data : dict
        The data to be encoded into the JWT token.

    Returns
    -------
    str
        The JWT token string.

    Notes
    -----
    This function sets the expiration time of the token to one week from the current time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(weeks=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt
    
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get the current user based on the provided JWT token.

    Parameters
    ----------
    token : str
        JWT token for authentication.

    Raises
    ------
    HTTPException
        If the credentials cannot be validated.

    Returns
    -------
    User
        The user associated with the provided token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get('username')

        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    db_user: dict = recipes_db.users_collection.find_one({'username': token_data.username}, {'_id': 0, 'password': 0})

    if db_user is None:
        raise credentials_exception
    
    user: User = User.model_validate(db_user)
    
    return user

def authenticate_user(username: str, password: str) -> Token:
    """
    Authenticate a user based on the provided username and password.

    Parameters
    ----------
    username : str
        The username of the user.
    password : str
        The password of the user.

    Raises
    ------
    HTTPException
        If the credentials are invalid.

    Returns
    -------
    Token
        JWT access token.
    """
    user: dict = recipes_db.users_collection.find_one({'username': username})

    if user and password_context.verify(password, user['password']):
        # Generate a JWT token
        token = create_jwt_token({'username': user['username']})

        return Token(access_token=token, token_type='bearer')

    # Return an error if credentials are invalid
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

