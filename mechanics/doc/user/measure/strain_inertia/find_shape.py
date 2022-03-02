import Image
from vplants.plantgl.math import Vector2

ref_im = Image.open("reference_shape.png")
act_im = Image.open("actual_shape.png")

imax,jmax = ref_im.size
ref_shp = [Vector2(i % imax,
                   i / imax) \
           for i,col in enumerate(ref_im.getdata() ) \
           if col[0] == 0]

imax,jmax = act_im.size
act_shp = [Vector2(i % imax,
                   i / imax) \
           for i,col in enumerate(act_im.getdata() ) \
           if col[0] == 0]
