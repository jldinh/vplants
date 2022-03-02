# Location

"""
    Vertex defining the father of a vertex with maximum scale.

    If no options are supplied, this function returns the vertex defining the father of a vertex
    with maximum scale (cf. `Father`). If it does not exist, None is returned.
    If a scale is specified, the function is equivalent to `Father(v, Scale=s)`.

    Usage
    -----
    .. python ::
        Location(v)
        Location(v, Scale=s)
        Location(v, ContainedIn=complex_id)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG.

    Optional Parameters
    -------------------
        - Scale (int) : scale at which the location is required.
        - ContainedIn (vtx_id) : cf. `Father`

    Returns
    -------
        vtx_id

    See Also
    --------
        `MTG`, `Father`.

    Examples
    --------
    .. python ::
        >>> Father(v, EdgeType='+')
        7
        >>> Complex(v)
        4
        >>> Components(7)
        [9,19,23, 34, 77, 89]
        >>> Location(v)
        23
        >>> Location(v, Scale= Scale(v)+1)
        23
        >>> Location(v, Scale= Scale(v))
        7
        >>> Location(v, Scale= Scale(v)-1)
        4
    
"""
