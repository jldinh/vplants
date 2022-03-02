# -*- python -*-
#
#       vplants.mars_alt.alt.mapping
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


__license__ = "CeCILL v2"
__revision__ = " $Id: mapping.py 15613 2014-01-29 18:05:34Z jlegra02 $ "



import os
import os.path
from openalea.misc.temp import temp_name
from openalea.image.serial import inrimage

from vplants.mars_alt.alt import candidate_lineaging
from vplants.mars_alt.alt import optimal_lineage

from openalea.core.logger import get_logger
myLogger = get_logger(__name__)


def mapping(im_0,
            im_1,
            dist=3,
            expert_lineage=None,
            ndiv=8,
            use_binary=False,
            candidate_method="cell_shape",
            flow_method="rf_flow"):
    """ Given two images of an organ at t0 and t1, tries to find cell lineages.

    It does both the candidate estimation (guided by expert lineages) AND the flow algorithm
    to optimize the minimal cost lineage.

    .. note:: Image labels are expected to start from 2 (1 being the background)

    :TODO:
    - Move this function to vplants.mars_alt.alt.mapping.py.
    - integrate lineage filtering loop

    :Parameters:
      - `im_0` (|SpatialImage|) -  segmented image of meristem a t0
      - `im_1` (|SpatialImage|) -  segmented image of meristem a t1
      - `expert_lineage` (dict) - a dictionnary mapping mother labels to a list of child labels.
      - `ndiv` (int) -  an limit to the number of children a mother can have.  (used by graph flow)
      - `use_binary` (bool) - if True, will attempt to call directly the MAPPING binary if available instead of
         using the CTypes wrapping. This is the ground truth to assert that other implmentations
         yield similar results. If this is used, "candidate_method" and "flow_method" are not used.
      - `candidate_method` (str) - name of the method to use. "cell_shape" means that the distance `dist` is computed
         starting from the mother cell's boundary. "cell_as_box" considers cells as spheres and the distance
         is computed from the mother cell's barycenter corrected by the mean radius of cells. The mean radius of cell
         is the mean diagonal of all cells' bounding boxes.
      - `flow_method` (str) - name of the flow graph solving. "rf_flow" is the original published implementation by Romain Fernandez.

    """

    # be a bit defensive
    assert im_0.shape == im_1.shape
    assert im_0.voxelsize == im_1.voxelsize

    # don't put default container arguments as they are shared between instances
    # and bring in MANY side effects:
    if expert_lineage is None:
        expert_lineage = {}

    if None in [im_0, im_1]:
        myLogger.error("Lineaging got null input image")
        return None,None

    # If use_binary is True, candidate_method and flow_method are discarded and we attempt
    # to use Romain Fernandez' MAPPING binary.
    if use_binary:
        solver = RomainLineageTrackingDummyWrapper(im_0, im_1, dist, expert_lineage, ndiv)
    else:
        if candidate_method not in candidate_meth_map:
            myLogger.error("Unknown candidate methode: %s"%candidate_method)
            return None,None

        if flow_method not in flow_meth_map:
            myLogger.error("Unknown candidate methode: %s"%candidate_method)
            return None,None

        cfunc = candidate_meth_map[candidate_method]
        ffunc = flow_meth_map[flow_method]

        solver = PyLineageTracking( cfunc, ffunc,
                                    im_0, im_1, dist, expert_lineage, ndiv)

    solver.run()

    # return outputs
    return solver.get_lineages(), solver.get_candidates()


candidate_meth_map = {"cell_shape":candidate_lineaging.rfernandez_get_candidate_successors,
                      "cell_as_box":candidate_lineaging.py_get_candidate_successors}

flow_meth_map = {"rf_flow": optimal_lineage.rfernandez_flow_solving,
                 "nx_simplex": optimal_lineage.nx_flow_solving}


##################################################################################
# ############################################################################## #
# # CLASSES THAT HANDLE THE FULL CANDIDATE IDENTIFICATION + GRAPH FLOW SOLVING # #
# ############################################################################## #
##################################################################################

class LineageTracking(object):

    TRACKING_MODE   = 1
#    COMPARISON_MODE = 2

    def __init__(self, image_T0, image_T1, distance, expert=None, ndiv=8):
        """|SpatialImage|, |SpatialImage|, integer, dict."""
        self._t0 = image_T0
        self._t1 = image_T1
        self._lineages = {}
        self._mode     = LineageTracking.TRACKING_MODE
        self._distance = distance
        self._expert   = expert
        self._ndiv     = ndiv

    def run(self):
        self._lineages = self.compute_lineages()

    def compute_lineages(self):
        raise NotImplementedError

    def get_lineages(self):
        return self._lineages

    def get_candidates(self):
        return self._candidates


#####################################################################
# A Dummy Wrapper around the MAPPING executable by Romain Fernandez #
#####################################################################
class RomainLineageTrackingDummyWrapper(LineageTracking):

    # : Name of the binary to call, depending on the platform.
    exe = "MAPPING" if os.name == "posix" else "MAPPING.exe"

    def __init__(self, image_T0, image_T1, distance, expert=None, ndiv=8):
        LineageTracking.__init__(self, image_T0, image_T1, distance, expert, ndiv)

        # -- the idea is that we request the system for a valid temporary
        # file name that we will use to write/read data to/from.
        # since the binary takes file names as input. --

        # -- The images that we will read with mapping --
        self.__tempInr0    = temp_name(suffix=".inr.gz")
        self.__tempInr1    = temp_name(suffix=".inr.gz")
        inrimage.write_inrimage(self.__tempInr0, image_T0)
        inrimage.write_inrimage(self.__tempInr1, image_T1)

        # -- the output results --
        self.__outName     = temp_name(suffix=".inr.gz")
        self.__outScores   = temp_name(suffix=".inr.gz")
        self.__mappingFile = temp_name(suffix=".txt")

        # -- if we have an expert dictionnary, write it down --
        if expert is not None:
            self.__expertFname = temp_name(".txt")
            lineage_to_file(self.__expertFname, expert)
        else:
            self.__expertFname = None

    def compute_lineages(self):
        args = [self.__tempInr0,
                self.__tempInr1,
                self.__outName,
                self.__outScores]

        if self.__expertFname:
            args.append("-fixKnownCells")
            args.append(self.__expertFname)

        if self._mode == LineageTracking.TRACKING_MODE:
            args.append("-tracking")
            args.append(str(self._distance))
        else:
            args.append("-comparison")

        args.append(self.__mappingFile)

        command = RomainLineageTrackingDummyWrapper.exe + " " + " ".join(args)

        print command
        os.system(command)
        mapping = lineage_from_file(self.__mappingFile)

        self._candidates = self.__make_candidate_file()

        return mapping

    def __make_candidate_file(self):
        print "__make_candidate_file 0"
        di = {}
        with open("SuiviSeg.debugScoresTries.debug", "r") as realScores:
            lines = realScores.readlines()
            for l in lines:
                l = l.split()
                m,k,d = int(float(l[4])), int(float(l[7])), float(l[11])
                di.setdefault(m, []).append((k,1.0-d))
        #lineage_to_file("RomainLineageTrackingDummyWrapper.candy", di)
        return di



################################################################
# Base class for solvers that allow to choose which solver     #
# for either candidate estimation or flow solving.             #
################################################################
class LineageingException(Exception):
    pass

class CandidateMothersDoesNotContainExpertMothersException(LineageingException):
    pass

class CandidateKidsDoesNotContainExpertKidsException(LineageingException):
    pass

class PyLineageTracking(LineageTracking):
    def __init__(self, candidate_strategy, flow_strategy,
                 image_T0, image_T1, distance, expert=None, ndiv=8):
        LineageTracking.__init__(self, image_T0, image_T1, distance, expert, ndiv)
        self.__candidate_strat = candidate_strategy
        self.__flow_strat      = flow_strategy

    def compute_lineages(self):
        print "compute_lineages: candidates"
        candidates = self.__candidate_strat(self._t0,
                                            self._t1,
                                            self._distance,
                                            ndiv=self._ndiv,
                                            bkgdLabel=1,
                                            as_scores=self.__flow_strat.distances_as_scores)

        self._candidates = candidates

        # -- if we have expert lineaging, fix the candidates --
        if False: #self._expert is not None:
            print "merging candidates"
            candidates = optimal_lineage.merge_expert_and_candidates(self._expert, candidates)

        included, missedkids, missedmoms = candidate_lineaging.candidate_contains_expert(self._expert, candidates)

        #lineage_to_file(self.__candidate_strat.__name__+".candy", candidates)
        print candidates
        maxLabel0 = self._t0.max()
        maxLabel1 = self._t1.max()

        print "graph flow", maxLabel0, maxLabel1
        return self.__flow_strat(self._ndiv, candidates, maxLabel0, maxLabel1)



#####################
# SOME IO FUNCTIONS #
#####################

def lineage_to_file(filename, lineage):
    """Writes a lineage dictionnary to a file if RomainFernandez format"""
    text = "NombreDeCellules="+str(len(lineage))+"\n"
    for m, daugh in lineage.iteritems():
        daugh.sort()
        text += str(m) + " : " + "nbFilles=" + str(len(daugh)) + " -> ["
        for d in daugh:
            if isinstance(d, tuple): #we have a daughter+distance tuple
                text += "(%i, %.3f),"%d
            else:
                text += str(d)+","
        text += "-1,]\n"
    with open(filename, "w+t") as expertFile:
        expertFile.write(text)
    return lineage


def lineage_from_file(filename):
    """Reads a lineage definition file and outputs a dict"""
    d = {}
    with open(filename, "r") as f:

        # -- in case the file is a python module that encodes the mapping
        # as a dictionnary. We simply evaluate the second part of the assignment
        # operator ( thus the split("=")[1] ) --
        try:
            d = eval(f.read().split("=")[1])
            check_lineage_input(d)
        except:
            # --rewind and try classical read. --
            f.seek(0)

        lines = f.readlines()
        # -- Find out if we are looking at a mapping in the Romain Fernandez format --
        rf_style = False
        for l in lines:
            if "NombreDeCellules" in l:
                rf_style = True
                break

        if rf_style: # is RomainFernandez format
            for l in lines[1:]:
                if not "->" in l:
                    continue
                colon = l.index(":")
                arrow = l.index(">")
                d[ eval( l[:colon] ) ] = list(eval( l[arrow+1:] )[:-1])
            check_lineage_input(d)
        else: # brute text (Mirabet Style)
            for l in lines:
                if l == "\n": continue
                if "[" in l: # avoid sub_lineage and iterative list creation
                    l=l.replace("[", "")
                    l=l.replace("]", "")
                try:
                    values = list(eval(l.replace(" ", ",")))
                except SyntaxError: # avoid SyntaxError if '*' marker in the lineage file.
                    l=l.replace("*", "")
                    values = list(eval(l.replace(" ", ",")))
                if len(values) <= 1: continue
                d[values[0]] = values[1:]
    return d


def sub_lineage_from_file(filename):
    """Reads a lineage definition file and outputs a dict"""
    d = {}
    with open(filename, "r") as f:

        # -- in case the file is a python module that encodes the mapping
        # as a dictionnary. We simply evaluate the second part of the assignment
        # operator ( thus the split("=")[1] ) --
        try:
            d = eval(f.read().split("=")[1])
            check_lineage_input(d)
        except:
            # --rewind and try classical read. --
            f.seek(0)

        lines = f.readlines()
        # -- Find out if we are looking at a mapping in the Romain Fernandez format --
        rf_style = False
        for l in lines:
            if "NombreDeCellules" in l:
                rf_style = True
                break

        if rf_style: # is RomainFernandez format
            for l in lines[1:]:
                if not "->" in l:
                    continue
                colon = l.index(":")
                arrow = l.index(">")
                d[ eval( l[:colon] ) ] = list(eval( l[arrow+1:] )[:-1])
            check_lineage_input(d)
        else: # brute text (Mirabet Style)
            for l in lines:
                if l == "\n": continue
                try:
                    values = list(eval(l.replace(" ", ",")))
                except SyntaxError: # avoid SyntaxError if '*' marker in the lineage file.
                    l=l.replace("*", "")
                    values = list(eval(l.replace(" ", ",")))
                if len(values) <= 1: continue
                d[values[0]] = values[1:]
    return d


def check_lineage_input(mapping):
    for mom, kids in mapping.iteritems():
        if not isinstance(mom, int):
            raise Exception("Badly formatted mapping, mom %s not int"%str(mom))
        for kid in kids:
            if isinstance(kid, tuple):
                if not isinstance(kid[0], (int, long)):
                    raise Exception("Badly formatted mapping, kid %s of mom %d not int"%(str(kid), mom))
                if not isinstance(kid[1], float):
                    raise Exception("Badly formatted mapping, kid distance or score %s of mom %d not float"%(str(kid), mom))
            elif not isinstance(kid, (int, long)):
                raise Exception("Badly formatted mapping, kid %s of mom %d not int"%(str(kid), mom))


















###############################
# TESTING FUNCTIONS COME NEXT #
###############################

def test_base(distance=3,
              if1 = "/user/dbarbeau/home/Devel/hackaton/Daniel-mapping/imgSegDefStep2_1_12_iter_1_TEST_INIT_12.inr.gz",
              if2 = "/user/dbarbeau/home/Devel/hackaton/Daniel-mapping/imgSeg_2_12.inr.gz",
              expertf = "/user/dbarbeau/home/Devel/hackaton/Daniel-mapping/mapping_init_TEST_INIT_12_iter_1_TEST_INIT_12") :
    image_T0 = inrimage.read_inrimage(if1)
    image_T1 = inrimage.read_inrimage(if2)
    exp      = lineage_from_file(expertf)
    return image_T0, image_T1, exp, distance



#########################################################
# TESTING METHODS -- TESTING METHODS -- TESTING METHODS #
#########################################################
def test_RomainLineageTrackingDummyWrapper():
    image_T0, image_T1, expert, distance = test_base()
    solverCls = RomainLineageTrackingDummyWrapper
    solver = solverCls(image_T0, image_T1, distance, expert)
    solver.run()
    return solver


def test_Py_Nx_LineageTracking():
    image_T0, image_T1, expert, distance = test_base()
    solver = PyLineageTracking(candidate_lineaging.py_get_candidate_successors,
                               optimal_lineage.nx_flow_solving,
                               image_T0, image_T1, distance, expert)
    solver.run()
    return solver

def test_Py_RF_LineageTracking():
    image_T0, image_T1, expert, distance = test_base()
    solver = PyLineageTracking(candidate_lineaging.py_get_candidate_successors,
                               optimal_lineage.rfernandez_flow_solving,
                               image_T0, image_T1, distance, expert)
    solver.run()
    return solver

def test_RF_Nx_LineageTracking():
    image_T0, image_T1, expert, distance = test_base()
    solver = PyLineageTracking(candidate_lineaging.rfernandez_get_candidate_successors,
                               optimal_lineage.nx_flow_solving,
                               image_T0, image_T1, distance, expert)
    solver.run()
    return solver

def test_RF_RF_LineageTracking():
    image_T0, image_T1, expert, distance = test_base()
    solver = PyLineageTracking(candidate_lineaging.rfernandez_get_candidate_successors,
                               optimal_lineage.rfernandez_flow_solving,
                               image_T0, image_T1, distance, expert)
    solver.run()
    return solver



def full_test_suite(prefix=None):
    if prefix==None:
        import time
        prefix = time.strftime("%d_%b_%Y__%H_%M_%S", time.localtime())

    funcs = [test_RomainLineageTrackingDummyWrapper,
             #test_Py_Nx_LineageTracking,
             #test_Py_RF_LineageTracking,
             #test_RF_Nx_LineageTracking,
             test_RF_RF_LineageTracking ]

    for f in funcs:
        filename = prefix+"_"+f.__name__+".txt"
        try:
            lin = f()
        except Exception, e:
            print "Couldn't execute", f.__name__
            print e
            continue
        else:
            lineage_to_file(filename, lin.get_lineages())
