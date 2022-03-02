How to generate and analyse a Spatio-temporal object :class:`TemporalPropertyGraph`
###################################################################################

.. topic:: Section contents

    In this section, we introduce the analysis of temporal series of segemented tissu images.
    We are going to assemble several :class:`PropertyGraph` (spatial graph) into a new class :class:`TemporalPropertyGraph` (spatio-temporal graph).

.. warning:: If you want to use display functions (2D and 3D), make sure you launch python or ipython with the ``-q4thread`` option, laoading the Qt4 environnement.

.. code-block:: bash
    
    user@computer:$ ipython -q4thread

.. note:: You can use simultaneously the ``-pylab`` option, a matplotlib-based Python environment.

.. code-block:: bash
    
    user@computer:$ ipython -q4thread -pylab



The 4D Structure : :class:`TemporalPropertyGraph`
-------------------------------------------------

Loading the images and creating the corresponding :class:`PropertyGraph`
========================================================================

.. code-block:: python

    import openalea.container
    from openalea.deploy.shared_data import shared_data
    data_files = shared_data(openalea.container, pattern='*.inr.gz') # return a list

    # -- We load the images corresponding to the different time points
    from openalea.image.serial.basics import imread
    t1 = imread(shared_data(openalea.container, 'p58-t1_imgSeg_cleaned.inr.gz'))
    t2 = imread(shared_data(openalea.container, 'p58-t2_imgSeg_cleaned.inr.gz'))
    t3 = imread(shared_data(openalea.container, 'p58-t3_imgSeg_cleaned.inr.gz'))

    # -- We create the corresponding SpatialImageAnalysis objets
    from openalea.image.algo.analysis import SpatialImageAnalysis
    analysis1 = SpatialImageAnalysis(t1)
    analysis2 = SpatialImageAnalysis(t2)
    analysis3 = SpatialImageAnalysis(t3)

    # -- We don't want to compute values (in `graph_from_image()`) for cells at the margins of the stack.
    analysis1.remove_margins_cells(verbose=True)
    analysis2.remove_margins_cells(verbose=True)
    analysis3.remove_margins_cells(verbose=True)

    # -- We now create the PropertyGraphs
    from openalea.image.algo.graph_from_image import graph_from_image
    graph_1 = graph_from_image( analysis1.image )
    graph_2 = graph_from_image( analysis2.image )
    graph_3 = graph_from_image( analysis3.image )

For more detailed instruction concerning this part, see :ref:`Data-from-Segmented-Image`

Loading the lineages
====================

To link cells over time we need to have information about their fate. 

.. code-block:: python

    from vplants.mars_alt.alt.mapping import lineage_from_file

    lin_12=lineage_from_file(shared_data(openalea.container, 'suiviExpertEntier58-12.txt'))
    l12=lin_12
    lin_23=lineage_from_file(shared_data(openalea.container, 'suiviExpertEntier58-23.txt'))
    l23=lin_23

``l12`` and ``l23`` are dictionaries containing the cell mother labels (keys) and the labels of the corresponding daughter cells.


Creating the :class:`TemporalPropertyGraph`
===========================================

To create the :class:`TemporalPropertyGraph` we now need to link the graphs (:class:`PropertyGraph`) over time using the lineages.

.. code-block:: python

    from openalea.container import TemporalPropertyGraph
    g = TemporalPropertyGraph()
    g.extend([graph_1,graph_2,graph_3],[l12,l23])

We now have a 4D structure containing the maximum information we could extract from the segmented images (:class:`SpatialImage`).

.. warning:: The cells labels have been renamed during this step. To find the conversion dictionary use:

.. code-block:: python

    g.vertex_property('old_label')

In the output dictionary, the keys correspond to the new labels and the values to the old ones.


Browsing the :class:`TemporalPropertyGraph`
===========================================

As for the :class:`PropertyGraph`, we can move through the structure that we have generated (:class:`TemporalPropertyGraph`).

`edge_type` can be 's' (space) or 't' (time)

Moving through space
^^^^^^^^^^^^^^^^^^^^

* ``neighbors(self, vid, edge_type='s')``: to kown the neighbors of one cell (`vid`)

.. code-block:: python

    g.neighbors(5)
    set([83, 126, 532, 581, 595])

* ``edges(self, vid, edge_type='s')``: for the edges linking the vertex `vid` to its neighbors.

.. code-block:: python

    g.edges(5)
    set([50, 51, 52, 53, 54])

* ``neighborhood(self, vids, rank, edge_type='s')``: the label list containing the neighborhood of the vertex `vids` within 0 and distance `rank`.

.. code-block:: python

    g.neighborhood(5,1)
    set([5, 83, 126, 532, 581, 595])

    g.neighborhood(5,2)
    set([3, 5, 9, 11, 15, 20, 39, 79, 83, 92, 105, 126, 193, 208, 287, 340, 343, 389, 391, 417, 441, 487, 529, 532, 569, 572, 581, 595, 675, 684, 694, 743, 768])
    # -- Note that if you ask for a rank >= 2, lower ranks neighbors will be returned too !!!


Moving through time
^^^^^^^^^^^^^^^^^^^

* ``children(self, vid)``: to get the children of the vertex `vid`.

.. code-block:: python

    g.children(2)
    set([1531, 1595])

* ``parent(self, vid)``: for the informations about the parents.

.. code-block:: python

    g.parent(1531)
    set([2])

* ``sibling(self, vid)``: returns sibling of the vertex vid.

.. code-block:: python

    g.sibling(1531)
    set([1595])

    g.sibling(1595)
    set([1531])

* ``descendants(self, vids, rank)``: returns the 0, 1, ..., n\ :sup:`th` descendants of the vertex `vid`.

.. code-block:: python

    g.descendants(2,1)
    set([2, 1531, 1595])
    # -- Note that appart from the provided `vids`, at rank=1 the function returns the same thing that children.

    g.descendants(2,2)
    set([2, 1531, 1595, 2677, 2749, 2833, 2878])
    # -- Note that the function returns also descendants at lower rank !!!


* ``ancestors(self, vids, rank)``: returns the 0, 1, ..., n\ :sup:`th` ancestors of the vertex `vid`.

.. code-block:: python

    g.ancestors(2833,1)
    set([1595, 2833])
    # -- Note that appart from the provided `vids`, at rank=1 the function returns the same thing that parent.

    g.ancestors(2833,2)
    set([2, 1595, 2833])
    # -- Note that the function returns also descendants at lower rank !!!




Analysing Spatio-temporal objects (:class:`TemporalPropertyGraph`)
------------------------------------------------------------------
Available in ‘.../vplants/vplants/container/src/container/temporal_graph_analysis.py’.

.. code-block:: python

    from openalea.container.temporal_graph_analysis import mean_abs_dev, laplacian

Spatial analysis
================

* ``mean_abs_dev(graph, vertex_property, vid, rank)``: mean sum of absolute difference between the vertex id `vid` and its neighbors at `rank`.

.. math:: 

    \text{mean abs dev}(i)= \dfrac{1}{N} \sum_{k \in N} p_{k}-p_{i},

for `k` in ``self.neighbors(i)``, where `p` is a property of a vertex and `i` the cell to be compared to its `N` neighbors.


* ``laplacian(graph, vertex_property, vid, rank)`` : difference between the vertex id `vid` and the mean of its neighbors at `rank`.

.. math:: 

    \text{laplacian(i)} = p_{i} - \dfrac{1}{N} \sum_{k \in N} p_{k},

for `k` in ``self.neighbors(i)``, where `p` is a property of a vertex and `i` the cell to be compared to its `N` neighbors.




Temporal analysis
=================
Available in ‘.../vplants/vplants/container/src/container/temporal_graph_analysis.py’.

Change in number
^^^^^^^^^^^^^^^^
Should return the evolution of the number of cells in the FM. Problem, we don’t have the whole meristem after mid-stage 2, and defining the limit between the FM and the SAM could be difficult and criticized. We could use complete cell lineage (those covering every stages) to compute division speed (first derivative) and acceleration (second derivative).

Change in size
^^^^^^^^^^^^^^
Should return the evolution of any spatial property like volumetric or areal growth. 

.. warning:: Since the time interval between each time point can be different, we should **normalize** by the time interval between the :class:`PropertyGraph`.

.. code-block:: python

    from openalea.container.temporal_graph_analysis import temporal_change, relative_temporal_change

* ``temporal_change(graph, vertex_property, vids = None, rank = 1, labels_at_t_n = True, check_full_lineage = True, verbose = False)``: difference between the parent vertex id `vid` and its children at `rank`. 

.. math::

    \text{temporal change}(i)= \sum_{k \in N} (p_k) - p_i,

for `k` in ``self.children(i)`` or in ``self.descendants(i)`` where `p` is a property of a vertex and `i` the parent vertex.

* ``relative_temporal_change(graph, vertex_property, vids = None, rank = 1, labels_at_t_n = True, check_full_lineage = True, verbose = False)``: relative difference between the parent vertex id `vid` and its children at `rank`.

.. math::

    \text{relative temporal change}(i)= \dfrac{\sum_{k \in N} p_k - p_i}{p_i},

for `k` in ``self.children(i)`` or in ``self.descendants(i)`` where `p` is a property of a vertex and `i` the parent vertex.


Spatio-temporal analysis
========================

Change in shape
^^^^^^^^^^^^^^^
Should return the evolution of shape.

**cell_vertex_association**: associate cell vertices according to the 4 cells ids that define them and the cell lineage.

**strain**: 3D tensor indicating the direction and extent of deformation along the 3 major axis of deformation. One should be able to use an affine model or not. 

eigenvectors(i)=3x3 matrix, eigenvalues(i)=s\ :sub:`11`,s\ :sub:`22`, s\ :sub:`23`

**strain rate** :

.. math::

    \dfrac{\log s_{11}}{\Delta t}, \dfrac{\log s_{22} }{\Delta t}, \dfrac{\log s_{33} }{\Delta t}


**growth anisotropy**: example in 2D 

.. math::

    \text{growth anisotropy}(i)= \dfrac{s_{11}-s_{22}}{s_{11}+s_{22}}


**division plane**: the plane fitted to the cell wall between two sibling is a division plane.



.. sectionauthor:: Jonathan LEGRAND, Maryline LIÉVRE
