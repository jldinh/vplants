#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#       Vplants.tissue_analysis
#
#       Copyright 2011 INRIA - CIRAD - ENS 
#
#       File author(s): Jonathan Legrand <jlegra02@ens-lyon.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "CeCILL v2"
__revision__ = " $Id$ "

from openalea.image.serial.basics import imread,imsave
import numpy as np
import scipy.ndimage as nd
from vplants.tissue_analysis.LienTissuTXT import LienTissuTXT
import time
from numpy.linalg import svd, lstsq
import math
from enthought.mayavi import mlab


def wra_LienTissuTXT(f):
    """
    Wrapping of class 'LienTissuTXT'.
    """
    lien=LienTissuTXT(f)
    
    return lien.cellT1_cellT2,lien.cellT2_cellT1,lien


def lineage_extension(l12,l23):
    """
    Create a lineage between t_n and t_n+2 from t_n/t_n+1 and t_n+1/t_n+2.
    
    :INPUTS:
        .l12: t1 -> t2 cells lineage (form LienTissuTXT.cellT1_cellT2 dictionnary)
        .l23: t2 -> t3 cells lineage (from LienTissuTXT.cellT1_cellT2 dictionnary)

    :OUTPUTS:
        .l13: t1 -> t3 cells lineage (dictionnary   *keys = mothers labels; *values = corresponding number of daugthers)
    """
    l13={}
    for c in l12.keys():
        tmp=[]
        for cc in l12[c]:
            if cc in l23.keys():
                tmp.extend(l23[cc])
        l13[c]=tmp
    for c in l13.keys():
        if l13[c]==[]:
            l13.pop(c)

    return l13


def nb_Daugthers(lineage_12):
    """
    Create a dictionnary containing:
        .keys: mothers labels;
        .values: corresponding number of daugthers;
    """
    nbD={}
    for k in lineage_12.keys():
        nbD[k]=len(lineage_12[k])
    
    return nbD              


def dict_cells_slices(mat,labels=None):
    """
    Creation of a dictionnary of cells' slices coordinates using 'scipy.ndimage.find_objects'.
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
        .labels: if given, return a dict containing only the cells labels provided; if None, will return a dict of all cells present in the spatial image (*Optional*)
    
    :OUTPUT:
        .dict_sli: dict of cells' slices coordinates by cell
            *keys = cell ID;
            *values = scipy ndimage slice (<type 'tuple'>);
    """
    
    cell_list=list(np.unique(mat))
    if type(labels)==int:
        if labels in cell_list:
            labels=[0,labels] # Allow to iterate over a 'list' (0 isn't searched by 'ndimage.find_objects()')
        else:
            print "You have asked to find a slice for a cell ID (",labels,") not present in the Spatial image..."
            sys.exit(1)
    if type(labels)!=int and labels!=None:
        for l in labels:
            if l not in cell_list:
                print "You have asked to find a slice for a cell ID (",l,") not present in the Spatial image..."
                sys.exit(1)

    print 'Slicing the Spatial Image: ndimage.find_objects()...'
    if labels!=None:
        sli=nd.find_objects(mat, max_label=max(labels))
    else:
        labels=cell_list
        sli=nd.find_objects(mat)

    print 'Creating a dictionnary of slices...'
    dict_sli={}
    l=set(range(len(sli)+1))&set(labels)
    for k in l:
        if sli[k-1]:
            dict_sli[k]=sli[k-1]

    return dict_sli


def dict_cells_coordinates(mat,dict_sli,labels=None):
    """
    Creation of a dictionnary of cells' voxels coordinates using 'scipy.ndimage.find_objects'.
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
        .dict_sli: dict of cells' slices coordinate by cell
        .labels: if given, return a dict containing only the cells labels provided (*Optional*)
    
    :OUTPUT:
        .dict_coord: dict of cells' voxels coordinates by cell
            *keys = cell ID;
            *values = '3 x Nc' np.array (Nc=number of voxels defining each cell 'c');
    """
    if labels==None:
        labels=dict_sli.keys()

    print "Creating a dictionnary of cells' voxels coordinates..."
    dict_coord={}

    if type(labels)==int:
        x,y,z=dict_sli[c]
        dict_coord[c]=np.array(np.where(mat[x.start:x.stop,y.start:y.stop,z.start:z.stop]==c))
        dict_coord[c][0] = dict_coord[c][0]+x.start
        dict_coord[c][1] = dict_coord[c][1]+y.start
        dict_coord[c][2] = dict_coord[c][2]+z.start     
    else:
        for c in labels:
            x,y,z=dict_sli[c]
            dict_coord[c]=np.array(np.where(mat[x.start:x.stop,y.start:y.stop,z.start:z.stop]==c))
            dict_coord[c][0] = dict_coord[c][0]+x.start
            dict_coord[c][1] = dict_coord[c][1]+y.start
            dict_coord[c][2] = dict_coord[c][2]+z.start

    return dict_coord


def cell_volume(coord,labels=None):
    """
    Compute Cells' volumes :in VOXELS: !!!!!
    
    :INPUT:
        .coord: dictionnary of cells' voxels coordinates
        .labels: if given, return a dict containing only the cells labels provided (*Optional*)

    :OUTPUT:
        .vol: dictionnary of cells volume in voxels
            *keys=cell id;
            *values= cell's volume.
    """ 
    if labels==None:
        labels=coord.keys()

    print "Computing cells' volumes"
    vol={}
    vol[1]=0
    for c in labels:
        vol[c]=coord[c].shape[1]
    
    return vol


def cell_surface_area(surface,labels=None):
    """
    Compute Cells' volumes :in VOXELS: !!!!!
    
    :INPUT:
        .surface: Spatial Image of cells' 'top surface'.
        .labels: if given, return a dict containing only the cells labels provided (*Optional*)

    :OUTPUT:
        .area: dictionnary of cells area in voxels
            *keys=cell id;
            *values= cell's volume.
    """
    sli=dict_cells_slices(surface,labels)
    coord=dict_cells_coordinates(surface,sli,labels)

    if labels==None:
        labels=coord.keys()

    print "Computing cells' surface area (L1)"
    area={}
    for c in labels:
        area[c]=coord[c].shape[1]
    
    return area


def dict_cells_walls_coordinates(mat,dict_sli,return_walls_image=False,labels=None):
    """
    Laplacian filter used to dectect cells walls (return a dict of cells' voxels coordinate by cells).
    The Laplacian of an image highlights regions of rapid intensity change (i.e. the cells' walls).
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
        .dict_sli: dict of cells' slices coordinate by cell
        .return_walls_image: boolean, if 'True' return the Spatial Image of the cells walls only (*Optional*)
        .labels: if given, return a dict containing only the cells labels provided (*Optional*)
    
    :OUTPUT:
        .cells_wall_coord: dict of cells' voxels coordinate by cells
            *keys = cell ID;
            *values = [x_n,y_n,z_n]: coordinates of the cells' walls (array);
        .mat: if asked, Spatial Image of the cells walls only
    """
    
    import copy
    m=copy.copy(mat)

    print 'Detecting boundaries of cells: nd.laplace()...'
    b=nd.laplace(m)
    m[b==0]=0
    m[np.where(mat==1)]=0
    
    if labels==None:
        labels=dict_sli.keys()

    print "Creating a dictionnary of cells' walls (voxels) coordinates..."
    dict_coord={}
    for c in labels:
        x,y,z=dict_sli[c]
        dict_coord[c]=np.array(np.where(m[x.start:x.stop,y.start:y.stop,z.start:z.stop]==c))
        dict_coord[c][0] = dict_coord[c][0]+x.start
        dict_coord[c][1] = dict_coord[c][1]+y.start
        dict_coord[c][2] = dict_coord[c][2]+z.start
    
    if return_walls_image:
        return dict_coord,m
    else:
        return dict_coord

def cells_walls_coordinates(mat,labels):
    """
    Laplacian filter used to dectect cells walls (return a dict of cells' voxels coordinate by cells).
    The Laplacian of an image highlights regions of rapid intensity change (i.e. the cells' walls).
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
        .labels:
    
    :OUTPUT:
        .cells_wall_coord: dict of cells' voxels coordinate by cells
            *keys = cell ID;
            *values = [x_n,y_n,z_n]: coordinates of the cells' walls (array);
    """
    
    import copy
    m=copy.copy(mat)

    print 'Detecting boundaries of cells: nd.laplace()...'
    b=nd.laplace(m)
    m[b==0]=0
    m[np.where(mat==1)]=0
    
    if labels==None:
        labels=dict_sli.keys()

    print "Creating a dictionnary of cells' walls (voxels) coordinates..."
    dict_coord={}
    for c in labels:
        x,y,z=dict_sli[c]
        dict_coord[c]=np.array(np.where(m[x.start:x.stop,y.start:y.stop,z.start:z.stop]==c))
        dict_coord[c][0] = dict_coord[c][0]+x.start
        dict_coord[c][1] = dict_coord[c][1]+y.start
        dict_coord[c][2] = dict_coord[c][2]+z.start
    
    if return_walls_image:
        return dict_coord,m
    else:
        return dict_coord

def volumetric_growth(graph_1,graph_2,lineage_12):
    """
    Create a dictionnary containing t_n cells ids (keys) and their volumetric growth (values).
    
    :INPUTS:
        .t1: Spatial Image @ t_n containing cells (segmented image)
        .t2: Spatial Image @ t_n+1 containing cells (segmented image)
        .lineage_12: t1 -> t2 cells lineage.
    
    :OUPUT: 
        .VG_12: *keys= mothers cells ids; *values= corresponding volumetric growth (%)
            :VG_12_j=sum_i(Vf_ij)-Vm_j/Vm_j*100:;
        .VG_21: Inverted volumetric_growth dict.
    """
    print 'Graph @ t_n'
    cell_volume_1=graph_1.vertex_property('volume')
    print 'Graph @ t_n+1'
    cell_volume_2=graph_2.vertex_property('volume')
    
    # Retreive the sum volumes of each daugthers' cells 
    print 'Compute the sum volume of each daugthers'' cells'
    sum_Vf={}
    for k in lineage_12.keys():
        if k in cell_volume_1: #-- we check if the lineaged cell is in graph @t_n
            v=0
            for j in lineage_12[k]:
                v+=cell_volume_2[j]
            sum_Vf[k]=v
    
    # Compute the Absolute Ratio of Volumetric Growth:
    print 'Compute the Absolute Ratio of Volumetric Growth(%): VG_j=sum_i(Vf_ij)-Vm_j/Vm_j*100'
    VG_12={}
    for k in lineage_12.keys():
        if k in cell_volume_1: #-- we check if the lineaged cell is in graph @t_n
            if lineage_12[k]!=[] and cell_volume_1[k]!=0:
                VG_12[k]=float(sum_Vf[k]-cell_volume_1[k])/cell_volume_1[k]*100
    
    #Inverting volumetric_growth dict:
    VG_21={}
    for k in VG_12.keys():
        for v in lineage_12[k]:
            VG_21[v]=VG_12[k]

    return VG_12,VG_21


def areal_growth(surf_t1,surf_t2,lineage_12,return_cells_area=False):
    """
    Create a dictionnary containing t_n cells ids (keys) and their areal growth (values).
    Works for L1 and L2.
    
    :INPUTS:
        .surf_t1: Spatial Image @ t_n containing cells' (top) surface (segmented image)
        .surf_t2: Spatial Image @ t_n+1 containing cells' (top) surface (segmented image)
        .lineage_12: t1 -> t2 cells lineage.
    
    :OUPUT: 
        .:AG_12_j=sum_i(Af_ij)-Am_j/Am_j*100:
            *keys= mothers cells ids; 
            *values= corresponding areal growth (%)
        .AG_21: Inverted areal_growth dict.
    """

    L1_t1=list(np.unique(surf_t1))
    if L1_t1.__contains__(0):
        L1_t1.remove(0)
    l12={}
    for l in L1_t1:
        if lineage_12.has_key(l):
            l12[l]=lineage_12[l]

    print 'Spatial Image @ t_n'
    cell_area_1=cell_surface_area(surf_t1)
    print 'Spatial Image @ t_n+1'
    cell_area_2=cell_surface_area(surf_t2)
    
    # Retreive the sum areas of each daugthers' cells 
    print 'Compute the sum areas of each daugthers'' cells'
    sum_Af={}
    for k in l12.keys():
        a=0
        for j in l12[k]:
            a+=cell_area_2[j]
        sum_Af[k]=a
    
    # Compute the Absolute Ratio of areal Growth:
    print 'Compute the Absolute Ratio of areal Growth(%): aG_j=sum_i(Af_ij)-am_j/am_j*100'
    aG_12={}
    for k in l12.keys():
        if l12[k]!=[] and cell_area_1[k]!=0:
            aG_12[k]=float(sum_Af[k]-cell_area_1[k])/cell_area_1[k]*100
    
    #Inaerting areatric_growth dict:
    aG_21={}
    for k in aG_12.keys():
        for a in l12[k]:
            aG_21[a]=aG_12[k]

    if return_cells_area:
        return aG_12,aG_21,cell_area_1,cell_area_2
    else:
        return aG_12,aG_21


def centroid(dict_coord,labels=None):
    """
    Compute the centroids of cells according to the coordinates of their voxels.
    The centroids coordinates will be expressed in the Spatial Image reference system (not in real world metrics).

    :INPUT:
        .dict_coord: dict of cells' voxels coordinate by cells ( 'dict_cells_walls_coord()' )
        .labels: if given, return a dict containing only the cells'centroids for the provided labels(*Optional*)
    
    :OUTPUT:
        .bary:
            *keys = cell ID;
            *values = np.array((x,y,z)): coordinates of the cells' centroid;
    """
    if labels==None:
        labels=dict_coord.keys()
    
    # Loop over the cells list to compute the centroids.
    bary={}
    for n,c in enumerate(labels):
        bary[c]=np.mean(dict_coord[c],axis=1)
    
    return bary


def geometric_median(dict_coord,labels=None):
    """
    Compute the geometric medians of cells according to the coordinates of their voxels.
    The geometric medians coordinates will be expressed in the Spatial Image reference system (not in real world metrics).
    We use the Weiszfeld's algorithm (http://en.wikipedia.org/wiki/Geometric_median)

    :INPUT:
        .dict_coord: dict of cells' voxels coordinate by cells ( 'dict_cells_walls_coord()' is enough )
        .labels: if given, return a dict containing only the cells'centroids for the provided labels(*Optional*)
    
    :OUTPUT:
        .geom:
            *keys = cell ID;
            *values = np.array((x,y,z)): coordinates of the cells' geometric median;
    """
    if labels==None:
        labels=dict_coord.keys()
    
    if labels.__contains__(0):
        labels.remove(0)
    if labels.__contains__(1):
        labels.remove(1)

    #Create a starting 'median': the geometric mean (i.e. the first candidate median)
    means=centroid(dict_coord,labels)
    
    medians={}
    for n,c in enumerate(labels):
        print "computing median for cell #",c,"(",n,'/',len(labels),")"
        # Recovering the set of points to witch we want to calculate the geometric median.
        X = dict_coord[c]
        # Initialising 'median' to the centroid
        y = means[c]

        convergence=False #boolean testing the convergence toward a global optimum
        dist=[] #list recording the distance evolution
        numIter=50 # limit the length of the search for global optimum
        
        # Minimizing the sum of the squares of the distances between each points in 'X' (cells walls voxels) and the median.
        i=0
        while ( (not convergence) and (i < numIter) ):
            num_x, num_y, num_z = 0.0, 0.0, 0.0
            denum=0.0
            m=X.shape[1]
            d=0
            for j in range(0,m):
                div = math.sqrt( (X[0,j]-y[0])**2 + (X[1,j]-y[1])**2 + (X[2,j]-y[2])**2 )
                num_x += X[0,j] / div
                num_y += X[1,j] / div
                num_z += X[2,j] / div
                denum += 1./div
                d+=div**2 #distance (to the median) to miminize
            dist.append(d) #update of the distance évolution
            y = [num_x/denum, num_y/denum, num_z/denum] #update to the new value of the median
            if i>3:
                convergence=(abs(dist[i]-dist[i-2])<0.1) #we test the convergence over three steps for stability
                #~ print abs(dist[i]-dist[i-2]), convergence
            i+=1
        if i==numIter:
            print "The Weiszfeld's algoritm did not converged after",numIter,"iterations for cell #",c,"!!!!!!!!!"
        #When convergence or iterations limit is reached we assume that we found the median.
        medians[c]=y

    return medians


def visu_spatial_image(mat,glyph='point',colormap='prism'):
    """
    Display cells.

    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
    
    :OUTPUT:
        Mayavi2 scene where cells are 
    """
    mlab.figure(size=(800, 800))
    x,y,z=cells_walls_coords(mat)
    if isinstance(colormap,tuple):
        mlab.points3d( x,y,z, color=colormap, mode=str(glyph), scale_factor=1, scale_mode='none' )
    if isinstance(colormap,str):
        mlab.points3d( x,y,z,mat[x,y,z], colormap=str(colormap), mode=str(glyph), scale_factor=1, scale_mode='none' )


def visu_cells_spatial_image(image, cells, image_glyph='point', cell_glyph='cube', image_colormap=tuple([1.,1.,1.]), cell_colormap='prism'):
    """
    Display cells.

    :INPUT:
        .image: Spatial Image containing cells (segmented image)
    
    :OUTPUT:
        Mayavi2 scene where cells are 
    """
    mlab.figure(1, fgcolor=(1, 1, 1), bgcolor=(0, 0, 0), size=(800, 800))
    x,y,z=cells_walls_coords(image)
    if isinstance(image_colormap,tuple):
        pts = mlab.points3d( x,y,z, color=image_colormap, mode=str(image_glyph), scale_factor=1, scale_mode='none' )
    if isinstance(image_colormap,str):
        pts = mlab.points3d( x,y,z,image[x,y,z], colormap=str(image_colormap), mode=str(image_glyph), scale_factor=1, scale_mode='none' )
    
    if isinstance(cells,int): cells=[cells]

    import copy
    hollowed_out_image = copy.copy(image)
    b=nd.laplace(hollowed_out_image)
    hollowed_out_image[b==0]=0
    hollowed_out_image[np.where(hollowed_out_image==1)]=0
    for n,i in enumerate(cells):
        if n%1==0: print n,'/',len(cells)
        x,y,z =np.where(hollowed_out_image==i)
        if isinstance(cell_colormap,tuple):
            pts_cell = mlab.points3d( x,y,z, color=cell_colormap, mode=str(cell_glyph), scale_factor=1, scale_mode='none' )
        if isinstance(cell_colormap,str):
            pts_cell = mlab.points3d( x,y,z,image[x,y,z], colormap=str(cell_colormap), mode=str(cell_glyph), scale_factor=1, scale_mode='none' )


def cells_walls_coords(mat):
    """
    Laplacian filter used to dectec and return cells walls.
    The Laplacian of an image highlights regions of rapid intensity change.
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
    
    :OUTPUT:
        .x,y,z: coordinates of the cells' boundaries (walls)
    """
    
    print 'Detecting boundaries of cells...'
    b=nd.laplace(mat)
    mat[b==0]=0
    mat[np.where(mat==1)]=0
    x,y,z=np.where(mat!=0)
    print 'Done !!'

    return list(x),list(y),list(z)
    

def remove_margins_cells(mat,dict_coord,display=False):
    """
    Function removing the cell's at the magins, because most probably cut during stack aquisition
    Load a Spatial Image and return a Spatial image without cell's at the magins of the stack.
    
    :INPUTS:
        .mat: Spatial Image containing cells (segmented image)
        .dict_coord: dict of cells' voxels coordinate by cells ( 'dict_cells_coordinate()' ONLY )
        .save: text (if present) indicating under which name to save the Spatial Image containing the cells of the first layer;
        .display: boolean indicating if we should display the previously computed image;
    
    :OUPUT:
        .mat: Spatial Image containing cells belonging to the fisrt Layer (L1)
    """
    b_cells=border_cells(mat)
    
    import copy
    m=copy.copy(mat)
    
    print "Removing the cell's at the magins..."
    for n,c in enumerate(b_cells):
        if n%20==0:
            print n,'/',len(b_cells)
        m[tuple(dict_coord[c])]=0
    
    if dict_coord.has_key(1):
        m[tuple(dict_coord[1])]=1
    else:
        m[np.where(mat==1)]=1

    if display:
        visu_spatial_image(m)
    
    print 'Done !!'

    return m


def L1_cells_list(mat,return_surface=False):
    """
    Function loading a Spatial Image and returning the the first layer cells list (L1, cells at the surface of the meristem).
    
    :INPUTS:
        .mat: Spatial Image containing cells (segmented image)
        .return_surface: boolean indicating if we should return the Spatial Image containing only the surface (first layer of voxels).
    
    :OUPUT:
        .L1: the first layer cells list
    """
    print 'Creating  the list of cells belonging to the first layer (L1).'
    un=(mat==1)
    deux=nd.binary_dilation(un,iterations=1)
    trois=deux-un
    surf=mat*trois
    L1=list(np.unique(surf))    # Create L1 cells List
    
    if 0 in L1:
        L1.remove(0)
    if 1 in L1:
        L1.remove(1)
    
    print 'Done !!'
    if return_surface:
        return L1,surf
    else:
        return L1
    

def L2_cells_list(mat,dict_coord,return_surface_matrix=False):
    """
    Function loading a Spatial Image and returning the the first layer cells list (L1, cells at the surface of the meristem).
    
    :INPUTS:
        .mat: Spatial Image containing cells (segmented image)
        .dict_coord: dict of cells' voxels coordinate by cells ( 'dict_cells_coordinate()' ONLY )
    
    :OUPUT:
        .L1: the first layer cells list
    """
    L1=L1_cells_list(mat)

    import copy
    m=copy.copy(mat)
    for c in L1:
        m[tuple(dict_coord[c])]=1
    
    print 'Creating  the list of cells belonging to the second layer (L2).'
    un=(m==1)
    deux=nd.binary_dilation(un,iterations=1)
    trois=deux-un
    surf=m*trois
    L2=list(np.unique(surf))    # Create L2 cells List
    
    if 0 in L2:
        L2.remove(0)
    if 1 in L2:
        L2.remove(1)
    
    print 'Done !!'
    if return_surface_matrix:
        return L2,surf
    else:
        return L2
    

def spatial_image_cell_list(mat,cells_list,dict_coord,display=False):
    """
    Function loading a Spatial Image and returning a Spatial image containing only cells belonging to the surface (L1).
    
    :INPUTS:
        .mat: Spatial Image containing cells (segmented image)
        .cells_list: can be "L1", "L2" or an arbitrary list of cell
        .dict_coord: dict of cells' voxels coordinate by cells ( 'dict_cells_coordinate()' ONLY )
        .save: text (if present) indicating under which name to save the Spatial Image containing the cells of the first layer;
        .display: boolean indicating if we should display the previously computed image;
    
    :OUPUT:
        .m: Spatial Image containing cells belonging to the fisrt Layer (L1)
    """
    if type(cells_list)!=str:
        if type(cells_list)==int and cells_list!=1:
            cells_list=[1,cells_list]
        else:
            cells_list=list(cells_list)
            print 'Checking that all the cells IDs provided exist in the segmented image and the dictionnary of coordinates...'
            cells=np.unique(mat)
            for c in cells_list:
                if c not in cells:
                    print "You've asked for a cell that isn't present in the segemented image:",c
                else:
                    if c not in dict_coord.keys():
                        print "The requested cell #",c, "is not in the dictionnary of cells' voxels coordinate! Trying to find it..."
                        dict_coord[c]=dict_cells_coordinates(mat,dict_cells_slices(mat,c))
    #~ else:
        #~ print "No cells to display, most probably because the list provided is empty or contain only cell '#1'",'/n',"Please provide one or ask for 'L1' or 'L2' !!!!"

    import copy
    m=copy.copy(mat)
    m.fill(0)
    for n,c in enumerate(cells_list):
        if n%10==0:
            print n,'/',len(cells_list)
        m[tuple(dict_coord[c])]=c
    
    if dict_coord.has_key(1):
        m[tuple(dict_coord[1])]=1
    else:
        m[np.where(mat==1)]=1

    if display:
        visu_spatial_image(m)

    return m


def coordinate_surf(mat,remove_borders=True):
    """
    Function loading a Spatial Image and returning x,y,z coordinates of the first layer (L1) surface.
    
    :INPUTS:
        .mat: Spatial Image containing cells (segmented image)
    
    :OUPUTS:
        .x,y,z: coordinates of the voxels at the surface of the meristem (also called the first layer or L1)
        
    :WARNINGS:
        .Assume that the outer is defined by the value '1' !!!!
    """
    ti_1=time.time()

    L1,surf=L1_cells_list(mat,True)
    surf[np.where(surf==0)]=1
    if remove_borders:
        from vplants.tissue_analysis.growth_analysis import border_cells,dict_cells_coordinates,dict_cells_slices
        rm=border_cells(surf)
        xyz=dict_cells_coordinates(surf,dict_cells_slices(surf,rm),rm)
        for i in rm:
            surf[tuple(xyz[i])]=1

    print 'Extracting the surface''s coordinates of the first layer (L1).'
    x,y,z=np.where(surf!=1)
    
    ti_2=time.time()
    print 'Elapsed time for extracting the surface of the first Layer (L1):',ti_2-ti_1

    return surf,x,y,z


def border_cells(mat,margins_thickness=1):
    """
    This function create a list of the cells in contact with the border of the stack (spatial image).
    
    :INPUT:
        .mat: Spatial Image containing cells (segmented image)
    
    :OUPTUT:
        .list of the cells in contact with the border of the stack
    """
    print 'Creating list of the cells in contact with the border of the spatial image.'
    xm,ym,zm=mat.shape
    cells=[]
    if margins_thickness != 1:
        mi=margins_thickness-1
        cells.extend(np.unique(mat[0:mi,:,:]))
        cells.extend(np.unique(mat[:,0:mi,:]))
        cells.extend(np.unique(mat[:,:,0:mi]))
        cells.extend(np.unique(mat[xm-margins_thickness:xm-1,:,:]))
        cells.extend(np.unique(mat[:,ym-margins_thickness:ym-1,:]))
        cells.extend(np.unique(mat[:,:,zm-margins_thickness:zm-1]))
    else:
        cells.extend(np.unique(mat[0,:,:]))
        cells.extend(np.unique(mat[:,0,:]))
        cells.extend(np.unique(mat[:,:,0]))
        cells.extend(np.unique(mat[xm-1,:,:]))
        cells.extend(np.unique(mat[:,ym-1,:]))
        cells.extend(np.unique(mat[:,:,zm-1]))

    print 'Done !!'
    return np.unique(cells)


def vector_xyz(walls_coord):
    ## We first regroup all the voxels coordinates in three vectors 'x','y' and 'z'.
    x,y,z=[],[],[]
    for c in walls_coord.keys():
        x.extend(walls_coord[c][0,:]),y.extend(walls_coord[c][1,:]),z.extend(walls_coord[c][2,:])
    return x,y,z


def reduce_lineage(lineage,cells):
    """
    Reduce the lineage dictionnary ('lineage'), by keeping only its keys if present in the cells id list ('cells')
    """
    lin={}
    for i in cells:
        if i in lineage:
            lin[i]=lineage[i]
        else:
            print 'There is non known lineage for cell'+str(i)
    
    return lin


def dictionaries(Bary_vrtx):
    """
    Creates vrtx2cell, cell2vrtx & vrtx2bary dictionaries.
    
    :INPUT:
        .Bary_vrtx: dict *keys=the 4 cells ids at the vertex position ; *values=3D coordinates of the vertex in the Spatial Image.
    
    :OUPTUTS:
        .vrtx2cell: dict *keys=vertex id ; *values=ids of the 4 associated cells
        .cell2vrtx: dict *keys=cell id ; *values=ids of the vertex defining the cell
        .vrtx2bary: dict *keys=vertex id ; *values=3D coordinates of the vertex in the Spatial Image
    """
    print 'Creates vrtx2cell(vertex and its cells) , cell2vrtx(cell and its vertices) dictionaries'
    vrtx2cell={} #associated cells to each vertex;
    cell2vrtx={} #associated vertex to each cells;
    vrtx2bary={}
    for n,i in enumerate(Bary_vrtx.keys()):
        vrtx2cell[n]=list(i)
        vrtx2bary[n]=list(Bary_vrtx[i])
        for j in list(i):
            #check if cell j is already in the dict
            if cell2vrtx.has_key(j): 
                cell2vrtx[j]=cell2vrtx[j]+[n] #if true, keep the previous entry (vertex)and give the value of the associated vertex
            else:
                cell2vrtx[j]=[n] #if false, create a new one and give the value of the associated vertex
    #~ del(cell2vrtx[1]) #cell n°1 doesn't really exist...
    print 'Done !!'
    return vrtx2cell, cell2vrtx, vrtx2bary


def V2V(l21, vrtx2cell_1, vrtx2cell_2):
    """
    Creates vrtx2vrtx dictionnary (v2v): associate the corresponding vertex over time.
    
    :INPUTS:
        .l21: t_n+1-> t_n (LienTissuTXT) cells lineage
        .vrtx2cell_1: dict at t_n *keys=vertex id ; *values=ids of the 4 associated cells
        .vrtx2cell_2: dict at t_n+1 *keys=vertex id ; *values=ids of the 4 associated cells
    
    :OUPTUT:
        .v2v: dict *keys=t_n+1 vertex number; *values=associated t_n vertex.
    """
    v2v={} ##vertex t2 vers t1
    l21[1]=1
    ## Loop on the vertices label of t2:
    for v in vrtx2cell_2.keys():
        g=list(vrtx2cell_2[v])
        ## For the 4 (daugthers) cells associated to this vertex, we temporary replace it by it's mother label:
        for n,i in enumerate(g):
            if l21.has_key(i): ## if "lineaged" (the cell has been associated to a mother)...
                g[n]=l21[i] ## ...we replace the daughters' label by the one from its mother.
            else:
                g[n]=0 ## ...else we code by a 0 the absence of a mother in the lineage file (for one -or more- of the 4 daugthers)
        if 0 not in g: ## If the full topology around the vertex is known:
            g.sort()
            for k in vrtx2cell_1.keys(): 
                if len(set(vrtx2cell_1[k])&set(g))==4:
                    v2v[v]=k

    return v2v


def vrtx_2_direct_neighbours(vrtx2cells,cells2vrtx):
    """
    Function creating a dictionnary of direct neighbours for each vertex.
    
    :INPUTS:
        .vrtx2cells: dict *keys=vertices numbers ; *values=corresponding cells numbers (cells sharing the same vertex)
        .cells2vrtx: dict *keys=cells numbers ; *values=corresponding vertex number (vertices defining the cell)
    
    :OUPUT:
        .v2dn: dictionnary of direct neighbours for each vertex
    """
    v2dn={}
    nb_v=len(vrtx2cells.keys())
    for v in vrtx2cells.keys():
        if v%100==0:
            print v,'/',nb_v
        l=[cells2vrtx[i] for i in vrtx2cells[v] if i!=1] ## vertices of the surrounding cells associated with the vertex k. (!!!include the vertex k!!!)
        l2=np.unique([l[t][tt] for t in range(len(l)) for tt in range(len(l[t]))]) ## We create a unique array of the previous list.
        tmp=[]
        for j in l2: ## Loop on only those potentially edge-related vertices;
            test1=set(vrtx2cells[v])
            test2=set(vrtx2cells[j])
            if ( j!=v ) and ( len(test1&test2)==3 ):
                tmp=np.concatenate((tmp,[j]))
        v2dn[v]=tmp
    
    return v2dn


def V2MAP(l12, vrtx2cell_1):
    """
    Create a list of vertex that need to be mapped according to lineage and vertex associated to lineaged cells.
    (all vertex from t_n lineaged cells should be associated to their corresponding vertex over time, i.e. at t_n+1)
    
    :INPUTS:
        .l12: t_n-> t_n+1 (LienTissuTXT) cells lineage
        .vrtx2cell_1: dict at t_n *keys=vertex id ; *values=ids of the 4 associated cells
    
    :OUTPUT:
        .v2map: list of vertex to be mapped according to lineage and vertex associated to lineaged cells
    """
    v2map=[]
    for i in l12.keys():
        if i in vrtx2cell_1.keys():
            v2map.extend(vrtx2cell_1[i])

    v2map.sort()
    v2map=np.unique(v2map)
    
    return v2map



def Strain_2D(t1,t2,l12,l21,deltaT=24):
    """
    Strain computation based on the 3D->2D->3D GOODALL method.
    
    :INPUTS:
        .t1: t_n Spatial Image containing cells (segmented image)
        .t2: t_n+1 Spatial Image containing cells (segmented image)
        .l12: lineage between t_n & t_n+1;
        .l21: INVERTED lineage between t_n & t_n+1;
        .deltaT: time interval between two time points;
        
    :Variables:
        .v2v_21: vertex (keys=t_n+1) to vertex (values=t_n) association.
        .c2v_1: cells 2 vertex @ t_n
        .v2b_1: vextex 2 barycenters @ t_n
        .v2b_2: vextex 2 barycenters @ t_n+1
    
    :OUTPUTS: (c= keys= mother cell number)
        .sr[c]: Strain Rate = np.log(D_A[0])/deltaT , np.log(D_A[1])/deltaT
        .asr[c]: Areal Strain Rate = (sr1+sr2)
        .anisotropy[c]: Growth Anisotropy = (sr1-sr2)/(sr1+sr2)
        .s_t1[c]: t_n strain cross in 3D (tensor)
        .s_t2[c]: t_n+1 strain cross in 3D (tensor)
    
    ########## Relationship between least-squares method and principal components: ##########
    ## The first principal component about the mean of a set of points can be represented by that line which most closely approaches the data points 
    #(as measured by squared distance of closest approach, i.e. perpendicular to the line).
    ## In contrast, linear least squares tries to minimize the distance in the y direction only.
    ## Thus, although the two use a similar error metric, linear least squares is a method that treats one dimension of the data preferentially, while PCA treats all dimensions equally.
    #########################################################################################
    """
    from vplants.tissue_analysis.mesh_computation import calcule_vertex2
    ## Extract infos form t1:
    print "Extract infos from tn:"
    surf_1,x_1,y_1,z_1=coordinate_surf(t1)
    vertex_1=calcule_vertex2(surf_1,x_1,y_1,z_1)
    v2c_1, c2v_1, v2b_1 = dictionaries(vertex_1)

    ## Extract infos form t2:
    print "Extract infos from tn+1:"
    surf_2,x_2,y_2,z_2=coordinate_surf(t2)
    vertex_2=calcule_vertex2(surf_2,x_2,y_2,z_2)
    v2c_2, c2v_2, v2b_2 = dictionaries(vertex_2)

    v2v_21=V2V(l21,v2c_1,v2c_2)
    v2map=V2MAP(l12,v2c_1)
    print 'Percentage of associated Vertex :',float(len(v2v_21))/len(v2map)*100.,'%'

    ## Variable creation used to comput the strain.
    v2v_12 = dict((v,k) for k, v in v2v_21.items())
    lsq={}
    s_t1,s_t2={},{}
    sr={}
    asr={}
    anisotropy={}

    for c in l12.keys():
        if c in c2v_1.keys():
            if sum([(c2v_1[c][k] in v2v_12.keys()) for k in range(len(c2v_1[c]))])==len(c2v_1[c]):
                N = len(c2v_1[c])
                if N>2:
                    ## Retreive positions of the vertices belonging to cell 'c':
                    xyz_t1=np.array([v2b_1[c2v_1[c][k]] for k in range(N)])
                    xyz_t2=np.array([v2b_2[v2v_12[c2v_1[c][k]]] for k in range(N)])
                    ## Compute the centroids:
                    c_t1=np.array((np.mean(xyz_t1[:,0]),np.mean(xyz_t1[:,1]),np.mean(xyz_t1[:,2])))
                    c_t2=np.array((np.mean(xyz_t2[:,0]),np.mean(xyz_t2[:,1]),np.mean(xyz_t2[:,2])))
                    ## Compute the centered matrix:
                    c_xyz_t1=np.array(xyz_t1-c_t1)
                    c_xyz_t2=np.array(xyz_t2-c_t2)
                    ## Compute the Singular Value Decomposition (SVD) of centered coordinates:
                    U_t1,D_t1,V_t1=svd(c_xyz_t1, full_matrices=False)
                    U_t2,D_t2,V_t2=svd(c_xyz_t2, full_matrices=False)
                    V_t1=V_t1.T ; V_t2=V_t2.T
                    ## Projection of the vertices' xyz 3D co-ordinate into the 2D subspace defined by the 2 first eigenvector
                    #(the third eigenvalue is really close from zero confirming the fact that all the vertices are close from the plane -true for external part of L1, not for inner parts of the tissue).
                    c_xy_t1=np.array([np.dot(U_t1[k,0:2],np.diag(D_t1)[0:2,0:2]) for k in range(N)])
                    c_xy_t2=np.array([np.dot(U_t2[k,0:2],np.diag(D_t2)[0:2,0:2]) for k in range(N)])
                    ## Compute the Singular Value Decomposition (SVD) of the least-square estimation of A.
                    #A is the (linear) transformation matrix in the regression equation between the centered vertices position of two time points:
                    lsq[c]=lstsq(c_xy_t1,c_xy_t2)
                    ##  Singular Value Decomposition (SVD) of A.
                    R,D_A,Q=svd(lsq[c][0])
                    Q=Q.T
                    # Compute Strain Rates and Areal Strain Rate:
                    sr[c] = np.log(D_A)/deltaT
                    asr[c] = sum(sr[c])
                    anisotropy[c]=((sr[c][0]-sr[c][1])/asr[c])
                    ##  Getting back in 3D: manually adding an extra dimension.
                    R=np.hstack([np.vstack([R,[0,0]]),[[0],[0],[1]]])
                    D_A=np.hstack([np.vstack([np.diag(D_A),[0,0]]),[[0],[0],[0]]])
                    Q=np.hstack([np.vstack([Q,[0,0]]),[[0],[0],[1]]])
                    ##  Getting back in 3D: strain of cell c represented at each time point.
                    s_t1[c] = np.dot(np.dot(np.dot(np.dot(V_t1, R), D_A), R.T), V_t1.T)
                    s_t2[c] = np.dot(np.dot(np.dot(np.dot(V_t2, Q), D_A), Q.T), V_t2.T)

    return sr,asr,anisotropy,s_t1,s_t2
