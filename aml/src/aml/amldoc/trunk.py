# This file has been extracted from AMAPmod documentation (refermanual 18)

# Trunk
"""
    List of vertices constituting the bearing botanical axis of a branching system.

    Trunk returns the list of vertices representing the botanical axis defined as 
    the bearing axis of the whole branching system defined by `v`. 
    The optional argument enables the user to choose the scale at which the trunk should be detailed.

    Usage
    -----
    .. python ::
        Trunk(v)
        Trunk(v, Scale=s)

    Parameters
    ----------
        - v (vtx_id) : Vertex of the active MTG.

    Optional Parameters
    -------------------
        - Scale (str): scale at which the axis components are required.

    Returns
    -------
        list of vtx_id

    See Also
    --------
        `MTG`, `Path`, `Ancestors`, `Axis`.
"""
