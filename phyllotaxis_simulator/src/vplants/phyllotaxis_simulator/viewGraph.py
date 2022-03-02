from numpy import array
from openalea.container.graph import Graph
from openalea.plantgl.all import *
import pickle

gObj = Graph()
#fobj = file("ppos.yr", "r")
fobj = file("parastichies_1.pk", "r")
(parastichiesGraph, primordiaPositions) = pickle.load(fobj)
for i in parastichiesGraph.vertices():
    print i
pNb = parastichiesGraph.nb_vertices()
fobj.close()
        
def view(vertex_radius=1, edge_radius=0.1):
    vertices = dict((i, primordiaPositions[i]) for i in xrange(pNb))
    newEdges = [(parastichiesGraph.source(i), parastichiesGraph.target(i))for i in parastichiesGraph.edges()]
    scene = Scene()
    sphere = Sphere(vertex_radius)
    for v,pos in vertices.iteritems():
        color = Material(Color3(100,200,10))
        newP = (pos[0], pos[1], pos[2])
        shape = Shape(Translated(newP, sphere), color)
        scene.add(shape)
        
    for k, v in newEdges:
        if k >1 and v > 1:
            color = Material(Color3(0,0,200))
            geom = Polyline([vertices[k], vertices[v]], width= 1 + int(edge_radius))
            shape = Shape(geom, color)
            scene.add(shape)
        
    return scene

scene = view()
Viewer.display(scene)
raw_input('type enter')
