.. Openalea Documentation (2011)
.. intitutes : INRIA, CIRAD, INRA
.. authors : Daniel BARBEAU (INRIA)


.. _asclepios_ref_guide:

Asclepios Reference Guide
#########################

The Asclepios subpackage serves as a swiss-army toolkit for MARS ALT as
it implements many image processing routines used throughout the pipeline.
The code is contributed by the INRIA Asclepios Team.

.. contents::


Registration
============

.. autofunction:: vplants.asclepios.vt_exec.baladin.baladin

.. autofunction:: vplants.asclepios.vt_exec.superbaloo.superbaloo


Resampling
==========

.. autofunction:: vplants.asclepios.vt_exec.reech3d.reech3d

.. autofunction:: vplants.asclepios.vt_exec.reech3d.reech3d_voxels


Segmentation
============

.. automodule:: vplants.asclepios.vt_exec.watershed
   :members:

Morphology
==========

.. automodule:: vplants.asclepios.vt_exec.morpho
   :members: dilation, erosion

Filtering
=========

.. automodule:: vplants.asclepios.vt_exec.recfilters
   :members:

Local Minima
============

.. automodule:: vplants.asclepios.vt_exec.regionalmax
   :members:

Connexity
=========

.. automodule:: vplants.asclepios.vt_exec.connexe
   :members:

