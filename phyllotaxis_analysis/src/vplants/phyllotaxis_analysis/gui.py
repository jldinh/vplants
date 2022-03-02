#       
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA  
#
#       File author(s): Yassin REFAHI <yassin.refahi@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__ = "Cecill-C"

__doc__ = """
Graphical user interface for phyllotaxis analysis package. 
"""
import icons_rc  
import os
import sys
import shutil
import numpy as np
from time import time
from PyQt4 import QtCore, QtGui 
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from read_file import readCSVFile, withOutExtension, extension, readTxtDataFile, readSeqFile#, readVData
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from parameters import maxInversion, phylType, probCriteria, concentrationParameter
from parameters import intervalsDic as bordersDict
from analysis_functions import codeSequence, theoretical_divergence_angles, isN_admissible2, counterClockWise, invalidateSeq

class myWindow(QtGui.QMainWindow):
    """
    A widget to view a plotted figure.
    """
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self, parent)
        saveAs = QtGui.QAction('Save &As...', self)
        saveAs.setStatusTip('Save As..')
        self.connect(saveAs, QtCore.SIGNAL('triggered()'), self.saveAsFile )
        fileMenu = self.menuBar()
        file = fileMenu.addMenu('&File')
        file.addAction(saveAs)
        self.statusBar()
    
    def saveAsFile(self):
        fileChoices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', fileChoices))
        if path:
            self.canvas.print_figure(path)#, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Phyllotaxis Analyzer")
        self.setWindowIcon(QtGui.QIcon(':I/icons/vplants.png')) 
        self.resize(1024,768)
        self.center()
        self.setFont(QtGui.QFont('OldEnglish', 8))
        
        self.stBarLabel = QtGui.QLabel("")
        
        exit = QtGui.QAction(QtGui.QIcon(':I\icons\exit.png'), '&Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setToolTip('Exit Phyllotaxis Analyzer')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        open = QtGui.QAction(QtGui.QIcon(':I/icons/open.png'),'&Open', self)
        open.setShortcut('Ctrl+O')
        open.setToolTip('Open data file')
        self.connect(open, QtCore.SIGNAL('triggered()'), self.openFileDialog )
        
        save = QtGui.QAction(QtGui.QIcon(':I/icons/save.png'),'&Save', self)
        save.setShortcut('Ctrl+S')
        save.setToolTip('Save')
        self.connect(save, QtCore.SIGNAL('triggered()'), self.saveFun )
        
        saveAs = QtGui.QAction('Save &As...', self)
        saveAs.setToolTip('Save As..')
        self.connect(saveAs, QtCore.SIGNAL('triggered()'), self.saveAsFile )
        
        about = QtGui.QAction('&About', self)
        self.connect(about, QtCore.SIGNAL('triggered()'), self.aboutFun)
        aboutQt = QtGui.QAction('About Qt', self)
        self.connect(aboutQt, QtCore.SIGNAL('triggered()'), self.aboutQtFun)
        
        printAction = QtGui.QAction(QtGui.QIcon(':I/icons/print.png'), '&Print...', self)
        printAction.setToolTip("Print text edit")
        printAction.setShortcut('Ctrl+P')
        self.connect(printAction, QtCore.SIGNAL('triggered()'), self.printActionFun)
        
        fileMenu = self.menuBar()
        file = fileMenu.addMenu('&File')
        file.addAction(open)
        file.addAction(save)
        file.addAction(saveAs)
        file.addSeparator()
        file.addAction(printAction)
        file.addSeparator()
        file.addAction(exit)
        
        toolbar1 = self.addToolBar('File')
        toolbar1.addAction(open)
        toolbar1.addAction(save)
        toolbar1.addAction(printAction)
        toolbar1.addAction(exit)
        
        clearAction = QtGui.QAction( QtGui.QIcon(':I/icons/clear.png'),'Clear', self)
        clearAction.setToolTip("Clear text edit")
        
        toolbar3 = self.addToolBar('TextEdit')
        toolbar3.addAction(clearAction)
        editMenu = fileMenu.addMenu('&Edit')
        editMenu.addAction(clearAction)
        
        self.showAction = QtGui.QAction( QtGui.QIcon(':I/icons/show.png'),'S&how', self) 
        self.showAction.setToolTip("Show the sequence")
        self.connect(self.showAction, QtCore.SIGNAL('triggered()'), self.showSeq)
        self.showAction.setDisabled(True)
        
        self.getSeq = QtGui.QAction(QtGui.QIcon(':I/icons/enter.png'), 'Get Sequence', self)
        self.getSeq.setToolTip("Enter manually a sequence of measured angles")
        self.userSeq = None
        self.connect(self.getSeq, QtCore.SIGNAL('triggered()'), self.getSeqFun)
        
        self.getSeqAnalyze = QtGui.QAction(QtGui.QIcon(':I/icons/loupe2.png'), 'Analyze the entered sequence', self)
        self.connect(self.getSeqAnalyze, QtCore.SIGNAL('triggered()'), self.userSeqAnalyse)
        self.getSeqAnalyze.setDisabled(True)
        
        self.analyzeAction = QtGui.QAction(QtGui.QIcon(':I/icons/loupe.png'), 'Ana&lyze', self)
        self.analyzeAction.setToolTip("Analyze the sequence")
        self.connect(self.analyzeAction, QtCore.SIGNAL('triggered()'), self.analyze)
        self.analyzeAction.setDisabled(True)

        self.analyzeAllAction = QtGui.QAction(QtGui.QIcon(':I/icons/analyzeAll.png'), 'Analyze the &file', self)
        self.analyzeAllAction.setToolTip("Analyze all the sequences in the input file")
        self.connect(self.analyzeAllAction, QtCore.SIGNAL('triggered()'), self.analyzeAll)
        self.analyzeAllAction.setDisabled(True)
        
       
        self.plotAction = QtGui.QAction( QtGui.QIcon(':I/icons/matplotlib.png'),'Plo&t', self)
        self.plotAction.setToolTip("Analyze and plot the results")
        self.connect(self.plotAction, QtCore.SIGNAL('triggered()'), self.plotSequence)
        self.plotAction.setDisabled(True)
        
        analyzeMenu = fileMenu.addMenu('&Analyse')
        analyzeMenu.addAction(self.showAction)
        analyzeMenu.addAction(self.getSeq)
        analyzeMenu.addSeparator()
        analyzeMenu.addAction(self.analyzeAllAction)
        analyzeMenu.addAction(self.analyzeAction)
        analyzeMenu.addAction(self.getSeqAnalyze)
        analyzeMenu.addSeparator()
        analyzeMenu.addAction(self.plotAction)
        
        toolbar2 = self.addToolBar('Analyze')
        toolbar2.addAction(self.showAction)
        toolbar2.addAction(self.analyzeAllAction)
        toolbar2.addAction(self.analyzeAction)
        toolbar2.addAction(self.plotAction)
        toolbar2.addAction(self.getSeq)
        toolbar2.addAction(self.getSeqAnalyze)
        
        helpMenu = self.menuBar()
        help = helpMenu.addMenu('&Help')
        help.addAction(about)
        help.addAction(aboutQt)
        
        self.central = QtGui.QWidget(self)
        self.setCentralWidget(self.central)
        
        mainVBox = QtGui.QVBoxLayout(self.central)
        
        hbox1 = QtGui.QHBoxLayout()
        
        vbox01 = QtGui.QVBoxLayout()
        self.central.analyzeGroup = QtGui.QGroupBox("Analyze Data", self.central)
        
        hbox0101 = QtGui.QHBoxLayout()
        
        self.central.permLenlabel = QtGui.QLabel("Permutation Length", self.central)
        hbox0101.addWidget(self.central.permLenlabel)
        
        self.central.maxInvSpinBox = QtGui.QSpinBox(self.central)
        self.central.maxInvSpinBox.setToolTip("maximum number of organs involved in a permutation")  
        self.central.maxInvSpinBox.setValue(maxInversion)
        hbox0101.addWidget(self.central.maxInvSpinBox)

        vbox01.addLayout(hbox0101)
        
        self.central.analyzeGroup.setLayout(vbox01)        
        
        hbox0102 = QtGui.QHBoxLayout()
        
        self.central.plantNolabel = QtGui.QLabel("Plant Number", self.central)
        hbox0102.addWidget(self.central.plantNolabel)
        self.central.plantNoSpinBox = QtGui.QSpinBox(self.central)
        self.central.plantNoSpinBox.setToolTip("Plant number to analyze")          
        self.central.plantNoSpinBox.setDisabled(True)
        hbox0102.addWidget(self.central.plantNoSpinBox)
        
        vbox01.addLayout(hbox0102)
        
        hbox0104 = QtGui.QHBoxLayout()
        
        self.central.dirLabel = QtGui.QLabel("Direct", self.central)
        hbox0104.addWidget(self.central.dirLabel)
        self.central.dirCheck = QtGui.QCheckBox(self.central)
        self.central.dirCheck.setToolTip("Analyze the sequence from left to right") 
        self.central.dirCheck.setChecked(True)
        hbox0104.addWidget(self.central.dirCheck)
        self.central.reverseLabel = QtGui.QLabel("Reverse", self.central)
        hbox0104.addWidget(self.central.reverseLabel)
        self.central.reverseCheck = QtGui.QCheckBox(self.central)
        self.central.reverseCheck.setToolTip("Analyze the sequence from right to left")
        self.central.reverseCheck.setChecked(True)
        hbox0104.addWidget(self.central.reverseCheck)
        self.central.directionLabel = QtGui.QLabel("Change orientation", self.central)
        hbox0104.addWidget(self.central.directionLabel)
        self.central.directionCheck = QtGui.QCheckBox(self.central)
        self.central.directionCheck.setToolTip("Change orientation of the sequence from clockwise to counterclockwise or vice versa")
        hbox0104.addWidget(self.central.directionCheck)
        
        vbox01.addLayout(hbox0104)
        
            
        self.central.infoLabel = QtGui.QLabel("<font color = 'red'>Please open the data file!</font>",self.central) #label6
        vbox01.addWidget(self.central.infoLabel)
        
        hbox1.addWidget(self.central.analyzeGroup)
        
        vbox02 = QtGui.QVBoxLayout()
        
        self.central.angleGroup = QtGui.QGroupBox("Canonical Divergence Angle", self.central)
        
        self.central.fibRadio = QtGui.QRadioButton("Fibonnacci", self.central)
        self.central.fibRadio.setToolTip("Canonical divergence angle is 137.5 degrees") 
        vbox02.addWidget(self.central.fibRadio)
        if phylType == 137.5:
            self.central.fibRadio.setChecked(True)
        self.connect(self.central.fibRadio, QtCore.SIGNAL("clicked()"), self.setSPB1ToFib)
        
        self.central.lucRadio = QtGui.QRadioButton("Lucas", self.central)
        self.central.lucRadio.setToolTip("Canonical divergence angle is 99.5 degrees") 
        if phylType == 99.5:
            self.central.lucRadio.setChecked(True)
        self.connect(self.central.lucRadio, QtCore.SIGNAL("clicked()"), self.setSPB1ToLucas)
        vbox02.addWidget(self.central.lucRadio)
        
        hbox0201 = QtGui.QHBoxLayout()
        self.central.otherRadio = QtGui.QRadioButton("Other", self.central) 
        self.central.otherRadio.setToolTip("Enter canonical divergence angle")
        self.connect(self.central.otherRadio, QtCore.SIGNAL("clicked()"), self.otherEnable)
        hbox0201.addWidget(self.central.otherRadio)
        
        self.central.phylType = QtGui.QDoubleSpinBox(self.central) 
        self.central.phylType.setRange(0, 360)
        self.central.phylType.setValue(phylType)
        self.central.phylType.setDecimals(1)
        self.central.phylType.setDisabled(True)
        if phylType != 137.5 and phylType != 99.5:
            self.central.phylType.setDisabled(False)
            self.central.otherRadio.setChecked(True)
        self.connect(self.central.otherRadio, QtCore.SIGNAL("clicked()"), self.activateSP1)
        
        hbox0201.addWidget(self.central.phylType)
        
        vbox02.addLayout(hbox0201)
        self.central.angleGroup.setLayout(vbox02)
        hbox1.addWidget(self.central.angleGroup)
        
        vbox03 = QtGui.QVBoxLayout()
        
        self.central.statGroup = QtGui.QGroupBox("Statistical Parameters", self.central)
        
        hbox0303 = QtGui.QHBoxLayout()
        self.central.stdDevLabel = QtGui.QLabel("Concentration parameter", self.central)
        hbox0303.addWidget(self.central.stdDevLabel)
        self.central.consPar = QtGui.QDoubleSpinBox(self.central) 
        self.central.consPar.setToolTip("Circular concentration parameter") 
        self.central.consPar.setRange(0, 40)
        self.central.consPar.setValue(concentrationParameter)
        hbox0303.addWidget(self.central.consPar)
        
        vbox03.addLayout(hbox0303)
        
        hbox0304 = QtGui.QHBoxLayout()
        self.central.probCriteriaLabel = QtGui.QLabel("Threshold", self.central)
        hbox0304.addWidget(self.central.probCriteriaLabel)
        self.central.probCriteria = QtGui.QDoubleSpinBox(self.central) 
        self.central.probCriteria.setToolTip("Threshold used to prune candidate angles") 
        self.central.probCriteria.setDecimals(3) 
        self.central.probCriteria.setRange(0, 1)
        self.central.probCriteria.setSingleStep(.001)
        self.central.probCriteria.setValue(probCriteria)
        hbox0304.addWidget(self.central.probCriteria)
        
        vbox03.addLayout(hbox0304)
        
        self.central.statGroup.setLayout(vbox03)
        hbox1.addWidget(self.central.statGroup)
       
        mainVBox.addLayout(hbox1)
        
        hbox2 = QtGui.QHBoxLayout()
        self.central.textEdit = QtGui.QTextEdit(self.central)
        self.central.textEdit.setFont(QtGui.QFont('OldEnglish', 8))
        self.connect(clearAction, QtCore.SIGNAL('triggered()'), self.central.textEdit.clear)
        hbox2.addWidget(self.central.textEdit)
        
        mainVBox.addLayout(hbox2)
        self.central.setLayout(mainVBox)
        
        self.stBar = self.statusBar()
        
    def printActionFun(self):
        printer=QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer)
        dialog.setModal(True)
        dialog.setWindowTitle("Print Document" )
        if dialog.exec_() == True:
            self.central.textEdit.document().print_(printer)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Phyllotaxis Analyzer',"Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def aboutQtFun(self):
        QtGui.QMessageBox.aboutQt(self, "here")
    
                
    def getSeqFun(self):
        ok, text =  text, ok = QtGui.QInputDialog.getText(self, 'Enter a sequence', 'Enter the sequence:')
        text = str(text).strip()
        self.userSeqtxt = text.split(',')
        if self.userSeqtxt != ['']:
            self.userSeq = [float(i) for i in self.userSeqtxt]
        else:
            self.userSeq = [] 
        self.getSeqAnalyze.setDisabled(False)

    def userSeqAnalyse(self):
        self.plotSequence(self.userSeq)
        
    def aboutFun(self):
        text = """
        <h4>Phyllotaxis Analyzer</h4>
        Version: 1.0 <br>
        Copyright 2006 - 2012 INRIA - CIRAD - INRA  
        Distributed under the Cecill-C License.
        
        Phyllotaxis Analyzer has been developped in Virtual Plants and is the result of research in collaboration with RDP ENS Lyon.<br>
        Designed and implemented by Y.Refahi.<br>
        For the documentation see:
        <address><a href='http://openalea.gforge.inria.fr/doc/vplants/phyllotaxis_analysis/doc/_build/html/contents.html'> http://openalea.gforge.inria.fr/doc/vplants/phyllotaxis_analysis</a></address> <br>
        To know more about us visit <address><a href='http://www-sop.inria.fr/virtualplants/'> http://www-sop.inria.fr/virtualplants/</a></address>"""
        QtGui.QMessageBox.about(self, "Phyllotaxis Analyzer", QtCore.QString(text))
    
    def activateSP1(self):
        self.central.phylType.setReadOnly(False)
         
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def openFileDialog(self):
        self.datafilename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '','*.csv *.txt *.seq *.vxt')
        if self.datafilename == '':
            QtGui.QMessageBox.warning(self, 'File Warning', 'No opened file!', QtGui.QMessageBox.Ok)
        else:
            if self.datafilename.split('.')[-1] == 'csv':
                self.data = readCSVFile(self.datafilename)
            elif self.datafilename.split('.')[-1] == 'txt':
                self.data = readTxtDataFile(self.datafilename)
            elif self.datafilename.split('.')[-1] == 'seq':
                self.data = readSeqFile(self.datafilename)
            elif self.datafilename.split('.')[-1] == 'vxt':
                self.data = readVData(self.datafilename)
                
            self.central.infoLabel.setText("There are %d sequences in the file."%len(self.data))
            self.central.plantNoSpinBox.setDisabled(False)
            self.showAction.setDisabled(False)
            self.analyzeAction.setDisabled(False)
            self.analyzeAllAction.setDisabled(False)
            self.plotAction.setDisabled(False)
            self.central.plantNoSpinBox.setRange(0, len(self.data) - 1)
            self.central.textEdit.setText("%s is opened." %self.datafilename)
        
    def saveAsFile(self):
        try:
            savefilename = QtGui.QFileDialog.getSaveFileName(self, 'Save As', '%s_analyze.html'%withOutExtension(self.datafilename))
            if self.datafilename == '':
                self.central.textEdit.append("<font color = 'red'>IOError, no file!</font>")
            else:
                self.savefilename = savefilename
                self.saveFObj = file(self.savefilename, 'w')
                if extension(self.savefilename) == 'html':
                    self.saveFObj.write(str(self.central.textEdit.toHtml()))
                    self.saveFObj.flush()
                elif extension(self.savefilename) == 'txt':
                    self.saveFObj.write(self.central.textEdit.toPlainText())
                    self.saveFObj.flush()
        except AttributeError:
            self.savefilename = QtGui.QFileDialog.getSaveFileName(self, 'Save As','analyze.html')
    
    def saveFun(self):
        try:
            self.saveFObj = file(self.savefilename, 'w')
            if extension(self.savefilename) == 'html':
                self.saveFObj.write(str(self.central.textEdit.toHtml()))
                self.saveFObj.flush()
            elif extension(self.savefilename) == 'txt':
                self.saveFObj.write(str(self.central.textEdit.toPlainText()))
                self.saveFObj.flush()
        except AttributeError, e:
            self.saveAsFile()
    
    def showSeq(self):
        try:
            self.central.textEdit.append("<h5><font color = 'blue'>The sequence number %d of measured angles in file %s: <h5>%s<br></font>" % (self.central.plantNoSpinBox.value(),  self.datafilename ,str(self.data[self.central.plantNoSpinBox.value()])) )
        except AttributeError, e:
            reply = QtGui.QMessageBox.warning(self, 'File Warning',
            "Open a data file please!", QtGui.QMessageBox.Ok)
            
    def pbarFunc(self, value):
        self.stBar.addPermanentWidget(self.pbar, 1)
        self.pbar.show()
        self.pbar.setValue(int(100 * value))
        
    def setSPB1ToLucas(self):
        self.central.phylType.setValue(99.5)
        self.central.phylType.setDisabled(True)
        
    def setSPB1ToFib(self):
        self.central.phylType.setValue(137.5)
        self.central.phylType.setDisabled(True)
    
    def otherEnable(self):
        self.central.phylType.setDisabled(False)

    def analyze(self, userEnter = None, reverseAnalysis = False):
        if ( not self.central.dirCheck.isChecked() ) and (not self.central.reverseCheck.isChecked()):
            QtGui.QMessageBox.warning(self, 'Check box warning', 'Please choose a direction!', QtGui.QMessageBox.Ok)
            return False
        else:
            try:
                maxInv = self.central.maxInvSpinBox.value()
                phylAngle = self.central.phylType.value()
                consParVal = self.central.consPar.value()
    
                self.stBarLabel.setText("Analyzing...")
                self.stBar.addWidget(self.stBarLabel, 1)
                allSeqs = []
                if userEnter == None:
                    seq = list(self.data[self.central.plantNoSpinBox.value()])
                else:
                    seq = self.userSeq
                if self.central.directionCheck.isChecked():
                    seq = counterClockWise(seq)
                allSeqs = []
                if self.central.dirCheck.isChecked() and self.central.reverseCheck.isChecked():
                    self.dirRev = True
                else:
                    self.dirRev = False
                if self.central.dirCheck.isChecked():
                   allSeqs.append(seq) 
                if self.central.reverseCheck.isChecked() or reverseAnalysis:
                    seq2 = list(seq)
                    seq2.reverse()
                    allSeqs.append(seq2)
                self.currentSeq = allSeqs[0]# used for plotting!
    #            
                MainListOfTreesIndex = []
                for i in xrange(len(allSeqs)):
                    S = allSeqs[i]
                    ListOfTreesIndex = codeSequence(S, maxInv, phylAngle, bordersDict, consParVal, self.central.probCriteria.value() )
                    MainListOfTreesIndex.append(ListOfTreesIndex)
                self.stBarLabel.setText("")
                #sequence analyzed, now the results are going to be displayed
                self.showAnalyze(MainListOfTreesIndex, allSeqs, userEnter)
            except AttributeError, e:
                print e
                QtGui.QMessageBox.warning(self, 'File Warning', "Open a data file please!", QtGui.QMessageBox.Ok)
                return False
            return True
    
    def analyzeAll(self):
        time1 = time()
        self.pbar = QtGui.QProgressBar()
        self.pbar.setMaximumSize( 220, 12)
        
        self.stBar.addPermanentWidget(self.pbar,1)
        pBarMultiple = 100.0 / len(self.data)
        self.central.plantNoSpinBox.setValue(0)
        L = len(self.data)
        for i in xrange(len(self.data)):
            print "The sequence number %d of %d"%(i, L)
            self.analyze()
            self.pbar.setValue(int(i * pBarMultiple))
            self.central.plantNoSpinBox.setValue(self.central.plantNoSpinBox.value()+ 1 )
        self.stBarLabel.setText("")
        self.stBar.removeWidget(self.pbar)
        self.central.plantNoSpinBox.setValue(0)
        
    
    def plotSequence(self, userSeq = None):
        try:
            widget = myWindow(self)
            if userSeq == None:
                analyzeResult = self.analyze()
                WindowMessage = "The plotted measured sequence and predicted sequence for the plant number %d "%self.central.plantNoSpinBox.value()
                if self.central.directionCheck.isChecked():
                    WindowMessage += " in anti current wise"
                if self.central.reverseCheck.isChecked() and not self.central.dirCheck.isChecked():
                    WindowMessage += " in reverse order"
                if self.central.reverseCheck.isChecked() and self.central.dirCheck.isChecked():
                    WindowMessage += " in direct and in reverse order"
                widget.setWindowTitle(WindowMessage)
            else:
                widget.setWindowTitle("The plotted measured sequence and predicted sequence for the entered sequence" )
                analyzeResult = self.analyze(userSeq)
            if self.dirRev:
                self.seqRev = list(self.currentSeq)
                self.seqRev.reverse()
            if analyzeResult:
                allInvalidesDir = []
                for l1 in self.invalidesDir:
                    l2 = []
                    for i in xrange(l1[0], l1[1] + 1):
                        l2.append(i)
                    allInvalidesDir.extend(l2)
                    
                if self.dirRev:
                    allInvalidesReverse = []
                    for l1 in self.invalidesReverse:
                        l2 = []
                        for i in xrange(l1[0], l1[1] + 1):
                            l2.append(i)
                        allInvalidesReverse.extend(l2)
                    
                invalidesXDir = [ self.currentSeq[i] for i in allInvalidesDir]
                if self.dirRev:
                    invalidesXReverse = [ self.seqRev[i] for i in allInvalidesReverse]
                
                notExplainedXDir = [ self.currentSeq[i] for i in self.notExplainedListDir ]
                if self.dirRev:
                    notExplainedXReverse = [ self.seqRev[i] for i in self.notExplainedListRev ]
                
                x = [i for i in xrange( len(self.currentSeq)) ]
                
                widget.dpi = 100
                fig = Figure((15.0, 12.0), dpi = widget.dpi)
                ax = fig.add_subplot(211)
                ax.grid(True)
                line0, line1 = ax.plot(x, self.currentSeq, 'k', x ,self.predictionDir)
                line2 = ax.plot(x, self.currentSeq, 'go')
                line3 = ax.plot(self.notExplainedListDir, notExplainedXDir,'ro')
                line4 = ax.plot(allInvalidesDir, invalidesXDir,'wo')
                ax.legend((line0, line1 ,line2, line3, line4), ("data", " prediction ","explained", "not explained", "invalidated"), loc = 'best')
                titleText1 = ""
                if self.central.dirCheck.isChecked():
                    titleText1 += " Direct analyze"
                if (not self.central.dirCheck.isChecked()) and (self.central.reverseCheck.isChecked()):
                    titleText1 += " (reverse analyze)" 
                ax.set_title( titleText1 )
                ax.set_xlabel("Successive angles")
                ax.set_ylabel("Divergence angles")
                ax.axis([0, len(self.currentSeq), 0, 360])
                widget.canvas = FigureCanvas(fig)
                widget.canvas.setParent(widget)
                widget.setCentralWidget(widget.canvas)
                widget.plotNo = self.central.plantNoSpinBox.value()
                widget.show()
                widget.resize(1400, 1100)
                del self.predictionDir

                if self.dirRev:
                    ax2 = fig.add_subplot(212)
                    ax2.grid(True)
                    predictionRevRev = list(self.predictionReverse)
                    predictionRevRev.reverse()
                    line02, line12 = ax2.plot(x, self.currentSeq, 'k', x ,predictionRevRev)
                    line22 = ax2.plot(x, self.currentSeq, 'go')
                    notExplainedListRevRev = [(len(self.currentSeq) - 1 - j) for j in self.notExplainedListRev]
                    allInvalidesReverseRev = [(len(self.currentSeq) - 1 - j) for j in allInvalidesReverse]
                    line32 = ax2.plot(notExplainedListRevRev, notExplainedXReverse,'ro')
                    line42 = ax2.plot(allInvalidesReverseRev, invalidesXReverse,'wo')
                    ax2.legend((line02, line12, line22, line32, line42), ("data", " rev. prediction ","explained", "not explained", "invalidated"), loc = 'best')
                    ax2.set_title( "reverse analyze" )
                    ax2.set_xlabel("Successive angles")
                    ax2.set_ylabel("Divergence angles")
                    ax2.axis([0, len(self.currentSeq), 0, 360])
                    del self.predictionReverse
                    
        except AttributeError,e:
            print e
            reply = QtGui.QMessageBox.warning(self, 'Plot Warning', "Analyze the sequence then plot!", QtGui.QMessageBox.Ok)
            
    def showAnalyze(self, MainListOfTreesIndex, allSeqs, userEnter):
        maxInv = self.central.maxInvSpinBox.value()
        phylAngle = self.central.phylType.value()
        consParVal = self.central.consPar.value()
        plantNo = self.central.plantNoSpinBox.value()
        pbCr = self.central.probCriteria.value()
        theoreticalAngles, theoreticalCoeffAngles = theoretical_divergence_angles(self.central.maxInvSpinBox.value(), self.central.phylType.value())
        D_n_coeffDict = dict( (theoreticalAngles[i], theoreticalCoeffAngles[i]) for i in xrange(3 * self.central.maxInvSpinBox.value()  - 2) )

        if self.central.reverseCheck.isChecked():
            revesreAnalysed = True
        else:
            revesreAnalysed = False
        self.central.textEdit.append("Begin")
        for i in xrange(len(allSeqs)):
            seq = allSeqs[i]
            ListOfTreesIndex = MainListOfTreesIndex[i]
            if userEnter == None:
                self.central.textEdit.append("<h5><font color = 'blue'>The sequence number %d of measured angles in file %s: </h5>%s</font>" % (plantNo, self.datafilename ,str(seq)) )
            else:
                self.central.textEdit.append("<h5><font color = 'blue'>The sequence of measured angles: </h5>%s</font>" % (str(seq)) ) 
            self.central.textEdit.append("maxInversion: %d, canonical divergence angle: %.1f "%(maxInv, phylAngle))
            self.central.textEdit.append("<font color = red> The number of %d-admissible trees corresponding to subsequences of this sequence is: %d</font>"%(maxInv, len(ListOfTreesIndex)))
            index = 0
            bestSeq = []
            bestProb = 0
            for treeIndex in ListOfTreesIndex:
                bestPath = []
                self.central.textEdit.append("<font color = red>The sequences corresponding to <br>%s  <br> are:</font>" %(seq[index: treeIndex[1] + 1]) )
                seqList = []
                maxProb = None
                for pathAll in treeIndex[0].allPathsAll():
                    self.central.textEdit.append("<font color = 'green'> %s </font> "% str(pathAll[0]))
                    self.central.textEdit.append("<font color = 'green'> %s</font>" % str( [ D_n_coeffDict[pathAll[0][j]] for j in xrange(len ( pathAll[0 ]) )] ) )
                    self.central.textEdit.append( "<font color = 'red'>The sequence of probabilities: </font><br> <font color = 'green'>prob = %s</font>" % str(pathAll[1]) )
                    result, inversionList = isN_admissible2(pathAll[0], maxInv, phylAngle, D_n_coeffDict)
                    if not result: 
                        result, inversionList = isN_admissible2(pathAll[0][:-1], maxInv, phylAngle, D_n_coeffDict)
                    newInversionList = list()
                    for inversion in inversionList:
                        newInversion = [j + index for j in inversion]
                        newInversionList.append(newInversion)
                    self.central.textEdit.append("<font color = 'red'> the list of inversionsList is: <br></font> <font color = 'green'>%s </font>" % str(inversionList))
                    self.central.textEdit.append("<font color = 'red'> the list of inversions is: <br></font> <font color = 'green'>%s </font>" % str(newInversionList))
                    self.central.textEdit.append("<font color = 'red'> The probability of this sequence is: </font> <br> <font color = 'green'>%s <br></font>" % str(np.exp(pathAll[3])))
                    seqList.append(pathAll)
                    if maxProb == None:
                        maxProb = pathAll[3]
                    elif maxProb < pathAll[3]:
                        maxProb = pathAll[3]
                for pathAll in seqList:
                    if pathAll[3] == maxProb:
                        bestPath.append(pathAll)
                        break #???
                bestProb += maxProb
                bestSeq.append(bestPath)
                index = treeIndex[1] + 1
            ind = 0
            self.central.textEdit.append("<h5><font color = 'red'>The best sequence according to our statistic criteria is: </font></h5>")
            notExplainedList = []
            self.prediction = []
            self.notExplainedList = [] 
            self.inversions = []
            allProb = []
            for sList in bestSeq:
                for pathAll in sList:
                    self.central.textEdit.append("<font color = 'red'>The subsequence of measured angles:<br></font><font color = 'blue'>%s</font>"%str ( seq[ind: ind + len(pathAll[0]) ] ) ) 
                    self.central.textEdit.append("<font color = 'blue'>%s</font>" % str(pathAll[0]))
                    self.prediction.extend(pathAll[0])
                    self.central.textEdit.append("<font color = 'green'> %s</font>" % str( [ D_n_coeffDict[pathAll[0][j]] for j in xrange(len ( pathAll[0 ]) )] ) )
                    self.central.textEdit.append("<font color = 'red'>prob = %s</font>"% str(pathAll[1]))
                    allProb.extend(pathAll[1])
                    self.central.textEdit.append("<font color = 'blue'>%s</font>" % str(np.exp(pathAll[3])) )
                    self.central.textEdit.append("<font color = 'red'>Not explained:  </font>%s"% str(pathAll[2]))
                    notExplainedList.extend([j[1] + ind for j in pathAll[2]])
                    result, inversionList = isN_admissible2(pathAll[0], maxInv, phylAngle, D_n_coeffDict)
                    if not result: 
                        result, inversionList = isN_admissible2(pathAll[0][:-1], maxInv, phylAngle, D_n_coeffDict)

                    newInversionList = list()
                    for inversion in inversionList:
                        newInversion = [j + ind for j in inversion]
                        newInversionList.append(newInversion)
                    self.inversions.extend(newInversionList)
                    self.central.textEdit.append("<font color = 'red'> the list of inversions is: </font> <font color = 'green'>%s </font>" % str(newInversionList))
                    ind += len(pathAll[0])
            self.central.textEdit.append("<font color = 'green'>%s</font>"% str(np.exp(bestProb)))
            notExplainedAngles = [seq[j] for j in notExplainedList]
            self.notExplainedAngles = notExplainedAngles
            self.notExplainedList = notExplainedList
            
            self.central.textEdit.append("<h5><font color = 'green'><br />Analysis summary:</font></h5>" )
            self.central.textEdit.append("<font color = 'red'> Measured sequence: <br/></font><font color = 'green'>%s </font>" % str(seq))
            self.central.textEdit.append("<font color = 'red'> Predicted sequence: <br/></font> <font color = 'green'>%s </font>" % str(self.prediction))
            if i == 0:
                self.predictionDir = self.prediction
            elif i == 1:
                self.predictionReverse = self.prediction
                
            D_n , D_n_com = theoretical_divergence_angles(self.central.maxInvSpinBox.value(), self.central.phylType.value())
            code = dict((D_n[j], D_n_com[j]) for j in xrange(len(D_n)) )
            codedSeqNow = [code[j] for j in self.prediction]
                
            self.central.textEdit.append("<font color = 'red'> Predicted coded sequence: <br/></font> <font color = 'green'>%s </font>" % str(codedSeqNow))
            self.central.textEdit.append("<font color = 'red'> allProb: <br/></font><font color = 'green'>%s </font>" % str(allProb))
            self.central.textEdit.append("<font color = 'red'> notExplainedList: <br/></font><font color = 'green'>%s </font>" % str(notExplainedList))
            self.central.textEdit.append("<font color = 'red'> notExplainedAngles: <br/></font><font color = 'green'>%s </font>" % str(notExplainedAngles))
            self.central.textEdit.append("<font color = 'red'> the list of inversions is:<br/> </font> <font color = 'green'>%s </font>" % str(self.inversions))
            self.invalides = invalidateSeq(codedSeqNow, self.notExplainedList, maxInv)
                            
            if i == 0:
                self.codedDir = codedSeqNow
                self.probDir = allProb
                self.notExplainedDir = notExplainedList
                self.notExplainedAnglesDir = notExplainedAngles
                self.notExplainedListDir = self.notExplainedList
                self.inversionsDir = self.inversions
                self.invalidesDir= self.invalides
            elif i == 1:
                self.notExplainedListRev = self.notExplainedList
                self.codedReverse = codedSeqNow
                self.probReverse = allProb
                self.notExplainedReverse = notExplainedList
                self.notExplainedReverse = notExplainedAngles
                self.inversionsReverse = self.inversions
                self.invalidesReverse = self.invalides
            
            self.central.textEdit.append("<font color = 'red'> the list of invalides is: <br/></font> <font color = 'green'>%s </font>" % str(self.invalides))
            
            self.central.textEdit.append("\n")
        self.central.textEdit.append("End\n")
        self.central.textEdit.append(100*"_")
    

def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()
