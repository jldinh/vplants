# -*- python -*-
#
#       vplants.mars_alt.alt.init_alt
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################
"""
This module provide a Tool for the initialization of ALT
"""

__license__= "Cecill-C"
__revision__=" $Id$ "

__all__ = ["Init_ALT","initialization_alt"]


from PyQt4.QtCore import Qt,QObject,SIGNAL,QRectF,QPointF, QPoint
from PyQt4.QtGui import (QApplication,QMainWindow,QGraphicsScene,QGraphicsPixmapItem,
                         QToolBar,QSlider,QLabel,QComboBox,QIcon,QActionGroup,
                         QColor,QPen,QBrush,QGraphicsSimpleTextItem,QTransform,
                         QFileDialog,QMessageBox,QSplitter)

import numpy as np
import scipy.ndimage as ndimage
from openalea.image.algo.basic import reverse_image,  end_margin
from openalea.image.algo.morpho import connectivity_26
from openalea.image.spatial_image import SpatialImage
from openalea.image.all import point_selection
from openalea.image.gui.palette import palette_factory

from vplants.mars_alt.analysis.analysis import VTissueAnalysis, extract_L1
from vplants.mars_alt.analysis.structural_analysis import draw_walls



try:
    from openalea.container.utils import IdSetGenerator
except ImportError:
    from id_generator import IdSetGenerator


class Init_ALT (QMainWindow) :

    def __init__ (self) :
        QMainWindow.__init__(self)

        # points
        self._id_gen = IdSetGenerator()
        self._pid = None
        self.pid_changed = False

        self.pts2 = {}

        self._widget1 = PointSelection()
        self._widget2 = PointSelection()

        self._widget1._action_add.setVisible(False)
        self._widget2._action_add.setVisible(False)
        self._widget1._action_delete.setVisible(False)
        self._widget2._action_delete.setVisible(False)

        ################### toolbar ###################
        self._toolbar = self.addToolBar("tools")
        self._toolgroup = QActionGroup(self)

        # QWidgetAction : "Add point"
        self._action_add = self._toolbar.addAction("Add point")
        self._action_add.setCheckable(True)
        self._toolgroup.addAction(self._action_add)
        self._action_add.setIcon(QIcon(":/image/add.png") )

        # QWidgetAction : "Delete point"
        self._action_delete = self._toolbar.addAction("Delete point")
        self._action_delete.setCheckable(True)
        self._toolgroup.addAction(self._action_delete)
        self._action_delete.setIcon(QIcon(":/image/delete.png") )

        ################### mouse handling ###################
        self._widget1.setMouseTracking(True)
        self._last_mouse_x1 = 0
        self._last_mouse_y1 = 0
        self._last_slice1 = 0

        QObject.connect(self._widget1._widget,
                    SIGNAL("mouse_press"),
                    self.mouse_pressed1)

        QObject.connect(self._widget2._widget,
                    SIGNAL("mouse_press"),
                    self.mouse_pressed2)

        self.splitter = QSplitter()
        self.splitter.addWidget(self._widget1)
        self.splitter.addWidget(self._widget2)

        self.setCentralWidget(self.splitter)


    def set_image (self, img1,img2) :
        self._widget1.set_image(img1)
        self._widget2.set_image(img2)


    def set_palette (self, palette1,palette2) :
        self._widget1.set_palette(palette1)
        self._widget2.set_palette(palette2)


    def set_points(self,points1,points2):
        points1 = mapping.key()
        points2 = mapping.values()
        self._widget1.set_points(points1)
        self._widget2.set_points(points2)

    def get_mapping(self,im1,im2):
        """
        get the mapping from pts given in the tool

        :Parameters:
        - `im1` (|SpatialImage|) - segmented image T1
        - `im2` (|SpatialImage|) - segmented image T2
        """
        mapping = {}
        pts1 = self._widget1.get_points()
        for pt in pts1:
            cell1 = im1[pt[0],pt[1],pt[2]]
            mapping[cell1] = []
            coords = self.pts2[pts1.index(pt)]
            for coord in coords:
                cell2 = im2[coord[0],coord[1],coord[2]]
                mapping[cell1] += [cell2,]
        return mapping


    def get_mapping_from_surface(self,image1,image2):
        """
        get the mapping from pts positioned on the surface of meristem

        :Parameters:
        - `im1` (|SpatialImage|) - segmented image T1
        - `alt1` (|SpatialImage|) - altitude of maximum intensity projection T1
        - `im2` (|SpatialImage|) - segmented image T2
        - `alt2` (|SpatialImage|) - altitude of maximum intensity projection T2
        """
        mapping = {}

        im1 = segmentation2surface(image1)
        im2 = segmentation2surface(image2)

        pts1 = self._widget1.get_points()
        pts2 = self.pts2

        for pt in pts1:
            cell1 = im1[pt[0],pt[1],pt[2]]
            mapping[cell1] = []
            coords = self.pts2[pts1.index(pt)]
            for coord in coords:
                cell2 = im2[coord[0],coord[1],coord[2]]
                mapping[cell1] += [cell2,]
        return mapping


    def mouse_pressed1 (self, pos):
        if pos is not None :
            sc_coords = self._widget1._widget.mapToScene(pos)
            if self._action_add.isChecked() :
                if not self.pid_changed :
                    self._pid = self._id_gen.get_id()
                self.pid_changed = False
                ind,(i,j,k) = self._widget1.add_point(sc_coords,self._pid)
                self.pts2[ind] = []
            elif self._action_delete.isChecked() :
                ind = self._widget1.del_point(sc_coords)
                self._widget2.del_point(sc_coords,ind)
                self._pid=ind
                self.pid_changed = True

    def mouse_pressed2 (self, pos):
        if pos is not None :
            sc_coords = self._widget2._widget.mapToScene(pos)
            if self._action_add.isChecked() :
                ind,(i,j,k) = self._widget2.add_point(sc_coords,self._pid)
                self.pts2[ind]+=[(i,j,k),]
            elif self._action_delete.isChecked() :
                ind = self._widget2.del_point(sc_coords)
                self.pts2.pop(ind)









def segmentation2surface(image):
    """
    It computes a surfacic view of the meristem from a segmented image.
    :Parameters:
    - `image` (|SpatialImage|) - segmented image to be masked
    :Returns:
    - `mip_img` (|SpatialImage|) - maximum intensity projection
    - `alt_img` (|SpatialImage|) - altitude of maximum intensity projection
    """
    if not isinstance(image,SpatialImage):
        image = SpatialImage(image)

    #DESSINERSEPARATIONS imgSeg_0.inr.gz separationsEpaisses.inr.gz 2
    walls = draw_walls(image,True)
    walls_inv = reverse_image(walls)

    L1 = extract_L1(image)

    # echo "Construction d'un masque de la surface"
    #seuillage -sb 2 ${f}.inr.gz  ${f}sb.inr.gz
    threshold = np.where(image < 2, False, True)

    #morpho -ero ${f}sb.inr.gz ${f}PT1.inr.gz -i 2 -con 26
    iterations = 10
    erosion =  ndimage.binary_erosion(threshold, connectivity_26, iterations, border_value=1)
    erosion =  np.select([erosion == 1], [255], default=0)

    #zcopy -o 1 ${f}PT1.inr.gz ${f}PT1.inr.gz
    erosion = np.ubyte(erosion)

    #Logic -xou ${f}sb.inr.gz ${f}PT1.inr.gz ${f}Xou.inr.gz
    m_xor = np.logical_xor(threshold, erosion)

    #METTRE_A_ZERO_LES_DERNIERES_COUPES ${f}Xou.inr.gz ${f}Xou2.inr.gz $tailleZ
    mat = end_margin(m_xor,10,2)

    # echo "Masque des parois, de la surface et de la L1 dans l'image :"

    #Logic -mask $2 $1 ${f}first.inr.gz
    m_mask = np.where(walls_inv!=0,image,0)

    #Logic -mask ${f}Xou2.inr.gz ${f}first.inr.gz ${f}And.inr.gz
    m_mask2 = np.where(mat!=0,m_mask,0)

    #Logic -mask layer1.inr.gz ${f}And.inr.gz ${f}And2.inr.gz
    m_mask3 = np.copy(m_mask2)
    for cell in xrange(1,image.max()) :
        if cell not in L1 :
            m_mask3[m_mask3==cell] = 0

    #mip_project ${f}And.inr.gz mip${f}Surf
    x,y,z = m_mask3.shape
    m_mip = m_mask3.max(2).reshape(x,y,1)

    return SpatialImage(m_mip,image.resolution)




def initialization_alt (im1, im2, points1=None, points2=None, palette_name = "grayscale", color_index_max = None) :

    if not isinstance(im1,SpatialImage):
        im1 = SpatialImage(im1)
    if not isinstance(im2,SpatialImage):
        im2 = SpatialImage(im2)

    w = Init_ALT()
    w.set_image(im1,im2)

    if color_index_max is None :
        cmax1 = im1.max()
        cmax2 = im2.max()
    else :
        cmax1 = cmax2 = color_index_max

    palette1 = palette_factory(palette_name,cmax1)
    palette2 = palette_factory(palette_name,cmax2)

    w.set_palette(palette1,palette2)

    if (points1 is not None) & (points2 is not None) :
        w.set_points(points1,points2)

    w.show()

    return w

