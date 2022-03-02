def read (filename) :
    f=open(filename,'r')
    lines=f.readlines()
    f.close()
    offset=0
    while "++++++++++++++++" not in lines[offset] :
        offset+=1
    gr=lines[offset+1].split(":")
    elem=gr[1].split(" ")
    dimX=int(elem[0])
    dimY=int(elem[1])
    dimZ=int(elem[2])
    vX=float(elem[3])
    vY=float(elem[4])
    vZ=float(elem[5])
    image_prop=([dimX,dimY,dimZ,vX,vY,vZ])
    
    while "-------------------" not in lines[offset] :
        offset+=1
    ########################################################
    #
    #	read vertices
    #
    ########################################################
    vertex_offset=offset+2
    nb_vertices=int(lines[vertex_offset][7:])
    vertex_prop={}
    for line in lines[vertex_offset+1:vertex_offset+nb_vertices+1] :
        gr=line.replace("\n","").split(":")
        vertex_prop[int(gr[0])]=(None,tuple(float(val) for val in gr[1].split(" ") if len(val)>0))
    
    ########################################################
    #
    #	read edges
    #
    ########################################################
    edge_offset=vertex_offset+nb_vertices+2
    nb_edges=int(lines[edge_offset][5:])
    edge_prop={}
    for line in lines[edge_offset+1:edge_offset+nb_edges+1] :
        gr=line.replace("\n","").split(":")
        edge_prop[int(gr[0])]=(tuple(int(val) for val in gr[1].split(" ") if len(val)>0),None)
    
    ########################################################
    #
    #	read faces
    #
    ########################################################
    face_offset=edge_offset+nb_edges+2
    nb_faces=int(lines[face_offset][5:])
    face_prop={}
    for line in lines[face_offset+1:face_offset+nb_faces+1] :
        gr=line.replace("\n","").split(":")
        face_prop[int(gr[0])]=(tuple(int(val) for val in gr[1].split(" ") if len(val)>0),None)
     
    ########################################################
    #
    #	read cells
    #
    ########################################################
    cell_offset=face_offset+nb_faces+2
    nb_cells=int(lines[cell_offset][5:])
    cell_prop={}
    for line in lines[cell_offset+1:cell_offset+nb_cells+1] :
        gr=line.replace("\n","").split(":")
        vox,vol,lay,barX,barY,barZ=gr[1].split(" ")
        vox=int(vox)
        vol=float(vol)
        lay=int(lay)
        barX=float(barX)
        barY=float(barY)
        barZ=float(barZ)
        cell_prop[int(gr[0])]=(tuple(int(val) for val in gr[2].split(" ") if len(val)>0),(vox,vol,lay,barX,barY,barZ) )
    
    return vertex_prop,edge_prop,face_prop,cell_prop,image_prop

