from openalea.plantgl.all import *
from openalea.vmanalysis.serial.raw_read import read

vertex_prop,edge_prop,face_prop,cell_prop,image_prop=read("meristem_graph.txt")
(dimX,dimY,dimZ,vX,vY,vZ)=image_prop
dimX=int(dimX)
dimY=int(dimY)
dimZ=int(dimZ)
vX=float(vX)
vY=float(vY)
vZ=float(vZ)

pos=dict( (pid,Vector3(coord[0]*vX,coord[1]*vY,-coord[2]*vZ)) for pid,(dum,coord) in vertex_prop.iteritems() )
bary=sum(pos.values(),Vector3())/len(pos)
bary[2]=min(v[2]for v in pos.itervalues())
pos=dict( (pid,v-bary) for pid,v in pos.iteritems() )

sc=Scene()
geom=PointSet(pos.values())
sc.add(Shape(geom,Material((255,0,0))))
mat=Material( (0,255,0) )
for eid,(pids,dum) in edge_prop.iteritems() :
    if len(pids)==2 :
        geom=Polyline([pos[pid] for pid in pids])
        sc.add(Shape(geom,mat))

Viewer.display(sc)
