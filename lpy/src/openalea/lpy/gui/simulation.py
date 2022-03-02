from openalea.vpltk.qt import qt
from openalea.lpy import *
from openalea.plantgl.all import PglTurtle, Viewer, Material, PyStrPrinter, eStatic, eAnimatedPrimitives, eAnimatedScene
import optioneditordelegate as oed
import os, shutil, sys, traceback
from time import clock
from lpystudiodebugger import AbortDebugger
from scalar import *
import cProfile as profiling
from lpyprofiling import *
from lpytmpfile import *

defaultcode = "Axiom: \n\nderivation length: 1\nproduction:\n\n\ninterpretation:\n\n\nendlsystem\n"

   
class LpySimulation:
    def __init__(self,lpywidget,index = 0, fname = None):
        self.lpywidget = lpywidget
        self.index = index
        self.lsystem = Lsystem()
        self._fname = fname
        self._tmpfname = None
        self.tree = None
        self.nbiterations = 0
        self.timestep = 50
        self.textedition = False
        self._edited = False
        self._oldedited = False
        self.code = defaultcode
        self.textdocument = None
        self.cursor = None
        self.optionModel = None
        self.optionDelegate = None
        self.firstView = True
        self.autorun = False
        self.iterateStep = None
        self.desc_items = {'__authors__'    : '' ,
                          '__institutes__'  : '' ,
                          '__copyright__'   : '' ,
                          '__description__' : '' ,
                          '__references__'  : '' }
        #self.functions = []
        #self.curves = []
        self.visualparameters = [({'name':'Panel 1'},[])]
        self.scalars = []
        self.scalarEditState = None
        self.keepCode_1_0_Compatibility = True
        self.readonly = False
        self._oldreadonly = False
        if not fname is None:
            self.open(fname)
        else:
            self.setFname(None)         
    def getFname(self) : return self._fname
    def setFname(self,value) :
        self._fname = value
        self.lpywidget.documentNames.setTabText(self.index,self.getShortName())
    fname = property(getFname,setFname)
    def isEdited(self):
        return self._edited 
    def setEdited(self,value):
        self._edited = value
        self.lpywidget.printTitle()
        self.updateTabName()
    edited = property(isEdited,setEdited)
    def textEdited(self):
        self.textedition = True
        self._edited = True
        self.lpywidget.printTitle()
        self.updateTabName()
    def isTextEdited(self):
        r = self.textedition
        self.textedition = False
        self.lpywidget.printTitle()
        self.updateTabName()
        return r
    def isCurrent(self):
        return self.index == self.lpywidget.currentSimulationId
    def makeCurrent(self):
        self.lpywidget.changeDocument(self.index)
    def isDefault(self):
        if self.isCurrent():
            self.saveState()
        if not self.fname is None : return False
        if self.code != defaultcode : return False
        if self.textedition == True : return False
        if self._edited == True: return False
        for i in self.desc_items.itervalues():
            if len(i) > 0:
                return False
        ini = self.getInitialisationCode()
        if len(ini) > 0: return False
        return True            
    def getShortName(self):
        if self._fname is None : return 'New'
        else : return os.path.splitext(os.path.basename(self.fname))[0]
    def getBaseName(self):
        if self._fname is None : return 'New'
        else : return os.path.basename(self.fname)
    def getTabName(self):
        t = ''
        #if self.textedition:
        #    t += '*'
        if self.fname is None:
            t += 'New'
        else:
            t += os.path.splitext(os.path.basename(self.fname))[0]
        #if self._edited:
        #    t += '*'
        return t
    def generateIcon(self):
        import svnmanip
        if self.readonly is True:
            pixmap = qt.QtGui.QPixmap(":/images/icons/lock.png")
        elif self._edited:
            pixmap = qt.QtGui.QPixmap(":/images/icons/codefile-red.png")
        else:
            pixmap = qt.QtGui.QPixmap(":/images/icons/codefile.png")
        if not self.readonly and not self.fname is None and svnmanip.hasSvnSupport() :
            if svnmanip.isSvnFile(self.fname):
                status = svnmanip.svnFileTextStatus(self.fname)
                self.svnstatus = status
                if  status == svnmanip.modified:
                    pixmap2 = qt.QtGui.QPixmap(":/images/icons/svn-modified.png")
                elif status == svnmanip.normal:
                    pixmap2 = qt.QtGui.QPixmap(":/images/icons/svn-normal.png")
                elif status == svnmanip.conflicted:
                    pixmap2 = qt.QtGui.QPixmap(":/images/icons/svn-conflict.png")
                elif status == svnmanip.added:
                    pixmap2 = qt.QtGui.QPixmap(":/images/icons/svn-add.png")
                else:
                    pixmap2 = None
                if not pixmap2 is None:
                    painter = qt.QtGui.QPainter(pixmap);
                    painter.drawPixmap(pixmap.width()-pixmap2.width(),pixmap.height()-pixmap2.height(),pixmap2)
                    painter.end()
        icon = qt.QtGui.QIcon()
        icon.addPixmap(pixmap.scaledToHeight(32),qt.QtGui.QIcon.Normal,qt.QtGui.QIcon.Off)
        return icon
    def registerTab(self):
        self.lpywidget.documentNames.insertTab(self.index,self.generateIcon(),self.getTabName())
    def updateTabName(self, force = False):
        if self._oldedited != self._edited or self._oldreadonly != self.readonly:
            self._oldedited = self._edited
            self._oldreadonly = self.readonly
        self.lpywidget.documentNames.setTabIcon(self.index,self.generateIcon())
        self.lpywidget.documentNames.setTabText(self.index,self.getTabName())
    def getTimeStep(self):
        return self.timestep*0.001
    def getOptimisationLevel(self):
        return self.lsystem.context().options.find('Optimization').selection
    def getBackupName(self):
        if self.fname:
            return os.path.join(os.path.dirname(self.fname),'#'+os.path.basename(self.fname)+'#')
        else:
            if not self._tmpfname:
                self._tmpfname = getNewTmpLpyFile()
            return self._tmpfname
    def restoreState(self):        
        self.lpywidget.textEditionWatch = False
        te, tf = self.textedition, self._edited
        self.lpywidget.codeeditor.restoreSimuState(self)
        if self.optionModel is None:
            self.initializeParametersTable()
        self.lpywidget.parametersTable.setModel(self.optionModel)
        self.lpywidget.parametersTable.setItemDelegateForColumn(1,self.optionDelegate)
        self.textedition, self._edited = te, tf
        for key,editor in self.lpywidget.desc_items.iteritems():
            editor.setText(self.desc_items[key])
        self.lpywidget.setTimeStep(self.lsystem.context().animation_timestep)
        self.lpywidget.materialed.setTurtle(self.lsystem.context().turtle)
        #self.lpywidget.functionDock.setFunctions(self.functions)
        #self.lpywidget.curveDock.setCurves(self.curves)
        self.lpywidget.setObjectPanelNb(len(self.visualparameters))
        for panel,data in zip(self.lpywidget.getObjectPanels(),self.visualparameters):
            panelinfo,objects = data
            panel.setInfo(panelinfo)
            panel.setObjects(objects)
        self.lpywidget.scalarEditor.setScalars(self.scalars)
        if not self.lpywidget.interpreter is None:
            self.lpywidget.interpreter.locals['lstring'] = self.tree
            self.lpywidget.interpreter.locals['lsystem'] = self.lsystem
        self.lpywidget.printTitle()
        self.lpywidget.setTimeStep(self.lsystem.context().animation_timestep)
        if self.lpywidget.documentNames.currentIndex() != self.index:
            self.lpywidget.documentNames.setCurrentIndex(self.index)
        self.lpywidget.textEditionWatch = True
        if not self.fname is None:
            os.chdir(os.path.dirname(self.fname))         
        self.lpywidget.actionAutoRun.setChecked(self.autorun)
        self.updateReadOnly()
        #if not self.lsystem.isCurrent() : self.lsystem.makeCurrent()
    def saveState(self):
        #if self.lsystem.isCurrent() :self.lsystem.done()
        self.lpywidget.codeeditor.saveSimuState(self)
        for key,editor in self.lpywidget.desc_items.iteritems():
            if type(editor) == qt.QtGui.QLineEdit:
                self.desc_items[key] = editor.text()
            else:
                self.desc_items[key] = editor.toPlainText().encode('iso-8859-1','replace')
        #self.functions = self.lpywidget.functionpanel.getFunctions()
        #self.curves = self.lpywidget.curvepanel.getCurves()
        self.visualparameters = [(panel.getInfo(),panel.getObjects()) for panel in self.lpywidget.getObjectPanels()]
        self.scalars = self.lpywidget.scalarEditor.getScalars()
    def initializeParametersTable(self):
        self.optionModel = qt.QtGui.QStandardItemModel(0, 1)
        self.optionModel.setHorizontalHeaderLabels(["Parameter", "Value" ])
        options = self.lsystem.context().options
        self.optionDelegate = oed.OptionEditorDelegate()
        category = None
        categoryItem = None
        indexitem = 0
        for i in xrange(len(options)):
            option = options[i]
            if option.category != category:
                category = option.category
                sc = qt.QtGui.QStandardItem(category)                
                sc.setEditable(False)
                sc.setBackground(qt.QtGui.QBrush(qt.QtGui.QColor(172,168,153)))
                sc.setForeground(qt.QtGui.QBrush(qt.QtGui.QColor(255,255,255)))
                qf = qt.QtGui.QFont()
                qf.setBold(True)
                sc.setFont(qf)
                self.optionModel.setItem(indexitem, 0, sc)
                sc = qt.QtGui.QStandardItem()                
                sc.setEditable(False)
                sc.setBackground(qt.QtGui.QBrush(qt.QtGui.QColor(172,168,153)))
                sc.setForeground(qt.QtGui.QBrush(qt.QtGui.QColor(255,255,255)))
                self.optionModel.setItem(indexitem, 1, sc)
                indexitem += 1             
            si = qt.QtGui.QStandardItem(option.name)
            si.setToolTip(option.comment)
            si.setEditable(False)
            self.optionModel.setItem(indexitem, 0, si)
            si = qt.QtGui.QStandardItem(option.currentValue())
            si.option = option
            self.optionModel.setItem(indexitem, 1, si)
            indexitem += 1
        qt.QtCore.QObject.connect(self.optionModel,qt.QtCore.SIGNAL('itemChanged(QStandardItem*)'),self.textEdited)
    def setTree(self,tree,nbiterations,timing=None, plottiming = None):
        self.tree = tree
        self.nbiterations = nbiterations
        msg = 'Nb Iterations : '+str(self.nbiterations)
        if not timing is None:
            msg += " in "+str(round(timing,3))+" sec."
        if not plottiming is None:
            msg += " Plot in "+str(round(plottiming,3))+" sec."
        self.lpywidget.statusBar().showMessage(msg)
        if not self.lpywidget.interpreter is None:
            self.lpywidget.interpreter.locals['lstring'] = self.tree
    def updateLsystemCode(self):
        if self.lpywidget.codeBackupEnabled:
            if  self._edited:
                bckupname = self.getBackupName()
                if self.isCurrent():
                    self.saveState()
                self.saveToFile(bckupname)
        self.lsystem.clear()
        if self.fname:
            self.lsystem.filename = self.getStrFname()
        self.code = self.lpywidget.codeeditor.getCode()
        lpycode = self.code
        lpycode += '\n'+self.getInitialisationCode(False)
        res = self.lsystem.set(lpycode,{},self.lpywidget.showPyCode)
        if not res is None: print res
    def close(self):
        if self._edited:
            if not self.isCurrent():
                self.makeCurrent()
            answer = qt.QtGui.QMessageBox.warning(self.lpywidget,self.getShortName(),"Do you want to save this document ?",
                                     qt.QtGui.QMessageBox.Save,qt.QtGui.QMessageBox.Discard,qt.QtGui.QMessageBox.Cancel)
            if answer == qt.QtGui.QMessageBox.Save: self.save()
            elif answer == qt.QtGui.QMessageBox.Cancel: return False
            elif answer == qt.QtGui.QMessageBox.Discard:
                bckupname = self.getBackupName()
                if bckupname and os.path.exists(bckupname): os.remove(bckupname)
        return True
    def save(self):
        if self.fname and not self.readonly:
            if self.isCurrent():
                self.saveState()
            bckupname = self.getBackupName()
            if bckupname and os.path.exists(bckupname):
                os.remove(bckupname)
            if os.path.exists(self.fname) and  self.lpywidget.fileBackupEnabled :
                try:
                    shutil.copy(self.fname,self.fname+'~')
                except Exception,e:
                    print 'Cannot create backup file',repr(self.fname+'~')
                    print e
            self.saveToFile(self.fname)
            self.mtime = os.stat(self.fname).st_mtime
            self.lpywidget.statusBar().showMessage("Save file '"+self.fname+"'",2000)
            self.lpywidget.appendInHistory(self.fname)
            self.lsystem.filename = self.getStrFname()
            self.setEdited(False)
            self.updateReadOnly()
        else:
            self.saveas()
    def saveas(self):
        bckupname = self.getBackupName()
        fname = str(qt.QtGui.QFileDialog.getSaveFileName(self.lpywidget,"Open Py Lsystems file",self.fname if self.fname else '.',"Py Lsystems Files (*.lpy);;All Files (*.*)"))
        if fname:
            if not os.path.exists(fname):
                self.readonly = False  
            else : self.readonly = (not os.access(fname, os.W_OK))
            self.fname = fname
            os.chdir(os.path.dirname(fname))
            if not self.readonly and bckupname and os.path.exists(bckupname):
                os.remove(bckupname)
            self.save()
    def removeReadOnly(self):
        if not os.access(self.fname, os.W_OK):
            import stat
            st = os.stat(self.fname)[0]
            os.chmod(self.fname,st | stat.S_IWRITE)
            self.readonly = not os.access(self.fname, os.W_OK)
            self.updateTabName()
            self.updateReadOnly()
    def setReadOnly(self):
        if os.access(self.fname, os.W_OK):
            import stat
            st = os.stat(self.fname)[0]
            os.chmod(self.fname,st ^ stat.S_IWRITE)
            self.readonly = not os.access(self.fname, os.W_OK)
            self.updateTabName()
            self.updateReadOnly()
    def updateReadOnly(self):
        self.lpywidget.codeeditor.setReadOnly(self.readonly)
        self.lpywidget.materialed.setEnabled(not self.readonly)
        self.lpywidget.parametersTable.setEnabled(not self.readonly)
        self.lpywidget.scalarEditor.setEnabled(not self.readonly)
        self.lpywidget.animtimeSpinBox.setEnabled(not self.readonly)
        self.lpywidget.profileView.setEnabled(not self.readonly)
        self.lpywidget.descriptionEdit.setEnabled(not self.readonly)
        self.lpywidget.referenceEdit.setEnabled(not self.readonly)
        self.lpywidget.authorsEdit.setEnabled(not self.readonly)
        self.lpywidget.intitutesEdit.setEnabled(not self.readonly)
        self.lpywidget.copyrightEdit.setEnabled(not self.readonly)
        self.lpywidget.copyrightEdit.setEnabled(not self.readonly)
        for panel in self.lpywidget.getObjectPanels():
            panel.setEnabled(not self.readonly)
    def saveToFile(self,fname):
        f = file(fname,'w')
        f.write(self.code)
        initcode = self.getInitialisationCode()
        if len(initcode) > 0 :
            if self.code[-1] != '\n':
                f.write('\n')
            f.write(initcode)
        f.close()
    def getInitialisationCode(self,withall=True):
        code = self.initialisationFunction(withall)
        code += self.creditsCode()
        if len(code) > 0:
            code = LpyParsing.InitialisationBeginTag+'\n\n'+'__lpy_code_version__ = '+str(1.1)+'\n\n'+code
        return code
    def getStrFname(self):
        return self.fname.encode('iso-8859-1','replace')
    def initialisationFunction(self,withall=True):
        header = "def "+LsysContext.InitialisationFunctionName+"(context):\n"
        init_txt = ''
        if withall:
            defaultlist = PglTurtle().getColorList()
            currentlist = self.lsystem.context().turtle.getColorList()
            nbdefault = len(defaultlist)
            nbcurrent = len(currentlist)
            firstcol = True
            defaultmat = Material('default')
            printer = PyStrPrinter()
            printer.pglnamespace = 'pgl'
            printer.indentation = '\t'
            printer.indentation_increment = '\t'
            printer.line_between_object = 0
            if self.fname and len(self.fname) > 0:
                printer.reference_dir = os.path.abspath(os.path.dirname(self.getStrFname()))
                #print printer.reference_dir
            for i in xrange(nbcurrent):
                cmat = currentlist[i]
                if ( (i >= nbdefault) or 
                    (cmat.isTexture()) or
                    (not cmat.isSimilar(defaultlist[i])) or 
                    (cmat.name != defaultlist[i].name)):
                    if cmat.isTexture() or not cmat.isSimilar(defaultmat):
                        if firstcol :
                            init_txt += "\timport openalea.plantgl.all as pgl\n"
                            firstcol = False
                        cmat.name = 'Color_'+str(i)
                        cmat.apply(printer)
                        init_txt += printer.str()
                        printer.clear()
                        init_txt += '\tcontext.turtle.setMaterial('+repr(i)+','+str(cmat.name)+')\n'
            if not self.lsystem.context().is_animation_timestep_to_default():
                init_txt += '\tcontext.animation_timestep = '+str(self.getTimeStep())+'\n'           
            options = self.lsystem.context().options
            for i in xrange(len(options)):
                if not options[i].isToDefault():
                    init_txt += '\tcontext.options.setSelection('+repr(options[i].name)+','+str(options[i].selection)+')\n'
        if len(self.scalars):
            init_txt += '\tscalars = '+str([i.tostr() for i in self.scalars])+'\n'
            init_txt += '\tcontext["__scalars__"] = scalars\n'
            init_txt += '\tfor s in scalars:\n\t\tif not s[1] == "Category" : context[s[0]] = s[2]\n'
        def emptyparameterset(params):
            for panel,data in params:
                if len(data) > 0: return False
            return True
        if not emptyparameterset(self.visualparameters) :
            intialized_managers = {}
            panelid = 0
            for panelinfo,objects in self.visualparameters:
                if panelinfo.get('active',True) or withall:
                    for manager,obj in objects:
                        if not intialized_managers.has_key(manager):
                            intialized_managers[manager] = True
                            init_txt += manager.initWriting('\t') 
                        init_txt += manager.writeObject(obj,'\t')
                    init_txt += '\tpanel_'+str(panelid)+' = ('+repr(panelinfo)+',['+','.join(['('+repr(manager.typename)+','+manager.getName(obj)+')' for manager,obj in objects])+'])\n'
                panelid += 1    
            init_txt += '\tparameterset = ['
            panelid = 0
            for panelinfo,objects in self.visualparameters:
                if panelinfo.get('active',True) or withall:
                    init_txt += 'panel_'+str(panelid)+','
                panelid += 1
            init_txt += ']\n'
            if withall and self.keepCode_1_0_Compatibility:
                init_txt += '\tcontext["__functions__"] = ['
                for panelinfo,objects in self.visualparameters:
                    if panelinfo.get('active',True):
                        for manager,obj in objects:
                            if manager.typename == 'Function':
                                init_txt += '('+repr(manager.getName(obj))+','+manager.getName(obj)+'),'
                init_txt += ']\n'
                init_txt += '\tcontext["__curves__"] = ['
                for panelinfo,objects in self.visualparameters:
                    if panelinfo.get('active',True):
                        for manager,obj in objects:
                            if manager.typename == 'Curve2D':
                                init_txt += '('+repr(manager.getName(obj))+','+manager.getName(obj)+'),'
                init_txt += ']\n'
                
            init_txt += '\tcontext["__parameterset__"] = parameterset\n'
            for panelinfo,objects in self.visualparameters:
                if panelinfo.get('active',True):
                    for manager,obj in objects:
                        init_txt += '\tcontext["'+manager.getName(obj)+'"] = '+manager.writeObjectToLsysContext(obj) + '\n'
        if len(init_txt) > 0:
            return header+init_txt
        else:
            return '' 
    def creditsCode(self):
        txt = ''
        for key,value in self.desc_items.iteritems():             
            if len(value) > 0:
                txt += key+' = '+repr(str(value))+'\n'
        return txt
    def importcpfgproject(self,fname):
        from openalea.lpy.cpfg_compat.cpfg2lpy import translate_obj
        self.textedition = True
        self.setEdited(True)
        try:
            lpycode = translate_obj(fname)
            self.opencode(lpycode)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        
    def open(self,fname):
        self.setFname(fname)
        assert self._fname == fname
        recovery = False
        readname = self.fname
        bckupname = self.getBackupName()
        if bckupname and os.path.exists(bckupname):
            answer = qt.QtGui.QMessageBox.warning(self.lpywidget,"Recovery mode","A backup file '"+os.path.basename(bckupname)+"' exists. Do you want to recover ?",qt.QtGui.QMessageBox.Ok,qt.QtGui.QMessageBox.Discard)
            if answer == qt.QtGui.QMessageBox.Ok:
                recovery = True
                readname = bckupname
            elif answer == qt.QtGui.QMessageBox.Discard:
                os.remove(bckupname)     
        os.chdir(os.path.dirname(self.fname))        
        code = file(readname,'rU').read()
        self.readonly = (not os.access(fname, os.W_OK))
        self.textedition = recovery
        self.setEdited(recovery)
        self.opencode(code)
        self.mtime = os.stat(self.fname).st_mtime
        self.updateReadOnly()
    
    def importtmpfile(self,fname):
        self.textedition = True
        self.setEdited(True)
        try:
            lpycode = file(fname,'rU').read()
            self.opencode(lpycode)
            self._tmpfname = fname
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        
        
    def opencode(self,txt):
        txts = txt.split(LpyParsing.InitialisationBeginTag)            
        self.code = txts[0]
        if len(txts) == 2:
            context = self.lsystem.context()
            try:
                init = context.initialiseFrom(LpyParsing.InitialisationBeginTag+txts[1])
            except:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                init = None
            if context.has_key(context.InitialisationFunctionName):
                del context[context.InitialisationFunctionName]
            for key in self.desc_items.iterkeys():
                if context.has_key(key):
                    self.desc_items[key] = context[key]
                    if init is None:
                        init = True
                else:
                    self.desc_items[key] = ''
            from objectmanagers import get_managers
            managers = get_managers()
            self.visualparameters = []
            lpy_code_version = 1.0
            if context.has_key('__lpy_code_version__'):
                lpy_code_version = ['__lpy_code_version__']
            if context.has_key('__functions__') and lpy_code_version <= 1.0 :
                functions = context['__functions__']
                for n,c in functions: c.name = n
                # self.functions = [ c for n,c in functions ]
                funcmanager = managers['Function']
                self.visualparameters += [ ({'name':'Functions'}, [(funcmanager,func) for n,func in functions]) ]
            if context.has_key('__curves__') and lpy_code_version <= 1.0 :
                curves = context['__curves__']
                for n,c in curves: c.name = n
                # self.curves = [ c for n,c in curves ]
                curvemanager = managers['Curve2D']
                self.visualparameters += [ ({'name':'Curve2D'}, [(curvemanager,curve) for n,curve in curves]) ]
            if context.has_key('__scalars__'):
                scalars = context['__scalars__']   
                self.scalars = [ ProduceScalar(v) for v in scalars ]
            if context.has_key('__parameterset__'):
                def checkinfo(info):    
                    if type(info) == str:
                        return {'name':info}
                    return info
                parameterset = context['__parameterset__']
                parameterset = [ (checkinfo(panelinfo), [(managers[typename],obj) for typename,obj in objects]) for panelinfo,objects in parameterset]
                self.visualparameters += parameterset
            if init is None:
                import warnings
                warnings.warn('initialisation failed')
        else:
            for key in self.desc_items.iterkeys():
                self.desc_items[key] = ''
        if self.textdocument:
            self.lpywidget.textEditionWatch = False
            self.textdocument.clear()
            self.textdocument.setPlainText(self.code)
            self.lpywidget.textEditionWatch = True
    def reload(self):
        if self.fname:
            self.open(self.fname)
    def run(self,task):
        dl = self.lsystem.derivationLength
        timing = clock()
        task.result = self.lsystem.derive(dl)
        task.timing = clock() - timing
        task.dl = self.lsystem.getLastIterationNb()+1
    def post_run(self,task):
        if hasattr(task,'result'):
            self.firstView = False
            plottiming = clock()
            self.lsystem.plot(task.result,True)
            plottiming = clock() - plottiming
            self.setTree(task.result,task.dl,task.timing,plottiming)
            if self.lpywidget.displayMetaInfo and not self.autorun and  self.lsystem.context().has_key('__description__'):
                self.lpywidget.viewer.showMessage(self.lsystem.context()['__description__'],5000)
    def animate(self,task):
        edition = self.isTextEdited()
        nbiter = self.nbiterations
        dt = self.getTimeStep()
        dl = self.lsystem.derivationLength
        if self.firstView and task.fitAnimationView:
            nbiter = self.lsystem.context().get('initial_view',dl)
            self.lsystem.plot(self.lsystem.derive(nbiter),True)
            self.firstView = False
            self.lpywidget.viewer.setAnimation(eAnimatedPrimitives)
        timing = clock()
        make_animation = self.lsystem.animate 
        if hasattr(task,'recording') :
            def record(*args):
                # removing dt arg
                args = list(args)
                if len(args) == 4: args.pop(1)
                else: args.pop(0)
                self.lsystem.record(task.recording,*args)
            make_animation = record
        if (not edition) and (not self.tree is None) and (0 < nbiter < dl):
            task.result = make_animation(self.tree,dt,nbiter,dl-nbiter)
        else:
            task.result = make_animation(dt,dl)
        task.timing = clock() - timing
        task.dl = self.lsystem.getLastIterationNb()+1
    def pre_animate(self,task):
        if self.isTextEdited() or self.lsystem.empty() or self.nbiterations == 0 or self.nbiterations >= self.lsystem.derivationLength:
            self.updateLsystemCode()
        self.lpywidget.viewer.start()
        self.lpywidget.viewer.setAnimation(eStatic if self.firstView and task.fitAnimationView else eAnimatedPrimitives)
    def post_animate(self,task):
        if hasattr(task,'result'):
            self.setTree(task.result,task.dl,task.timing)
    def pre_step(self,task):
        if self.isTextEdited() or self.lsystem.empty() or not self.tree or self.nbiterations >= self.lsystem.derivationLength:
            self.updateLsystemCode()
            self.nbiterations = 0
            self.tree = self.lsystem.axiom
            task.done = True
        else: task.done = False
    def step(self,task):
        if not task.done and self.nbiterations < self.lsystem.derivationLength:
            timing = clock()
            task.result = self.lsystem.derive(self.tree,self.nbiterations,1)
            task.timing = clock() - timing
            task.dl = self.lsystem.getLastIterationNb()+1
        else:
            task.dl = 0
            task.timing = 0
            task.result = self.lsystem.axiom
    def post_step(self,task):
        if hasattr(task,'result'):
            self.setTree(task.result,task.dl,task.timing)
            self.lsystem.plot(self.tree,True)
            self.firstView = False
    def iterate(self,task,n = None):    
        timing = clock()
        task.result = self.lsystem.self.tree(self.tree,self.nbiterations,self.iterateStep)        
        task.timing = clock() - timing
        task.dl = self.lsystem.getLastIterationNb()+1
    def debug(self):
        self.lsystem.setDebugger(self.lpywidget.debugger)
        try:
            if self.isTextEdited() or self.lsystem.empty() or not self.tree:
                self.updateLsystemCode()
                self.setTree(self.lsystem.derive(self.lsystem.axiom,0,1),1)
            else:
                if self.nbiterations < self.lsystem.derivationLength:
                    self.setTree(self.lsystem.derive(self.tree,self.nbiterations,1),self.nbiterations+1)
                else:
                    self.setTree(self.lsystem.derive(self.lsystem.axiom,0,1),1)
        except AbortDebugger,e :
            self.lsystem.clearDebugger()            
            return
        except :
            self.lsystem.clearDebugger()
            raise
        self.lsystem.clearDebugger()
        self.lsystem.plot(self.tree,True)
        self.firstView = False
    def rewind(self):
        self.updateLsystemCode()
        self.isTextEdited()
        self.setTree(self.lsystem.axiom,0)
        self.lsystem.plot(self.tree)
    def pre_stepInterpretation(self,task):
        if self.isTextEdited() or self.lsystem.empty() or not self.tree:
            self.updateLsystemCode()
            self.nbiterations = 0
            self.tree = self.lsystem.axiom
        self.lpywidget.viewer.start()
        self.lpywidget.viewer.setAnimation(eAnimatedScene)
    def stepInterpretation(self,task):
        if self.tree:
            self.lsystem.stepInterpretation(self.tree)
        else:
            self.lsystem.stepInterpretation(self.lsystem.axiom)
            task.dl = 0
            task.result = self.lsystem.axiom
    def post_stepInterpretation(self,task):
        if hasattr(task,'result'):
            self.setTree(task.result,task.dl)
            self.firstView = False
    def profile(self,task):
        edition = self.isTextEdited()
        nbiter = self.nbiterations
        dl = self.lsystem.derivationLength
        timing = clock()
        profile = profiling.Profile()
        def run():
            if task.mode == AnimatedProfiling:
                task.result = self.lsystem.animate(0,dl) 
            else:
                task.result = self.lsystem.derive(dl) 
                if task.mode == ProfilingWithFinalPlot:
                    self.lsystem.plot(task.result,True)
        profile.enable()
        run()
        profile.disable()
        task.profile_stats = profile.getstats()
        task.timing = clock() - timing
        task.dl = self.lsystem.getLastIterationNb()+1
    def pre_profile(self,task):
        if self.isTextEdited() or self.lsystem.empty() :
            self.updateLsystemCode()
        self.lpywidget.viewer.start()
        self.lpywidget.viewer.animation(True)
    def post_profile(self,task):
        if hasattr(task,'result'):
            self.setTree(task.result,task.dl,task.timing)
        rt = self.lsystem.get_rule_fonction_table()
        drawProfileTable(task.profileView,task.profile_stats,rt,task.timing,self.fname,self.lpywidget)
    def clear(self):
        self.lsystem.clear()
        self.setTree(None,0)
    def cancel(self):
        self.lsystem.early_return = True
    def cleanup(self):
        self.lsystem.forceRelease()
        self.lsystem.clear()

    def monitorfile(self):
        if not hasattr(self,'monitoring'):
          self.monitoring = True
          if not self.fname is None:
            if not os.path.exists(self.fname):
                answer = qt.QtGui.QMessageBox.warning(self.lpywidget,"Removed file","File '"+os.path.basename(self.fname)+"' do not exists anymore. Do you want to keep it in editor ?",qt.QtGui.QMessageBox.Yes,qt.QtGui.QMessageBox.No)
                if answer == qt.QtGui.QMessageBox.No:
                    self.lpywidget.closeDocument(self.index)
            elif os.stat(self.fname).st_mtime > self.mtime :
                answer = qt.QtGui.QMessageBox.warning(self.lpywidget,"File has changed","File '"+os.path.basename(self.fname)+"' has changed on disk. Do you want to reload it ?",qt.QtGui.QMessageBox.Yes,qt.QtGui.QMessageBox.No)
                if answer == qt.QtGui.QMessageBox.Yes:
                    self.reload()
                else:
                    self.mtime = os.stat(self.fname).st_mtime +1
            self.updateSvnStatus()

          del self.monitoring

    def updateSvnStatus(self):
        import svnmanip
        if svnmanip.hasSvnSupport():
            if (not hasattr(self,'svnstatus') and svnmanip.isSvnFile(self.fname)) or (hasattr(self,'svnstatus') and svnmanip.svnFileTextStatus(self.fname) != self.svnstatus):
                self.updateTabName(force=True)

    def svnUpdate(self):
        import svnmanip
        hasupdated = svnmanip.svnUpdate(self.fname,self.lpywidget)
        if hasupdated: self.reload()
        self.updateSvnStatus()
        
    def svnIsUpToDate(self):
        import svnmanip
        svnmanip.svnIsUpToDate(self.fname,self.lpywidget)
        self.updateSvnStatus()
        
    def svnAdd(self):
        import svnmanip
        svnmanip.svnFileAdd(self.fname)
        self.updateSvnStatus()
        
    def svnRevert(self):
        import svnmanip
        svnmanip.svnFileRevert(self.fname)
        self.reload()
        self.updateSvnStatus()
        
    def svnCommit(self):
        import svnmanip
        svnmanip.svnFileCommit(self.fname, None, self.lpywidget)
        self.updateSvnStatus()
