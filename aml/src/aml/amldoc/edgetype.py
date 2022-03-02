# This file has been extracted from AMAPmod documentation (refermanual 18)

# EdgeType
"""
    Type of connection between two vertices.

    Returns the symbol of the type of connection between two vertices (either `<' or `+'). 
    If the vertices are not connected, Undef is returned.

    Usage
    -----
    .. python ::
        EdgeType(v1, v2)

    Parameters
    ----------
        v1 (vid) : vertex of the active MTG
        v2 (vid) : vertex of the active MTG

    Returns
    -------
        '<' (successor), '+' (branching) or `None`

    See Also
    --------
        `MTG`, `Sons`, `Father`.

"""
