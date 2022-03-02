# -*- python -*-
#
#       OpenAlea.Image
#
#       Copyright 2006 - 2008 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

from PyQt4.QtCore import QObject,SIGNAL
from openalea.visualea.node_widget import NodeWidget
from openalea.core.observer import lock_notify
from openalea.image.spatial_image import SpatialImage
from openalea.image.gui.palette import palette_names,palette_factory
from vplants.mars_alt.alt.init_alt import Init_ALT

class InitALTWidget(NodeWidget,Init_ALT) :
    """
    """
    def __init__ (self, node, parent = None) :

	Init_ALT.__init__(self)
    	NodeWidget.__init__(self, node)

        self.notify(node, ('input_modified',))

        self.connect(self, SIGNAL("points_changed"), \
                     self.pointsChanged)

        self.window().setWindowTitle(node.get_caption())


    @lock_notify
    def pointsChanged(self,event):
        """ update points """
        print "update points"
        pts1,pts2 = self.get_points()
        self.node.set_input(4, pts1)
        self.node.set_output(2, pts2)
        self.node.set_input(5, pts1)
        self.node.set_output(3, pts2)


    def notify(self, sender, event):
        """ Notification sent by node """
        if event[0] == 'caption_modified':
            self.window().setWindowTitle(event[1])

        if event[0] == 'input_modified' :
            image1 = self.node.get_input(0)
            image2 = self.node.get_input(1)

            if image1 is not None :
                if image1.ndim == 2:
                    image1 = image1.reshape(image1.shape + (1,))
                if not isinstance(image1,SpatialImage):
                    image1 = SpatialImage(image1)
            if image2 is not None :
                if image2.ndim == 2:
                    image2 = image2.reshape(image2.shape + (1,))
                if not isinstance(image2,SpatialImage):
                    image2 = SpatialImage(image2)

                self.set_palette(palette_factory("grayscale",image1.max()),palette_factory("grayscale",image2.max()))
                self.set_image(image1,image2)

            points1 = self.node.get_input(2)
            points2 = self.node.get_input(3)

            self.node.set_input(4, points1)
            self.node.set_input(5, points2)

            if (points1 is not None) & (points2 is not None):
                self.set_points(points1,point2)

