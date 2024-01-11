from pymongo import MongoClient

class RecipeDatabase:
    """
    A class for interacting with a MongoDB database for storing recipes and user information.

    Parameters
    ----------
    uri : str, optional
        The MongoDB connection URI. Default is 'mongodb://localhost:27017/'.
    db_name : str, optional
        The name of the database. Default is 'recipe_db'.

    Attributes
    ----------
    client : pymongo.MongoClient
        The MongoDB client connected to the specified URI.
    db : pymongo.database.Database
        The MongoDB database instance.
    users_collection : pymongo.collection.Collection
        The collection for storing user information.
    recipes_collection : pymongo.collection.Collection
        The collection for storing recipes.

    Notes
    -----
    This class assumes the existence of a MongoDB server running at the specified URI.
    """
    def __init__(self, uri: str = 'mongodb://localhost:27017/', db_name: str = 'recipe_db'):
        """
        Initialize a connection to the Recipe Sharing MongoDB database.

        Parameters
        ----------
        uri : str, optional
            The MongoDB connection URI. Default is 'mongodb://localhost:27017/'.
        db_name : str, optional
            The name of the database. Default is 'recipe_db'.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users_collection = self.db['users']
        self.users_collection.create_index([('username', 1)], unique=True)
        self.recipes_collection = self.db['recipes']