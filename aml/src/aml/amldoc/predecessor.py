# This file has been extracted from AMAPmod documentation (refermanual 18)

# Predecessor
"""
    Father of a vertex connected to it by a '<' edge

    This function is equivalent to Father(v, EdgeType-> '<'). 
    It thus returns the father (at the same scale) of the argument 
    if it is located in the same botanical. 
    If it does not exist, None is returned.

    Usage
    -----
    .. python ::
        Predecessor(v)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - RestrictedTo (str): cf. `Father`
        - ContainedIn (vtx_id): cf. `Father`

    Returns
    -------
        vtx_id

    See Also
    --------
        `MTG`, `Father`, `Successor`.

    Examples
    --------
    .. python ::
        >>> Predecessor(v)
        7
        >>> Father(v, EdgeType='+')
        >>> Father(v, EdgeType-> '<')
        7
"""
