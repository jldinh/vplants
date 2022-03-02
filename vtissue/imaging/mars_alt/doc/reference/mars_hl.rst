.. Openalea Documentation (2011)
.. intitutes : INRIA, CIRAD, INRA
.. authors : Daniel BARBEAU (INRIA)

.. _mars_high_level_api:

High Level API
##############

This section presents high level functions that let you do
registrations, fusions and segmetations without the hassle
of knowing how they internally work.

Introduction : Tasks
====================

The high-level **Reconstruction** and **Fusion** API both use a "task"
concept. A *task* is an association of *what* will be processed
and *how* it will be processed. This allows the user to specify processes
and the system will ensure they are ordered in a coherent manner.


.. note::

    While these APIs are easy to use and rather flexible, they
    might not suite your need and you might want to build
    your own pipeline with the :ref:`low level api <mars_low_level_api>`.

Registration
************

**Registration** is an operation where we try to find the best transformation
that places an object B (floating) on an object A (reference).

If we want to register "floating_0.inr.gz" and "floating_1.inr.gz" on "reference.inr.gz"
with an automatic linear registration and then fuse them to a superresolution
image we first import the necessary functions::

   from openalea.image.all import imread, imsave, display
   from vplants.mars_alt.mars.reconstruction import reconstruction_task, automatic_linear_parameters
   from vplants.mars_alt.mars.reconstruction import reconstruct, fuse_reconstruction


We read the images ::

   imref = imread("reference.inr.gz")
   imflo_0 = imread("floating_0.inr.gz")
   imflo_1 = imread("floating_1.inr.gz")


We build the *reconstruction task* and request a reconstruction (registration)::

   task_0 = reconstruction_task( imref, imflo_0, auto_linear_params = automatic_linear_parameters() )
   task_1 = reconstruction_task( imref, imflo_1, auto_linear_params = automatic_linear_parameters() )
   tasks, recon_results = reconstruct([task_0, task_1])


The we can fuse them into a super-resolution (if relevant) and display the fused image::

   fused_im = fuse_reconstruction(tasks, recon_results)
   display(fused)

And save it::

    imsave("fused.inr.gz", fused)


Fusion
******

Fusion is an operation where several acquisitions of the same
object are meaned together to obtain a final image of the object
with a higher definition.

.. note:: This example is a spin-off of :ref:`centered_rotation_know`.

If we have two images ("angle_0.inr.gz" and "angle_1.inr.gz")
of the same object with a 90° rotation around Y axis
and want to fuse them together, first in a |QtEnSh| import the relevant functions::

    from openalea.image.all import imread, imsave, display
    from openalea.numpy_wralea.creation.numpy_utils import axis_rotation_matrix
    from openalea.image.registration.matrix import matrix_real2voxels

Read the images::

     angle_0 = imread("angle_0.inr.gz")
     angle_1 = imread("angle_1.inr.gz")
     angle_2 = imread("angle_2.inr.gz")

Create a resampling rotation matrix (see |resampling transformation| for details).
The rotation is centered in angle_0's bounding box::

    mat_1 = axis_rotation_matrix( "Y", 90.0, min_space=(0.,0.,0.,),
    	      			  max_space = angle_0.real_shape)
    mat_2 = axis_rotation_matrix( "Y", 180.0, min_space=(0.,0.,0.,),
    	      			  max_space = angle_0.real_shape)



The :func:`~openalea.numpy_wralea.creation.numpy_utils.axis_rotation_matrix` call
creates a 4x4 real-space rotation matrix. The *min_space* and *max_space* arguments are used
to center the rotation in the middle of that space.

.. note:: Since a resampling transformation is oriented from the reference space to the
          floating space, the rotation is the opposite of the rotation that places the floating object
	  on the reference object.

We must convert *mat_1* and *mat_2* to a |resampling transformation| using
:func:`~openalea.image.registration.matrix.matrix_real2voxels`::

    mat_1 = matrix_real2voxels(mat_1, angle_1.voxelsize, angle_0.voxelsize)
    mat_2 = matrix_real2voxels(mat_2, angle_2.voxelsize, angle_0.voxelsize)

Create the fusion tasks, fuse, display::

    task_0 = fusion_task(angle_0)
    task_1 = fusion_task(angle_1, [mat_1])
    task_2 = fusion_task(angle_2, [mat_2])

    fused = fusion([task_0, task_1, task_2])

    display(fused) # make sure there's a QApplication before!!!

Save::

    imsave("fused_multiangle.inr.gz", fused)


Reference
=========

Registration API
****************

.. autofunction:: vplants.mars_alt.mars.reconstruction.reconstruct

.. autofunction:: vplants.mars_alt.mars.reconstruction.fuse_reconstruction

.. autofunction:: vplants.mars_alt.mars.reconstruction.reconstruction_task

.. autofunction:: vplants.mars_alt.mars.reconstruction.surface_landmark_matching_parameters

.. autofunction:: vplants.mars_alt.mars.reconstruction.automatic_linear_parameters

.. autofunction:: vplants.mars_alt.mars.reconstruction.automatic_non_linear_parameters

Interchange structures
''''''''''''''''''''''
.. autoclass::  vplants.mars_alt.mars.reconstruction.ImageReconstructTask

.. autoclass::  vplants.mars_alt.mars.reconstruction.ImageReconstructResult

Fusion API
**********

.. autofunction:: vplants.mars_alt.mars.fusion.fusion_task

.. autofunction:: vplants.mars_alt.mars.fusion.fusion

.. autoclass:: vplants.mars_alt.mars.fusion.attenuation


Segmentation API
****************

.. autofunction:: vplants.mars_alt.mars.segmentation.cell_segmentation
