#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- python -*-
#
#       vplants.mars_alt.alt.lineage_editor
#
#       Copyright 2010-2011 INRIA - CIRAD - INRA - ENS-Lyon
#
#       File author(s): Vincent Mirabet - Eric Moscardi, Manuel Forero
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__license__ = "Cecill-C"
__revision__ = " $Id$ "

import sys

# import libraries
import numpy as np
from scipy import ndimage

# from openalea.image import *
try:
    from enthought.tvtk.api import tvtk
except:
    from tvtk.api import tvtk

try:
    from enthought.traits.api import HasTraits, String, List, Dict, Int, Bool, Tuple, Button, Instance, on_trait_change
except:
    from traits.api import HasTraits, String, List, Dict, Int, Bool, Tuple, Button, Instance, on_trait_change

try:
    from enthought.traits.ui.api import View, Group, Item, HSplit, VSplit, FileEditor
except:
    from traitsui.api import View, Group, Item, HSplit, VSplit, FileEditor

try:
    from enthought.mayavi.core.api import Engine
except:
    from mayavi.core.api import Engine

try:
    from enthought.mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor
except:
    from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor

from openalea.image.serial.basics import imread
from CellEditor import Mapping, Cells



def img2polydata(image, subdivision=64):
    """
    Convert a |SpatialImage| to a PolyData object with cells surface

    : Parameters :

    """
    # to dig the cells and create a space between them
    mask = ndimage.laplace(image)
    image[mask != 0] = 0
    mask = ndimage.laplace(image)
    image[mask == 0] = 0

    xyz = {}

    liste = list(np.unique(image))
    try:
        liste.remove(0)
        liste.remove(1)
    except:
        print "try problem, we skip that (no big deal!)"
    for i in liste:
        xyz[i] = np.ndarray((0, 3))

    # subdivise space for runtime optimisation
    # cells part are bound afterwards
    # TODO : use shift function
    xdim, ydim, zdim = image.shape
    for i in xrange(0, xdim, subdivision):
        for j in xrange(0, ydim, subdivision):
            for k in xrange(0, zdim, subdivision):
                data = image[i:i + subdivision, j:j + subdivision, k:k + subdivision]
                # creation of the locale cells list
                for cel in list(np.unique(data)):
                    if cel not in [0, 1] and cel in data:
                        coords = np.array(np.where(data == cel)).T
                        coords += [i, j, k]
                        xyz[cel] = np.vstack((xyz[cel], coords))

    max_id = 2 * max(xyz.keys())

    polydata = tvtk.AppendPolyData()
    polys = {}
    for c in xyz:
        pd = tvtk.PolyData(points=xyz[c])
        pd.point_data.scalars = [c for i in xrange(len(xyz[c]))]

        f = tvtk.VertexGlyphFilter(input=pd)
        f2 = tvtk.PointDataToCellData(input=f.output)
        polys[c] = f2.output
        polydata.add_input(polys[c])
        polydata.set_input_array_to_process(0, 0, 0, 0, 0)


    return polydata, polys, max_id


class MyLineage(object):
    """
    """
    def __init__(self):
        """
        """
        self.mothers = list()
        self.daughters = list()

        self.mapping = {}
        self.current_mother = None

        self._id = 0

    def get_current_mother(self):
        return self.current_mother

    def get_mothers(self):
        return self.mapping.keys()

    def get_daughters(self, label):
        if label in self.mapping.keys():
            return self.mapping[label]
        else:
            return None

    def add_mother(self, label):
        if label not in self.mapping.keys():
            self.mapping[label] = []
            self.mothers.append(label)

    def add_daughter(self, label):
        self.mapping[self.current_mother].append(label)
        if label not in self.daughters:
            self.daughters.append(label)
            print self.daughters

    def remove_mother(self, label):
        self.mothers.remove(label)
        for d in self.mapping[label]:
            self.daughters.remove(d)
        self.mapping.pop(label)

    def remove_daughter(self, label):
        self.daughters.remove(label)
        for k, v in self.mapping.iteritems():
            if label in v:
                self.mapping[k].remove(label)

    def set_current_mother(self, label):
        self.current_mother = label


    def set_id(self, label):
        """
        """
        self._id = self.mothers.index(label)

    def get_id(self):
        """
        """
        return self.mothers.index(self.current_mother)


    # def load_mapping(self, mapping):
        # for k,v in mapping.iteritems():
            # self.add_mother(k)
            # self.set_current_mother(k)
            # for value in v:
                # self.add_daughter(value)

    # def write_mapping(self, mapping):
        # try:
            # f=open("current_lineage.txt","w")
        # except IOError:
            # print "saving lineage impossible"
        # for i in mapping.keys():
            # f.write(str(i))
            # f.write(" ")
            # for d in mapping[i]:
                # f.write(str(d))
                # f.write(" ")
            # f.write("\n")
        # f.close()

################################################################################
class MyApp(HasTraits):

    # The first engine. As default arguments (an empty tuple) are given,
    # traits initializes it.
    def __init__(self, img1, img2):
        HasTraits.__init__(self)
        self.img1 = img1
        self.img2 = img2

    engine1 = Instance(Engine, args=())
    scene1 = Instance(MlabSceneModel)
    hide = Bool(False)
    new_lineage = Bool(False)
    mapping = Instance(Mapping, ())
    lineage = MyLineage()

    mother_id = Int(0)

    mother = Int(0)
    moutlines = List()
    doutlines = List()
    colors = List()
    color = Tuple()
    daughters = List()

    # for the moment, we don't use the show/hide button
    # hide_show_cells = Button('Hide/Show Cells')


    fileEditor = FileEditor()

    @on_trait_change('fileEditor')
    def load_mapping(self):
        print "fileEditor"

    @on_trait_change('mapping._load_fired')
    def add_lineage(self):
        for c in self.mapping.cells :
            if (c.mother not in self.lineage.mothers) & (c.mother != 0) :
                self.lineage.add_mother(c.mother)
                self.mapper1.input.cell_data.scalars = [ (x, x + self.max_id1) [ x == c.mother ] for x in self.mapper1.input.cell_data.scalars ]
                self.mapper1.update()

                for d in c.daughters:
                    self.lineage.add_daughter(d)
                    self.mapper2.input.cell_data.scalars = [ (x, x + self.max_id2) [ x == d ] for x in self.mapper2.input.cell_data.scalars ]
                    self.mapper2.update()

    def _scene1_default(self):
        " The default initializer for 'scene1' "
        self.engine1.start()
        scene1 = MlabSceneModel(engine=self.engine1)
        return scene1


    engine2 = Instance(Engine, args=())
    scene2 = Instance(MlabSceneModel)

    def _scene2_default(self):
        " The default initializer for 'scene2' "
        self.engine2.start()
        scene2 = MlabSceneModel(engine=self.engine2)
        return scene2


    # We populate the scenes only when it is activated, to avoid problems
    # with VTK objects that expect an active scene
    @on_trait_change('scene1.activated')
    def populate_scene1(self):

        ############################################
        print "creation of the input image T1"

        ap, polys, self.max_id1 = img2polydata(self.img1)
        m = tvtk.PolyDataMapper(input=ap.output)
        m.scalar_range = [0, self.max_id1 + max(polys.keys())]
        col1 = np.random.randint(low=123, high=256, size=(self.max_id1, 4))
        col1[:, 3] = 255
        col1[:, 2] = 0
        col2 = np.random.randint(low=123, high=256, size=(self.max_id1, 4))
        col2[:, 3] = 255
        col2[:, 0] = 0
        col2[:, 1] = 0
        self.col1 = list(col1) + list(col2)
        m.lookup_table.table = self.col1


        a = tvtk.QuadricLODActor(mapper=m)
        a.property.point_size = 4

        self.mapper1 = m
        self.scene1.add_actor(a)


        self.picker1 = self.scene1.mayavi_scene.on_mouse_pick(self.picker_callback1, type="cell")
        self.picker1 = self.scene1.mayavi_scene.on_mouse_pick(self.picker_return_callback1, type="cell", button="Right")
        self.picker1.tolerance = 0.01
        print "scene 1 cree"

    def picker_callback1(self, picker_obj):
        if self.picker1.mapper is None:
            return
        label = int(self.picker1.mapper.input.cell_data.scalars[picker_obj.cell_id])
        if label > 0 and label <= self.max_id1:
            print label
            self.lineage.set_current_mother(label)
            for mother in self.lineage.get_mothers() :
                daughter = self.lineage.get_daughters(mother)

            if label not in self.lineage.get_mothers():
                ############################################
                # add mother in the mapping
                self.mapping.cells.append(Cells(mother=label))
                self.lineage.add_mother(label)
                self.picker1.mapper.input.cell_data.scalars = [ (x, x + self.max_id1) [ x == label ] for x in self.picker1.mapper.input.cell_data.scalars ]

                ############################################

            daughter = self.lineage.get_daughters(label)

            print "add cell number = ", label

        if label > self.max_id1:
            self.lineage.set_current_mother(label - self.max_id1)

    def picker_return_callback1(self, picker_obj):
        if self.picker1.mapper is None :
            return
        label = int(self.picker1.mapper.input.cell_data.scalars[picker_obj.cell_id])
        if label > self.max_id1:
            print "remove cell number = ", label - self.max_id1

            if label - self.max_id1 in self.lineage.mapping.keys() :
                # self.hdata1[self.data1==label] = label
                for labs in self.lineage.get_daughters(label - self.max_id1):
                    print "le voila !", labs
                    self.mapper2.input.cell_data.scalars = [ (x, x - self.max_id2) [ x == labs + self.max_id2 ] for x in self.mapper2.input.cell_data.scalars ]
                self.mapping.cells.pop(self.lineage.mothers.index(label - self.max_id1))
                self.lineage.remove_mother(label - self.max_id1)
                self.picker1.mapper.input.cell_data.scalars = [ (x, x - self.max_id1) [ x == label ] for x in self.picker1.mapper.input.cell_data.scalars ]


    @on_trait_change('scene2.activated')
    def populate_scene2(self):

        ############################################
        print "creation of the input image T2"

        ap, polys, self.max_id2 = img2polydata(self.img2)
        m = tvtk.PolyDataMapper(input=ap.output)
        m.scalar_range = [0, self.max_id2 + max(polys.keys())]

        col1 = np.random.randint(low=123, high=256, size=(self.max_id2, 4))
        col1[:, 3] = 255
        col1[:, 2] = 0
        col2 = np.random.randint(low=123, high=256, size=(self.max_id2, 4))
        col2[:, 3] = 255
        col2[:, 0] = 0
        col2[:, 1] = 0
        self.col1 = list(col1) + list(col2)
        m.lookup_table.table = self.col1


        a = tvtk.QuadricLODActor(mapper=m)
        a.property.point_size = 4


        self.scene2.add_actor(a)
        self.mapper2 = m



        self.picker2 = self.scene2.mayavi_scene.on_mouse_pick(self.picker_callback2, type="cell")
        self.picker2 = self.scene2.mayavi_scene.on_mouse_pick(self.picker_return_callback2, type="cell", button="Right")
        self.picker2.tolerance = 0.01
        print "scene 2 cree"

    def picker_callback2(self, picker_obj):
        if self.picker2.mapper is None:
            return
        label = int(self.picker2.mapper.input.cell_data.scalars[picker_obj.cell_id])

        if label > 0 and label <= self.max_id2:
            liste = self.lineage.get_daughters(self.lineage.get_current_mother())
            if type(liste) == type([]):
                if label not in liste :
                    self.picker2.mapper.input.cell_data.scalars = [ (x, x + self.max_id2) [ x == label ] for x in self.picker2.mapper.input.cell_data.scalars ]
                    # add label in the daughters list
                    self.lineage.add_daughter(label)
                    cid = self.lineage.get_id()
                    if cid >= 0 :
                        self.mapping.cells[cid].daughters.append(int(label))

            self.new_lineage = False

    def picker_return_callback2(self, picker_obj):
        if self.picker2.mapper is None :
            return
        label = int(self.picker2.mapper.input.cell_data.scalars[picker_obj.cell_id])
        if label > self.max_id2:
            print "remove cell number = ", label - self.max_id2

            if (label - self.max_id2) in self.lineage.daughters :
                    # self.hdata2[self.data2==label] = label
                    # remove label from the daughters list
                    self.picker2.mapper.input.cell_data.scalars = [ (x, x - self.max_id2) [ x == label ] for x in self.picker2.mapper.input.cell_data.scalars ]
                    self.lineage.remove_daughter(label - self.max_id2)
                    for cid in self.mapping.cells:
                        if (label - self.max_id2) in cid.daughters:
                            cid.daughters.remove(label - self.max_id2)


    def get_mapping(self):
        return self.lineage.mapping

    # The layout of the view
    view = View(HSplit
                (VSplit(
                        Group(Item('mapping', show_label=False, style="custom"),),
                        # Group(Item('hide_show_cells', show_label=False ), ),
                        ),
                    Group(Item('scene1',
                        editor=SceneEditor(scene_class=MayaviScene),
                        width=480, height=480, show_label=False)),
                    Group(Item('scene2',
                        editor=SceneEditor(scene_class=MayaviScene),
                        width=480, height=480, show_label=False)),
                    ),
                    resizable=True
                )


def main():
    args = sys.argv[1:]
    # print args
    if args == []:
        import openalea.container
        from openalea.deploy.shared_data import shared_data
        from openalea.image.serial.basics import SpatialImage
        im1 = imread(shared_data(openalea.container, "p58-t1_imgSeg_cleaned.inr.gz"))
        im2 = imread(shared_data(openalea.container, "p58-t2_imgSeg_cleaned.inr.gz"))
        im1_crop = SpatialImage(im1[120:380, 120:380, 0:80])
        im2_crop = SpatialImage(im2[140:430, 140:430, 0:80])
        MyApp(im1_crop, im2_crop).configure_traits()
    elif len(args) == 2:
        try:
            im1 = imread(args[0])
            im2 = imread(args[1])
            MyApp(im1, im2).configure_traits()
        except:
            print "les images ne sont pas au bon format ou ce ne sont pas des images"
            sys.exit(0)
    else:
        print "vous n'avez pas entré le bon nombre d'arguments, recommencez en mettant deux segmentations"




if __name__ == '__main__':
    main()


# if __name__ == '__main__':
    # from openalea.image.all import *
    # im1 = imread('/var/softs/logiciels/pipe/p181/120117-p181-t2/120117-p181-ahp6gfp-t2SegMIPS-filtreCellulesAberrantes_130312.inr.gz')
    # im2 = imread('/var/softs/logiciels/pipe/p181/120118-p181-t3/120118-p181-ahp6gfp-t3SegMIPS_140312-filtreCellulesAberrantes.inr.gz')
    # im1 = imread('/var/softs/logiciels/pipe/rdp/p114-t2-L1.inr.gz')
    # im2 = imread('/var/softs/logiciels/pipe/rdp/p114-t3-L1.inr.gz')
    # MyApp(im1,im2).configure_traits()
#
