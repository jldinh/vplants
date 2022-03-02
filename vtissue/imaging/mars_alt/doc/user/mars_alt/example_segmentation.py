# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE fusion.rst !!!!!!!!!!!!!

################################################################################
# A simple segmentation example :                                              #
# Starts where example_fusion.py ended                                         #
################################################################################

print "running the example_fusion reconstruction"
from example_fusion import * # this will execute the module.
fusion_do_doc_images = do_doc_images



from vplants.mars_alt.mars.segmentation import cell_segmentation

imseg_t0 = cell_segmentation( fused_im_0_1_2, h_minima=3, volume=1000, real=False,
                              prefilter=True, filter_type="gaussian", filter_value=1.0)




#######################################
# THIS IS NOT PART OF THE EXAMPLE     #
# BUT IS USEFUL FOR THE DOCUMENTATION #
# AS IT CREATES THE FIGURES.          #
#######################################
def do_doc_images():
    from openalea.image.all import SpatialImage
    # fusion_do_doc_images()

    ############################################
    # Save XY cross section of segmented image #
    ############################################
    im = imseg_t0[0]
    imsave("segmented_image.png", SpatialImage(im[:,:,im.shape[2]/2.].T))
