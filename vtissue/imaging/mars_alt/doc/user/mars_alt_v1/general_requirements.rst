====================
General Requirements
====================

This page describes the specific requirements of components on which MARS and ALT depends. 

**OpenAlea**

`OpenAlea <http://openalea.gforge.inria.fr/dokuwiki/doku.php>`_ is an open source project primarily aimed at the plant research community, with a particular focus on Plant Architecture Modeling at different scales. It is a distributed collaborative effort to develop Python libraries and tools which address the needs of current and future work in Plant Architecture modeling. OpenAlea includes modules to represent, analyze, and model the functioning and growth of plant architecture.
OpenAlea is developed concurrently on Windows, MacOsX and Linux. The source code is available under a free and libre license. If you are interested in OpenAlea and would like to help it grow, please join in the process.

How to build and install OpenAlea.

* `Installing OpenAlea <http://openalea.gforge.inria.fr/dokuwiki/doku.php?id=download>`_

.. note:: Among all openalea packages you must install at least **container** and **vmanalysis**.


**PyLSM, Free Software Biology to read LSM images**

`PyLSM <http://www.freesbi.ch/en/pylsm>`_ is a python module used to read LSM images. 

How to build and install PyLSM.

* `Installing PyLSM <http://www.freesbi.ch/fr/download>`_


**Numpy, Scientific Computing Tools For Python**

`Numpy <http://numpy.scipy.org/>`_ is a python module used to manipulate N-dimensional array object. 

How to build and install Numpy.

* `Installing Numpy <http://new.scipy.org/download.html>`_

**VTK, Visualization Toolkit**

`VTK <http://www.vtk.org/>`_ is an open-source, freely available software system for 3D computer graphics, image processing and visualization.

How to build and install VTK.

* `Installing VTK <http://www.vtk.org/VTK/resources/software.html#latest>`_

.. note:: When building VTK with CMake, any build options are displayed and you can modify them. VTK_WRAP_PYTHON option must be actived (“ON”).
