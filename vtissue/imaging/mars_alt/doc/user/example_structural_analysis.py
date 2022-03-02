# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE reconstruction_tips.rst!!!!!!!!!

# MOST IMPORTANT : DO NOT INSERT OR DELETE LINES
# OR ELSE THE NUMBERING IN reconstruction_tips.rst!!!!!!!!!
# WILL BE WRONG

# OK, the following goes into the doc:

# -- read the data --
from openalea.image.all import imread, display
imort vtissuedata

im = imread( vtissuedata.get_shared_data('segmentation.inr.gz') )
display(im)

# -- Draw walls --
from vplants.mars_alt.analysis.all import draw_walls
walls = draw_walls(im)
display(walls)

# -- Inverse --
from openalea.image.algo.all import reverse_image
walls_inv = reverse_image(walls)
display(walls_inv)

# -- Draw L1 --
from vplants.mars_alt.analysis.all import draw_L1
imL1 = draw_L1(im)
display(imL1)
