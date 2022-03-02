.. _multi_angle_reconstruction:

Multi-Angle-Reconstruction
##########################

In this section we will see how to register and fuse several (potentially anisotropic) images
- acquired from different angles but at the same time step - into one high resolution isotropic
image. First we will see how to register images by pairs, and then how to combine them into
a higher-resolution (super-resolution) image.


Obtaining the data paths from the Package Mananger
==================================================


In this tutorial we are using data from a special python package named vtissuedata
So we must first get the paths to that data::

    # -- import the data package --
    import vtissuedata

    # -- get the paths --
    im0_path_t0 = vtissuedata.get_shared_data("plantB-1.lsm")
    im1_path_t0 = vtissuedata.get_shared_data("plantB-2.lsm")


In the rest of the tutorial, any variable with "0" inside (im0, pts0, etc...) refers to
the reference image used for the reconstruction.

Please note also that MARS works in a single time step, whereas ALT needs two time steps.
Variables suffixed with "*_t0*" or "*_t1*" (*etc...*) refer to the time step they were
acquired (t0 is the first time step, t1 the second time step, and so on...). To simplify
the code, in this document all the data that is manipulated corresponds to one time step.

.. note::

    Of course, you can directly reference your own data paths if they aren't managed by the package manager.




Registering two images
======================

Landmark registration
~~~~~~~~~~~~~~~~~~~~~

This registration method is based on corresponding landmarks placed on each image and we try to minimise
the distance between each pair to obtain a transformation.

To obtain the points you can use the PointSelection tool (see :ref:`using_point_selection`) or
whichever tool you prefer. We will use PointSelection combined with Maximum Intensity Projection (MIP)::

    from PyQt4 import QtGui
    from openalea.image.all import imread, point_selection
    from vplants.mars_alt.mars.all import im2surface, surface2im

    # -- read the two images --
    im0_t0 = imread(im0_path_t0)
    im1_t0 = imread(im1_path_t0)

    # -- project the two images --
    threshold = 45 #: the projection will only consider voxels of intensity higher than this
    mip0, altitude0 = im2surface(im0_t0, threshold_value=threshold)
    mip1, altitude1 = im2surface(im1_t0, threshold_value=threshold)

    # -- place points --
    qapp = QtGui.QApplication([])
    ps0  = point_selection(mip0)
    ps1  = point_selection(mip1)


Now you need to place matching landmarks on both images. Since we did a MIP, the points are placed in 2D.
Now we need to recover full 3D information::

    # -- recover points from views --
    pts0 = ps0.get_points()
    pts1 = ps1.get_points()

    # -- recover REAL coordinates of the points --
    pts0_3D = surface2im(pts0, altitude0)
    pts1_3D = surface2im(pts1, altitude1)


.. note::

    Since we are working with spatial data, images have voxel sizes.
    PointSelection returns point coordinates in voxel coordinates.
    However, to compute a sensible registration, both point sets must
    be expressed in real space (voxel_coordinates * voxel_sizes). This
    is done by surface2im which also retreives the third dimension of points.


.. _configure_registration:

Finally, we compute the registration::

    from vplants.mars_alt.mars.all import reconstruct, reconstruction_task, surface_landmark_matching_parameters

    # -- parameterise the landmark registration --
    ldmark_params = surface_landmark_matching_parameters(pts0_3D, pts1_3D)

    # -- create the reconstruction task --
    recon_task1_0 = reconstruction_task(im0_t0, im1_t0, initialisation = ldmark_params)

    # -- compute the registration --
    recons_task, recon_results = reconstruct(recon_task1_0)


.. _fuse_them:

At this point, **recon_tasks** and **recon_results** contain everything needed to fuse these two images, all
that's missing is one line (well, three with the import and the useful comment) ::

    from vplants.mars_alt.mars.all import fuse_reconstruction
    # -- now, just fuse! --
    fused_im_0_1 = fuse_reconstruction(recons_task, recon_results)


That's it. It might seem overkill for a simple manual registration. However, this way of doing things makes
adding linear and non-linear registrations a breeze. Read on!


The Visualea equivalent:

.. dataflow:: vplants.mars_alt.demo.reconstruction tasks:fusing_two_images_landmarks

Automated Registrations
~~~~~~~~~~~~~~~~~~~~~~~

All you need to do to add automated registrations is to give the parameters for them.
Let's change the few previous lines to add these new registration steps ::

    from vplants.mars_alt.mars.all import reconstruct, reconstruction_task, surface_landmark_matching_parameters
    from vplants.mars_alt.mars.all import automatic_linear_parameters, automatic_non_linear_parameters

    # -- parameterise the landmark registration --
    ldmark_params = surface_landmark_matching_parameters(pts0_3D, pts1_3D)
    # -- parametrise the auto-linear registration --
    auto_lin_params = automatic_linear_parameters(transfo_type='rigid', estimator='ltsw', pyramid_levels=6, finest_level=2)
    # -- parametrise the auto-non-linear registration --
    auto_nonlin_params = automatic_non_linear_parameters(start_level=3, end_level=1)

    # -- create the reconstruction task that registers image 1 on image 0 --
    recon_task0_1 = reconstruction_task(im0_t0, im1_t0, initialisation = ldmark_params,
					auto_rigid_params=auto_lin_params,
					auto_non_linear_params=auto_nonlin_params)

    # -- compute the registration. Now this will take much more time! --
    recons_task, recon_results = reconstruct(recon_task0_1)

    from vplants.mars_alt.mars.all import fuse_reconstruction
    # -- now, just fuse! --
    fused_im_0_1 = fuse_reconstruction(recons_task, recon_results)


And this is how it looks like in Visualea:

.. dataflow:: vplants.mars_alt.demo.reconstruction tasks:fusing_two_images_with_auto


Fusing more images
==================

Fusing more images is simply a matter of adding more reconstruction tasks. For example, if
we are adding a third image registered with the same reference image. We will assume you
have obtained landmarks like previously (projection threshold = 45) for each registration and saved them to files:
    * image 1 on image 0 : "p12-1.txt" contains landmarks for image 0 in **2D voxel** coordinates and
      "p12-2.txt" contains landmarks for image 1 in **2D voxel** coordinates.
    * image 2 on image 0 : "p13-1.txt" contains landmarks for image 0 in **2D voxel** coordinates and
      "p13-3.txt" contains landmarks for image 2 in **2D voxel** coordinates.

.. note::

    The point set for the reference image (0) is different for each task. This is simply
    because we might not find the same correspondences when looking at image 0 and image 1 or looking at image 0
    and image 2.


Here is the full fusion example for three images::

    from PyQt4 import QtGui
    import numpy
    from openalea.image.all import imread, point_selection
    from vplants.mars_alt.mars.all import im2surface, surface2im
    from vplants.mars_alt.mars.all import reconstruct, reconstruction_task, surface_landmark_matching_parameters
    from vplants.mars_alt.mars.all import automatic_linear_parameters, automatic_non_linear_parameters
    from vplants.mars_alt.mars.all import fuse_reconstruction

    # -- import the data package --
    import vtissuedata

    # -- get the paths --
    im0_path_t0 = vtissuedata.get_shared_data("plantB-1.lsm")
    im1_path_t0 = vtissuedata.get_shared_data("plantB-2.lsm")
    im2_path_t0 = vtissuedata.get_shared_data("plantB-3.lsm")

    # -- read them --
    im0_t0 = imread(im0_path_t0)
    im1_t0 = imread(im1_path_t0)
    im2_t0 = imread(im2_path_t0)

    # -- read the point sets --
    #  - point set files in package manager. The file numbers are +1 compared to our variable naming -
    pt_set_names = "p12-1.txt", "p12-2.txt", "p13-1.txt", "p13-3.txt",
    pt_set_paths = [vtissuedata.get_shared_data(pt_set) for pt_set in pt_set_names]
    pts01_0_2D, pts01_1_2D, pts02_0_2D, pts02_2_2D = [numpy.loadtxt(f) for f in pt_set_paths]

    # -- parameterise the landmark registration. Points are in 2D, we ask to spatialise them.
    # For this we need the exact threshold used for the projection that was used to place the points. --
    threshold = 45 #: the projection only considered voxels of intensity higher than this
    ldmark_params_01 = surface_landmark_matching_parameters(pts01_0_2D, pts01_1_2D,
                                                            spatialise_points=True, mip_threshold=threshold)
    ldmark_params_02 = surface_landmark_matching_parameters(pts02_0_2D, pts02_2_2D,
                                                            spatialise_points=True, mip_threshold=threshold)

    # -- parametrise the auto-linear registration --
    auto_lin_params = automatic_linear_parameters(transfo_type='rigid', estimator='ltsw', pyramid_levels=6, finest_level=2)
    # -- parametrise the auto-non-linear registration --
    auto_nonlin_params = automatic_non_linear_parameters(start_level=3, end_level=1)

    # -- create the reconstruction task that registers image 1 on image 0 --
    recon_task0_1 = reconstruction_task(im0_t0, im1_t0, initialisation = ldmark_params_01,
					auto_rigid_params=auto_lin_params,
					auto_non_linear_params=auto_nonlin_params)

    # -- create the reconstruction task that registers image 2 on image 0,
    # Cheat : reuse auto parameters from the previous task. --
    recon_task0_2 = reconstruction_task(im0_t0, im2_t0, initialisation = ldmark_params_02,
					auto_rigid_params=auto_lin_params,
					auto_non_linear_params=auto_nonlin_params)

    # -- compute the registration. Now this will take quite more time! --
    recons_task, recon_results = reconstruct([recon_task0_1, recon_task0_2])

    # -- now, just fuse! --
    fused_im_0_1_2 = fuse_reconstruction(recons_task, recon_results)

    # -- display --
    from openalea.image.all import display
    app = QtGui.QApplication([])
    display(fused_im_0_1_2)


And the Visualea version:

.. dataflow:: vplants.mars_alt.demo.reconstruction tasks:reconstruction
