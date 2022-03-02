# Complex

"""
    Complex of a vertex.
    
    Returns the complex of `v`. The complex of a vertex `v` has a scale lower than `v` :
    `Scale(v)` - 1. In a MTG, every vertex except for the MTG root (cf. `MTGRoot`),
    has a uniq complex. None is returned if the argument is the MTG Root 
    or if the vertex is undefined.

    Usage
    -----
    .. python ::
        Complex(v)
        Complex(v, Scale=2)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - Scale (int) : scale of the complex

    Returns
    -------
        vtx_id

    Details
    -------
        When a scale different form Scale(v)-1 is specified using the optional parameter
        `Scale`, this scale must be lower than that of the vertex argument.

    See Also
    --------
        `MTG`, `Components`.
"""
