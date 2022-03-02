Tracking Cell Lineages
######################

This section will present you how to identify cell lineages between images
of an organ acquired at two different time steps.

In the previous section we saw how to obtain high resolution images from
multi-angle acquisitions, and how to segment those images.

We will start off with those segmented images. First of all, we need to register
the two images into the same space. The image at time 0 will be put in the space
of the image at time 1 (Fernandez 2010, $5.4.1). To do so we need an initial
mapping where cells from image 0 are "mapped to" (*i.e.* assigned as parents of)
cells image 1 ::

    from vplants.mars_alt.gui import something
    print "TODO: put some sensible code to do an initial mapping"
    expert_mapping = "..." # TBD


Now we can prepare the ALT process::

    from vplants.mars_alt.alt.all import alt_preparation

    # -- We obtained imseg_t0 and imseg_t1 in the segmentation step.
    # They correspond to the segmentation of the organ a time 0 and at time 1 --


    fus_prime, seg_prime, ts0, ts1, trsf_vox = alt_preparation(expert_mapping,
                                                               imseg_t0, imseg_t1,
                                                               resampled=False)


This function will essentially compute a rigid transform *trsf_vox* of t0 on t1. The *resampled=False* parameter tells the
function **not** to compute the resampled version of the fused t0 image nor that of the segemented t0 image.
For this reason, fus_prime and seg_prime will be None.

The *ts0* and *ts1* variables are graphs that represent the topology of each segmented organ.

Finally we can run the lineaging algorithm::

    from vplants.mars_alt.alt.all import alt_loop
    from vplants.mars_alt.alt.all import has_descendant_filter, growth_conservation_filter, \
                                         one_connected_component_filter, adjacencies_preserved_filter

    # -- Create the rules that will be used to clean the computed lineages --
    filters = [has_descendant_filter(), growth_conservation_filter(),
               one_connected_component_filter(), adjacencies_preserved_filter()]

    # -- the following call can take some time! --
    final_map, reason, scores = alt_loop(imseg_t0, imseg_t1, expert_mapping, ts0, ts1, mat_init=trsf_vox, filter_params=filters)

The **alt_loop** function will iteratively try to converge to a stable mapping by performing
an alternate deformation field computation and lineage estimation and optimsation (Fernandez 2010, $5.4.1).


