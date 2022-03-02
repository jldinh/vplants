Segmentation
############

In this section we will try to automatically segment an image using watershed algorithm.

This sections starts off where the :ref:`multi_angle_reconstruction` ended. We had a
variable called **fused_im_0_1_2** corresponding to the super-resolution fusion of
three images taken at different angles at the same time step. This is the image we will
segment, so let's go::

    from vplants.mars_alt.segmentation import cell_segmentation

    imseg_t0 = cell_segmentation( fused_im_0_1_2, h_minima=3, volume=1000,
                                  real=False )

The **cell_segmentation** function operates a seed extraction, a watershed, and a cell-volume
filter to remove small cells. The *h_minima* parameter defines the *height* of the frontier
between two bassins below which the two bassins will be merged. The *volume* parameter is the volume
of a cell below which it will be removed. The *real* parameter tells the algorithm to consider
*volume* is given in number of voxels (*real* is **False**) or in real units, *i.e* it takes the voxel
sizes into account (*real* is True).


The updated Visualea dataflow with the cell_segmentation node:

.. dataflow:: vplants.mars_alt.demo.reconstruction mars
