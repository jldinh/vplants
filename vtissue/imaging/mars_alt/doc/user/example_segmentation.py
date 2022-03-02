# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE reconstruction_tips.rst!!!!!!!!!

# MOST IMPORTANT : DO NOT INSERT OR DELETE LINES
# OR ELSE THE NUMBERING IN reconstruction_tips.rst!!!!!!!!!
# WILL BE WRONG


from openalea.image.all import imread, display
import vtissuedata

# -- load the data --
im_fus = imread( vtissuedata.get_shared_data("t1_fused.inr.gz") )
w1 = display(im_fus)

# -- filter the image with asf --
from vplants.mars_alt.mars.segmentation import filtering
img_d_asf = filtering(im_fus,filter_type="asf",filter_value=3)

# -- or with gauss --
img_d_gauss = filtering(im_fus,"gaussian",0.5)

# -- Seed extraction --
from vplants.mars_alt.mars.segmentation import seed_extraction
seeds = seed_extraction(img_d_asf,3)
w2 = display(seeds)

# -- Watershed --
from vplants.asclepios.vt_exec.watershed import watershed
wat = watershed(seeds,im_fus)
w3 = display(wat)

# -- Over segmentation correction --
from vplants.mars_alt.mars.segmentation import remove_small_cells
new_seeds = remove_small_cells(wat,seeds,volume=1000,real=False)
new_wat = watershed(new_seeds,im_fus)
