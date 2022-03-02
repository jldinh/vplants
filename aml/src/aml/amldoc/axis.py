# This file has been extracted from AMAPmod documentation (refermanual 18)

# Axis
"""
    Array of vertices constituting a botanical axis

    An axis is a maximal sequence of vertices connected by '<'-type edges. 
    Axis return the array of vertices representing the botanical axis which the argument v belongs to. 
    The optional argument enables the user to choose the scale at which the axis decomposition is required.
    
    Usage
    -----
    .. python ::
        Axis(v)
        Axis(v, Scale=s)

    Parameters
    ----------
        - v (vtx_id) : Vertex of the active MTG

    Optional Parameters
    -------------------
        - Scale (str): scale at which the axis components are required.

    Returns
    -------
        list of vtx_id

    See Also
    --------
        `MTG`, `Path`, `Ancestors`.
"""
