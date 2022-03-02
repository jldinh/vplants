.. _tissue_reference:

Tissue Reference Guide
#######################

:Version: |version|
:Release: |release|
:Date: |today|

Tissue simulation use numerous atomic packages to manage each aspect of tissues:
 - `openalea.celltissue <../../../../../celltissue/doc/_build/html/user/autosum.html>`_ propose a general data structure to encapsulate:
    - multi-topological representations of tissues
    - properties associated with elements of a tissue
 - `openalea.tissueshape <../../../../../tissueshape/doc/_build/html/user/autosum.html>`_ deals with geometrical aspects of a tissue:
    - geometrical embedding of tissue topological structure in 1D, 2D or 3D spaces
    - predefined tissue like grids
 - `openalea.tissueview <../../../../../tissueview/doc/_build/html/user/autosum.html>`_ offers numerous representions of tissues used to display informations.
 - `openalea.tissueedit <../../../../../tissueedit/doc/_build/html/user/autosum.html>`_ inconjonction with `openalea.tissueview <../../../../../tissueview/doc/_build/html/user/autosum.html>`_ allows graphically to edit tissue structure and properties associated with a tissue.

Build on top of these packages, other packages offer other aspects of tissue simulation:
 - `openalea.genepattern <../../../../../genepattern/doc/_build/html/user/autosum.html>`_ to play with abstract gene expression patterns.
 - `openalea.growth <../../../../../growth/doc/_build/html/user/autosum.html>`_ offers some pure geometrical growth functions.
 - `openalea.vmanalysis <../../../../../vmanalysis/doc/_build/html/user/autosum.html>`_ allow to construct tissues from 3D stacks of confocal images.
