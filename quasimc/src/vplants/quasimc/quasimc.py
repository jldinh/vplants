""" A Python interface to the light environment program QuasiMC,
    which is part of the Virtual Laboratory plant modelling software
    created at the University of Calgary (http://www.algorithmicbotany.org).
    This interface, however, is based on the one developed for another
    light environment program, Caribu (see caribu.py).
"""

from subprocess import Popen,STDOUT, PIPE
import tempfile
import platform
from itertools import groupby, izip
from openalea.core.path import path
import openalea.plantgl.all as pgl
import numpy as np

def _process(cmd, directory, out):
    """ 
    Run a process in a shell. 
    Return the outputs in a file or string.
    """
    f = open(out,'w')
    ferror = open(directory/'error.dat','w')
    if platform.system() == 'Darwin':
        p = Popen(cmd, shell=True, cwd=directory,
              stdin=PIPE, stdout=f, stderr=ferror) # do not pipe stderr for QuasiMC
        status = p.communicate()
    else:
        p = Popen(cmd, shell=True, cwd=directory,
              stdin=PIPE, stdout=f, stderr=ferror)
        status = p.wait()

    f.close()
    ferror.close()
    return status

class QuasiMCError(Exception): pass
class QuasiMCOptionError(QuasiMCError): pass
class QuasiMCIOError(QuasiMCError): pass
class QuasiMCRunError(QuasiMCError): pass
    
class QuasiMC(object):
    
    def __init__(self,
                 inputfile = None, 
                 skyfile = None, 
                 optfile = None,
                 envirofile = None,
                 debug = False,
                 resfile = None
                 ):
        """
        Class for quasi-Monte Carlo path tracing on a 3D scene.
        
        debug : print messages and prevent removal of tempdir
        resfile : store output dictionary in file resfile (with pickle) if resfile is not None, store nothing otherwise
        """
        
        #print "\n >>>> QuasiMC.__init__ starts...\n"
        #debug mode
        self.my_dbg = debug
        
        #tempdir (initialised to allow testing of  existence in del)
        self.tempdir = path('')

        # Input files
        self.scene = inputfile
        self.skyfile = skyfile
        self.envfile = envirofile
        self.optfile = optfile
        self.output_triangles_str = ''
        self.light_source_str = ''

        # Output files
        self.resfile = resfile # is the name of file with the standard output from QuasiMC
        self.addresfile = 'addoutput.dat' # is the name of the file with additional output from QuasiMC

        # User options
        self.quasimc_name = "quasimc"
        self.ready = True
        
        # set default QuasiMC parameters
        self.verbose = 0

        #print "\n <<<< QuasiMC.__init__ ends...\n"

    def __del__(self):
        #print "QuasiMC.__del__ called !"

        if self.my_dbg == False and self.tempdir.exists():
            #print 'Remove tempfile %s'%self.tempdir
            self.tempdir.rmtree()
    
    def show(self, titre="############"):
        print "\n>>> QuasiMC state in ", titre
        print(self)
        print "<<<<\n\n"

    def init(self):
        if self.scene == None and self.output_triangles_str == '':
            raise QuasiMCOptionError(">>> The QuasiMC has not been fully initialized: scene has to be defined\n     =>  QuasiMC can not be run... - MC & CF 2012")
        
        #self.show("QuasiMC::init()")
        
        # Working directory
        try: 
            if self.my_dbg:
                print "I'm here ..."
                self.tempdir=path("./Run-tmp")
                if not self.tempdir.exists():
                    self.tempdir.mkdir() 
            else:
                # build a temporary directory
                self.tempdir = path(tempfile.mkdtemp())

        except:
            raise QuasiMCIOError(">>> QuasiMC can't create appropriate directory on your disk : check for read/write permission")
        
        # Copy the files (or file content) in the tempdir
        self.copyfiles()
           

    def copyfiles(self):
        d = self.tempdir
        
        if self.scene != None and os.path.exists(self.scene):
            fn = path(self.scene)
            fn.copy(d/fn.basename())
        else :
            fn = d/'input.dat'
            fn.write_text(self.output_triangles_str + "Control: 8\n")
        self.scene = path(fn.basename())

        if self.skyfile != None and os.path.exists(self.skyfile):
            fn = path(self.skyfile)
            fn.copy(d/fn.basename())
        else :
            fn = d/'sky.light'
            fn.write_text(self.light_source_str)
        self.skyfile = path(fn.basename())

        if self.optfile != None and os.path.exists(self.optfile):
            fn = path(self.optfile)
            fn.copy(d/fn.basename())
        else :
            fn = d/'quasimc.cfg'
            fn.write_text(self.quasimc_options())
        self.optfile = path(fn.basename())

        if self.envfile != None and os.path.exists(self.envfile):
            fn = path(self.envfile)
            fn.copy(d/fn.basename())
        else :
            fn = d/'enviro.e'
            fn.write_text(self.enviro_options())
        self.envfile = path(fn.basename()) 
                    
    def store_result(self):
        self.ids = []
        self.flux = []
        self.values = np.array([])
        if self.resfile != None:
            f = open(self.resfile)
            f.read(1) # read first byte that is comm lib's header
            for line in f:
                tokens = line.split()
                try:
                    self.ids.append(int(tokens[0]))
                    tokens[1] = tokens[1].strip('E()')
                    flux_per_w = tokens[1].split(',')
                    self.flux.append(float(flux_per_w[0]))
                except:
                    # THIS IS A BAD WAY TO SKIP BAD INPUT!
                    pass
            f.close()
            # check for additional output file
            if self.addresfile != None:
                f = open(self.addresfile)
                f.readline() # remove header line
                self.values = np.fromfile(f, dtype=np.float, count=len(self.ids)*7, sep=" ")
                self.values = self.values.reshape([len(self.ids),7])            
                f.close()

    def run(self):
        """
        The main QuasiMC program.
        """
        print "\n >>>> QuasiMC.run() starts...\n"
        self.init()
        d = self.tempdir
        #name, ext = self.scene.splitext()
        #fname = 'out_' + name + ext
        outname = d/'out_id_flux.dat' # the output from QuasiMC: in format 'id' E('flux') per object
        cmd = '%s -e %s %s -no_xserver < %s'%(self.quasimc_name,self.envfile,self.optfile,self.scene)
        #cmd = '%s -e %s %s -debug < %s'%(self.quasimc_name,self.envfile,self.optfile,self.scene)
        status = _process(cmd, d, outname)
        if (outname).exists():
            self.resfile = outname
            self.addresfile = d/self.addresfile
        else:
            raise QuasiMCRunError("Run failed (no output created).")
            
        self.store_result()

        print "\n <<<< QuasiMC.run() ends...\n"
                
    def enviro_options(self):
        line1 = "executable: QuasiMC.exe -e enviro.e quasimc.cfg\n"
        line2 = "communication type: pipes\n"
        line3 = "verbose: off\n"
        line4 = "interpreted modules: all\n"
        return line1 + line2 + line3 + line4
        
    def set_options(self,pars):
    
        return
        
    def quasimc_options(self):
        # would be nice to check for errors
        
        if (self.verbose >= 0 and self.verbose <= 3):
            out_str = "verbose: " + str(self.verbose) + "\n"
        else:
            out_str = "verbose: 1\n"
            print self.name + "error: verbose should be in range 0 to 3"            

        out_str += "number of runs: 1\n"
        out_str += "sampling method: korobov\n"
        out_str += "number of rays: 65536\n"

        out_str += "maximum depth: 4\n"
        out_str += "Russian roulette: 0.0 0.7\n"

        out_str += "grid size: 10 x 10 x 10\n"
        out_str += "remove objects:	yes\n"
        out_str += "rays from objects: no\n"
        out_str += "one ray per spectrum: yes\n"
        out_str += "ignore direct light: no\n"
        out_str += "return type: D\n"
        
        out_str += "output file: yes " + self.addresfile + "\n"
        
        out_str += "local light model: Lambertian\n"
        out_str += "spectrum samples: 1\n"
        out_str += "source spectrum: 660 1\n"
        out_str += "leaf material (top): 0.0 0 0.0 0 1\n"
        out_str += "leaf material (bottom): 0.0 0 0.0 0 1\n"
        
        if self.light_source_str == '':
            out_str += "light source: 0.0 -1.0 0.0 1.0\n"
        else:
            out_str += self.light_source_str

        return out_str
        
    def add_light_sources(self,lights):
        # input: weight,x_dir,y_dir,z_dir (in PlantGL basis, z = up)
        # output: x_dir,z_dir,y_dir,weight (in QuasiMC/lpfg basis, y = up)
        self.light_source_str = ''
        for light in lights:
            self.light_source_str += "light source: " + str(light[1]) + " " + str(light[3]) + " " + str(light[2]) + " " + str(light[0]) + "\n"
        return
        
    def add_shape(self,shape,tessel):
        shape.apply(tessel)
        mesh = tessel.triangulation
        pts = np.array(mesh.pointList)
        index = np.array(mesh.indexList)
        triangles = pts[index]

        for tri in triangles:
            out_str = str(shape.id) + " E(0)\n"
            out_str += "Dbegin\n"
            out_str += "polygon\n"
            for vec in tri:
                out_str += " " + str(vec[0]) + " " + str(vec[2]) + " " + str(vec[1]) + "\n"
            out_str += "Dend\n"
            
            self.output_triangles_str += out_str
            
    def add_triangle(self,shape):
        # ensure the shape specifies only a single triangle in its indexList
        if shape.geometry.indexListSize() != 1:
            print self.quasimc_name + " warning: add_triangle() was given a shape with indexListSize != 1"
        inds = np.array(shape.geometry.indexList[0])
        # ensure there are only three indivices to the list of vertices given
        if len(inds) != 3:
            print self.quasimc_name + " warning: add_triangle() was given a shape with more than 3 vertices specified in the indexList"
        # the pointList can have any number of vertices, because we check above that only 3 indicies are given.
        pts = np.array(shape.geometry.pointList)
        # change of coordinates
        pts = pts[:,[0,2,1]]
        
        # write the triangle to QuasiMC input file
        out_str = str(shape.id) + " E(0)\n"
        out_str += "Dbegin\n"
        out_str += "polygon\n"
        out_str += " " + str(pts[inds[0]]).strip("[]") + "\n"
        out_str += " " + str(pts[inds[1]]).strip("[]") + "\n"
        out_str += " " + str(pts[inds[2]]).strip("[]") + "\n"
        out_str += "Dend\n"
            
        self.output_triangles_str += out_str

    def get_flux_density(self,aggregate=True,fun=sum):
        """returns absorbed flux density per leaf"""
        if (aggregate == False):
            return {'index':self.ids, 'flux_density':self.flux}
        else:
            ag = {}
            for key,group in groupby(sorted(izip(self.ids,self.flux),key=lambda x: x[0]),lambda x : x[0]) :
                ag[key] = fun([elt[1] for elt in group])
            return ag

    def get_sunlit_leaf_area(self,aggregate=True):
        if (aggregate == False):
            return {'index':self.ids, 'sunlit_leaf_area':self.values[:,2].tolist()}
        else:
            groups = np.array(self.ids)
            unique_groups = np.unique(groups)
            sums = []
            for group in unique_groups:
                sums.append(self.values[groups == group,2].sum())
            return dict(zip(unique_groups.tolist(), sums))

