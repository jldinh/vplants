.. Openalea Documentation (2011)
.. intitutes : INRIA, CIRAD, INRA
.. authors : Daniel BARBEAU (INRIA)

.. _mars_low_level_api:

Low Level API
#############

This section presents low level functions that let you
customize the registration, fusion (to some extent),
and segmentation process.

Introduction
============

While the :ref:`high level api <mars_high_level_api>` offers
quick and easy ways to do registrations, fusions and
segmentations, it doesn't give you total freedom on how
to chain the operations. This section exposes the API
on which the high level api is built.

.. note ::

    The reason for a high level api is to hide the complexity
    of lower level functions. The functions here are not complex
    by themselves but can be complex to combine, be warned.


Reference
=========

Registration API
****************

Manual surfacic registration
''''''''''''''''''''''''''''
.. autofunction:: vplants.mars_alt.mars.reconstruction.im2surface

.. autofunction:: vplants.mars_alt.mars.reconstruction.surface2im

.. autofunction:: vplants.mars_alt.mars.reconstruction.spatialise_matrix_points

.. autofunction:: vplants.mars_alt.mars.reconstruction.surface_landmark_matching


.. note::

    :func:`surface_landmark_matching <vplants.mars_alt.mars.reconstruction.surface_landmark_matching>`
     can also be used for standard landmark registration if
     the provided points are in real 3D coordinates.

Automated registration
''''''''''''''''''''''
.. autofunction:: vplants.mars_alt.mars.reconstruction.automatic_linear_registration

.. autofunction:: vplants.mars_alt.mars.reconstruction.automatic_non_linear_registration


Fusion API
**********

The fusion module doesn't present a much lower API than the one
provided in :ref:`high level api <mars_high_level_api>`. However
it does provide an alternative to the
:func:`fusion <vplants.mars_alt.mars.fusion.fusion>` function
called *original_fusion* (not a music band name). It is the
original implementation of the fusion algorithm with a different
API. It also uses a different strategy to compute the contribution
of each image to each pixel (exact but slow) and has limited
support for voxelsizes.

.. autofunction:: vplants.mars_alt.mars.fusion.original_fusion

.. note:: The actual hard work is done by :func:`vplants.asclepios.vt_exec.reech3d.reech3d`.


Segmentation API
****************

Many of the functions in this section are implemented with :ref:`asclepios_ref_guide`.

.. autofunction:: vplants.mars_alt.mars.segmentation.filtering

.. autofunction:: vplants.mars_alt.mars.segmentation.seed_extraction

.. autofunction:: vplants.mars_alt.mars.segmentation.remove_small_cells

Filters
'''''''

The :func:`~vplants.mars_alt.mars.segmentation.filtering` call
relies on the following functions. Prefer it over directly using
these.

.. autofunction:: vplants.mars_alt.mars.segmentation.mostRepresentative_filter

.. autofunction:: vplants.mars_alt.mars.segmentation.alternate_sequential_filter

.. autofunction:: vplants.mars_alt.mars.segmentation.euclidean_sphere





