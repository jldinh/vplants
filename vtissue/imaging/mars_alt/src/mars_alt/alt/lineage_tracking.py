# -*- python -*-
#
#       vplants.mars_alt.alt.lineage_tracking
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "

print "deprecated module"
# import numpy as np
# import scipy.ndimage as ndimage
# from openalea.image.spatial_image import SpatialImage
# from openalea.image.algo.basic import reverse_image, grey2color, end_margin
# from openalea.image.algo.morpho import connectivity_26
# from openalea.image.registration.registration import pts2transfo
# from vplants.asclepios.vt_exec.reech3d import reech3d


# from vplants.mars_alt.analysis.analysis import VTissueAnalysis, extract_L1
# from vplants.mars_alt.analysis.structural_analysis import draw_walls


# mat_over_sampling = np.array([[ 0.5, 0.,  0. , -0.25],
#                               [ 0.,  0.5, 0. , -0.25],
#                               [ 0.,  0.,  0.5, -0.25],
#                               [ 0.,  0.,  0. ,    1.]])



# def segmentation2surface(image):
#     """
#     It computes a surfacic view of the meristem from a segmented image.
#     :Parameters:
#     - `image` (openalea.image.SpatialImage) - segmented image to be masked
#     :Returns:
#     - `mip_img` (openalea.image.SpatialImage) - maximum intensity projection
#     - `alt_img` (openalea.image.SpatialImage) - altitude of maximum intensity projection
#     """
#     if not isinstance(image,SpatialImage):
#         image = SpatialImage(image)

#     #DESSINERSEPARATIONS imgSeg_0.inr.gz separationsEpaisses.inr.gz 2
#     walls = draw_walls(image,True)
#     walls_inv = reverse_image(walls)

#     L1 = extract_L1(image)

#     # echo "Construction d'un masque de la surface"
#     #seuillage -sb 2 ${f}.inr.gz  ${f}sb.inr.gz
#     threshold = np.where(image < 2, False, True)

#     #morpho -ero ${f}sb.inr.gz ${f}PT1.inr.gz -i 2 -con 26
#     iterations = 10
#     erosion =  ndimage.binary_erosion(threshold, connectivity_26, iterations, border_value=1)
#     erosion =  np.select([erosion == 1], [255], default=0)

#     #zcopy -o 1 ${f}PT1.inr.gz ${f}PT1.inr.gz
#     erosion = np.ubyte(erosion)

#     #Logic -xou ${f}sb.inr.gz ${f}PT1.inr.gz ${f}Xou.inr.gz
#     m_xor = np.logical_xor(threshold, erosion)

#     #METTRE_A_ZERO_LES_DERNIERES_COUPES ${f}Xou.inr.gz ${f}Xou2.inr.gz $tailleZ
#     mat = end_margin(m_xor,10,2)

#     # echo "Masque des parois, de la surface et de la L1 dans l'image :"

#     #Logic -mask $2 $1 ${f}first.inr.gz
#     m_mask = np.where(walls_inv!=0,image,0)

#     #Logic -mask ${f}Xou2.inr.gz ${f}first.inr.gz ${f}And.inr.gz
#     m_mask2 = np.where(mat!=0,m_mask,0)

#     #Logic -mask layer1.inr.gz ${f}And.inr.gz ${f}And2.inr.gz
#     m_mask3 = np.copy(m_mask2)
#     for cell in xrange(1,image.max()) :
#         if cell not in L1 :
#             m_mask3[m_mask3==cell] = 0

#     #mip_project ${f}And.inr.gz mip${f}Surf
#     x,y,z = m_mask3.shape
#     m_mip = m_mask3.max(2).reshape(x,y,1)

#     return SpatialImage(m_mip,image.resolution)


################################################
# All of these are implemented in other places #
################################################
# def mapping2pts(mapping):
#     """
#     :Parameters:
#         - mapping` (dict) - mapping between cells of the two list of points T1 and T2
#     :Returns:
#         - `pts1` (list) - list of points
#         - `pts2` (list) - list of points
#     """
#     pts1 = mapping.keys()
#     v = [item for values in d.values() for item in values]
#     pts2 = list(np.unique(v))
#     return pts1,pts2


# def pts2mapping(im1,pts1,im2,pts2):
#     """
#     :Parameters:
#         - `im1` (openalea.image.SpatialImage) - segmented image T1
#         - `pts1` (list) - list of points
#         - `im2` (openalea.image.SpatialImage) - segmented image T2
#         - `pts2` (list) - list of points

#     :Returns:
#         - `mapping` (dict) - mapping between cells of the two list of points T1 and T2
#     """
#     mapping = {}
#     for pt in pts1 :
#         c1 = im1[pt[0],pt[1],pt[2]]
#         mapping[c1]=[]
#         for pt in pts2:
#             pass



# def mapping2lset ( image0, image1, mapping ):
#     """
#     convert the initial set of cell lineages to voxel correspondances.

#     :Parameters:
#       - `image0` (openalea.image.SpatialImage) - segmented image T0
#       - `image1` (openalea.image.SpatialImage) - segmented image T1
#       - `mapping` (dictionnary) - initial set of cell lineages

#     :Return:
#       - `points0` (list) - barycenters of the parent cells
#       - `points1` (list) - barycenters of the daughter cells
#     """
#     #CONVERTIR_MAPPING_EN_CORRESPONDANCES_VOXELLIQUES
#     property0 = VTissueAnalysis(image0)
#     property1 = VTissueAnalysis(image1)

#     points0 = property0.center_of_mass(mapping.keys())
#     points1 = []
#     for v in mapping.values():
#         if len(v)>1:
#             points1.append(list(np.sum(property1.center_of_mass(v),0)/len(v)))
#         else :
#             points1.append(property1.center_of_mass(v))
#     return points0, points1

# def estimate_rigid_transformation ( points1, points0 ):
#     """
#     compute the rigid transformation estimated between the two images
#     by minimizing the total square distance between each parent cell in the set of high confidence lineages and its descendants.

#     :Parameters:
#       - `points1` (list) - barycenters of the daughter cells lineage
#       - `points0` (list) - barycenters of the parent cells

#     :Return:
#       - `matrix` (numpy.ndarray) - transformation matrix
#     """
#     points1 = np.array(points1)
#     points0 = np.array(points0)

#     mat = pts2transfo(points1,points0)
#     return np.linalg.inv(mat)

# def _scalar_product(image, scalar):
#     """
#     multiply an image by a scalar
#     """
#     if not isinstance(image,SpatialImage) :
#         image = SpatialImage(image)

#     return (image*scalar)

# def compute_def_field ( image1, points1, points0 ):
#     """
#     define non-linear transformation (as a dense vector field) by using the residual positioning error of the high confidence lineages

#     :Parameters:
#       - `image1` (openalea.image.SpatialImage) - segmented image T1
#       - `points1` (list) - barycenters of the daughter cells lineage
#       - `points0` (list) - barycenters of the parent cells

#     :Return:
#       - `matrix` (numpy.ndarray) - transformation matrix

#     """

#     # STEP 1 Calcul du champ vectoriel a partir du mapping precedent

#     points1 = np.array(points1)
#     points0 = np.array(points0)

#     if not isinstance(image,SpatialImage) :
#         image = SpatialImage(image)


#     dimx,dimy,dimz = image1.shape
#     vx = image.resolution[0]
#     vy = image.resolution[1]
#     vz = image.resolution[2]

#     # explain in the voxel world
#     points0[:,0] *= vx
#     points0[:,1] *= vy
#     points0[:,2] *= vz
#     points1[:,0] *= vx
#     points1[:,1] *= vy
#     points1[:,2] *= vz

#     # compute by interpolating the 2 vectors
#     vector = points0 - points1
#     xmin, ymin, zmin = np.min(vector, 0)
#     xmax, ymax, zmax = np.max(vector, 0)

#     img = SpatialImage( np.zeros_like(image), image.resolution)

#     #for dim in x y z

#     #MULTPLIER_IMAGE
#     f2x = _scalar_product(fx,2)

#     #reech3d
#     f2xr = reech3d( f2x, mat=mat_over_sampling, output_shape=(dimx,dimy,dimz) )
#     f2xr.resolution = (vx,vy,vz)

#     #grey2color
#     field = grey2color(f2xr, f2yr, f2zr)

#     #applyTrsfSerie

#     # STEP 2 Recalage dense avec SuperBaloo

#     # STEP 3 Calcul du mapping de cout minimal



