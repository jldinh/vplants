# This file has been extracted from AMAPmod documentation (refermanual 18)

# Components
"""
    Set of components of a vertex.

    The set of components of a vertex is returned as a list of vertices. 
    If `s` defines the scale of `v`, components are defined at scale `s` + 1. 
    The array is empty if the vertex has no components. 
    The order of the components in the array is not significant.
    
    When a scale is specified using optional argument `Scale`, 
    it must be necessarily greater than the scale of the argument.

    Usage
    -----
    .. python ::
        Components(v)
        Components(v, Scale=2)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - Scale (int) : scale of the components.

    Returns
    -------
        list of vtx_id

    See Also
    --------
        `MTG`, `Complex`.
"""
