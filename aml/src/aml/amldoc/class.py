# This file has been extracted from AMAPmod documentation (refermanual 18)

# Class
"""
    Class of a vertex

    The `Class` of a vertex is a feature always defined and independent of time 
    (like the index). 
    It is represented by an alphabetic character in upper or lower case 
    (lower cases characters are considered different from upper cases). 
    The label of a vertex is the string defined by the concatenation 
    of its class and its index. 
    The label thus provides general information about a vertex and 
    enables us to encode the plant components.

    Usage
    -----
    .. python ::
        Class(v)

    Properties
    ----------
        v (VTX) : vertex of the active MTG

    Returns
    -------
        str

    See Also
    --------	
	`MTG`, `Index`.
"""
