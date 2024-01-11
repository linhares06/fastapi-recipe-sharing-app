from typing import List
from pydantic import BaseModel, Field


class Comment(BaseModel):
    """
    Pydantic model representing a comment.

    Attributes
    ----------
    id : str
        The identifier of the comment.
    content : str
        The content of the comment.
    author : str
        The author of the comment.
    """
    id: str
    content: str
    author: str

class Recipe(BaseModel):
    """
    Pydantic model representing a recipe.

    Attributes
    ----------
    id : str
        The identifier of the recipe (aliased as '_id').
    title : str
        The title of the recipe.
    author : str
        The author or creator of the recipe.
    ingredients : List[str]
        The list of ingredients for the recipe.
    instructions : str
        The instructions for preparing the recipe.
    categories : List[str]
        The list of categories or tags associated with the recipe.
    """
    id: str = Field(alias='_id')
    title: str
    author: str
    ingredients: List[str]
    instructions: str
    categories: List[str]

class RecipeDetails(Recipe):
    """
    Pydantic model representing detailed information about a recipe, including comments.

    Attributes
    ----------
    comments : List[Comment]
        The list of comments associated with the recipe.
    """
    comments: List[Comment] = []