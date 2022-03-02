import Image
from math import radians
from vplants.plantgl.math import Vector2,Matrix2

#find points in reference_shape image
ref_im = Image.open("reference_shape.png")

imax,jmax = ref_im.size
ref_shp = [Vector2(i % imax,
                   i / imax) \
           for i,col in enumerate(ref_im.getdata() ) \
           if col[0] == 0]

#find transformation
execfile("create_actual_shape.py")

T = Vector2(200,200)

S = Matrix2()
S[0,0],S[1,1] = (val / 50. for val in shp.radius() )

gt = shp.transformation()

F = Matrix2(gt._m00,gt._m01,gt._m10,gt._m11) * S

act_shp = [F * (vec - (200,200) ) + T for vec in ref_shp]

#test
act_im = Image.open("actual_shape.png")

for vec in act_shp :
	act_im.putpixel(tuple(int(c) for c in vec),(255,0,0) )

act_im.save("actual_shape_test.png")
