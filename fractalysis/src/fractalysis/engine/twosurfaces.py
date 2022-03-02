"""two surface module"""

__docformat__ = "restructuredtext en"

from  openalea.plantgl.algo import surface


def scene2surfacedict(sc):
    """convert a scene to a surface dictionary"""
    surfdict = {}
    for sh in sc:
        surfdict[sh.id] = surface(sh.geometry)
    return surfdict

def TwoSurfaces(leaves, macroreps=[]):
    """Compute the surface of envelope and leaves representations.

    :Parameters:

    - `Leaves` : scene representing considered leaves
    - `Macrorep` : scale by scale cople where each shape is associated to 
      id list of embeded leaves

    :Types:

    - `Leaves` : Pgl scene
    - `Macrorep` : [ ( [Shape], [ [ int ] ] ) ] 

    :returns:

    - `Macrosurfaces` : List of surfaces of Shape
    - `Microsurfaces` : List of embeded leaf area

    :returntype:

    - `Macrosurfaces` : [ float ]
    - `Microsurfaces` : [ float ]

    """

    microsurface = []
    macrosurface = []
    detailsurf = scene2surfacedict(leaves)
    for macrosc, macrograph in macroreps:
        compodict = {}
        for components in macrograph:
            compodict[components[0]] = components
        for sh in macrosc:
            root = sh.id
            macrosurface.append(surface(sh))
            microsurface.append(sum([detailsurf.get(i, 0)
                                     for i in compodict[root]]))
    return (macrosurface, microsurface)
