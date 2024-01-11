from fastapi import APIRouter, Header, HTTPException
from app.api.models.recipe import Recipe, RecipeDetails, Comment
from app.database import RecipeDatabase
from typing import Annotated
from bson import ObjectId

from app.api.dependencies import decode_token
from app.utils import convert_objectid_to_str, convert_str_to_objectid


router = APIRouter()
recipes_db = RecipeDatabase()

@router.get('/', response_model=list[RecipeDetails])
def get_all_recipes():
    """
    Retrieve a list of all recipes.

    Returns
    -------
    List[RecipeDetails]
        A list of recipes with detailed information, including comments.
    """
    recipes = recipes_db.recipes_collection.find()
    
    return convert_objectid_to_str(cursor=recipes)

@router.get('/{recipe_id}', response_model=RecipeDetails)
def get_recipe(recipe_id):
    """
    Retrieve a specific recipe by its identifier.

    Parameters
    ----------
    recipe_id : str
        The identifier of the recipe.

    Returns
    -------
    RecipeDetails
        Detailed information about the requested recipe, including comments.

    Raises
    ------
    HTTPException
        If the recipe with the given identifier is not found.
    """
    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)
    
    recipe = recipes_db.recipes_collection.find_one({'_id': recipe_id})

    if not recipe:
        raise HTTPException(status_code=404, detail='Recipe not found')
      
    return convert_objectid_to_str(dictionary=recipe)

@router.put('/{recipe_id}')
def edit_recipe(recipe_id: str, recipe: Recipe, token: Annotated[str | None, Header()]):
    """
    Edit an existing recipe.

    Parameters
    ----------
    recipe_id : str
        The identifier of the recipe to be edited.
    recipe : Recipe
        The updated recipe data.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        The updated recipe data.

    Raises
    ------
    HTTPException
        If the recipe is not found or if the user is not authorized to edit the recipe.
    """
    # Get logged in user from token
    user = decode_token(token)
    author = user['username']

    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)

    # Convert the updated_data to a dictionary
    recipe_to_update = recipe.model_dump()

    # Update the existing recipe using $set
    result = recipes_db.recipes_collection.update_one(
        {'_id': recipe_id, 'author': author},
        {'$set': recipe_to_update},
        upsert=False
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Recipe not found')
    
    updated_recipe = recipes_db.recipes_collection.find_one({'_id': recipe_id}, {'_id': 0})
    return updated_recipe

@router.post('/')
def add_recipe(recipe: Recipe, token: Annotated[str | None, Header()]):
    """
    Add a new recipe.

    Parameters
    ----------
    recipe : Recipe
        The recipe data to be added.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        The added recipe data.

    Raises
    ------
    HTTPException
        If the user is not authenticated.
    """
    user = decode_token(token)
    recipe.author = user['username']

    result = recipes_db.recipes_collection.insert_one(recipe.model_dump())
    return recipes_db.recipes_collection.find_one({'_id': result.inserted_id}, {'_id': 0})

@router.delete('/{recipe_id}')
def delete_recipe(recipe_id: str, token: Annotated[str | None, Header()]):
    """
    Delete a recipe.

    Parameters
    ----------
    recipe_id : str
        The identifier of the recipe to be deleted.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        A message indicating the success of the operation.

    Raises
    ------
    HTTPException
        If the recipe is not found or if the user is not authorized to delete the recipe.
    """
    # Get logged in user from token
    user = decode_token(token)
    author = user['username']

    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)
    
    result = recipes_db.recipes_collection.delete_one({'_id': recipe_id, 'author': author})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Recipe not found')
    return {"message": "Recipe deleted successfully"}

@router.post('/comments/{recipe_id}')
def add_recipe_comment(comment: str, recipe_id, token: Annotated[str | None, Header()]):
    """
    Add a comment to a recipe.

    Parameters
    ----------
    comment : str
        The content of the comment.
    recipe_id : str
        The identifier of the recipe to which the comment is added.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        The updated recipe data after adding the comment.

    Raises
    ------
    HTTPException
        If the recipe is not found.
    """
    # Get logged in user from token
    user = decode_token(token)
    author = user['username']
    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)

    new_comment = Comment(id=str(ObjectId()), content=comment, author=author)

    # Convert Pydantic models to Python dictionaries
    comment_data = new_comment.model_dump()

    # Add the new comment to the comments array
    result = recipes_db.recipes_collection.update_one(
        {"_id": recipe_id},
        {"$push": {"comments": comment_data}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Recipe not found')
    
    updated_recipe = recipes_db.recipes_collection.find_one({'_id': recipe_id}, {'_id': 0})
    return updated_recipe

@router.get('/comments/{recipe_id}', response_model=list[Comment])
def get_all_recipe_comments(recipe_id: str):
    """
    Retrieve all comments for a recipe.

    Parameters
    ----------
    recipe_id : str
        The identifier of the recipe.

    Returns
    -------
    List[Comment]
        A list of comments associated with the recipe.

    Raises
    ------
    HTTPException
        If the recipe is not found.
    """
    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)

    comments_cursor = recipes_db.recipes_collection.find({'_id': recipe_id}, {'_id': 0, 'comments': 1})
    # Extract the comments from the cursor
    comments = next(comments_cursor, None).get('comments', [])
    
    return comments

@router.delete('/comments/{recipe_id}/{comment_id}')
def delete_recipe_comment(recipe_id: str, comment_id: str, token: Annotated[str | None, Header()]):
    """
    Delete a comment from a recipe.

    Parameters
    ----------
    recipe_id : str
        The identifier of the recipe from which the comment is deleted.
    comment_id : str
        The identifier of the comment to be deleted.
    token : str, optional, header
        The JWT token for authentication.

    Returns
    -------
    dict
        A message indicating the success of the operation.

    Raises
    ------
    HTTPException
        If the comment is not found or if the user is not authorized to delete the comment.
    """
    # Get logged in user from token
    user = decode_token(token)
    author = user['username']

    # Convert the str id to ObjectId
    recipe_id = convert_str_to_objectid(recipe_id)

    result = recipes_db.recipes_collection.delete_one({"_id": recipe_id, 'author': author, "comments": {"$elemMatch": {"id": comment_id}}})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Comment not found')
    return {"message": "Comment deleted successfully"}