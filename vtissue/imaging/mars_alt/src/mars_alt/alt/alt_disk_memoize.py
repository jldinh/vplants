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
__revision__ = " $Id: alt_disk_memoize.py 11319 2011-10-27 15:44:03Z dbarbeau $ "


import os
import os.path
import datetime
import traceback

def alt_intermediate(context, *dataspecs):
    """ Creates a decorator that retreives intermediate data from the intermediate data object"""
    def decorator(f):
        def decorated(*args, **kwargs):
            idata = kwargs.get("intermediate_data")
            if idata:
                idata.set_context(context)
                paths = [os.path.join(idata.get_wd(), idata.get_data_path(spec)) for spec in dataspecs]
                existence = [os.path.exists(pth) for pth in paths]
                if False in existence:
                    print f.__name__, "cannot reload intermediate data", existence, "::", dataspecs
                    results = f(*args, **kwargs)
                    assert len(results) == len(dataspecs)
                    for spec, res in zip(dataspecs, results):
                        idata.save_data(spec, res)
                    return results
                else:
                    try:
                        print "trying to reuse previous data"
                        return [idata.load_data(spec) for spec in dataspecs]
                    except Exception, e:
                        print f.__name__, "cannot reload intermediate data", e
                        results = f(*args, **kwargs)
                        assert len(results) == len(dataspecs)
                        for spec, res in zip(dataspecs, results):
                            idata.save_data(spec, res)
                        return results
            else:
                return f(*args, **kwargs)
        return decorated
    return decorator


from vplants.mars_alt.alt.mapping import lineage_from_file, lineage_to_file
from openalea.image.all import imread, imsave
import cPickle
import numpy


class IntermediateData(object):

    dt_to_ext = {"image"        : ".inr.gz",
                 "clineage"     : ".clin",
                 "lineage"      : ".lin",
                 "picklable"    : ".pk",
                 "small_matrix" : ".txt",
                 }

    dt_fmt = "%Y-%m-%d-%H-%M-%S"

    def __init__(self, workingdir, dt=None, logfile=None):
        self.time_stamp = dt or datetime.datetime.now()
        self.iteration  = 0
        self.context    = ""
        self.set_working_dir(workingdir)
        self.set_logfile(logfile)

    def log(self, msg, exc=False):
        try:
            fd = open(self.logfile, "a")
            fd.write( str(datetime.datetime.now()) + " : " + msg +"\n")
            if exc:
                traceback.print_exc(file=fd)
                traceback.print_exc()
            fd.close()
        except:
            print str(datetime.datetime.now()) + " : " + msg

    def set_context(self, context):
        self.context = context

    def set_iteration(self, iteration):
        self.iteration = iteration

    def set_working_dir(self, workingdir):
        abspath = os.path.abspath(os.path.expanduser(workingdir))
        if not os.path.exists(abspath):
            try:
                os.makedirs(abspath)
            except:
                print "cannot create", abspath
        self.wd = abspath

    def get_working_dir(self):
        return self.wd

    get_wd = get_working_dir

    def set_logfile(self, logfile):
        if isinstance(logfile, file) and logfile.mode == "w":
            self.logfile = logfile.name
            logfile.close()
        elif isinstance(logfile, str):
            self.logfile = os.path.join(self.wd, logfile)
        else:
            self.logfile = os.path.join(self.wd,  "_".join([self.context, self.time_stamp.strftime(self.dt_fmt)+".log"]) )

    def _make_file_name(self, spec):
        name, dt = spec
        return "_".join([self.context, self.time_stamp.strftime(self.dt_fmt), str(self.iteration), name+self.dt_to_ext[dt]])

    get_data_path = _make_file_name

    def save_data(self, spec, res):
        name, dt = spec
        fullpath = os.path.join(self.wd, self._make_file_name(spec))
        self.log("saving " + str(spec) + " to " + fullpath)
        if res is None:
            self._save_None(fullpath)
        else:
            try:
                getattr(self, "_save_"+dt)(fullpath, res)
            except:
                self.log("saving " + str(spec) + " to " + fullpath + ": FAILED", exc=True)
                raise

    def load_data(self, spec):
        name, dt = spec
        fullpath = os.path.join(self.wd, self._make_file_name(spec))
        self.log("loading " + str(spec) + " from " + fullpath)
        if self._read_None(fullpath):
            return None
        else:
            try:
                return getattr(self, "_load_"+dt)(fullpath)
            except:
                self.log("loading " + str(spec) + " from " + fullpath + ": FAILED", exc=True)
                raise

    ###############################################################
    # Sometimes functions return None objects and meant to do so! #
    ###############################################################
    def _save_None(self, path):
        f = open(path, "w")
        f.write("Python::NoneType\n")
        f.close()

    def _read_None(self, path):
        f = open(path, "r")
        t = f.read(16)
        f.close()
        return t=="Python::NoneType"

    ##############################
    # specific load/save methods #
    ##############################
    def _save_image(self, path, image):
        imsave(path, image)

    def _load_image(self, path):
        return imread(path)

    def _save_clineage(self, path, clineage):
        lineage_to_file(path, clineage)

    def _load_clineage(self, path):
        return lineage_from_file(path)

    _save_lineage = _save_clineage
    _load_lineage = _load_clineage

    def _save_picklable(self, path, obj):
        cPickle.dump(obj, open(path, "w"))

    def _load_picklable(self, path):
        return cPickle.load(open(path))

    def _save_small_matrix(self, path, obj):
        numpy.savetxt(path, obj)

    def _load_small_matrix(self, path):
        return numpy.loadtxt(path)






