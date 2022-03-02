from vplants.asclepios.vt_exec.reech3d   import reech3d
from vplants.asclepios.vt_exec.watershed import watershed

###########################
# Reech3D resampling node #
###########################
wra_reech3d = reech3d

#############
# Watershed #
#############
wra_watershed = watershed

###########################################################
# The Baladin node: it is implemented here and not in the #
# __wralea__.py because it is a bit too big to elegantly  #
# take place there.                                       #
###########################################################
from openalea.core import Node
from openalea.core import IFloat, IEnumStr
from vplants.asclepios.vt_exec.baladin import baladin

class BlockMatching(Node):
    __doc__ = baladin.__doc__

    def __init__(self):
        Node.__init__(self,

        inputs = [  {"name" : "reference image", "interface" : None},
                    {"name" : "floating image", "interface" : None},
                    {"name" : "initial matrix", "interface" : None},
                    {"name" : "initial real matrix", "interface" : None},

                    {"name" : "voxel size of the floating image", "interface" : "ITuple", "value" : None, "hide" : True},
                    {"name" : "voxel size of the reference image", "interface" : "ITuple", "value" : None, "hide" : True},

                    {"name" : "low_threshold_floating", "interface" : "IInt", "value" : -100000, "hide" : True},
                    {"name" : "high_threshold_floating", "interface" : "IInt", "value" : 100000, "hide" : True},
                    {"name" : "low_threshold_reference", "interface" : "IInt", "value" : -100000, "hide" : True},
                    {"name" : "high_threshold_reference", "interface" : "IInt", "value" : 100000, "hide" : True},
                    {"name" : "fraction_block-reference", "interface" : "IFloat", "value" : 0.5, "hide" : True},
                    {"name" : "fraction-block-floating", "interface" : "IFloat", "value" : 0.5, "hide" : True},

                    {"name" : "transformation", "interface" : IEnumStr(["Rigid","Similitude","Affine"]), "value" : "Rigid"},

                    {"name" : "estimator", "interface" : IEnumStr(["Weighted Least Trimmed Squares","Least Trimmed Squares","Weighted Least Squares","Least Squares"]),
                     "value" : "Weighted Least Trimmed Squares"},

                    {"name" : "ltscut", "interface" : IFloat(0.,1.,0.01), "value" : 0.75},

                    {"name" : "similarity-measure", "interface" : IEnumStr(["correlation coefficient","extended correlation coefficient"]),
                     "value" : "correlation coefficient", "hide" : True},

                    {"name" : "threshold-similarity-measure", "interface" : "IFloat", "value" : 0., "hide" : True},
                    {"name" : "max-iterations", "interface" : "IInt", "value" : 4, "hide" : True},
                    {"name" : "block-sizes", "interface" : "ITuple", "value" : (4,4,4), "hide" : True},
                    {"name" : "block-spacing", "interface" : "ITuple", "value" : (3,3,3), "hide" : True},
                    {"name" : "block-borders", "interface" : "ITuple", "value" : (0,0,0), "hide" : True},
                    {"name" : "block-neighborhood-sizes", "interface" : "ITuple", "value" : (3,3,3), "hide" : True},
                    {"name" : "block-steps", "interface" : "ITuple", "value" : (1,1,1), "hide" : True},
                    {"name" : "fraction-variance-blocks", "interface" : "IFloat", "value" : 0.75},
                    {"name" : "decrement-fraction-variance-blocks", "interface" : "IFloat", "value" : 0.2, "hide" : True},
                    {"name" : "minimum-fraction-variance-blocks", "interface" : "IFloat", "value" : 0.5, "hide" : True},

                    {"name" : "pyramid-levels", "interface" : "IInt", "value" : 6},

                    {"name" : "pyramid-finest-level", "interface" : "IInt", "value" : 1},

                    {"name" : "pyramid-filtered", "interface" : "IInt", "value" : 0, "hide" : True},
                    {"name" : "rms", "interface" : "IBool", "value" : True, "hide" : True},

                    {"name" : "no fraction variance blocks", "interface" : "IBool", "value" : False, "hide" : True},
                    {"name" : "automated version", "interface" : "IBool", "value" : False, "hide" : True},
                    {"name" : "inverse", "interface" : "IBool", "value" : False, "hide" : True},
                    {"name" : "just resample", "interface" : "IBool", "value" : False, "hide" : True}
                    ],

        outputs = [ {"name" : "result image", "interface" : None},
                    {"name" : "block-matching transformation", "interface" : None}])

    def __call__(self, inputs):

        ref = self.get_input("reference image")
        flo = self.get_input("floating image")

        inivox = self.get_input("initial matrix")
        inireel = self.get_input("initial real matrix")

        vsr = self.get_input("voxel size of the reference image")
        vsf = self.get_input("voxel size of the floating image")

        ltr = self.get_input("low_threshold_reference")
        htr = self.get_input("high_threshold_reference")
        ltf = self.get_input("low_threshold_floating")
        htf = self.get_input("high_threshold_floating")

        fbr = self.get_input("fraction_block-reference")
        fbf = self.get_input("fraction-block-floating")

        transformation = None
        transfo = self.get_input("transformation")
        if transfo == "Rigid":
            transformation = "rigi"
        elif transfo == "Similitude":
            transformation = "simi"
        elif transfo == "Affine":
            transformation = "affi"

        estimator = None
        estim = self.get_input("estimator")
        if estim == "Weighted Least Trimmed Squares":
            estimator = "ltsw"
        elif estim == "Least Trimmed Squares":
            estimator = "lts"
        elif estim == "Weighted Least Squares":
            estimator = "lsw"
        elif estim == "Least Squares":
            estimator = "ls"

        ltscut = self.get_input("ltscut")

        similarity_measure = None
        mesure = self.get_input("similarity-measure")
        if mesure == "correlation coefficient":
            similarity_measure = "cc"
        elif mesure == "extended correlation coefficient":
            similarity_measure = "ecc"

        tsi = self.get_input("threshold-similarity-measure")
        nbiter = self.get_input("max-iterations")

        bld = self.get_input("block-sizes")
        blp = self.get_input("block-spacing")
        blb = self.get_input("block-borders")
        bldv = self.get_input("block-neighborhood-sizes")
        blpv = self.get_input("block-steps")

        v = self.get_input("fraction-variance-blocks")
        vs = self.get_input("minimum-fraction-variance-blocks")
        vd = self.get_input("decrement-fraction-variance-blocks")

        pyn = self.get_input("pyramid-levels")
        pys = self.get_input("pyramid-finest-level")
        pyfilt = self.get_input("pyramid-filtered")
        rms = self.get_input("rms")

        nov = self.get_input("no fraction variance blocks")
        auto = self.get_input("automated version")
        inv = self.get_input("inverse")
        stop = self.get_input("just resample")

        img_result, transformation_result = baladin(ref, flo, inivox, inireel, vsf, vsr, ltf, htf, ltr, htr, fbr, fbf, transformation,
                                                    estimator, ltscut, similarity_measure, tsi, nbiter, rms, bld, blp, blb, bldv, blpv,
                                                    v, vd, vs, nov, pyn, pys, pyfilt, auto, inv, stop)

        return img_result,transformation_result



##############################################################
# The SuperBaloo node: it is implemented here and not in the #
# __wralea__.py because it is a bit too big to elegantly     #
# take place there.                                          #
##############################################################
from openalea.core import Node
from openalea.core import IInt, IBool, IFloat, \
    ISequence, IEnumStr, IStr, IDirStr, ITuple, IDict
from vplants.asclepios.vt_exec import superbaloo

class SuperBaloo(Node):
    __doc__ = superbaloo.superbaloo.__doc__

    def __init__(self):
        Node.__init__(self,

                      inputs = [  {"name" : "reference image", "interface" : None},
                                  {"name" : "floating image", "interface" : None},
                                  {"name" : "initial transforms list", "interface" : "ISequence"},
                                  {"name" : "start level", "interface" : "IInt", "value": 3},
                                  {"name" : "end level", "interface" : "IInt", "value": 1},
                                  {"name" : "max_iterations", "interface" : "IInt", "value": 10},
                                  {"name" : "highest_fraction", "interface" : IFloat(0.0,1.0,0.05), "value": 0.5},
                                  {"name" : "minimal_variance", "interface" : "IFloat", "value": 0.0},
                                  {"name" : "blockSize", "interface" : "ITuple", "value": (2,2,2)},
                                  {"name" : "neighborhood", "interface" : "ITuple", "value": (3,3,3)},
                                  {"name" : "similarity", "interface" : IEnumStr(["ssd","cc","scc","tcc","tscc"]), "value":"cc"},
                                  {"name" : "outlier_sigma", "interface": "IFloat", "value": 3},
                                  {"name" : "threads", "interface": "IInt", "value": 1},
                                  {"name" : "use_binary", "interface": "IBool", "value": True},
                                ],
                      outputs = [ {"name" : "dense vector field", "interface" : None} ]
                      )

    def __call__(self, inputs):
        print [type(i) for i in inputs]
        return superbaloo.superbaloo(*inputs),
