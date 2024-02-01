from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """
    Pydantic model representing a user.

    Attributes
    ----------
    username : str
        The username of the user (maximum length: 50 characters).
    password : str
        The hashed password of the user.
    """
    username: str = Field(max_length=50, description='The username of the user.')
    password: Optional[str] = Field(default= None, description='The hashed password of the user.')

class Token(BaseModel):
    """
    Pydantic model representing an access token.

    Attributes
    ----------
    access_token : str
        The access token string.
    token_type : str
        The type of the token.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None