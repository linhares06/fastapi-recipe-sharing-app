from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

def convert_objectid_to_str(cursor=None, dictionary=None):
    """
    Converts ObjectId values to their string representation in a MongoDB query result.

    Parameters
    ----------
    cursor : pymongo.cursor.Cursor, optional
        A MongoDB cursor containing query results with ObjectId values.
    dictionary : dict, optional
        A dictionary with ObjectId values.

    Returns
    -------
    Union[List[Dict], Dict, None]
        If `cursor` is provided, returns a list of dictionaries with ObjectId values converted to strings.
        If `dictionary` is provided, returns the dictionary with ObjectId values converted to strings.
        If neither `cursor` nor `dictionary` is provided, returns None.
    """
    if cursor:
        return [{**doc, '_id': str(doc.get('_id'))} for doc in cursor]
    elif dictionary:
        dictionary['_id'] = str(dictionary.get('_id'))
        return dictionary
    else:
        return None
    
def convert_str_to_objectid(id):
    """
    Converts a string representation of ObjectId to ObjectId.

    Parameters
    ----------
    id : str
        A string representing ObjectId.

    Returns
    -------
    ObjectId
        The ObjectId corresponding to the input string.

    Raises
    ------
    HTTPException
        If the input string is not a valid ObjectId.
    """
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail='Invalid Id')