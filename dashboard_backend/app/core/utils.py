import json
from typing import Any


def maybe_load_json(x:Any) -> Any:
    
    """
    Attempts to parse a JSON string into a Python object using the `json.loads` function.
    If the input is not a valid JSON string, it returns the input string as-is.

    Parameters:
    -----------
    x : str
        The input string to be parsed as JSON.

    Returns:
    --------
    obj : Any
        A Python object parsed from the JSON string, or the input string as-is if it is not valid JSON.
    """
    try:
        return json.loads(x)
    except:
        return x