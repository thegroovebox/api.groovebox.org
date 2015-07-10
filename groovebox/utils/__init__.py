def subdict(d, keys):    
    """Create a dictionary containing only `keys`
    move to utils
    """
    return dict([(k, d[k]) for k in keys])
