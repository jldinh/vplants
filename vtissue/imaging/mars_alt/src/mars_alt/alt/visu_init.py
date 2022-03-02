# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.mars_alt.alt.visu_init
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__ = "Cecill-C"
__revision__ = " $Id$ "

##############################
# Code
##############################

import numpy as np
from scipy import ndimage
import math

# from openalea.image import *

##############################
# Define the sphere cut in two
##############################
def HSVtoRGB(h, s, v) :

    if s == 0 :
    # achromatic (grey)
        r = g = b = v
    return r, g, b

    h /= 60. # sector 0 to 5
    i = math.floor(h)
    f = h - i # factorial part of h
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    if  i == 0 :
        r = v
        g = t
        b = p
    elif i == 1 :
        r = q
        g = v
        b = p
    elif i == 2 :
        r = p
        g = v
        b = t
    elif i == 3 :
        r = p
        g = q
        b = v
    elif i == 4:
        r = t
        g = p
        b = v
    else :
        r = v
        g = p
        b = q

    return r, g, b

def create_meristem_T1 (R):
    xdim, ydim, zdim = 50, 50, 50
    vx, vy, vz = 1., 1., 1.
    # R = 25
    cx = 25
    cy = 25
    cz = 25

    data = np.zeros([xdim, ydim, zdim], np.uint8)

    for i in xrange(xdim):
        for j in xrange(ydim):
            for k in xrange(zdim):
                if (i * vx - cx) ** 2 + (j * vy - cy) ** 2 + (k * vz - cz) ** 2 < (R * R) :
                    if k < 10 :
                        data[i, j, k] = 10
                    if 10 < k < 20 :
                        data[i, j, k] = 50
                    if 20 < k < 30 :
                        data[i, j, k] = 100
                    if 30 < k < 40 :
                        data[i, j, k] = 150
                    if 40 < k < 50 :
                        data[i, j, k] = 200
    return data

def create_meristem_T2 (R):
    xdim, ydim, zdim = 50, 50, 50
    vx, vy, vz = 1., 1., 1.
    # R = 25
    cx = 25
    cy = 25
    cz = 25

    data = np.zeros([xdim, ydim, zdim], np.uint8)

    for i in xrange(xdim):
        for j in xrange(ydim):
            for k in xrange(zdim):
                if (i * vx - cx) ** 2 + (j * vy - cy) ** 2 + (k * vz - cz) ** 2 < (R * R) :
                    if k < 10 :
                        if j < 25:
                            data[i, j, k] = 10
                        if j > 25 :
                            data[i, j, k] = 25
                    if 10 < k < 20 :
                        if j < 20:
                            data[i, j, k] = 50
                        if j > 20 :
                            data[i, j, k] = 75
                    if 20 < k < 30 :
                        if j < 35:
                            data[i, j, k] = 100
                        if j > 35 :
                            data[i, j, k] = 125
                    if 30 < k < 40 :
                        if j < 5:
                            data[i, j, k] = 150
                        if j > 5 :
                            data[i, j, k] = 175
                    if 40 < k < 50 :
                        if j < 35:
                            data[i, j, k] = 200
                        if j > 35 :
                            data[i, j, k] = 210
    return data

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

try:
    from enthought.tvtk.api import tvtk
except ImportError:
    import tvtk

class MyOutlines(object):
    """
    """
    def __init__(self, img, scene):
        self.scene = scene
        self.objects = ndimage.find_objects(img)
        self.outlines = list()
        self.create()

    def create(self):
        """
        """
        for obj in self.objects:
            if obj is not None:
                x, y, z = obj

                h, s, v = (self.objects.index(obj) % 360., 1., 1.)
                color = HSVtoRGB(h, s, v)

                outline = self.scene.mlab.outline(name="%s" % self.objects.index(obj), line_width=3, color=color, figure=self.scene.mayavi_scene)
                # outline.outline_mode = 'cornered'
                outline.bounds = (x.start, x.stop,
                                    y.start, y.stop,
                                    z.start, z.stop
                                    )
                outline.visible = False
                self.outlines.append(outline)
            else :
                self.outlines.append(None)


    def get_outline(self, label):
        """
        """
        return self.outlines[label - 1]

    def set_visible(self, label):
        self.outlines[label - 1].visible = True

    def set_not_visible(self, label):
        self.outlines[label - 1].visible = False

    def get_color(self, label):
        return self.outlines[label - 1].actor.property.color

    def set_color(self, color, label):
        self.outlines[label - 1].actor.property.color = color

    def set_cornered(self, label):
        """
        """
        self.outlines[label - 1].outline_mode = 'cornered'

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
        return self.mapping[label]

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

################################################################################
class MyApp(HasTraits):

    # The first engine. As default arguments (an empty tuple) are given,
    # traits initializes it.
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
    hide_show_cells = Button('Hide/Show Cells')


    @on_trait_change('mapping.add')
    def add_lineage(self):
        for c in self.mapping.cells :
            if (c.mother not in self.lineage.mothers) & (c.mother != 0) :
                self.lineage.add_mother(c.mother)
                self.outlines1.set_cornered(c.mother)
                self.outlines1.set_visible(c.mother)
                self.color = self.outlines1.get_color(c.mother)

                for d in c.daughters:
                    self.lineage.add_daughter(d)
                    self.outlines2.set_cornered(d)
                    self.outlines2.set_visible(d)
                    self.outlines2.set_color(self.color, d)


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
        print "creating of the input image T1"
        from openalea.image.serial.basics import imread
        self.data1 = create_meristem_T1 (25)
        # ~ self.data1 = read_inrimage("mayavi_image.inr.gz")
        # ~ self.data1 = imread('/home/jonathan/Meristems/p58/segExpert58-day1.inr.gz')
        self.hdata1 = self.data1.copy()
        ############################################

        ############################################

        ############################################
        print "creating of the mayavi scene T1"
        ############################################

        self.src1 = self.scene1.mlab.pipeline.scalar_field(self.data1)
        self.src1.update_image_data = True

        contour = self.scene1.mlab.pipeline.contour(self.src1,)
        contour.filter.auto_contours = True
        contour.filter.minimum_contour = 1
        contour.filter.maximum_contour = 5

        connect_ = tvtk.PolyDataConnectivityFilter(extraction_mode=5, color_regions=True)
        connect = self.scene1.mlab.pipeline.user_defined(contour, filter=connect_)

        self.surf1 = self.scene1.mlab.pipeline.surface(connect)

        # self.col1 = np.random.randint(256,size=(int(self.data1.max()),4))
        # self.col1[:,3] = 255
        # self.surf1.module_manager.scalar_lut_manager.lut.table = self.col1

        ############################################
        print "creating of the bounding boxes T1"
        ############################################
        self.outlines1 = MyOutlines(self.data1, self.scene1)

        self.picker1 = self.scene1.mayavi_scene.on_mouse_pick(self.picker_callback1, type="cell")
        self.picker1 = self.scene1.mayavi_scene.on_mouse_pick(self.picker_return_callback1, type="cell", button="Right")


    def picker_callback1(self, picker_obj):
        if self.picker1.mapper is None:
            return
        label = self.data1[picker_obj.mapper_position]
        if label > 0 :

            self.lineage.set_current_mother(label)
            for mother in self.lineage.get_mothers() :
                outline = self.outlines1.get_outline(mother)
                outline.outline_mode = 'full'
                daughter = self.lineage.get_daughters(mother)
                for d in daughter :
                    outline = self.outlines2.get_outline(d)
                    outline.outline_mode = 'full'

            if label not in self.lineage.get_mothers():
                ############################################
                # add mother in the mapping
                self.mapping.cells.append(Cells(mother=label))
                self.lineage.add_mother(label)
                ############################################

            self.outlines1.set_cornered(label)
            self.outlines1.set_visible(label)

            daughter = self.lineage.get_daughters(label)
            for d in daughter :
                self.outlines2.set_cornered(d)

            self.color = self.outlines1.get_color(label)

            print "add cell number = ", label
            self.hide = True
            self.new_lineage = True


    def picker_return_callback1(self, picker_obj):
        if self.picker1.mapper is None :
            return
        label = self.data1[picker_obj.mapper_position]
        if label > 0 :
            print "remove cell number = ", label
            for d in self.lineage.mapping[label]:
                self.outlines2.set_not_visible(d)
                # self.lineage.remove_daughter(d)

            if label in self.lineage.mapping.keys() :
                # self.hdata1[self.data1==label] = label
                self.mapping.cells.pop(self.lineage.mothers.index(label))
                self.outlines1.set_not_visible(label)
                self.lineage.remove_mother(label)


    @on_trait_change('scene2.activated')
    def populate_scene2(self):

        ############################################
        print "creating of the input image T2"
        self.data2 = create_meristem_T2 (25)
        # self.data2 = read_inrimage("mayavi_image2.inr.gz")
        self.hdata2 = self.data2.copy()
        ############################################

        ############################################
        print "creating of the mayavi scene T2"
        ############################################

        self.src2 = self.scene2.mlab.pipeline.scalar_field(self.data2)
        self.src2.update_image_data = True

        contour = self.scene2.mlab.pipeline.contour(self.src2,)
        contour.filter.auto_contours = True
        contour.filter.minimum_contour = 1
        contour.filter.maximum_contour = 5

        connect_ = tvtk.PolyDataConnectivityFilter(extraction_mode=5, color_regions=True)
        connect = self.scene2.mlab.pipeline.user_defined(contour, filter=connect_)

        self.surf2 = self.scene2.mlab.pipeline.surface(connect)

        ############################################
        print "creating of the bounding boxes T2"
        ############################################
        self.outlines2 = MyOutlines(self.data2, self.scene2)

        self.picker2 = self.scene2.mayavi_scene.on_mouse_pick(self.picker_callback2, type="cell")
        self.picker2 = self.scene2.mayavi_scene.on_mouse_pick(self.picker_return_callback2, type="cell", button="Right")

    def picker_callback2(self, picker_obj):
        if self.picker2.mapper is None:
            return
        label = self.data2[picker_obj.mapper_position]

        if label > 0 :
            for k, v in self.lineage.mapping.iteritems() :
                if label not in v:
                    for daughter in v:
                        outline = self.outlines2.get_outline(daughter)
                        if daughter not in self.lineage.get_daughters(self.lineage.get_current_mother()) :
                            outline.outline_mode = 'full'
                        else :
                            outline.outline_mode = 'cornered'

            if label not in self.lineage.get_daughters(self.lineage.get_current_mother()) :
                self.hide = True

                # add label in the daughters list
                self.lineage.add_daughter(label)
                cid = self.lineage.get_id()
                if cid >= 0 :
                    self.mapping.cells[cid].daughters.append(int(label))

            self.outlines2.set_cornered(label)
            self.outlines2.set_visible(label)
            self.outlines2.set_color(self.color, label)
            self.new_lineage = False

    def picker_return_callback2(self, picker_obj):
        if self.picker2.mapper is None :
            return
        label = self.data2[picker_obj.mapper_position]
        if label > 0 :
            print "remove cell number = ", label

            if label in self.lineage.daughters :
                outline = self.outlines2.get_outline(label)
                if outline.outline_mode == 'cornered':
                    # self.hdata2[self.data2==label] = label
                    outline.visible = False
                    # remove label from the daughters list
                    self.lineage.remove_daughter(label)
                    cid = self.lineage.get_id()
                    if cid >= 0 :
                        self.mapping.cells[cid].daughters.remove(int(label))

    def _hide_show_cells_changed (self):
        """
        """
        for label in self.lineage.get_mothers() :
            outline1 = self.outlines1.get_outline(label)
            self.hdata1[self.hdata1 == label] = 0
            daughters = self.lineage.mapping[label]
            if self.hide :
                outline1.visible = False
                self.src1.mlab_source.scalars = self.hdata1
                for d in daughters :
                    outline2 = self.outlines2.get_outline(d)
                    outline2.visible = False
                    self.hdata2[self.hdata2 == d] = 0
                    self.src2.mlab_source.scalars = self.hdata2
            else :
                outline1.visible = True
                for d in daughters :
                    outline2 = self.outlines2.get_outline(d)
                    outline2.visible = True

                self.src1.mlab_source.scalars = self.data1
                self.src2.mlab_source.scalars = self.data2

            # for outline,label in zip(self.doutlines,self.daughters) :
            #    outline.visible = False
            #    self.hdata2[self.hdata2==label] = 0


            # self.src2.mlab_source.scalars = self.hdata2
        # else :
        #    for outline in self.moutlines :
        #        outline.visible = True
        #    for outline in self.doutlines :
        #        outline.visible = True
        #    self.src1.mlab_source.scalars = self.data1
        #    self.src2.mlab_source.scalars = self.data2

        self.hide = not(self.hide)

    def _full_outline(self, num_obj, label):
        """
        """
        if num_obj not in [1, 2]:
            return -1

        if num_obj == 1 :
            objects = self.moutlines
        else :
            objects = self.doutlines

        for o in objects :
            if o != self.moutlines[ self.lineage.mothers.index(label) ]:
                o.outline_mode = 'full'


    def _display_outline(self, num_obj, label):
        """
        """
        if num_obj not in [1, 2]:
            return -1

        if num_obj == 1 :
            objects = self.outlines1
            scene = self.scene1
        else :
            objects = self.outlines2
            scene = self.scene2

        x, y, z = objects[label - 1]

        h, s, v = (label % 360., 1., 1.)
        color = HSVtoRGB(h, s, v)
        self.colors.append(color)

        outline = scene.mlab.outline(name="%s" % label, line_width=3, color=color, figure=scene.mayavi_scene)
        outline.outline_mode = 'cornered'
        outline.bounds = (x.start, x.stop,
                            y.start, y.stop,
                            z.start, z.stop
                            )

        return outline


    # The layout of the view
    view = View(HSplit
                (VSplit(
                        Group(Item('mapping', show_label=False, style="custom"),),
                        Group(Item('hide_show_cells', show_label=False),),
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


if __name__ == '__main__':
    MyApp().configure_traits()

