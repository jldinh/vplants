############################################
#
print "read confocal image"
#
############################################
#begin read confocal image
from openalea.image import read_inrimage

wall_img = read_inrimage("confocal_image.inr.gz")

#end read confocal image
############################################
#
print "read segmented image"
#
############################################
#begin read segmented image

seg_img = read_inrimage("segmentation.inr.gz")

#end read segmented image
############################################
#
print "read auxin content"
#
############################################
#begin read auxin content
from random import random

auxin = dict( (cid,random() ) for cid in range(2,seg_img.max() + 1) )

#end read auxin content
############################################
#
print "erode cells"
#
############################################
#begin erode cells
from sys import stdout
from numpy import zeros,ones
from scipy.ndimage import binary_opening,binary_erosion
from openalea.image import bounding_box

#create structuring sphere element
struct = ones( (3,3,3) )

#apply it on each cell
res = zeros(seg_img.shape,seg_img.dtype)

print seg_img.max()

for cid in range(2,seg_img.max() + 1) :
	print cid,
	stdout.flush()
	
	loc_im = (seg_img == cid)
	bb = bounding_box(loc_im)
	
	if bb is not None :
		loc_im = loc_im[bb]
		
		loc_im = binary_opening(loc_im,struct,iterations=1)
		loc_im = binary_erosion(loc_im)
		
		res[bb] += loc_im * (cid - 1)

seg_img = seg_img.clone(res + 1)

#end erode cells
############################################
#
print "paint cytoplasm"
#
############################################
#begin paint cytoplasm
from numpy import array,uint32

#defines auxin for virtual cells
auxin[0] = 0.
auxin[1] = 0.

#construct palette
def color (IAA) :
	v = max(0,min(255,int(IAA * 255) ) )
	return (0,v,0,v)

pal = array([color(auxin[cid]) for cid in range(seg_img.max() + 1)],uint32)

#apply on segmented image
auxin_pix = seg_img.clone(pal[seg_img])

#end paint cytoplasm
############################################
#
print "display result"
#
############################################
#begin display result cyto
from openalea.image import imsave
from openalea.image.gui import StackView
from openalea.pglviewer import display

imsave("toto_cyto.png",auxin_pix[:,:,50])

sv = StackView(auxin_pix)
sv.redraw()
display(sv)

#end display result cyto
############################################
#
print "paint walls"
#
############################################
#begin paint walls

#create palette
pal = array([(int(100 + i * 155 / 255.),0,0,0) for i in range(101)] \
          + [(int(100 + i * 155 / 255.),0,0,
              int( (i - 100) * 255 / 155.)) for i in range(101,256)],uint32)

#apply palette
wall_pix = wall_img.clone(pal[wall_img])

#end paint walls
############################################
#
print "merge images"
#
############################################
#begin merge images
from openalea.image import flatten

img = flatten([auxin_pix,wall_pix],alpha = True)

#end merge images

############################################
#
print "display result"
#
############################################
#begin display result walled
imsave("toto_walled.png",img[:,:,50])

sv = StackView(img)
sv.redraw()
display(sv)

#end display result walled



