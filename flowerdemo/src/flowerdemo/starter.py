from base import *
from PyQt4.Qt import Qt, QTimer
from OpenGL.GL import glPushName, glPopName
import traceback as tb
import sys
from math import pi
from pglnqgl import toV3
from vplants.plantgl.math import angle, Vector3
from math import radians, degrees, pi, cos, sin

class MenuView(SceneView):
    def __init__(self,parent = None):
        SceneView.__init__(self,parent,'Menu')
        
        # The scene to display

        self.petal2panel = {}
        self.selectedid = -1
        self.focus = False
        
        self.standardColor = (1,1,1,0.8)
        self.focusColor = (0.8,0,0.8,0.8)
        self.selectedColor = (1,0,0,0.8)

        # mouse state
        self.mousePressed = False
        self.selectionMove = True
        
        # petal renderer
        self.setDynamic(True)
        self.petalrenderer = GLRenderer(self.discretizer)
        #self.petalrenderer.renderingMode = GLRenderer.Dynamic
        
        self.buttonAbout = GLButton(parent, 20, 20, 60, 48, text = 'A Propos', action = self.widget.showAboutView)
        self.addButton(self.buttonAbout)

    def create3DMenu(self,nb = 4):
        self.base = 'arabido'+str(nb)
        scene = Scene(str(get_shared_model(self.base+'.bgeom')))
        
        # petals
        info = eval(file(get_shared_model(self.base+'-petalid.txt')).readline())
        self.ids,self.petalangle = [i for i,j in info ],[j for i,j in info ]
        
        self.petals = dict([(i,scene.find(i)) for i in self.ids])
        for i in self.petals.itervalues(): del scene[scene.index(i)]
        
        self.petalscene = Scene([self.petals[i] for i in self.ids])
        
        self.petalangle = map(radians,self.petalangle)
        self.setScene(scene)
        self.updateCamera()
        
    def resizeWidgetEvent(self,w,h):
        self.buttonAbout.move(20,h-self.buttonAbout.height-20)
            
        
    def setPanels(self, panels):
        
        self.create3DMenu(len(panels))
        i = 0
        for pid,img in panels:
            sh = self.petalscene[i]
            print i,sh.id,pid, img, self.petalangle[i]
            sh.appearance = Texture2D('texture_'+str(i),ImageTexture(str(get_shared_image(img))), Texture2DTransformation('',scale=(-1,5/7.),rotationAngle = pi/2))
            self.petal2panel[sh.id] = pid
            i += 1
    
    
    def openView(self):
        SceneView.openView(self)
        QObject.connect(self.widget,SIGNAL('interpolationFinished()'),self.endTransition)
        self.resizeWidgetEvent(self.widget.width(),self.widget.height())
        if self.scene:
            self.updateCamera()
    
    def updateCamera(self):
        self.sceneCenter = Vec(0.161041,0.00831789,2.53419)
        self.widget.setSceneRadius(self.bbx.getZRange())
        self.widget.setSceneCenter(self.sceneCenter)
        self.widget.setSceneRadius(7)
        
        camera = self.widget.camera()
        camera.setPosition(Vec(0.15,-0.0205177,8))
        camera.setViewDirection(Vec(0,0,-1))
        camera.setUpVector(Vec(-1,0,0))
        camera.setRevolveAroundPoint(self.sceneCenter)

        # camera constraints
        self.viewConstraint = WorldConstraint()
        self.viewConstraint.setTranslationConstraintType(AxisPlaneConstraint.FORBIDDEN)
        self.viewConstraint.setRotationConstraint(AxisPlaneConstraint.AXIS,Vec(0,0,-1))
        camera.frame().setConstraint(self.viewConstraint)
        
        
        
    def closeView(self):
        SceneView.closeView(self)
        self.widget.camera().frame().setConstraint(None)
    
    def getSelection(self,pos):
        self.widget.select(pos)
        return self.widget.selectedName()        
    
    def updatePetals(self,selectedid = None, force = False):
        if selectedid:
            if selectedid != self.selectedid or force:
                self.selectedid = selectedid
        else:
            self.selectedid = -1
        self.petalrenderer.clear()
        self.widget.updateGL()
        
    def mousePressEvent(self,event):
        selection = self.getSelection(event.pos())
        self.selectionMove = (selection == -1)
        self.mousePressed = True 
        self.updatePetals(selection,True)
        return not self.selectionMove
        
    def mouseMoveEvent(self,event):
        if not self.selectionMove or not self.mousePressed :
            selection = self.getSelection(event.pos())
            self.updatePetals(selection)
        return not self.selectionMove
        
    def mouseReleaseEvent(self,event):        
        petalid = self.selectedid
        self.updatePetals()
        self.mousePressed = False
        sm = self.selectionMove
        self.selectionMove = True
        if petalid != -1 and not sm:
            self.transitionTo(petalid)
        return not sm

    def transitionTo(self,petalid):
        panelid = self.petal2panel[petalid]
        lang = self.petalangle[self.ids.index(petalid)] + pi
        
        camera = self.widget.camera()
        if camera.frame().isSpinning():
            camera.frame().stopSpinning()
        camera.frame().setConstraint(None)
        nframe = Frame(camera.frame())
        r = 0.3
        nframe.setPosition(Vec(r*cos(lang),r*sin(lang),5))
        timeint = 1.0
        self.widget.setMouseInteraction(False)
        self.panelid = panelid
        self.widget.interpolateTo(nframe,timeint)        
            
    def endTransition(self):
        if self.panelid is None : return
        panelid = self.panelid
        self.panelid = None
        try:
            self.widget.setCurrentViewId(panelid)
        except Exception,e :                
            tb.print_exception(*sys.exc_info())
            self.openView()
            self.widget.displayMessage('Exception:'+repr(e),3000)
        self.widget.setMouseInteraction(True)
        
    def keyPressEvent(self,event):
        return False
        
    def draw(self): 
        gang = angle(toV3(self.widget.camera().upVector()),(-1,0,0),(0,0,1))
        SceneView.draw(self)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        if True : #self.petalrenderer.beginSceneList():
            glEnable(GL_RESCALE_NORMAL)
            self.petalrenderer.beginProcess()
            for sh,ang in zip(self.petalscene,self.petalangle):
                lang = ang+gang
                if -pi < lang <= 0 or pi < lang < 2*pi :
                    sh.appearance.transformation.rotationAngle = - pi/2
                else:
                    sh.appearance.transformation.rotationAngle = pi/2
                sh.appearance.apply(self.petalrenderer)
                if sh.id == self.selectedid:
                    if self.selectionMove:
                        glColor4fv(self.focusColor)
                    else:
                        glColor4fv(self.selectedColor)
                else:
                    glColor4fv(self.standardColor)    
                glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE  )
                sh.geometry.apply(self.petalrenderer)
            self.petalrenderer.endProcess()
            #self.petalrenderer.endSceneList()
        
        
    def drawWithNames(self):
        oldmode = self.petalrenderer.renderingMode
        self.petalrenderer.renderingMode = GLRenderer.Selection
        self.petalscene.apply(self.petalrenderer)
        # for id,shape in self.petals.iteritems():
            # glPushName(id)
            # shape.apply(self.renderer)
            # glPopName()
        self.petalrenderer.renderingMode = oldmode



def generate_menu_shape(nbpetal = 4, nbsepal = 4, nbstamen = 5):
    l = Lsystem('arabido-menu.lpy')
    l.context()['nb_petal'] = nbpetal
    l.context()['nb_sepal'] = nbsepal
    l.context()['nb_stamen'] = nbstamen
    ls = l.iterate()
    sc = l.sceneInterpretation(ls)
    ls.find