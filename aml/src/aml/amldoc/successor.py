# This file has been extracted from AMAPmod documentation (refermanual 18)

# Successor
"""
    Vertex that is connected to a given vertex by a '<' edge type (i.e. in the same botanical axis).
    
    This function is equivalent to Sons(v, EdgeType='<')[0]. 
    It returns the vertex that is connected to a given vertex by a `<' edge type 
    (i.e. in the same botanical axis). 
    If many such vertices exist, an arbitrary one is returned by the function. 
    If no such vertex exists, None is returned.

  
    Usage
    -----
    -----
    .. python ::
        Successor(v)

    Parameters
    ----------
        v1 (VTX) : vertex of the active MTG
    Optional Parameters
    -------------------
        RestrictedTo (str): cf. Father
        ContainedIn (vtx_id): cf. Father

    Returns
    -------
        vtx_id

  
    See Also
    --------
    --------
        `MTG`, `Sons`, `Predecessor`.

    Examples
    --------
        >>> Sons(v) 
        [3,45,47,78,102]
        >>> Sons(v, EdgeType='+') # set of vertices borne by v
        [3,45,47,102]
        >>> Sons(v, EdgeType= '<') # set of successors of v
        [78]
        >>> Successor(v)
        78
"""
