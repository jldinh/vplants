from xml.dom.minidom import Document
from openalea.vmanalysis.serial.raw_read import read

vertex_prop,edge_prop,face_prop,cell_prop,image_prop=read("meristem_graph.txt")
x=0.
(dimX,dimY,dimZ,vX,vY,vZ)=image_prop
dimX=int(dimX)
dimY=int(dimY)
dimZ=int(dimZ)
vX=float(vX)
vY=float(vY)
vZ=float(vZ)
d=Document()

meristem=d.createElement("meristem")
d.appendChild(meristem)

for cid,(fidlist,(vox,vol,lay,barX,barY,barZ)) in cell_prop.iteritems() :
    cell=d.createElement("cell")
    cell.setAttribute("id","%d" % cid)
    cell.setAttribute("layer","%d" % lay)
    node=d.createElement("volume")
    node.setAttribute("voxels","%d" % vox)
    node.setAttribute("real","%f" % vol)
    cell.appendChild(node)
    coords=d.createElement("center_of_mass")
    coords.setAttribute("X","%f" % (barX*vX))
    coords.setAttribute("Y","%f" % (barY*vY))
    coords.setAttribute("Z","%f" % (barZ*vZ))
    cell.appendChild(coords)
    meristem.appendChild(cell)

f=open("morphometry.xml",'w')
f.write(d.toprettyxml())
f.close()

d=Document()
meristem=d.createElement("meristem")
d.appendChild(meristem)

for vid,(pouet,(coordX,coordY,coordZ)) in vertex_prop.iteritems() :
    vertex=d.createElement("vertex")
    vertex.setAttribute("id","%d" % vid)
    coords=d.createElement("coordinates")
    coords.setAttribute("X","%f" % (coordX*vX))
    coords.setAttribute("Y","%f" % (coordY*vY))
    coords.setAttribute("Z","%f" % (coordZ*vZ))
    vertex.appendChild(coords)
    meristem.appendChild(vertex)

for eid,(vid,noun) in edge_prop.iteritems() :
    edge=d.createElement("edge")
    edge.setAttribute("id","%d" % eid)
    vertices=d.createElement("vertices")
    vid1,vid2=vid
    vertices.setAttribute("v1","%d" % vid1)
    vertices.setAttribute("v2","%d" % vid2)
    edge.appendChild(vertices)
    meristem.appendChild(edge)

for fid,(listeFaces) in face_prop.iteritems() :
    face=d.createElement("face")
    face.setAttribute("id","%d" % fid)
    edges=d.createElement("edges")
    for vals in listeFaces:
        if vals == None :
            a=1
        else :
            i=1
            for val in vals:
                edges.setAttribute("edge_%.3d" % i,"%d" % val)
                i=i+1
    face.appendChild(edges)
    meristem.appendChild(face)

for cid,(fidlist,(vox,vol,lay,barX,barY,barZ)) in cell_prop.iteritems() :
    cell=d.createElement("cell")
    cell.setAttribute("id","%d" % cid)
    cell.setAttribute("layer","%d" % lay)
    node=d.createElement("volume")
    node.setAttribute("voxels","%d" % vox)
    node.setAttribute("real","%f" % vol)
    cell.appendChild(node)
    coords=d.createElement("center_of_mass")
    coords.setAttribute("X","%f" % (barX*vX))
    coords.setAttribute("Y","%f" % (barY*vY))
    coords.setAttribute("Z","%f" % (barZ*vZ))
    cell.appendChild(coords)
    faces=d.createElement("faces")
    i=1
    for vals in fidlist:
        if vals is None :
            a=1
        else :
            faces.setAttribute("face_%.3d" % i,"%d" % vals)
            i=i+1
    cell.appendChild(faces)
    meristem.appendChild(cell)
f=open("graph.xml",'w')
f.write(d.toprettyxml())
f.close()
