.. _mars_alt_user:

Welcome to the MARS-ALT user guide
##################################

.. contents::


In the current documentation, there are two versions of the
MARS_ALT pipeline described
here as the *Alpha* version and the *Beta* version. The first one
is quite low level and you have to handle by yourself the proper
chaining of functions. The Beta version is a higher abstraction
of the pipeline which hides the complexity of type/matrices
conversions that are needed between two pieces of the pipeline.

We recommend you use the Beta version, also know as the
"task based" version.

We will merge the two versions of the documentation as time allows.

.. warning::

    The algorithms used in MARS-ALT are extremely RAM hungry.
    We recommend using a 64 bits operating system with at
    least 8 gigabytes of RAM.


.. toctree::
    :maxdepth: 2

    The MARS-ALT Tutorial <mars_alt/tutorial.rst>
    Reconstruction tips <reconstruction_tips.rst>
    Segmentation tips <segmentation.rst>
    Modeling and Structural Analysis <analysis.rst>


The attic
=========

This section contains documentation that hasn't been reviewed
for some time and is probably outdated but can still be useful.


.. toctree::
    :maxdepth: 1

    reconstruction_old.rst
    visualization_old.rst
    reference_mars_v2_old.rst
    reference_alt_v2_old.rst
