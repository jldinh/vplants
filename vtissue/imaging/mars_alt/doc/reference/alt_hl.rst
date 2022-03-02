.. Openalea Documentation (2011)
.. intitutes  INRIA, CIRAD, INRA
.. authors  Daniel BARBEAU (INRIA)

.. _alt_high_level_api:

High Level API
##############


Introduction
============

This section presents high level functions that let you
easily setup a cell lineage tracking process.

.. note::

    Although these API provide a convenient way to quickly
    use the ALT loop, you might be interested in the
    :ref:`low level api <alt_low_level_api>` to customize
    the process for your needs.


Example
=======

For this example's sake we need to define the inputs:
 - Image of organ at time 0 : im_0.inr.gz
 - Image of organ at time 1 : im_1.inr.gz
 - Segmented image of organ at time 0 : im_seg_0.inr.gz
 - Segmented image of organ at time 1 : im_seg_1.inr.gz
 - a first fragmentary high-confidence mapping to initialise the process : lineage.txt


First, the imports::

    from openalea.image.all import imread, display
    from vplants.mars_alt.alt.alt_preparation import alt_preparation
    from vplants.mars_alt.alt.alt_loop import alt_loop
    from vplants.mars_alt.alt.update_lineages import has_descendant_filter
    from vplants.mars_alt.alt.mapping import lineage_from_file
    from vplants.mars_alt.mars.reconstruction import automatic_non_linear_parameters


Read the data::

    im_0 = imread("im_0.inr.gz")
    im_1 = imread("im_1.inr.gz")
    im_seg_0 = imread("im_seg_0.inr.gz")
    im_seg_1 = imread("im_seg_1.inr.gz")
    lineage = lineage_from_file("lineage.txt")


The :func:`~vplants.mars_alt.alt.mapping.lineage_from_file` function is used to read a file
containing high confidence lineages in different format. Please read the documentation of
the function for details.

Initialise the process::

    im_0_prime, im_seg_0_prime, tissue0, tissue1, trsf = alt_preparation(lineage, im_seg_0, im_seg_1)


The :func:`~vplants.mars_alt.alt.alt_preparation.alt_preparation` prepares the process by
computing an initial transform that registers im_0 on im_1:

* ``im_0_prime`` : would contain the result of *applying* **trsf** on im_0
  if `resampled=True` and im_0 had been passed to *alt_preparation*. In this case it is **None**.
* ``im_seg_0_prime`` : would contain the result of *applying* **trsf**
   on im_seg_0 if `resampled=True` had been passed to *alt_preparation*. In this case it is **None**.
* ``tissue_0`` : a graph structure representing the connectivity of cells in im_seg_0.
* ``tissue_1`` : a graph structure representing the connectivity of cells in im_seg_1.
* ``trsf`` : The transform that registers im_0 on im_1.


Then, we start the alt_loop::

    final_mapping, reason, scores = alt_loop(im_seg_0, im_seg_1, lineage, tissue0, tissue1,
                                             im_0, im_1, trsf,
					     non_linear_registration_params=automatic_non_linear_parameters(),
					     filter_params=[has_descendant_filter()])


The :func:`~vplants.mars_alt.alt.alt_loop.alt_loop` function will iteratively non linearly register
the images, compute candidate lineages, find the best mapping out of these lineages, filter
the wrong lineages through a set of rules and use this final lineage to compute a new linear registration.
Not sure how clear this was.

* ``final_mapping`` : the final lineage (a dictionary of parent labels to list of child labels)
* ``reason`` : the reason for the function to end. "MAX_ITER" if the maximum number of iterations
	   for alt_loop was reached.
* ``scores`` : a dictionnary of the score of each lineage for each filter at each iteration.


Initialisation
==============

.. autofunction:: vplants.mars_alt.alt.alt_preparation.alt_preparation

Optimisation
============

.. autofunction:: vplants.mars_alt.alt.alt_loop.alt_loop

Filtering Functions
===================

Filtering functions are used to verify lineages and ensure they are biologically valid.
They are subclasses of :class:`~vplants.mars_alt.alt.update_lineages.LineageFilterer`.

.. autoclass:: vplants.mars_alt.alt.update_lineages.LineageFilterer

Some preimplemented versions exist.

.. autofunction:: vplants.mars_alt.alt.update_lineages.has_descendant_filter

.. autofunction:: vplants.mars_alt.alt.update_lineages.growth_conservation_filter

.. autofunction:: vplants.mars_alt.alt.update_lineages.one_connected_component_filter

.. autofunction:: vplants.mars_alt.alt.update_lineages.adjacencies_preserved_filter

.. autofunction:: vplants.mars_alt.alt.update_lineages.adjacencies_preserved2_filter



