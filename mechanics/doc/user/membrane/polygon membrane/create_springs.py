from vplants.plantgl.math import Vector2
from openalea.mechanics import triangle_frame,\
          isotropic_material2D,PolygonMembrane3D

E = 10e9 #(Pa) #Young's modulus
nu = 0.1 #(None) #Poisson's ratio

mat = isotropic_material2D(E,nu)

fid, = mesh.wisps(2)
pids = tuple(mesh.borders(2,fid,2) )
ref_shape = dict( (pid,Vector2(pos[pid].x,pos[pid].y) ) for pid in pids)

spring = PolygonMembrane3D(pids,
                           mat,
                           ref_shape,
                           thickness)


