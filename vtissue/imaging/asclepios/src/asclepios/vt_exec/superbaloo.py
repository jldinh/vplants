# -*- python -*-
#
#       vplants.asclepios.vt_exec.superbaloo
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################
"""Different wrappers to superbaloo non linear registration algorithm"""


__license__ = "CeCILL v2"
__revision__ = " $Id: superbaloo.py 12424 2012-07-02 16:01:26Z chakkrit $ "



##########################################
# Entry point to superbaloo registration #
##########################################
def superbaloo( reference,
                floating,
                initial_trsfs    = None,
                start_level      = 3,
                end_level        = 1,
                max_iterations   = 10,
                highest_fraction = 0.5,
                minimal_variance = 0.0,
                blockSize        = None,
                neighborhood     = None,
                similarity       = "cc",
                outlier_sigma    = 3,
                threads          = 1,
                use_binary       = False):
    """
    Compute a non-linear transformation that places voxels from "floating" over those of
    "reference".

    SuperBaloo in an image registration algorithm based on a similar block-matching and pyramidal
    registration algorithm as Baladin. The main difference is that SuperBaloo estimates a dense
    deformation field instead of a linear or affine matrix.

    :Parameters:
      - `reference`        (|SpatialImage|) - The image to use as a reference for the registration
      - `floating`         (|SpatialImage|) - The image to register.
      - `initial_trsfs`    (list-of-vectorfields-and-affinematrices) - List of transformations (numpy.matrix / |SpatialImage|) to
         "apply" to the floating image before computing a finer registration. These transforms must be in ref->flo direction
         and in voxel space (from ref_space to flo_space, not real_space to real_space).
         This also means that the last initial deformation comes first in the list.
      - `start_level`      (int) - level of the pyramid to start at (the bigger the smaller the image will be at the highest level)
      - `end_level`        (int) - level of the pyramid to stop at.
      - `max_iterations`   (int) - number of iterations per level of pyramid (the actual number of iterations can be smaller:
         if their is no difference between two iterations, it will stop iterating.
      - `highest_fraction` (float) - fraction of the highest variance blocks to take into consideration.
      - `minimal_variance` (float) - value of variance below which blocks are disregarded.
      - `blockSize`        (tuple of ints) - Size of a block (in voxels).
      - `neighborhood`     (tuple of ints) - Size of the neighborhood to visit (in voxels).
      - `similarity`       (str) - Similarity measure to use:
          - ssd  : sum of quare differences
          - cc   : correlation coefficient
          - scc  : no idea
          - tcc  : trimmed correlation coefficient?
          - tscc : no idea
      - `outlier_sigma`    (float) - value beyond which estimator prunes pairings
      - `threads`          (int)   - number of threads to use
      - `use_binary`       (bool)  - use the SuperBaloo executable instead of the CTypes wrapper.
    """


    if use_binary:
        baloo  = SuperBalooBinWrapper(reference,
                                      floating,
                                      initial_trsfs,
                                      start_level,
                                      end_level,
                                      max_iterations,
                                      highest_fraction,
                                      minimal_variance,
                                      blockSize,
                                      neighborhood,
                                      similarity,
                                      outlier_sigma,
                                      threads)
    else:
        raise Exception("The ctypes wrapper to superbaloo does not exist yet")

    baloo.run()
    return baloo.get_deformation_field()





#####################################################################
# Different implementations of the wrapping of superbaloo come next #
#####################################################################
import numpy as np

identity = np.identity(4)

class SuperBalooRegistration(object):
    def __init__(self,
                 reference,
                 floating,
                 initial_trsfs    = None,
                 start_level      = 3,
                 end_level        = 1,
                 max_iterations   = 10,
                 highest_fraction = 0.5,
                 minimal_variance = 0.0,
                 blockSize        = None,
                 neighborhood     = None,
                 similarity       = "cc",
                 outlier_sigma    = 3,
                 threads          = 1):

        self._reference        = reference
        self._floating         = floating
        self._initial_trsfs    = initial_trsfs or [identity.copy()]
        self._start_level      = start_level
        self._end_level        = end_level
        self._max_iterations   = max_iterations
        self._highest_fraction = highest_fraction
        self._minimal_variance = minimal_variance
        self._blockSize        = blockSize    or (2,2,2)
        self._neighborhood     = neighborhood or (3,3,3)
        self._similarity       = similarity
        self._outlier_sigma    = outlier_sigma
        self._threads          = threads

    def run(self):
        self._deformation_field = self.compute_deformation()

    def compute_deformation(self):
        raise NotImplementedError

    def get_deformation_field(self):
        return self._deformation_field



#####################################################################
# A Dummy Wrapper around the SuperBaloo executable by O. Commowick  #
#####################################################################
import os
import os.path
from openalea.image.serial import inrimage
from openalea.image.serial.basics import imread, imsave
from openalea.image.spatial_image import SpatialImage
from openalea.misc.temp import temp_name

class SuperBalooBinWrapper(SuperBalooRegistration):

    # : Name of the binary to call, depending on the platform.
    exe = "SuperBaloo" if os.name == "posix" else "SuperBaloo.exe"
    available = os.system(exe) not in [1,32512] # Posix specific?

    def compute_deformation(self):
        # -- the idea is that we request the system for a valid temporary
        # file name that we will use to write/read data to/from.
        # since the binary takes file names as input. --
        __tempInr0    = temp_name(suffix=".inr.gz")
        __tempInr1    = temp_name(suffix=".inr.gz")
        __initTrsf    = temp_name(suffix=".tsl")
        __outName     = temp_name(suffix=".inr.gz")

        # -- The images that we will read with SuperBaloo --
        imsave(__tempInr0, SpatialImage(self._reference))
        imsave(__tempInr1, SpatialImage(self._floating))
        #inrimage.write_inrimage(__tempInr0, self._reference)
        #inrimage.write_inrimage(__tempInr1, self._floating)

        # -- write transform list --
        transform_list_to_tsl_file(__initTrsf, self._initial_trsfs)

        # -- output prefix --
        outprefix = __outName.split('.')[0]

        # -- now the command line --
        cmd  = "-ref %s -flo %s -res %s -ini %s -tran dense "%(__tempInr0, __tempInr1, outprefix, __initTrsf) +\
               "-lst %d -lnd %d -ptk %f -mV %f -iter %d -all "%(self._start_level, self._end_level, self._highest_fraction, self._minimal_variance, self._max_iterations) +\
               "-bhx %f -bhy %f -bhz %f "%(self._blockSize[0]/2., self._blockSize[1]/2., self._blockSize[2]/2.) +\
               "-blvx %f -blvy %f -blvz %f "%(self._neighborhood[0], self._neighborhood[1], self._neighborhood[2]) +\
               "-ssi %s -nbp %d -osig %f" %(self._similarity, self._threads, self._outlier_sigma)

        cmd =  " ".join([SuperBalooBinWrapper.exe, cmd])
        print "Starting superbaloo like this:", cmd
        os.system( cmd )
        trsfs = transform_list_from_tsl_file(outprefix+"_tr.tsl")
        return trsfs[-1].get_transformation()





#####################
# UTILITY FUNCTIONS #
#####################
def matrix_to_file(matrix, filename):
    with open(filename, "w") as trsFile:
        trsFile.write("(\nO8\n")
        # -- no other way to write a matrix than this boring loop? --
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                last = j == (matrix.shape[1]-1)
                num = matrix[i,j]
                trsFile.write(str(num))
                trsFile.write(" " if not last else "\n")
        trsFile.write(")")

def matrix_from_file(filename):
    lines = []
    with open(filename, "r") as trsFile:
        for l in trsFile:
            skipLine = "(" in l or ")" in l or "O8" in l
            if skipLine:
                continue
            lines.append( eval(", ".join(l.split(" "))) )
    return np.matrix(lines)


def transform_list_to_tsl_file(filename, trsfList):
    # -- TODO properly serialise the initial transforms
    # currently we only take affine matrices and deformation fields. --
    with open(filename, "w") as tslFile:
        for trsf in reversed(trsfList):
            matType = None
            if isinstance(trsf, SpatialImage):
                trsfTypeStr = "DENSE_FIELD"
                trsfFname   = temp_name(suffix=".inr.gz")
                prfix       = trsfFname.split(".")[0]
                inrimage.write_inrimage(trsfFname, trsf)
            elif isinstance(trsf, np.ndarray) and trsf.shape==(4,4):
                trsfTypeStr = "MATRICE"
                matType     = "AFFI"
                trsfFname   = temp_name(suffix=".trsf")
                prfix       = trsfFname.split(".")[0]
                matrix_to_file(trsf, trsfFname)
            else:
                raise Exception("Unknow transform type")
            tslFile.write("<TRSF>\n")
            tslFile.write("TRSF_TYPE=%s\n"%trsfTypeStr)
            if matType:
                tslFile.write("MAT_TYPE=%s\n"%matType)
            tslFile.write("PREFIX=%s\n"%prfix)
            tslFile.write("</TRSF>\n")


class TSLTransfoDescription(object):
    def __init__(self):
        self.type   = None
        self.file   = None
        self.invert = None
        self.mat_t  = None
        self.__tr = None

    def get_filename(self):
        if self.type == "MATRICE":
            return ".".join((self.file, "trsf"))
        elif self.type == "DENSE_FIELD":
            return ".".join((self.file, "inr.gz"))
        else:
            return None

    def get_transformation(self):
        return self.__tr

    def read_transformation(self):
        if self.type == "MATRICE":
            print "reading matrix"
            self.__tr = matrix_from_file(self.get_filename())
        elif self.type == "DENSE_FIELD":
            print "reading dense field"
            self.__tr = imread(self.get_filename())
        else:
            pass


def transform_list_from_tsl_file(filename):
    # -- TODO properly serialise the initial transforms
    # currently we only take affine matrices and deformation fields. --
    curTr = None
    trList = []
    with open(filename, "r") as tslFile:
        for l in tslFile:
            if "<TRSF>" in l:
                curTr = TSLTransfoDescription()
                trList.append(curTr)
            elif "TRSF_TYPE" in l and curTr:
                curTr.type = l.split("=")[1].strip()
            elif "PREFIX" in l and curTr:
                curTr.file = l.split("=")[1].strip()
            elif "INVERT" in l and curTr:
                curTr.invert = l.split("=")[1].strip()
            elif "MAT_TYPE" in l and curTr:
                curTr.mat_t = l.split("=")[1].strip()
            elif "</TRSF>" in l:
                curTr.read_transformation()
                curTr = None
    return trList
