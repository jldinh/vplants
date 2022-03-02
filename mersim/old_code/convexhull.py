#!/usr/bin/env python

"""convexhull.py

Calculate the convex hull of a set of n 2D-points in O(n log n) time.  
Taken from Berg et al., Computational Geometry, Springer-Verlag, 1997.
Dinu C. Gherman


:version: 2006-05-15 15:21:06CEST
:author: Dinu C. Gherman, szymon stoma
"""

######################################################################
# Helpers
######################################################################

def _my_det(p, q, r):
    """Returns determinant of a special matrix with three 2D points.

    The sign, "-" or "+", determines the side, right or left,
    respectivly, on which the point r lies, when measured against
    a directed vector from p to q.
    
    :return: determinant of a special matrix with three 2D points.
    """

    # We use Sarrus' Rule to calculate the determinant.
    # (could also use the Numeric package...)
    sum1 = q[0]*r[1] + p[0]*q[1] + r[0]*p[1]
    sum2 = q[0]*p[1] + r[0]*q[1] + p[0]*r[1]

    return sum1 - sum2


def _is_right_turn((p, q, r)):
    "Returns True iff vectors pq:qr form a right turn."

    assert p != q and q != r and p != r
            
    if _my_det(p, q, r) < 0:
        return 1
    else:
        return 0


def is_point_in_polygon(r, P):
    """Returns True iff point r is inside of the given polygon P.

    :return: True iff point r is inside of the given polygon P.
    :param r: point 2tuple
    :type r: 2tuple of point
    :param P: Polygon list of points
    :type P: list of points (r) in polygon.
    """

    # We assume the polygon is a list of points, listed clockwise!
    for i in xrange(len(P[:-1])):
        p, q = P[i], P[i+1]
        if not _is_right_turn((p, q, r)):
            return False # Out!        

    return True # It's within!



def convex_hull(P):
    """Calculate the convex hull of a set of points.
    Points are 2tuples.

    :param P: polygon.
    :type P: list of 2tuples of comparable objects.
    :returns: list of points which make convex hull of P.
    """

    # Get a local list copy of the points and sort them lexically.
    points = map(None, P)
    points.sort()

    # Build upper half of the hull.
    upper = [points[0], points[1]]
    for p in points[2:]:
        upper.append(p)
        while len(upper) > 2 and not _is_right_turn(upper[-3:]):
            del upper[-2]

    # Build lower half of the hull.
    points.reverse()
    lower = [points[0], points[1]]
    for p in points[2:]:
        lower.append(p)
        while len(lower) > 2 and not _is_right_turn(lower[-3:]):
            del lower[-2]

    # Remove duplicates.
    del lower[0]
    del lower[-1]

    # Concatenate both halfs and return.
    return tuple(upper + lower)



