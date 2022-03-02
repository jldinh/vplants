#!/usr/bin/env python


import sys
from PyQt4 import QtCore, QtGui
import visual
import math


class MyWidget(QtGui.QWidget):
    """This is common way of creating QT iface taken form PyQt5.
    """
    def __init__(self, myVisual, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.myVisual = myVisual

        quit = QtGui.QPushButton("Quit")

        lcd = QtGui.QLCDNumber(2)

        self.lcd2 = QtGui.QLCDNumber(2)
        
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 10)
        slider.setValue(0)

        self.connect(quit, QtCore.SIGNAL("clicked()"), QtGui.qApp, QtCore.SLOT("quit()"))
        self.connect(quit, QtCore.SIGNAL("clicked()"), self.prepare_to_quit)

        self.connect(slider, QtCore.SIGNAL("valueChanged(int)"), lcd, QtCore.SLOT("display(int)"))
        #adding the signal emission to the visual system 
        self.connect(slider, QtCore.SIGNAL("valueChanged(int)"), self.myVisual.set_C)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(quit)
        layout.addWidget(lcd)
        layout.addWidget(slider)
        layout.addWidget(self.lcd2)
        self.setLayout(layout)

    def prepare_to_quit( self ):
        self.myVisual.keep_running = False
        
    def lcd2_update( self, i):
        self.lcd2.display(  self.lcd2.intValue()+1)
        print " # recived from sphere id: %s" %i

class MyVisual( QtCore.QThread, QtCore.QObject ):
    """ This would be a visual window we want to connect to the QT iface.
    """
    def __init__( self ):
        QtCore.QThread.__init__( self )
        self.C = 0
        # it is requred to process input events from visual window
        self.display = visual.display()
        self.s = visual.sphere( pos=visual.vector( 1, 0, 0 ) )
        self.keep_running=True

    def run( self ):
        i = 0
        while self.keep_running:
            self.s.pos.x = self.C*math.sin(i)
            i+=0.00001
            self.process()
        self.display.visible=0
        #del self.display

    def quit( self ):
        self.keep_running=False

    def set_C( self, s):
        """This would be used as a QT "slot"
        """
        self.C = s

    def process( self ):
        """Used to get input events from visual display
        """
        if self.display.mouse.clicked: 
            click = self.display.mouse.getclick()
            if click.pick.__class__ == visual.sphere:
                # console event
                print " # clicked sphere id: %s" % self.__hash__()
                # qt event
                self.emit( QtCore.SIGNAL( "sphereClicked(int)" ), self.__hash__() )

app = QtGui.QApplication( sys.argv )
myVisual = MyVisual()
myVisual.start()
widget = MyWidget( myVisual )
widget.show()
myVisual.connect(myVisual, QtCore.SIGNAL("sphereClicked(int)"), widget.lcd2_update )
sys.exit(app.exec_())
