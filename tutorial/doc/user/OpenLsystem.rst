Open-Lsystem with Lpy: Simulation of plants interacting with their environment
##############################################################################

.. topic:: Section contents

    How to simulate LPy model with environmental factors?

The problem setting
===================

Open L-systems allows to simulate the interaction of plants with their environment. Lpy comes with an implementation of OpenL-system quite different from that of cpfg/lpfg. 
It is based on an indexing of modules that parrallels an uindexing of scene shapes.
In a first tutorial, we will illustrate this interface, both in the L-Py interpreter world, and in the visualea world. 
The tutorial is build on different environmental programs allowing to illuminate 3D scenes (QuasiMC, Caribu, Fractalysis, RATP). 
In a second tutorial, we will present the plant-gl grid object that allows representing the soil filled with water, and a plant growing and pumping in this soil. 
The grid object build aims a beeing reused and will satisfy the following interface : 
   - a grid where we can store scalars (shadow, water content)
   - a grid where we can store points with attributes.
   - sca, disease propagation
   - in both last 2 cases, we need the following access functions:
      
        - voxel corresponding to one point
        - voxels corresponding to one triangle:
            - barycentric method: one triangle is summarized by one point (see previous method) 
            - method from CG that gives intersection between triangle and box
            - method that gives surface of triangles in each intercepted voxel.
            
      we need a visualization functions

   

Loading an example dataset
==========================

 The `tutorial` package comes with a few datasets. The data are in
 `share` directory. See the `data howto <>` 
 for more details.::

    >>> import vplants.tutorial
    >>> from openalea.deploy.shared_data import get_shared_data_path
    >>> print get_shared_data_path(vplants.tutorial, 'empty.txt')

Write your tutorial
====================

.. toctree::

    LightComparison.rst
    Usegrid.rst
