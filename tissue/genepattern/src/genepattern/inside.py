from openalea.plantgl.math import Vector3
from openalea.plantgl.algo import Octree,Ray

def _inside (point, octree, heading=Vector3(0,0,1), threshold=1e-4) :
	"""
	test wether a point is inside the scene
	maintained by the octree
	"""
	ray = Ray(point,heading)
	count = 0
	intercept = octree.intersection(ray)
	while intercept :# is not None :
		count += 1
		ray.origin = intercept + heading * threshold
		intercept = octree.intersection(ray)
	return count%2 != 0

def inside (point, octree) :
	test=[_inside(point,octree,heading) for heading in (Vector3.OX,Vector3.OY,Vector3.OZ)]
	return test.count(True) > test.count(False)
