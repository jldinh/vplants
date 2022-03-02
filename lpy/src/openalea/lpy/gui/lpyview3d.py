from PyQGLViewer import QGLViewer, Vec
from openalea.plantgl.all import *
from openalea.plantgl.gui.pglnqgl import *
from openalea.vpltk.qt import qt

class LpyView3D (QGLViewer):
    def __init__(self,parent):
        QGLViewer.__init__(self,parent)
        self.scene = None
        self.discretizer = Discretizer()
        self.glrenderer = GLRenderer(self.discretizer)
        self.bboxcomputer = BBoxComputer(self.discretizer)
        self.animationMode = eStatic
        self.camera().setViewDirection(Vec(-1,0,0))
        self.camera().setUpVector(Vec(0,0,1))
    def display(self,scene = None):
        self.scene = scene
        if self.animationMode != eAnimatedScene:
            self.glrenderer.clear()
            self.discretizer.clear()
            self.bboxcomputer.clear()
        if self.animationMode == eStatic:
            if not scene is None:
                self.bboxcomputer.process(self.scene)
                bbx = self.bboxcomputer.result                
                #bbx = BoundingBox(self.scene)
                if bbx: 
                    self.camera().setSceneBoundingBox(*bbx2qgl(bbx))
                    self.showEntireScene()
                    self.updateGL()
                else: print 'error computing bbox'
        else :
            self.updateGL()
    def draw(self):        
        if self.scene and self.glrenderer.beginSceneList():
            self.glrenderer.beginProcess()
            self.scene.apply(self.glrenderer)
            self.glrenderer.endProcess()
            self.glrenderer.endSceneList()
    def start(self):
        pass
    def stop(self):
        pass
    def setAnimation(self,flag):
        self.animationMode = flag
        modemap = { eAnimatedPrimitives : GLRenderer.Dynamic , eAnimatedScene : GLRenderer.DynamicScene, eStatic : GLRenderer.Normal }
        self.glrenderer.renderingMode = modemap[flag]
    def showMessage(self,txt,timeout=0):
        self.displayMessage(txt,timeout)
    def saveTSnapshot(self,fname):
        self.saveSnapshot(fname,True)
        # e = qt.QtCore.QEvent(qt.QtCore.QEvent.MaxUser-1)
        # e.fname = fname
        # qt.QtCore.QCoreApplication.sendEvent(self,e)
    # def event(self,e):
        # if e.type() == qt.QtCore.QEvent.MaxUser-1:
            ## self.grabFrameBuffer(True).save(e.fname)
            # self.saveSnapshot(e.fname)
            # return True
        # else: return QGLViewer.event(self,e)