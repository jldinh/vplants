.. Openalea Documentation (2011)
.. intitutes : INRIA, CIRAD, INRA
.. authors : Daniel BARBEAU (INRIA)

.. _alt_low_level_api:

Low Level API
#############

Introduction
============


.. note::

    This section documents atomic alements forming the whole
    ALT pipeline. They are presented here so you can try
    to customize the pipeline. However, if you just want to
    try out the ALT loop, consider looking at
    :ref:`high level api <alt_high_level_api>`.


Initialisation
==============

Registration
============



Mapping
=======

The mapping process combines finding the candidate lineages (a lineage with costs per child)
and getting the best lineage out of this lineage by a flow graph algorithm.

.. autofunction:: vplants.mars_alt.alt.mapping.mapping

The :func:`~vplants.mars_alt.alt.mapping.mapping` function actually delegates to
an instance of a :class:`~vplants.mars_alt.alt.mapping.LineageTracking` subclass:


.. autoclass:: vplants.mars_alt.alt.mapping.LineageTracking
    :members:

.. autoclass:: vplants.mars_alt.alt.mapping.RomainLineageTrackingDummyWrapper
    :members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: vplants.mars_alt.alt.mapping.PyLineageTracking
    :members:
    :show-inheritance:
    :inherited-members:


Candidate Lineages
''''''''''''''''''

.. automodule:: vplants.mars_alt.alt.candidate_lineaging
    :members: rfernandez_get_candidate_successors, py_get_candidate_successors


Flow Graph
''''''''''

.. automodule:: vplants.mars_alt.alt.optimal_lineage
    :members: rfernandez_flow_solving, nx_flow_solving


Lineage Filtering (optimisation)
''''''''''''''''''''''''''''''''
.. autofunction:: vplants.mars_alt.alt.update_lineages.update_lineage


Testing functions
'''''''''''''''''

.. autofunction:: vplants.mars_alt.alt.candidate_lineaging.equal_lineages

.. autofunction:: vplants.mars_alt.alt.candidate_lineaging.compare_lineages

.. autofunction:: vplants.mars_alt.alt.candidate_lineaging.candidate_contains_expert

