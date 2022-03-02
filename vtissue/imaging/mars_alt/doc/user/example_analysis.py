# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE reconstruction_tips.rst!!!!!!!!!

# MOST IMPORTANT : DO NOT INSERT OR DELETE LINES
# OR ELSE THE NUMBERING IN reconstruction_tips.rst!!!!!!!!!
# WILL BE WRONG

# OK, the following goes into the doc:
from openalea.image.all import imread, display
import vtissuedata

im = imread( vtissuedata.get_shared_data('segmentation.inr.gz') )
display(im)

# -- First, let us read the properties of tissue with the function :func:`VTissueAnalysis`. --

from vplants.mars_alt.analysis.all  import VTissueAnalysis
properties = VTissueAnalysis(im)

# -- Number of cells --

properties.nlabels()

# -- Center of mass For a single cell : --

properties.center_of_mass(255)

# -- To compute the center of mass in voxels : --

properties.center_of_mass(255, real=False)

# -- Center of mass For a sequence of cells : --

properties.center_of_mass([265,300])

# -- Center of mass For all of cells : --

properties.center_of_mass()

# -- Volume For a single cell : --

properties.volume(255)

# -- To compute the volume in voxels : --

properties.volume(255, real=False)

# -- Volume For a sequence of cells : --

properties.volume([265,300])

# -- Volume For all of cells : --

properties.volume()

# -- Neighbors For a single cell : --

properties.neighbors(255)

# -- Neighbors For a sequence of cells : --

properties.neighbors([265,300])

# -- Neighbors For all of cells : --

properties.neighbors()

# -- Shared surface area of two neighboring cells --

properties.surface_area(255,1)

# -- Extract cells in the layer 1 --

from vplants.mars_alt.analysis.all import extract_L1
L1 = extract_L1(im)

