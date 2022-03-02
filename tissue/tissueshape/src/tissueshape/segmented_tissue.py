# -*- python -*-
#
#       tissueshape: function used to deal with tissue geometry
#
#       Copyright 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__ = """
This module defines functions to create a tissue from a segmented 3D image
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from sys import stdout

from scipy import ndimage
import numpy as np
from numpy import array,add,outer
from numpy.linalg import eig,norm
from openalea.celltissue import Tissue,TissueDB,Config,ConfigItem

def mult(l):
   return reduce(lambda x,y:x*y,l)

def dilation(slices):
    return [ slice(max(0,s.start-1), s.stop+1) for s in slices]

def shift(slices, axis=0, positive = True):
    s = list(slices)
    temp = s[axis]
    s[axis] = slice(max(0,temp.start-1), temp.stop+1)
    return s

def mask_image(label_id, slices, img):
    slices = dilation(slices)
    bbox = img[slices]
    mask_img = (bbox == label_id)
    return mask_img,slices

def compute_neigh(label_id, slices, img):
    mask_img,slices = mask_image(label_id, slices, img)
    neigh = set()
    for a in (0,1,2):
            slice_shift = shift(slices,a)
            view = img[slice_shift]
            mask_view = view[mask_img]
            neigh.update(np.unique(mask_view[mask_view!=label_id]))
    return neigh

def binary_structs():
    s=[]
    struct = np.zeros((3,3,3),np.bool)
    struct[:,1,1] = True
    s.append(struct)
    struct = np.zeros((3,3,3),np.bool)
    struct[1,:,1] = True
    s.append(struct)
    struct = np.zeros((3,3,3),np.bool)
    struct[1,1,:] = True
    s.append(struct)
    return s

def wall_surface(img, bbox_img, slices, label_id, neighbors, res):
    #def wall_surface( bbox_img, label_id, neighbors, res):
    neigh = [n for n in neighbors if n > label_id or n ==1]
    mask_img = (bbox_img == label_id)
    wall = {}

    xyz_structs = binary_structs()

    for a in (0,1,2):
        dil = ndimage.binary_dilation(mask_img, structure=xyz_structs[a])
        fronter = bbox_img[dil-mask_img]

        for n in neigh:
            nb_pix = len(fronter[fronter==n])
            surf = nb_pix*res[a]
            i,j = min(label_id,n), max(label_id,n)
            nbp, s = wall.get((i,j),(0,0.))
            wall[i,j] = nbp+nb_pix, s+surf

    return wall

def barycenter(img,labels,real=True):
    """
    Return the center of mass of the labels.

    :Parameters:
        - `img` (SpatialImage) - Segmented image
        - `real` (bool, optional) - If real = True, center of mass is in real-world units else in voxels.

    :Examples:

    >>> import numpy as np
    >>> a = np.array([[1, 2, 7, 7, 1, 1],
                  [1, 6, 5, 7, 3, 3],
                  [2, 2, 1, 7, 3, 3],
                  [1, 1, 1, 4, 1, 1]])

    >>> barycenter(a)
    [[1.8, 2.2999999999999998],
    [1.3333333333333333, 0.66666666666666663],
    [1.5, 4.5],
    [3.0, 3.0],
    [1.0, 2.0],
    [1.0, 1.0],
    [0.75, 2.75]]
    """
    img_type = img.astype(np.float)
    center = ndimage.center_of_mass(img_type, img_type, index=labels)
    if real is True:
        center = np.multiply(center,img.resolution)
        return center.tolist()
    else:
        return center


def volume(img,labels, real=True):
    """
    Return the volume of the labels.

    :Parameters:
        - `real` (bool, optional) - If real = True, volume is in real-world units else in voxels.

    :Examples:

    >>> import numpy as np
    >>> a = np.array([[1, 2, 7, 7, 1, 1],
                     [1, 6, 5, 7, 3, 3],
                     [2, 2, 1, 7, 3, 3],
                     [1, 1, 1, 4, 1, 1]])

    >>> volume(a)
    [10.0, 3.0, 4.0, 1.0, 1.0, 1.0, 4.0]
    """
    _volume = ndimage.sum(np.ones_like(img), img, index=labels)
    if real is True:
        _volume = np.multiply(_volume,mult(img.resolution))
        return _volume.tolist()
    else:
        return _volume

def contact_surface(mask_img,label_id):
    #background = 1
    img = wall(mask_img,label_id)
    neigh = set()
    neigh.update(np.unique(img))
#X     if background in neigh:
#X         neigh.remove(1)
    return neigh

def wall(mask_img,label_id):
    img = mask_img==label_id
    dil = ndimage.binary_dilation(img)
    contact = dil - img
    return mask_img[contact]

def create_graph_tissue (img, debug_info = True) :
    """Construct a tissue from a segmented image

    .. warning:: by convention index 0 correspond to the external part of the
                 image and index 1 correspond to the external part of the
                 tissue. Hence, the constructed tissue will have a cell 0
                 and 1 without volume

    .. warning:: the geometrical center of voxel i,j,k is
                 (i + 0.5,j + 0.5,k + 0.5) * im.resolution

    .. warning:: in the image i correspond to y and j to x

    :Parameters:
     - `img` (LxMxN array of int) - a 3D array where each voxel contains the
                                    the id of the cell it belongs to.
     - `debug_info` (bool) - tells the algo to display evolution

    :Returns: a tissue that contains :
     - a graph from cell neighborhood
     - the volume of each cell
     - the contact surface of each wall (edge) between two cells
     - the barycenter of each cell
     - the principal directions of each cell
     - the number of voxels in each cell
     - the number of voxel faces in each wall

    :Returns Type: TissueDB
    """

    # Create a structure :
    # - list all the cells (regions having a different label):
    #    np.unique(img)
    # - compute the neighborhood of each cell
    #  -
    imax,jmax,kmax = img.shape
    try :
        res = array(img.resolution)
    except AttributeError :
        res = array([1.,1.,1.])

    Sres = array([res[1] * res[2],res[2] * res[0],res[0] * res[1] ])
    Vres = res[0] * res[1] * res[2]

    ########################################################

    slice_label = ndimage.find_objects(img)[1:]
    facets = {}
    facets_nb = {}

    vertices = np.unique(img)
    edges = {} # store src, target
    walls = {} # store surface, nb for each wall

    ident = np.identity(3)
    inertia_eig_vec = {}
    inertia_eig_val = {}

    ########################################################
    # for each cell, we compute the volume, the barycenter and nb pixels

    NbPixels= volume(img, vertices, real=False)
    #Volumes = volume(img, vertices)
    Volumes= np.multiply(NbPixels,mult(res)).tolist()
    Barycenters = barycenter(img,vertices)
    # inertia axis

    assert (len(Volumes) == len(NbPixels) == len(Barycenters))

    #properties
    V = dict(zip(vertices,Volumes)) #cell volume
    nb = dict(zip(vertices,NbPixels)) #number of elements that geometricaly define an element
    bary = dict(zip(vertices,Barycenters)) #cell barycenter

    #########################################################

    for label, slices in enumerate(slice_label):
        # label_id = label +2 because the label_id begin at 2
        # and the enumerate begin at 0.
        label_id = label+2

        # sometimes, the label doesn't exist ans slices is None
        if slices is None:
           continue

        ex_slices = dilation(slices)
        mask_img = img[ex_slices]
        #neigh = compute_neigh(label_id, slices, img)
        neigh = list(contact_surface(mask_img,label_id))

        edges[label_id]=neigh

        # compute wall surface and nb wall elements
        edge_wall = wall_surface(img, mask_img, ex_slices, label_id, neigh, Sres)
        walls.update(edge_wall)

        # compute displacements of cell elements from barycentre
        b = bary[label_id]	# the barycentre of this cell
        pts = np.indices(mask_img.shape) # 3 element array of arrays, corresponding to x,y,z coordinates
        disp = np.zeros_like(pts)  # displacement from barycentre
        disp[0] = pts[0] - b[0]
        disp[1] = pts[1] - b[1]
        disp[2] = pts[2] - b[2]
        # compute moment of inertia matrix
        off_diags = array([[disp[0]*disp[0],disp[0]*disp[1],disp[0]*disp[2]],
                           [disp[1]*disp[0],disp[1]*disp[1],disp[1]*disp[2]],
                           [disp[2]*disp[0],disp[2]*disp[1],disp[2]*disp[2]]])
        off_diag_sum = sum_array(off_diags) #This and previous should have been done by next line but np.cov crashed
        #off_diag_sum = np.cov(disp)  # Finds outer(disp,disp) at each point and sums over points (covariance matrix)
        off_trace = np.trace(off_diag_sum)  # Finds sum over displacements
        I_principal = ident * off_trace
        I = (I_principal - off_diag_sum) #  Might need correction for resolution, like #/ float(len(flatten(mask_img)) )

        #compute eigen values
        w,v = eig(I)
        inertia_eig_vec[label_id]=v
        inertia_eig_val[label_id]=w

    ########################################################
    # for each wall, compute the surface and nb pixels
    # return edges

    ########################################################
    #create tissue
    t = Tissue()
    CELL = t.add_type("CELL")
    WALL = t.add_type("WALL")

    # remove info for background image
    V[1] = nb[1] = 0
    del bary[1]

    S = {} #wall surface
    axes = {} #cell main axes

    #create graph
    graph_id = t.add_relation("graph",(CELL,WALL) )
    graph = t.relation(graph_id)

    graph.add_vertex(0)
    for cid in vertices:
        graph.add_vertex(cid)

    _edges = set( (min(src, tgt), max(src, tgt)) for src,l in edges.iteritems() for tgt in l )

    for src, tgt in _edges :
        eid = graph.add_edge(src, tgt)
        nb[eid], S[eid] = walls[src,tgt]

    #geometrical descriptors
    if debug_info :
        print "geometrical descriptors"
    ident = np.identity(3)

    #write result
    db = TissueDB()
    db.set_tissue(t)

    cfg = Config("topology")
    cfg.add_item(ConfigItem("CELL",CELL) )
    cfg.add_item(ConfigItem("WALL",WALL) )
    cfg.add_item(ConfigItem("graph_id",graph_id) )

    db.set_config("config",cfg)

    db.set_property("bary",bary)
    db.set_description("bary","barycenter of cells")

    db.set_property("V",V)
    db.set_description("V","cell volume")

    db.set_property("S",S)
    db.set_description("S","wall surface")

    db.set_property("nb",nb)
    db.set_description("nb",
                       "number of geom elements used to define this element")

#X     db.set_property("axes",axes)
#X     db.set_description("axes","main axes of the cells")

    #return
    return db

def sum_array(_array) :
    """Returns a two-dimensional array by summing over the remaining axes. Written as a work-around for
    numpy.sum() acting up with large multidimensional arrays."""
    _dim = len(_array[0])    # Finds the spatial dimension of the corresponding image
    _sum = array([[sum(sum(_array[0,0],2),2),sum(sum(_array[0,1],2),2),sum(sum(_array[0,2],2),2)],[sum(sum(_array[1,0],2),2),sum(sum(_array[1,1],2),2),sum(sum(_array[1,2],2),2)],[sum(sum(_array[2,0],2),2),sum(sum(_array[2,1],2),2),sum(sum(_array[2,2],2),2)]])
    if _dim == 3 :
        _sum = array([[sum(_sum[0,0],2),sum(_sum[0,1],2),sum(_sum[0,2],2)],[sum(_sum[1,0],2),sum(_sum[1,1],2),sum(_sum[1,2],2)],[sum(_sum[2,0],2),sum(_sum[2,1],2),sum(_sum[2,2],2)]])
    return _sum

def extract_graph_tissue (img, debug_info = True) :
    """Construct a tissue from a segmented image

    .. warning:: deprecated

    .. warning:: by convention index 0 correspond to the external part of the
                 image and index 1 correspond to the external part of the
                 tissue. Hence, the constructed tissue will have a cell 0
                 and 1 without volume

    .. warning:: the geometrical center of voxel i,j,k is
                 (i + 0.5,j + 0.5,k + 0.5) * im.resolution

    .. warning:: in the image i correspond to y and j to x

    :Parameters:
     - `img` (LxMxN array of int) - a 3D array where each voxel contains the
                                    the id of the cell it belongs to.
     - `debug_info` (bool) - tells the algo to display evolution

    :Returns: a tissue that contains :
     - a graph from cell neighborhood
     - the volume of each cell
     - the contact surface of each wall (edge) between two cells
     - the barycenter of each cell
     - the principal directions of each cell
     - the umber of voxels in each cell
     - the number of voxel faces in each wall

    :Returns Type: TissueDB
    """

    imax,jmax,kmax = img.shape
    try :
        res = array(img.resolution)
    except AttributeError :
        res = array([1.,1.,1.])

    Sres = [res[1] * res[2],res[2] * res[0],res[0] * res[1] ]
    Vres = res[0] * res[1] * res[2]

    #extract infos
    vox = [[] for i in xrange(img.max() + 1)]
    facets = {}
    facets_nb = {}

    if debug_info :
        print "infos",img.shape

    for k in range(kmax) :
        if debug_info :
            print k,
            stdout.flush()

        for i in range(imax) :
            for j in range(jmax) :
                cid = img[i,j,k]
                if cid > 1 :
                    #cell voxels
                    vox[cid].append( (i + 0.5,j + 0.5,k + 0.5) * res)

                    #surface facets
                    if i == 0 :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[0]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    elif i == (imax - 1) :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[0]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    else :
                        nid = img[i + 1,j,k]
                        if nid != cid :
                            key = (min(cid,nid),max(cid,nid) )
                            facets[key] = facets.get(key,0) + Sres[0]
                            facets_nb[key] = facets_nb.get(key,0) + 1

                    if j == 0 :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[1]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    elif j == (jmax - 1) :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[1]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    else :
                        nid = img[i,j + 1,k]
                        if nid != cid :
                            key = (min(cid,nid),max(cid,nid) )
                            facets[key] = facets.get(key,0) + Sres[1]
                            facets_nb[key] = facets_nb.get(key,0) + 1

                    if k == 0 :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[2]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    elif k == (kmax - 1) :
                        nid = 0
                        key = (0,cid)
                        facets[key] = facets.get(key,0) + Sres[2]
                        facets_nb[key] = facets_nb.get(key,0) + 1
                    else :
                        nid = img[i,j,k + 1]
                        if nid != cid :
                            key = (min(cid,nid),max(cid,nid) )
                            facets[key] = facets.get(key,0) + Sres[2]
                            facets_nb[key] = facets_nb.get(key,0) + 1

    if debug_info :
        print "#end of war"

    #create tissue
    t = Tissue()
    CELL = t.add_type("CELL")
    WALL = t.add_type("WALL")

    #properties
    V = {} #cell volume
    S = {} #wall surface
    nb = {} #number of elements that geometricaly define an element
    #bary = {} #cell barycenter
    axes = {} #cell main axes

    #create graph
    graph_id = t.add_relation("graph",(CELL,WALL) )
    graph = t.relation(graph_id)

    for cid in range(len(vox) ) :
        graph.add_vertex(cid)
        V[cid] = len(vox[cid]) * Vres
        nb[cid] = len(vox[cid])

    for key in facets :
        eid = graph.add_edge(*key)
        S[eid] = facets[key]
        nb[eid] = facets_nb[key]

    #geometrical descriptors
    if debug_info :
        print "geometrical descriptors"

    bary = barycenter(img,_vertices)
    _ident = np.identity(3)
    for cid in graph.vertices() :
        print 'cid',cid
        pts = vox[cid]

        if len(pts) == 0 :
            #bary[cid] = None
            axes[cid] = None
        else :
            b = bary[cid]	# reduce(add,pts) / len(pts)
            #compute inertia

            #I = reduce(add,[outer(pt - b,pt - b) for pt in pts]) / float(len(pts) )
            I = reduce(add,[_ident*norm(pt-b)**2 - outer(pt-b,pt-b) for pt in pts]) / float(len(pts) )

            #compute eigen values
            w,v = eig(I)

            vecs = [(w[i],tuple(float(a) for a in v[:,i] * w[i]) ) \
                     for i in (0,1,2)]
            vecs.sort(reverse=True)

            #return
            #bary[cid] = b
            axes[cid] = [v for w,v in vecs]
            break      #remove after testing necessity of barycentre
    #write result
    db = TissueDB()
    db.set_tissue(t)

    cfg = Config("topology")
    cfg.add_item(ConfigItem("CELL",CELL) )
    cfg.add_item(ConfigItem("WALL",WALL) )
    cfg.add_item(ConfigItem("graph_id",graph_id) )

    db.set_config("config",cfg)

    db.set_property("bary",bary)
    db.set_description("bary","barycenter of cells")

    db.set_property("V",V)
    db.set_description("V","cell volume")

    db.set_property("S",S)
    db.set_description("S","wall surface")

    db.set_property("nb",nb)
    db.set_description("nb",
                       "number of geom elements used to define this element")

    db.set_property("axes",axes)
    db.set_description("axes","main axes of the cells")

    #return
    return db





