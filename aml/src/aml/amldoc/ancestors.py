# This file has been extracted from AMAPmod documentation (refermanual 18)

# Ancestors
"""
    Array of all vertices which are ancestors of a given vertex

    This function returns the array of vertices which are located 
    before the vertex passed as an argument. 
    These vertices are defined at the same scale as `v`. The array starts by `v`, 
    then contains the vertices on the path from `v` back to the root (in this order) 
    and finishes by the tree root.

    Note : The anscestor array always contains at least the argument vertex `v`.

    Usage
    -----
    .. python ::
        Ancestors(v)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - RestrictedTo (str): cf. `Father`
        - ContainedIn (vtx_id): cf. `Father`
        - EdgeType (str): cf. `Father`

    Returns
    -------
        list of vtx_id.

    See Also
    --------
        `MTG`, `Descendants`.

    Examples
    --------
    .. python ::
        >>> v # prints vertex v
        78
        >>> Ancestors(v) # set of ancestors of v at the same scale
        [78,45,32,10,4]
        >>> list(reversed(Ancestors(v))) # To get the vertices in the order from the root to the vertex v
        [4,10,32,45,78]
"""
