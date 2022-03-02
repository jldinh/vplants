from PyQt4.Qt import QObject, QImage, Qt, SIGNAL, QApplication, QFontMetrics, QTimer, QColor, QFont, QString
from PyQt4.QtOpenGL import QGLWidget

from openalea.lpy import *
from openalea.plantgl.all import *
from PyQGLViewer import *
from OpenGL.GL import *
from OpenGL.GLU import gluErrorString

from config import get_shared_model, get_shared_image
from copy import deepcopy
import os

class Action:
    def __init__(self, action = None, params = None):
        self.action = action
        self.params = params
   
    def applyAction(self):
        if self.action:
            if not self.params is None:
                self.action(*self.params)
            else:
                self.action()
        self.actionEvent()
                
    def setAction(self,action  = None ,params = None):
        self.action = action
        self.params = params
    
    def actionEvent(self):
        pass

class GLFrame:
    def __init__(self, parent, x = 0, y = 0, 
                       width = None, height = None):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = 0.1
        self.visible = True
    
    def hide(self): 
        self.visible = False
        if self.parent.isVisible(): self.parent.updateGL()
        
    def show(self): 
        self.visible = True
        if self.parent.isVisible(): self.parent.updateGL()
        
    def toogleVisibility(self): 
        self.visible = not self.visible
        if self.parent.isVisible(): self.parent.updateGL()
        
    def resize(self,width,height):
        self.width = width
        self.height = height
        self.geometryChangedEvent()
        
    def move(self,x,y):
        self.x = x
        self.y = y
        self.geometryChangedEvent()
    
    def geometryChangedEvent(self):
        pass
        
    def drawTexBox(self):
        depth = self.depth
        glBegin(GL_QUADS)
        glTexCoord2f(0,1)
        glVertex3f(self.x,self.y,depth)
        glTexCoord2f(1,1)
        glVertex3f(self.x+self.width,self.y,depth)
        glTexCoord2f(1,0)
        glVertex3f(self.x+self.width,self.y+self.height,depth)
        glTexCoord2f(0,0)
        glVertex3f(self.x,self.y+self.height,depth)
        glEnd()
        
    def drawBox(self):
        depth = self.depth
        glBegin(GL_QUADS)
        glVertex3f(self.x,self.y,depth)
        glVertex3f(self.x+self.width,self.y,depth)
        glVertex3f(self.x+self.width,self.y+self.height,depth)
        glVertex3f(self.x,self.y+self.height,depth)
        glEnd()

    def containspos(self,pos):
        if not (0 < pos.x() - self.x < self.width) : return False
        if not (0 < pos.y() - self.y < self.height) : return False
        return True

        
class GLButton (Action,GLFrame):
    def __init__(self, parent, x = 0, y = 0, 
                               width = None, height = None, 
                               img = None,
                               text = None, 
                               togglable = False,
                               imgoff = None, 
                               action = None, 
                               params = None):
        Action.__init__(self, action, params)
        GLFrame.__init__(self, parent, x, y, width, height)
        
        self.img = img
        self.setText(text)
        self.textColor = QColor(0,0,0)
        self.togglable = togglable
        self.toggled = False
        self.imgoff = imgoff
        
        self.focus = False
        self.enabled = True
        self.__initialized__ = False
    
    def setText(self,text):
        self.__text = text
        self.__computeTextPosition()
        
    def geometryChangedEvent(self):
        self.__computeTextPosition()
        
    def actionEvent(self):
        if self.togglable:
            self.toggled = not self.toggled
        
    def __computeTextPosition(self):
        if not self.__text is None:
            qf = QFontMetrics(self.parent.font())
            self.__textx = self.x+(self.width-qf.width(self.__text))/2
            self.__texty = self.y+qf.ascent()+(self.height-qf.height())/2
    
    def __del__(self):
        self.parent.deleteTexture(self.textureId)
        if self.imgoff :
            self.parent.deleteTexture(self.textureOffId)
    
    def init(self):
        if not self.__initialized__:
            self.__initialized__ = True
            
            if self.img:
                self.imgV = QImage(self.img)
                assert not self.imgV.isNull()
                
                if self.width is None:
                    self.width = self.imgV.width()
                if self.height is None:
                    self.height = self.imgV.height()
                
                self.textureId = self.importTexture(self.imgV)
                
                if self.imgoff :  
                    self.imgoffV = QImage(self.imgoff)
                    self.textureOffId = self.importTexture(self.imgoffV)
            
            self.__defaulttoggled = self.toggled
            self.__defaultenabled = self.enabled
        else:
            self.toggled = self.__defaulttoggled
            self.enabled = self.__defaultenabled
            
        
    def importTexture(self,img):    
        return self.parent.bindTexture(img)
       
    def draw(self):
        if self.visible:
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
            self.parent.startScreenCoordinatesSystem()
            glLineWidth(2)
            glDisable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            if not self.enabled :
                glColor4f(0.5,0.5,0.5,1.0)
            else:
                glColor4f(0,0,0,1.0)
            self.drawBox()
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
            if not self.enabled:
                glColor4f(1.0,1.0,1.0,0.2)
            elif self.focus :
                glColor4f(1.0,1.0,1.0,0.6)
            else:
                glColor4f(1.0,1.0,1.0,0.4)            
            self.drawBox()
            
            if self.img:
                glTranslatef(0,0,-0.05)
                glEnable( GL_TEXTURE_2D )
                if not self.toggled and self.enabled:
                    glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE  )
                    glBindTexture(GL_TEXTURE_2D, self.textureId)
                else:
                    if self.imgoff:
                        glBindTexture(GL_TEXTURE_2D, self.textureOffId)
                    else:
                        if not self.toggled :
                            glColor4f(1,1,1,0.7)
                        else:
                            if self.enabled:
                                glColor4f(0.2,0.2,0.2,0.5)
                            else:
                                glColor4f(0.2,0.2,0.2,0.3)  
                        glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE  )
                        glBindTexture(GL_TEXTURE_2D, self.textureId)
                glMatrixMode(GL_TEXTURE)
                glLoadIdentity()
                self.drawTexBox()
                glDisable( GL_TEXTURE_2D )
                glTranslatef(0,0,0.05)
            glLineWidth(1)
            if not self.__text is None:
                glColor4f(self.textColor.redF(),self.textColor.greenF(),self.textColor.blueF(),self.textColor.alphaF())
                self.parent.drawText(self.__textx,self.__texty,self.__text)
            glEnable(GL_LIGHTING)
            self.parent.stopScreenCoordinatesSystem()
        
        
    def mousePressEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) : 
            return True
        return False
        
    def mouseMoveEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) : 
            self.parent.setFocusWidget(self)
            return True
        return False
        
    def mouseReleaseEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) :
            self.parent.selectedButton = None
            self.applyAction()
            return True
        return False
    
        
class GLTextBox  (Action,GLFrame):
    def __init__(self, parent, text, x = 0, y = 0, 
                 width = 100, height = 30, 
                 action = None, params = None):
        Action.__init__(self, action, params)
        GLFrame.__init__(self,parent, x, y, width, height)
        self.margin = 20
        self.textColor = QColor(0,0,0)
        self.focus = False
        self.enabled = True
        self.font = QFont()
        self.font.setBold(True)
        self.setText(text)
        self.__initialized__ = False
    
    def setText(self,text):
        if len(text) == 0 : return
        lines = text.split('\n')
        qf = QFontMetrics(self.font)
        fmw = max(qf.maxWidth(),10)
        nlines = []
        w = self.width-2*self.margin
        for line in lines:
            if qf.width(line) > w:
                while qf.width(line) > w:
                    for i in xrange(w/fmw,len(line)):
                        if qf.width(line,i) > w:
                            if line[i].isalnum() and line[i-1].isalnum():
                                nlines.append(line[0:i-1]+('-' if line[i-2].isalnum() else ''))
                                line = line[i-1:]
                            else:
                                nlines.append(line[0:i])
                                line = line[i:]
                            break
                nlines.append(QString(line))
            else:
                nlines.append(QString(line))
        self.__text = nlines
        self.__computeTextPosition()
    
    def __computeTextPosition(self):
        if not self.__text is None:
            qf = QFontMetrics(self.font)
            self.__textx = self.x+self.margin
            self.__texty = self.y+self.margin+qf.ascent()+(self.height-2*self.margin-len(self.__text)*qf.height())/2
            self.__texth = qf.height()
    
    
    def init(self): 
        if not self.__initialized__:
            self.__initialized__ = True
            self.__defaultenabled = self.enabled
            self.__defaultvisible = self.visible
        else:
            self.enabled = self.__defaultenabled
            self.visible = self.__defaultvisible
        
    def draw(self):
        if self.visible:
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
            self.parent.startScreenCoordinatesSystem()
            glLineWidth(2)
            glDisable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            glColor4f(0,0,0,1.0)
            self.drawBox()
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
            glColor4f(1.0,1.0,1.0,0.8)            
            self.drawBox()
            self.parent.stopScreenCoordinatesSystem()
            glLineWidth(1)
            self.mcheckError('1')
            
            if not self.__text is None:
                glColor4f(self.textColor.redF(),self.textColor.greenF(),self.textColor.blueF(),self.textColor.alphaF())
                self.mcheckError('2')
                for i,line in enumerate(self.__text):
                    if len(line) > 0:
                        self.parent.renderText(self.__textx,self.__texty+i*self.__texth,line,self.font)
                        self.mcheckError('n'+str(i)+"'"+line+"'")
    
    def mcheckError(self,txt=None):
        err = glGetError()
        if err != GL_NO_ERROR:
            if txt: print txt,':',
            print gluErrorString(err)
            
        
    def mousePressEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) : 
            return True
        return False
        
    def mouseMoveEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) : 
            self.parent.setFocusWidget(self)
            return True
        return False
        
    def mouseReleaseEvent(self,event):
        if self.enabled and self.visible and self.containspos(event.pos()) :
            self.parent.selectedButton = None
            self.applyAction()
            return True
        return False
    

class View(QObject):
    def __init__(self, parent=None, name = ''):
        from config import display_help
        QObject.__init__(self, parent)
        self.widget = parent
        self.name = name
        self.activeView = False
        self.buttons = []
        self.widgets = []
        self.display_help = display_help()
    
    def addButton(self, button):
        self.buttons.append(button)
        if self.activeView:
            self.parent.addButton(button)
    
    def addWidget(self, widget):
        self.widgets.append(widget)
        if self.activeView:
            self.parent.addWidgets(widget)
    
    def removeButton(self, button):
        del self.buttons[self.buttons.index(button)]
        if self.activeView:
            self.parent.removeButton(button)
    
    def removeWidget(self, widget):
        del self.widgets[self.widgets.index(widget)]
        if self.activeView:
            self.parent.removeWidget(widget)
    
    def setParentWidget(self,parent):
        self.widget = parent

    def initView(self):
        if self.buttons:
            for but in self.buttons:
                but.init()
        if self.widgets:
            for widget in self.widgets:
                widget.init()
        
    def openView(self):
        self.activeView = True
        if self.buttons:
            for but in self.buttons:
                but.init()
        self.widget.addButtons(self.buttons)
        if self.widgets:
            for widget in self.widgets:
                widget.init()
        self.widget.addWidgets(self.widgets)
        
    def closeView(self):
        self.widget.removeButtons(self.buttons)
        self.widget.removeWidgets(self.widgets)
        self.activeView = False
        
    def mousePressEvent(self,event):
        return False
        
    def mouseMoveEvent(self,event):
        return False
        
    def mouseReleaseEvent(self,event):
        return False
        
    def keyPressEvent(self,event):
        return False
    
    def leaveEvent(self,event):
        return False
    
    def enterEvent(self,event):
        return False
    
    def draw(self):
        pass
    
    def drawWithNames(self):
        pass
    
    def resizeWidgetEvent(self,w,h):
        if self.display_help:
            self.buttonHelp.move(w-self.buttonHelp.width-20,self.buttonHelp.y)        
    
    def getTextFromFile(self,fname = None):
        if fname is None: fname = self.name.lower()+'.txt'
        from config import get_shared_data
        return open(get_shared_data(fname)).read()
        
    def createHelpWidgetFromFile(self,fname=None,height=20):
        if self.display_help:
            abouttxt = self.getTextFromFile(fname)
            self.display_help = len(abouttxt) > 0
        
            if self.display_help:
                self.createHelpWidget(abouttxt,height)
        
    def createHelpWidget(self,txt,height = 20):
        if self.display_help:
            self.textbox = GLTextBox(self.widget, txt , 300, 212, 800, 600)
            self.textbox.hide()
            self.textbox.setAction(self.textbox.hide)
            self.addWidget(self.textbox)
            
            self.buttonHelp = GLButton(self.widget, 100, height, 48, 48, 
                          text = 'Aide', 
                          action = self.textbox.toogleVisibility)
            self.buttonHelp.gene = False
            self.addButton(self.buttonHelp)
    
class SceneView(View):
    def __init__(self, parent=None, name = ''):
        View.__init__(self, parent,name)
        self.scene = Scene()
        self.discretizer = Discretizer()
        self.bboxcomputer = BBoxComputer(self.discretizer)
        self.renderer = GLRenderer(self.discretizer)
        self.autofit = False
        self.lighting = True
    
    def setDynamic(self, enabled = True):
        if enabled:
            self.renderer.renderingMode = GLRenderer.Dynamic
        else:
            self.renderer.renderingMode = GLRenderer.Static
        
    def setScene(self, scene):
        self.scene = scene
        self.renderer.clear()
        self.renderer.clearSceneList()
        self.bboxcomputer.clear()
        self.discretizer.clear()
        self.scene.apply(self.bboxcomputer)
        self.bbx = self.bboxcomputer.result
        if self.autofit:
            self.setSceneBoundingBox(Vec(*self.bbx.lowerLeftCorner),Vec(*self.bbx.upperRightCorner))
    
    def draw(self):        
        self.light = GL_LIGHT0
        if self.lighting:
            glEnable(GL_LIGHTING)
            glEnable(self.light)
            pos = list(self.widget.camera().position())+[1.0]
            glLightfv (self.light, GL_POSITION, pos)
            direction = list(self.widget.camera().viewDirection())+[1.0]
            glLightfv (self.light, GL_SPOT_DIRECTION, direction)
            glLightfv (self.light, GL_AMBIENT, (0.6,0.6,0.6,1.0))
            glLightfv (self.light, GL_DIFFUSE, (1.0,1.0,1.0,1.0))
            glLightfv (self.light, GL_SPECULAR, (1.0,1.0,1.0,1.0))
        if self.renderer.beginSceneList():
            glEnable(GL_RESCALE_NORMAL)
            self.scene.apply(self.renderer)
            self.renderer.endSceneList()
        if self.lighting:
            glDisable(GL_LIGHTING)
            pass
        View.draw(self)

class LpyModelView (SceneView):
    def __init__(self,parent = None, name = ''):
        SceneView.__init__(self,parent,name)
        self.lsystem = None
        self.lsystem_file = None
        self.variables = {}
        self.__animated = False
    
    def plot(self, scene):
        self.setScene(scene)
        self.widget.updateGL()
        if self.__animated:
            QApplication.processEvents()

    def selection(self):
        return None

    def waitSelection(self, txt):
        return None

    def setLsystem(self,fname):
        self.lsystem_file = str(get_shared_model(fname))
        self.lsystem = Lsystem(self.lsystem_file)
        
    def initView(self):
        SceneView.initView(self)
        self.__defaultVariables = deepcopy(self.variables)
        
    def openView(self):
        self.variables = deepcopy(self.__defaultVariables)
        SceneView.openView(self)
        registerPlotter(self)
    
    def closeView(self):
        SceneView.closeView(self)
        cleanPlotter()
    
    def computeScene(self):
        self.lsystem = Lsystem(self.lsystem_file)
        self.lsystem.context().updateNamespace(self.variables)
        return self.lsystem.sceneInterpretation(self.lsystem.iterate())
        
    def run(self):
        self.setScene(self.computeScene())
        self.widget.updateGL()
        
    def animate(self):
        self.emit(SIGNAL('animationStarted()'))
        self.__animated = True
        self.lsystem = Lsystem(self.lsystem_file)
        self.lsystem.context().updateNamespace(self.variables)
        self.lsystem.animate()
        self.__animated = False
        self.emit(SIGNAL('animationStopped()'))

import sys


class LpyModelWithCacheView (LpyModelView):
    def __init__(self,parent = None,name = ''):
        LpyModelView.__init__(self,parent,name)
        self.variations = {}
        self.cachefile = None
        self.cacherep = ''
        self.__use_cache = not '--no-cache' in sys.argv        
       
    def initView(self):
        LpyModelView.initView(self)
        if self.lsystem :
            res = self.computeCache(self.cachefile,self.cacherep)
            return res
        
    def openView(self):
        LpyModelView.openView(self)
    
    
    def computeCache(self,fname = None,rep = ''):
        from PyQt4.QtCore import QDir
        print 'compute cache'
        self.__cachedcariables = list(self.variations.iterkeys())
        if not fname or not self.__use_cache:
            print 'no cache :', not self.__use_cache
            for i,maxp in self.__computeCache():
                yield i,maxp
        else:
            from os.path import exists,join
            from os import mkdir, rmdir
            from shutil import rmtree
            tmpdir = str(QDir.tempPath())
            cachedir = join(tmpdir,'flowerdemo-cache')
            if '--re-cache' in sys.argv and exists(cachedir):
                print 'Remove cache dir :',repr(cachedir)
                try:
                    rmtree(cachedir)
                except Exception,e: 
                    print e
                    pass
            lcachedir = join(cachedir,rep)
            gfname = join(lcachedir,fname)
            outdated = False
            timestampfile = join(lcachedir,'timestamp.txt')
            self.cache = {}
            if  exists(timestampfile) and long(eval(file(timestampfile).readline())) < long(os.stat(self.lsystem_file).st_mtime):
                print 'Outdated cache for lsystem',self.lsystem_file
                outdated = True
            if not outdated and exists(gfname):
                print 'looking for cache files'
                cache = eval(file(gfname).readline())
                maxp = len(cache)
                i = 0
                for key,value in cache.iteritems():
                    valuepath = join(lcachedir,value)
                    if exists(valuepath):
                        self.cache[key] = Scene(valuepath)
                    else:
                        self.cache.clear()
                        break
                    i+=1
                    yield i,maxp
                print 'load cache ',fname
            if len(self.cache) == 0:
                print 'compute cache'
                for i,maxp in self.__computeCache():
                    yield i,maxp
                if not exists(cachedir):
                    mkdir(cachedir)
                if not exists(lcachedir):
                    mkdir(lcachedir)
                cache = {}
                for key,value in self.cache.iteritems():
                    lfname = '__'+''.join(['_' if not i.isalnum() else i for i in str(key)])+'.bgeom'
                    value.save(join(lcachedir,lfname))
                    cache[key] = lfname
                stream = file(gfname,'w')
                stream.write(str(cache)+'\n')
                stream = file(timestampfile,'w')
                stream.write(str(long(os.stat(self.lsystem_file).st_mtime))+'\n')
                yield 1,1
                print 'save cache',repr(fname)
        
    def __computeCache(self):
        from copy import deepcopy 
        previousconf = deepcopy(self.variables)        
        config = []
        for var in self.__cachedcariables:
            newconfig = []
            if config:
                for value in self.variations[var]:
                    for partialconf in config:
                        pconf = deepcopy(partialconf)
                        pconf.append(value)
                        newconfig.append(pconf)
                config = newconfig
            else:
                config = [ [value] for value in self.variations[var]]
        self.cache = {}
        maxp = len(config)
        for i,conf in enumerate(config):
            self.variables = deepcopy(previousconf)
            self.variables.update(dict(zip(self.__cachedcariables,conf)))
            self.cache[tuple(conf)] = self.computeScene()
            yield i+1,maxp
        self.variables = deepcopy(previousconf)
    
    def run(self):
        conf = tuple([self.variables[var] for var in self.__cachedcariables])
        self.setScene(self.cache[conf])
        self.widget.updateGL()   
    
        
class DemoWidget(QGLViewer):
    
    def __init__(self, parent=None):
        QGLViewer.__init__(self, parent)
        self.__views = []
        self.__currentview = None
        self.__initialview = None
        self.__aboutview = None
        self.setMouseTracking(True)
        self.backButton = GLButton(self, 20, 20, 48, 48, 
                                    img = get_shared_image('previous.png'), 
                                    action = self.setCurrentViewId, togglable = False,params = [self.__initialview])
        self.activeWidgets = [self.backButton]
        self.focusWidget = None
        self.selectedWidget = None
        self.__initiated__ = False
        self.mouseinteraction = True
        self.viewInterpolator = KeyFrameInterpolator()
        self.viewInterpolator.setFrame(self.camera().frame())
        QObject.connect(self.viewInterpolator, SIGNAL('interpolated()'), self.updateGL)
        QObject.connect(self.viewInterpolator, SIGNAL('endReached()'), self.endInterpolateView)
        self.__viewIter__ = iter(self.__views)
        self.__valueViewIter__ = None
        self.__first_initialization__ = True
    def init(self):
        self.backButton.init()
        self.setForegroundColor(QColor(0,0,0))
        # if not self.__initiated__:
            # self.__initiated__ = True
            # for v in self.__views:
                # v.init()
    def doInitialisation(self):
        if not self.__valueViewIter__ is None:
            try:
                result = self.__valueViewIter__.next()
                if not result is None:
                    p, maxp = result
                    return self.__initView__.name + ' ('+str(p*100./maxp)+'%)'
                else:
                    return self.__initView__.name
            except:
                self.__valueViewIter__ = None
        if self.__valueViewIter__ is None:
            try:
                self.__initView__  = self.__viewIter__.next()
                self.__valueViewIter__ = self.__initView__.initView()
                if self.__valueViewIter__ is None:
                    return self.__initView__.name
                else:
                    return self.doInitialisation()
            except Exception, e:
                print repr(e)
                del self.__initView__
                self.__viewIter__ = None
                self.__valueViewIter__ = None
                self.__initiated__  = True
                self.endInitialisation()
                return 'end'
    
    def endInitialisation(self):
        if self.__currentview:
            self.currentview.resizeWidgetEvent(self.width(),self.height())
    
    def setFocusWidget(self,widget = None):
        if self.focusWidget:
            self.focusWidget.focus = False
        if widget:
            widget.focus = True
            self.focusWidget = widget
        self.updateGL()
    
    def disableButtonInteraction(self): self.setButtonInteraction(False)   
    def enableButtonInteraction(self): self.setButtonInteraction(True)
    def setButtonInteraction(self,enabled):
        for button in self.activeWidgets:
            button.enabled = enabled
        self.updateGL()
        
    def setMouseInteraction(self,enabled):
        self.mouseinteraction = enabled
    
    def get_current_view(self): 
        return self.__views[self.__currentview] if not self.__currentview is None else None
        
    currentview = property(get_current_view)
    
    
    def get_initial_view(self): 
        return self.__views[self.__initialview] if not self.__initialview is None else None
        
    def setInitialViewId(self,id):
        assert id < len(self.__views)
        self.__initialview = id
        self.backButton.params = [id]
        self.setCurrentViewId(id)
        
    initialview = property(get_initial_view)
    
    def appendView(self,view):
        index = len(self.__views)
        self.__views.append(view)
        view.setParentWidget(self)
        if self.__initiated__:
            view.init()
        return index
        
    def appendAboutView(self,view):
        pid = self.appendView(view)
        self.setAboutViewId(pid)

    def appendInitialView(self,view):
        pid = self.appendView(view)
        self.setInitialViewId(pid)
        
    def setCurrentViewId(self,id = None):
        assert id < len(self.__views)        
        
        if self.backButton in self.activeWidgets and id == self.__initialview:
            self.removeButton(self.backButton)
        elif not self.backButton in self.activeWidgets and id != self.__initialview:
            self.addButton(self.backButton)
            
        if not self.__currentview is None:
            self.currentview.closeView()
        
        if not id is None:
            self.__currentview = id
            self.currentview.openView()
            self.currentview.resizeWidgetEvent(self.width(),self.height())
            if self.isVisible() : self.updateGL()
        else:
            self.__currentview = None
        
    def setAboutViewId(self,id):
        assert id < len(self.__views)
        self.__aboutview = id

    def showAboutView(self):
        assert not self.__aboutview is None
        self.setCurrentViewId(self.__aboutview)
        
    def showInitialView(self):
        self.setCurrentViewId(self.__initialview)
        
    def getCurrentViewId(self): return self.__currentview
    
    def closeCurrentView(self):
        if self.__currentview !=  self.__initialview:
            setCurrentView(self.__initialview)
    
    def drawInitialization(self):
            progress = self.doInitialisation()
            msg = "Initialisation ... "+progress
            fm = QFontMetrics(self.font())
            tw = fm.width(msg)
            self.drawText((self.width()-tw)/2, self.height()/2, msg)
            QTimer.singleShot(1,self.updateGL)
    
    def draw(self):
        if not self.__initiated__:
            self.drawInitialization()
        else:
            if not self.__currentview is None:
                self.currentview.draw()
            if self.activeWidgets:
                for widget in self.activeWidgets:
                    widget.draw()
                
   
    def drawWithNames(self):
        if not self.__currentview is None:
            self.currentview.drawWithNames()
    
    def mousePressEvent(self,event):
        if self.mouseinteraction:
            if self.activeWidgets:
                for widget in self.activeWidgets:
                    if widget.mousePressEvent(event) :
                        self.selectedWidget = widget
                        return 
            if not self.__currentview is None:
                if not self.currentview.mousePressEvent(event):
                    QGLViewer.mousePressEvent(self,event)
        
    def mouseMoveEvent(self,event):
        if self.mouseinteraction:
            for widget in self.activeWidgets:
                if widget.mouseMoveEvent(event) :
                    break
            else:
                self.setFocusWidget(None)
            if not self.selectedWidget:
                if not self.__currentview is None:
                    if not self.currentview.mouseMoveEvent(event):
                        QGLViewer.mouseMoveEvent(self,event)
        
    def mouseReleaseEvent(self,event):
        if self.mouseinteraction:
            if self.selectedWidget:
                if self.selectedWidget.mouseReleaseEvent(event) :
                    self.updateGL()
                    self.selectedWidget = None
            elif not self.__currentview is None:
                if not self.currentview.mouseReleaseEvent(event):
                    QGLViewer.mouseReleaseEvent(self,event)
        
    def keyPressEvent(self,event):
        if not self.__currentview is None:
            if not self.currentview.keyPressEvent(event):
                QGLViewer.keyPressEvent(self,event)
        if event.key() == Qt.Key_P:
            print 'pos=',self.camera().position(),'dir=',self.camera().viewDirection(),'up=',self.camera().upVector()

    def leaveEvent(self,event):
        if not self.__currentview is None:
            if not self.currentview.leaveEvent(event):
                QGLViewer.leaveEvent(self,event)
                
    def enterEvent(self,event):
        if not self.__currentview is None:
            if not self.currentview.enterEvent(event):
                QGLViewer.enterEvent(self,event)

    def resizeGL(self,w,h):
        QGLViewer.resizeGL(self,w,h)
        if self.__currentview:
            self.currentview.resizeWidgetEvent(w,h)
    
    def addButton(self,button):
        self.activeWidgets.append(button)
        
    def removeButton(self,button):
        del self.activeWidgets[self.activeWidgets.index(button)]
        
    def addButtons(self,buttons):
        self.activeWidgets += buttons
        
    def removeButtons(self,buttons):
        for button in buttons:
            self.removeButton(button)

    def addWidget(self,widget):
        self.activeWidgets.append(widget)
        
    def removeWidget(self,widget):
        del self.activeWidgets[self.activeWidgets.index(widget)]
        
    def addWidgets(self,widgets):
        self.activeWidgets += widgets
        
    def removeWidgets(self,widgets):
        for widget in widgets:
            self.removeWidget(widget)
            
    def interpolateTo(self,frame,duration):
        if self.viewInterpolator.interpolationIsStarted():
            self.viewInterpolator.stopInterpolation()

        self.viewInterpolator.deletePath()
        self.viewInterpolator.addKeyFrame(Frame(self.camera().frame()))
        self.viewInterpolator.addKeyFrame(frame, duration)

        self.viewInterpolator.startInterpolation()
        
    def endInterpolateView(self):
        self.emit(SIGNAL('interpolationFinished()'))