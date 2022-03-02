# -*- python -*-
#
#       registration algos test module
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################


__license__ = "CeCILL v2"
__revision__ = " $Id: test_registration.py 11016 2011-08-24 16:19:58Z dbarbeau $ "

import numpy as np
import scipy

import os
from os.path import join as pj

from openalea.misc.temp           import temp_name
from openalea.core.pkgmanager     import PackageManager
from openalea.image.serial.all    import imread
from openalea.image.serial        import inrimage
from openalea.image.algo.basic    import color2grey
from openalea.image.spatial_image import SpatialImage

from vplants.asclepios.vt_exec.baladin    import baladin
from vplants.asclepios.vt_exec.superbaloo import superbaloo
from vplants.asclepios.vt_exec.reech3d    import reech3d

pm = PackageManager()
pm.find_and_register_packages()

data_pkg = pm["vplants.mars_alt.data"]

refPath = pj(data_pkg.path, "plantB-1.lsm")
floPath = pj(data_pkg.path, "plantB-2.lsm")

I = np.linalg.inv

def test_baladin_identity():
    ref = imread(refPath)
    flo = imread(refPath)

    im, tr = baladin(ref, flo,
                     inivox = np.identity(4),
                     transformation="rigi",
                     estimator="ltsw",
                     ltscut=0.75,
                     similarity_measure="cc",
                     rms=True,
                     v = 0.75,
                     pyn = 6,
                     pys = 1)

    np.testing.assert_array_almost_equal(tr, np.identity(4))

    return ref, flo, tr


def test_superbaloo_identity():
    im1 = imread(refPath)
    im2 = imread(refPath)

    deform = superbaloo(im1, im2, [],
                        use_binary=True,
                        )

    np.testing.assert_array_almost_equal(deform, np.zeros(deform.shape), 4)
    return deform



def test_superbaloo_affine():
    mat2 = np.loadtxt("../share/plantB-data/temp/mat2.txt")
    im1  = scipy.ndimage.affine_transform(imread(refPath), mat2[:3,:3],
                                          offset=mat2[:3,3],
                                          order=1)
    im2  = imread(refPath)

    deform = superbaloo(im1, im2, [mat2],
                        use_binary=True,
                        )

    np.testing.assert_array_almost_equal(deform, np.zeros(deform.shape), 4)

    return deform


def test_reech3d_identity():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16, order="C"))

    # -- identity matrix in homogeneous coordinates --
    identity = np.identity(4)

    im_res = reech3d(im1, mat=identity)

    np.testing.assert_array_equal(im1, im_res)
    return im1, im_res

def test_reech3d_translation():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16, order="C"))

    # -- the hypothetical result --
    hypo_res = SpatialImage(np.ones((11,11,1), dtype=np.uint16, order="C"))
    hypo_res[:,0]=0
    hypo_res[0,:]=0

    # -- identity matrix in homogeneous coordinates --
    trans = np.identity(4)
    trans[:2,3] = 1
    trans = I(trans) # we take the invert, reech wants transfo from out to in.

    im_res = reech3d(im1, mat=trans)
    np.testing.assert_array_equal(hypo_res, im_res)

    return im1, im_res


def test_reech3d_null_deform():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16))

    # -- a null deformation field. Must be of type float32 --
    deform = SpatialImage(np.zeros((11,11,1,3), dtype=np.float32), vdim=3)

    # -- color2grey splits a deformation field into 3 scalar images (one per vect component) --
    im_res = reech3d(im1, deformation=color2grey(deform))

    np.testing.assert_array_equal(im1, im_res)
    return im1, im_res


def test_reech3d_null_deform_binary():

    exe = "reech3d" if os.name == "posix" else "reech3d.exe"
    tmpIm1 = temp_name(suffix=".inr.gz")
    tmpOut = temp_name(suffix=".inr.gz")
    tmpDef = temp_name(suffix=".inr.gz")

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16))

    # -- a null deformation field. Must be of type float32 --
    # -- the deformation field is also expected to be in
    # the out to in direction --
    deform = SpatialImage(np.zeros((11,11,1,3), dtype=np.float32), vdim=3)

    inrimage.write_inrimage(tmpIm1, im1)

    # -- we must split the deform field into 3 images
    inrimage.write_inrimage(tmpDef+".x", deform[:,:,:,0])
    inrimage.write_inrimage(tmpDef+".y", deform[:,:,:,1])
    inrimage.write_inrimage(tmpDef+".z", deform[:,:,:,2])

    cmd = " ".join((exe, tmpIm1, tmpOut, "-def" , tmpDef))
    print cmd
    os.system(cmd)
    im_res = imread(tmpOut)

    np.testing.assert_array_equal(im1, im_res)
    return im1, im_res


def test_reech3d_unit_vector_deform():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16))

    # -- a null deformation field. Must be of type float32 --
    # -- the deformation field is also expected to be in
    # the out to in direction --
    deform = SpatialImage(np.ones((11,11,1,3), dtype=np.float32), vdim=3)
    deform[:,:,:,2]=0

    # -- the hypothetical result image --
    hypo_res = SpatialImage(np.ones((11,11,1), dtype=np.uint16))
    hypo_res[-1,:,:] = 0
    hypo_res[:,-1,:] = 0

    # -- color2grey splits a deformation field into 3 scalar images (one per vect component) --
    im_res = reech3d(im1, deformation=color2grey(deform), interpolation="nearest")

    np.testing.assert_array_equal(hypo_res, im_res )
    return im1, im_res


def test_reech3d_pre_matrix_null_deform():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,1), dtype=np.uint16))

    # -- the matrix --
    trans = np.identity(4)
    trans[1,3] = -1
    trans = I(trans) # we take the invert, reech wants transfo from out to in.

    # -- a null deformation field. Must be of type float32 --
    # -- the deformation field is also expected to be in
    # the out to in direction --
    deform = SpatialImage(np.zeros((11,11,1,3), dtype=np.float32), vdim=3)

    # -- the hypothetical result image --
    hypo_res = SpatialImage(np.ones((11,11,1), dtype=np.uint16))
    hypo_res[:,-1,:] = 0

    # -- color2grey splits a deformation field into 3 scalar images (one per vect component) --
    im_res = reech3d(im1, mat_before=trans, deformation=color2grey(deform))

    np.testing.assert_array_equal(hypo_res, im_res)
    return hypo_res, im_res


def test_reech3d_pre_matrix_unit_vector_deform():

    # -- a fake image full of ones,
    # must be of type uint8, int8, uint16, int16 or float32 --
    im1 = SpatialImage(np.ones((11,11,3), dtype=np.uint16))

    # -- the matrix --
    trans = np.identity(4)
    # minus 0.5 in Z offset. The reason this is not -1 is that
    # if it was, the original point would end on the border
    # of the image and linear interpolation and then casting
    # would round this to 0 instead of 1.
    trans[2,3] = -0.5

    # -- a null deformation field. Must be of type float32 --
    # -- the deformation field is also expected to be in
    # the out to in direction --
    deform = SpatialImage(np.ones((11,11,3,3), dtype=np.float32), vdim=3)

    # -- the hypothetical result image --
    hypo_res = SpatialImage(np.ones((11,11,3), dtype=np.uint16))
    hypo_res[-1,:,:] = 0
    hypo_res[:,-1,:] = 0

    # -- color2grey splits a deformation field into 3 scalar images (one per vect component) --
    im_res = reech3d(im1, mat_before=trans, deformation=color2grey(deform))

    np.testing.assert_array_equal(hypo_res, im_res)
    return hypo_res, im_res
