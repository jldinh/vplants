

Reconstruction Tips
###################

.. contents::


.. _tips_reg_mips:

Using 2D projections to place 3D points
=======================================

Placing points in 3D space using the `point_selection_tool` can be tedious.
Instead, in some cases, we can project the 3D image into a 2D image (+ an altitude map)
to place the points in 2D. Then the altitude map can be used to recover
the third dimension. We will use :func:`~vplants.mars_alt.mars.reconstruction.im2surface`
to project to 2D, and :func:`~vplants.mars_alt.mars.reconstruction.surface2im`
to recover 3D info.

In a |QtEnSh| (*ie* : `ipython gui=qt`), the imports:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 10-14

Load the reference image:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 18-19

.. figure:: ./images/placeholder.png
    :figwidth: 100%

    Slices at similar places of the two images to register:

    .. plot:: user/plot_reconstruction_tips_1.py

    Placing points is not an easy task here as at similar 3D coordinates the
    the images are very different and placing 3D points in a 2.5D system is
    difficult.


Project the image to 2D and recover the altitude map:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 23-24

Load the floating image:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 28-29

Project it:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 33


.. figure:: ./images/placeholder.png
    :figwidth: 100%

    The projection and altitude map of both images:

    .. plot:: user/plot_reconstruction_tips_2.py

    These are 2D images. The projections give a good feedback
    on the surface of the organ. It is therefore easy to place
    corresponding lamndmarks. The altitude map encodes the depth
    of each pixel so we can retreive the 3D coordinates later on.


Place landmarks on the projected images (see :ref:`oaimage:point_selection_tool` for more details):

.. literalinclude:: example_reconstruction_tips.py
    :lines: 38-39

.. note:: It is important to have the same number of points and that point numbers match between the two images.
          For best results choose points that are well distributed throughout the image. A minimum of 6 pairs of
 	  points should be respected.

.. figure:: ./images/user_registration_with_mask.png
    :width: 60%
    :figwidth: 100%

    Placing matching points on both projections.

Recover REAL coordinates of the points:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 43-44

The *pts0_3D* and *pts1_3D* variables are 3D point lists in real coordinates
(already multiplied by the corresponding images' voxelsizes).

Before going further, in can be good to save them:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 48-49

These points can be used in the reconstruction pipeline:

.. literalinclude:: example_reconstruction_tips.py
    :lines: 51-62

The *recon_results* variable is a list of
:class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructResult` (one per task) that actually
contain the registration output (matrices, deformation fields) of the corresponding task.

The same can be acheived with a dataflow:

.. dataflow:: vplants.mars_alt.demo.reconstruction rigid_resampling


See :ref:`High level mars API <mars_high_level_api>` for details.






.. _centered_rotation_know:

Using prior centered rotation knowledge to initialize the reconstruction
========================================================================

Sometimes, knowledge about the acquisition can be used to initilise the reconstruction.
In this case we consider that the sample was rotated by 90° CCW around the vertical axis
(which matches the Y axis of a |SpatialImage|).

Suppose you have two images:

* *angle_0.inr.gz* is the reference image
* *angle_+90.inr.gz* is the floating one. It has a 90° CCW rotation around the vertical axis and some
   slight translation

The rotation will be corrected manually and the translation automatically.

In a |QtEnSh| (*ie* : `ipython gui=qt`), the imports::

    from openalea.numpy_wralea.creation.numpy_utils import axis_rotation_matrix
    from openalea.image.all import imread, imsave, display

Read the data::

    angle_0  = imread("angle_+0.inr.gz")
    angle_90 = imread("angle_+90.inr.gz")

Create the centered rotation matrix::

     mat = axis_rotation_matrix( "Y", 90.0, min_space=(0.,0.,0.,),
       	      			   max_space = angle_0.real_shape)

.. note:: Since a |resampling transformation| is oriented from the reference space to the
          floating space, the rotation is the opposite of the rotation that places the floating object
	  on the reference object. If the actual angle between the first and the second image
	  had been of 90° CW, which is -90° trigonometrically,
	  the angle argument would have also been -90.0


The reconstruction imports::

    from vplants.mars_alt.mars.reconstruction import (reconstruct, reconstruction_task,
                                                     automatic_linear_parameters)

The reconstruction parameters. We will use an automatic linear registration to recover the translation.
This is :func:`~vplants.mars_alt.mars.reconstruction.automatic_linear_parameters` with the default arguments::

    auto_lin_par = automatic_linear_parameters()

Creating a reconstruction association (task)::

    recon_task0_1 = reconstruction_task(angle0, angle90, initialisation = mat,
                                        auto_linear_params = auto_lin_par)

Computing the registration::

    recons_task, recon_results = reconstruct(recon_task0_1)

See :ref:`High level mars API <mars_high_level_api>` for more details.
