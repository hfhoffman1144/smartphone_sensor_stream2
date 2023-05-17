def flatten_dict(nested_dict, parent_key='', sep='_'):
    """
    This function takes in a nested dictionary and returns a flattened dictionary.
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)