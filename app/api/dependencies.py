from jose import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

secret_key = os.environ.get('SECRET_KEY')
algorithm = os.environ.get('ALGORITHM')

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

# Function to decode and verify the JWT token
def decode_token(token) -> dict:
    """
    Decode and verify a JWT token.

    Parameters
    ----------
    token : str
        The JWT token string to be decoded and verified.

    Returns
    -------
    dict
        The decoded data from the JWT token.

    Raises
    ------
    HTTPException
        If the token cannot be validated, raises an HTTPException with status code 401.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

