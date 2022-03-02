# Extremities

"""
    Set of vertices that are the extremities of the branching system 
    born by a given vertex.

    This function returns the extremities of the branching system defined by the argument
    as a list of vertices. These vertices have the same scale as `v` and their order in 
    the list is not signifiant. The result is always a non empty array.

    Usage
    -----
    .. python ::
        Extremities(v)

    Properties
    ----------
        -  v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - RestrictedTo (str): cf. `Father`
        - ContainedIn (vtx_id): cf. `Father`

    Returns
    -------
        list of vtx_id

    See Also
    --------
        `MTG`, `Descendants`, `Root`, `MTGRoot`.
    
    Examples
    --------
    .. python ::
        >>> Descendants(v)
        [3, 45, 47, 78, 102]
        >>> Extremities(v)
        [47, 102]
"""
