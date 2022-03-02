from math import radians
from time import time
from openalea.plantgl.math import Vector3,norm
from openalea.container import Grid
from openalea.cmechanics import triangle_frame,isotropic_material2D,\
                               TriangleMembrane3D,\
                               ForwardEuler3D,ForwardMarching3D


from vplants.plantgl.scenegraph import Shape,Material,Translated,Scaled,\
                                       Sphere,TriangleSet
from openalea.pglviewer import SceneView,display2D

NB = 4
grid = Grid( (NB + 1,NB + 1) )

pos = dict( (pid,Vector3(grid.coordinates(pid),0) ) for pid in grid)
weight = dict( (pid,1.) for pid in grid)

logout = open("logout.txt",'w')

springs = []
for i in xrange(NB) :
	for j in xrange(NB) :
		#lower right triangle
		pid0 = grid.index( (i,j) )
		pid1 = grid.index( (i + 1,j) )
		pid2 = grid.index( (i + 1,j + 1) )
		fr = triangle_frame(pos[pid0],pos[pid1],pos[pid2])
		lv0 = fr.local_point(pos[pid0])
		assert norm(lv0) < 1e-16
		lv1 = fr.local_point(pos[pid1])
		assert abs(lv1.y) < 1e-16
		lv2 = fr.local_point(pos[pid2])
		rest_shape = (lv1.x,lv2.x,lv2.y)
		
		spring = TriangleMembrane3D([pid0,pid1,pid2],
		                            isotropic_material2D(1.,0.),
		                            rest_shape,
		                            0.1)
		
		springs.append(spring)
		
		#upper left triangle
		pid0 = grid.index( (i,j) )
		pid1 = grid.index( (i,j + 1) )
		pid2 = grid.index( (i + 1,j + 1) )
		fr = triangle_frame(pos[pid0],pos[pid1],pos[pid2])
		lv0 = fr.local_point(pos[pid0])
		assert norm(lv0) < 1e-16
		lv1 = fr.local_point(pos[pid1])
		assert abs(lv1.y) < 1e-16
		lv2 = fr.local_point(pos[pid2])
		rest_shape = (lv1.x,lv2.x,lv2.y)
		
		spring = TriangleMembrane3D([pid0,pid1,pid2],
		                            isotropic_material2D(1.,0.),
		                            rest_shape,
			                        0.1)
		
		springs.append(spring)

def bound (solver) :
	for i in xrange(NB + 1) :
		pid = grid.index( (i,0) )
		F = solver.force(pid)
		solver.set_force(pid,Vector3(F.x,0,F.z) )
	
	for i in xrange(NB + 1) :
		pid = grid.index( (i,NB) )
		F = solver.force(pid)
		if i in (0,NB) :
			solver.set_force(pid,F + (0,0.05,0) )
		else :
			solver.set_force(pid,F + (0,0.1,0) )

def cf () :
	F = dict( (pid,Vector3() ) for pid in grid)
	for sp in springs :
		sp.assign_forces(F,pos)
	
	return F

ini_pos = dict( (pid,Vector3(vec) ) for pid,vec in pos.iteritems() )

#algo = ForwardEuler3D(weight,springs,bound,logout)
algo = ForwardMarching3D(weight,springs,bound,logout)
dt = 1.
tinit = time()
for pid,vec in pos.iteritems() :
	algo.set_position(pid,vec)
algo.deform_to_equilibrium(dt,1e-8)
for pid in pos :
	pos[pid] = algo.position(pid)
print "equilibrium computed in %f s" % (time() - tinit)

for i,sp in enumerate(springs) :
	st = sp.stress(pos)
	fr = triangle_frame(*tuple(pos[pid] for pid in sp.extremities() ) )
	print fr.global_tensor2(st)

logout.close()


#display
sc = SceneView()

sph = Sphere(0.2)

mat = Material( (0,0,255) )
for pid,vec in ini_pos.iteritems() :
	geom = Translated(vec,sph)
	sc.add(Shape(geom,mat) )

mat = Material( (0,255,0) )
for pid,vec in pos.iteritems() :
	geom = Translated(vec,sph)
	sc.add(Shape(geom,mat) )

mat = Material( (0,0,0) )
for sp in springs :
	pt0,pt1,pt2 = (pos[pid] for pid in sp._pids)
	if ( ( (pt1 -pt0) ^ (pt2 - pt0) ) * Vector3.OZ) < 0 :
		pt2,pt1 = pt1,pt2
	
	bary = (pt0 + pt1 + pt2) / 3.
	tr = TriangleSet([pt0,pt1,pt2],[(0,1,2)])
	geom = Translated(bary,
	         Scaled( (0.8,0.8,0.8),
	         Translated( -bary,tr) ) )
	
	sc.add(Shape(geom,mat) )

display2D(sc)

