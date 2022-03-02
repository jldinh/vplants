.. _tissue_delaunay2D:

#######################
 Delaunay 2D
#######################

:Version: |version|
:Release: |release|
:Date: |today|

The goal of this document is to explain one method to reconstruct a 2D tissue that use:
 - a Delaunay algorithm to find cell neighborhood
 - a Voronoi's tesselation to compute cell geometry

-------------------------
Data acquisition
-------------------------

To allow the reconstruction of a tissue with this method we must measure:
 - the position of cell centers
 - the exact geometry of the outer boundary of the tissue
 - an approximation of the outer limit of cell centers

Usually, data used correspond to a microscopic image of a slice of a tissue.

.. image:: data_microscope.png
    :width: 40%
    :align: center

Cell center are marked using a vectorial drawing editor like `inkscape <http://www.inkscape.org/>`_ for example.

.. image:: data_cell_center.png
    :width: 40%
    :align: center

The outer boundary that correspond to the surface of the tissue plus a bottom line is edited using a nurbs or a set of nurbs.

.. image:: data_outer_boundary.png
    :width: 40%
    :align: center

Then, another curve is edited to define the outer limit of cell centers. this curve will, later, allow us to remove unwanted element when the shape of the tissue is not convex.

.. image:: data_outer_limit.png
    :width: 40%
    :align: center

This acquisition provides the global shape of the tissue with cells marked by their center inside this curve (:download:`data.svg`).

.. image:: data_acquired.png
    :width: 40%
    :align: center

In the near future, automatic segmentation of images will directly take the microscopic image, segment it and return the informations needed.

-------------------------
Cell Neighborhood
-------------------------

Simple Delaunay
###############

The second step of the reconstruction consist in reading the informations acquired in the previous section and construct the Delaunay structure based on cell centers only.

.. literalinclude:: delaunay_simple.py

The result of this algorithm is a mesh where:
 - points correspond to cell centers
 - edges connect two neighbor cells
 - faces are triangles
 - the overall shape is convex

.. image:: delaunay_simple.png
    :width: 40%
    :align: center

Constrained Delaunay
####################

The previous algorithm creates links between neighbor cells but do not take into account the outer boundary of the tissue. The resulting global shape is convex. Hence, some created triangles lies outside of the tissue.

.. image:: delaunay_simple_boundary.png
    :width: 40%
    :align: center

However, these triangles are easily detected since at least one of their edges intersects the outer limit curve. Once detected, these triangles are removed from the Delaunay triangulation.

.. literalinclude:: delaunay_constrained.py

.. image:: delaunay_constrained.png
    :width: 40%
    :align: center

Remove flat triangles
#####################

All the triangles left in the Delaunay triangulation are located inside the provided boundary. However, locally, the shape is not exactly convex and the curve drawn by hand left some triangles on the boundary that are flat and unwanted. These triangles must be filtered too.

.. image:: delaunay_flat_triangles.png
    :width: 40%
    :align: center

These triangles are filtered according to the position of their circum center. The circum center of a Delaunay triangle correspond to a vertex of the Voronoi tesselation (see below). Since no vertices of the reconstructed tissue are outside of the provided boundary, every triangle with a circum center outside of the outer boundary curve is removed.

.. literalinclude:: delaunay_filtered.py

.. image:: delaunay_filtered.png
    :width: 40%
    :align: center

-------------------------
Cell geometry
-------------------------

So far the Delaunay meshing of the given set of cell center enable to know the direct neighborhood of each cell. However, we still need to compute an approximation of the geometry of each cell.

Voronoi
########

to compute the geometry of each cell, we choose to put a wall between two neighbor cells exactly in the mean distance between them. Hence, the obtained geometry correspond to a Voronoi tesselation of space (dual mesh of Delaunay mesh).

.. literalinclude:: voronoi_simple.py

.. image:: voronoi_simple.png
    :width: 40%
    :align: center

Handling of infinite points
###########################

By definition, a wall that correspond to a Delaunay edge on the boundary intersect another wall only on the side of the internal tissue. The other extremity of the wall lies in infinity. To avoid this and still have a good shape for cells on the border, we use the user defined outer boundary to compute the exacte position of the dangling points.

For an infinite wall, the position of the point is set by the voronoi algorithm to the middle of the corresponding delaunay edge. Hence, the exact position of dangling points is not so far away from the one returned by the voronoi algorithm (in the picture above, this information has been discarded to emphasize the problem). To compute the exact position of dangling point, we choose the most proximal point on the outer boundary curve.

.. literalinclude:: voronoi_projected.py

.. image:: voronoi_projected.png
    :width: 40%
    :align: center


-------------------------
Data comparison
-------------------------

The set of operation described above produce a realistic tissue. Realistic means that each cell is polygonal. However, we still need to test to know if the reconstructed tissue is far away from the initial data or not. To perform this test, we need to compare the reconstructed tissue with the initial data provided.

Cell center position
####################

The first test consist to display the cell centers on the reconstructed tissue to verify that the points are still in the centroid of the reconstructed cell.

.. image:: test_cell_center.png
    :width: 40%
    :align: center

The position of the wanted cell centers in red match the position of the reconstructed cell centers in black with a good approximation. However, on the boundary, in regions where the shape of the tissue change rapidly compared to the size of cells, the discretization induced by cells is too big and the geometry of cells in the corner is not correctly respected.

Geometry of cells
####################

Another way to estimate the validity of the reconstructed tissue consist in drawing the reconstructed walls on the initial image obtain by microscopy. Since no more informations are available, in this case, the validation will be expert, made by the user.

.. image:: test_cell_geometry.png
    :width: 40%
    :align: center





