.. _tissue_graph_segmented3D:

#################################################
Tissue (Graph) construction from segmented image
#################################################

:Version: |version|
:Release: |release|
:Date: |today|

The goal of this document is to describe the core methods used to explore and edit a tissue and its properties. The python script for this example can be downloaded (download file: :download:`create_tissue.py`) along with the image data file (download file: :download:`segmentation.inr.gz`). To run the script it must be in the same directory than the image file and run in a shell console using::

	user@computer:$ python create_tissue.py


-------------------------
Read image
-------------------------

.. literalinclude:: create_tissue.py
    :start-after: #begin read image
    :end-before: #end read image

-------------------------
Extract tissue
-------------------------

.. literalinclude:: create_tissue.py
    :start-after: #begin extract tissue
    :end-before: #end extract tissue

-------------------------
Filter tissue
-------------------------

.. literalinclude:: create_tissue.py
    :start-after: #begin filter tissue
    :end-before: #end filter tissue

-------------------------
Draw tissue
-------------------------

.. literalinclude:: create_tissue.py
    :start-after: #begin draw tissue
    :end-before: #end draw tissue

-------------------------
Display tissue
-------------------------

.. literalinclude:: create_tissue.py
    :start-after: #begin display tissue
    :end-before: #end display tissue


