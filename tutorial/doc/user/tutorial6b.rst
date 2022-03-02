.. _graph-from-tissue:

Exctracting a PropertyGraph from TissueDB zip file, svg file, or mesh
#####################################################################

.. topic:: Section contents

    In this section, we present three methods that allow a user to create 
    a PropertyGraph object from previously obtained tissues.
    The inputs can be either svg files, segmented manually as in 
    `draw-2D <http://openalea.gforge.inria.fr/doc/vplants/tissue/doc/_build/html/user/reconstruction/draw2D/index.html>`_ or the zip file containing the tissue structure built as in 
    `draw-2D <http://openalea.gforge.inria.fr/doc/vplants/tissue/doc/_build/html/user/reconstruction/draw2D/index.html>`_.
    
    Finally, you may want to extract a PropertyGraph from a tissue, 
    either in the form of a TissueDB stored in a zip file, or in the form of a 
    TopoMesh and a dictionary of vertex positions.



PropertyGraph from a svg file
=============================
 As presented in `draw-2D <http://openalea.gforge.inria.fr/doc/vplants/tissue/doc/_build/html/user/reconstruction/draw2D/index.html>`_, it is possible to segment a 2D image by hand, in svg format. We have applied this method to segment a shoot apical meristem (SAM) shown in a `publication <http://www.nature.com/uidfinder/10.1038/nmeth.1472>`_, resulting in the following image:

 .. image:: images/SAM7.png
    :height: 300pt
    :width: 300pt
    :align: center

 Once you are at this stage, you have generated a svg file containing a 2D mesh, and seeds to identify single cells (not shown above). It is then possible to extract directly a PropertyGraph from this image, which contains a number of geometric informations as properties of its vertices and edges.
 
 To do so, you need a svg file: :download:`images/SAM7.svg` . Then, assuming the file is in the current directory, you simply have to type the following in a python shell (warning: due to the tissue size, this step can be a little time-consuming):

 .. code-block:: python

    from openalea.container.readwrite.graph_from_tissue_file import graph_from_svg
    
    graph_svg = graph_from_svg('SAM7.svg')

 The created object graph_svg is a PropertyGraph, whose vertices represent cells, and edges represent walls between cells. It also contains additional geometrical information (see below).

PropertyGraph from a zip file containing a TissueDB
===================================================

 Alternatively you may have built a mesh (from the tissue package in vplants) of a segmented 2D tissue, and stored it in a zip file. Here again, you can simply extract the same graph from your file (:download:`images/tissue_sam.zip`):

 .. code-block:: python

    from openalea.container.readwrite.graph_from_tissue_file import graph_from_TissueDB
    
    graph_tdb = graph_from_TissueDB('tissue_sam.zip')

Display of a PropertyGraph
==========================

 Once you have created such a graph, you perform a number of operations. Here to visually inspect our graph, we can convert it to a `networkx <http://networkx.lanl.gov/>`_ graph:

 .. code-block:: python
 
    import networkx as nx
    
    graph_nx = graph_tdb.to_networkx()

 The graph graph_nx can be displayed, thanks to newtorkx built-in method. It contains only the adjacency information between cells, but we would like to use a layout that is consistent with the actual tissue geometry.
 
 The default properties of graph_tdb (or any property graph generated using one of the two methods above) include barycenter coordinates for all cells (stored as a property on vertices). It is also possible to access coordinates of cell corners (stored as pairs of point coordinates for each edge). With matplotlib, it is possible to use this information to also plot the actual geometry of cells:

 .. code-block:: python
 
    import matplotlib.pyplot as plt
    
    nx.draw(graph_nx, dict([(i, graph_nx.node[i]['barycenter']) for i in graph_nx.nodes()]), node_size=10, font_size=0)
    
    for e in graph_tdb.edge_property('wall_vertices_coordinates').keys():
        x,y = graph_tdb.edge_property('wall_vertices_coordinates')[e] 
        plt.plot([x[0],y[0]],[x[1],y[1]],color='g')

In order to visualize the two graphs (which are dual to each other), simply type:


 .. code-block:: python
 
    plt.show()

You should see the following
 .. image:: images/graph_property_SAM.png
    :width: 300pt
    :height: 300pt
    :align: center


PropertyGraph from a mesh and dictionary of vertex positions
============================================================

It can also happen that you have a Topomesh object, with a dictionary of positions of the vertices (i.e. zero-dimensional objects in your mesh). This can result from instance from the generation of a regular grid in 3D:

 .. code-block:: python

    from openalea.tissueshape import grid_tissue
    import numpy as np

    tissue=grid_tissue.regular_grid((5, 5, 5))
    mesh=tissue.get_topology("mesh_id")
    pos=tissue.get_property("position")
    position=dict([(i, 1.0*np.array(j)) for i,j in pos.iteritems()])

As before, you can create a PropertyGraph from this data:

 .. code-block:: python

    from openalea.container.readwrite.graph_from_tissue_file import graph_from_tissue
    
    graph_grid = graph_from_tissue(mesh, position)

Then, one possible thing is to display the graph, as we did above. Since it is now in 3D space, we use a little trick for the layout (easily understandable from the source below):

 .. code-block:: python

    import networkx as nx
    
    graph_nx = graph_grid.to_networkx()
    nx.draw(graph_nx, dict([(i, graph_nx.node[i]['barycenter'][:2]+.1*graph_nx.node[i]['barycenter'][-1]) for i in graph_nx.nodes()]), node_size=10, font_size=0)
    
    plt.show()


You should see the following
 .. image:: images/graph_property_grid.png
    :width: 400pt
    :align: center



Example: PropertyGraph display of a semgented 3D meristem (*A. thaliana*)
===========================================================================

 Using the same procedure as above, we have been able to build the following. The only step that is not shown above, is to build a PropertyGraph from a segmented image (using the function graph_from_image, from openalea.image.algo).

+------------------------------------------+------------------------------------------+
|  .. image:: images/view_image_SAM3D.png  |.. image:: images/graph_property_SAM3D.png|
|      :width: 200pt                       |    :width: 300pt                         |
|      :align: center                      |    :align: center                        |
+------------------------------------------+------------------------------------------+

.. sectionauthor:: Etienne Farcot, Léo Guignard
