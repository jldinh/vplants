# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.self_similarity
#
#       Copyright 2010 LaBRI
#
#       File author(s): Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#                       Frederic
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__doc__= "Example to use clustering from self_similarity package"
__docformat__ = "restructuredtext"
__license__= "Cecill-C"
__revision__= "$Id: $"


from openalea.aml import *
from openalea.plantgl.all import *
from PyQGLViewer import Quaternion, Vec

def compute_geom_parameters(pf, vtxlist, verbose = True, get_father = Father):
    """ retrieve geometrical info from a plantframe. 
        For now gives : 'Diameter' , 'Length', 'Azimuth', 'Elevation', 'Roll', 'AnchorT'
        Convert global orientation of plantframe into relative orientation. """
    if verbose : print 'Compute Diameters'
    diameters = dict([ (i , TopDiameter(pf,i)) for i in vtxlist ])
    if verbose : print 'Compute Length'
    lengths = dict([ (i , Length(pf,i)) for i in vtxlist ])

    def anchorT(pf,x):
        father = get_father(x)
        if father is None : return 1
        coord = Vector3(BottomCoord(pf,x))
        fathercoord = Vector3(BottomCoord(pf,father))
        fathertcoord = Vector3(TopCoord(pf,father))
        fatherpdir = Vector3(PDir(pf,father))
        fatherpdir.normalize()
        n = norm(fathertcoord-fathercoord)
        dcoord = coord - fathercoord
        if n == 0:
          n = 1
          if norm(dcoord) < 1e-8:
            return 1
        return dot(dcoord,fatherpdir)/n

    if verbose : print 'Compute anchorT'
    anchorTs = dict([ (i , anchorT(pf,i)) for i in vtxlist ])

    def rel_orientation(pf,x,get_father = get_father):
        father = get_father(x)
        xpdir = Vector3(PDir(pf,x))    
        xpdir.normalize()
        xsdir = Vector3(SDir(pf,x))
        xsdir.normalize()
        xdirs = Matrix3(xsdir,xpdir^xsdir,xpdir)
        assert xdirs.isValid()
        if not father is None :
            fatherpdir = Vector3(PDir(pf,father))
            if norm(fatherpdir) < 1e-5:
                while norm(fatherpdir) < 1e-5 :
                    father = get_father(father)
                    fatherpdir = Vector3(PDir(pf,father))
            fatherpdir.normalize()
            fathersdir = Vector3(SDir(pf,father))
            fathersdir.normalize()
            fatherdirs = Matrix3(fathersdir,fatherpdir^fathersdir,fatherpdir)
        else:
            fatherdirs = Matrix3()
        assert fatherdirs.isValid()
        ro =  xdirs * fatherdirs.inverse()
        if not ro.isValid():
            print x,father
            print fatherdirs
            print ro
            assert False
        xquat = Quaternion()
        xquat.setFromRotatedBasis(Vec(*ro.getColumn(0)),Vec(*ro.getColumn(1)),Vec(*ro.getColumn(2)))
        return xquat
        #r,s,t = Matrix4(ro).getTransformation()
        #return r

    if verbose : print 'Compute relative orientations'
    rel_orientations = dict([ (i , rel_orientation(pf,i)) for i in VtxList(Scale=3) ])

    def gb_orientation(pf,x):
        xpdir = Vector3(PDir(pf,x))
        xpdir.normalize()
        xsdir = Vector3(SDir(pf,x))
        xsdir.normalize()
        return xpdir,xsdir

    #if verbose : print 'Compute global orientations'
    #gb_orientations = dict([ (i , gb_orientation(pf,i)) for i in VtxList(Scale=3) ])
    
    def test(pf,x):
        xpdir = Vector3(PDir(pf,x))    
        xpdir.normalize()
        print xpdir
        xsdir = Vector3(SDir(pf,x))
        xsdir.normalize()
        print xsdir
        xdirs = Matrix3(xsdir,xpdir^xsdir,xpdir)
        print xdirs
        father = get_father(x)
        fatherpdir = Vector3(PDir(pf,father))
        fatherpdir.normalize()
        print fatherpdir
        fathersdir = Vector3(SDir(pf,father))
        fathersdir.normalize()
        print fathersdir
        fatherdirs = Matrix3(fathersdir,fatherpdir^fathersdir,fatherpdir)
        print fatherdirs
        ro =  xdirs * fatherdirs.inverse()
        print ro
        xquat = Quaternion()
        xquat.setFromRotatedBasis(Vec(*ro.getColumn(0)),Vec(*ro.getColumn(1)),Vec(*ro.getColumn(2)))
        print xquat
        h = Vec(*fatherpdir)
        u = Vec(*fathersdir)
        h = xquat*h
        u = xquat*u
        h = Vector3(*h)
        u = Vector3(*u)
        gh = xpdir
        gu = xsdir
        print x,h,gh,norm(h - gh) 
        print x,u,gu,norm(u - gu) 
        assert norm(h - gh) < 1e-3
        assert norm(u - gu) < 1e-3    
                    
    parameters = { 'Diameter' : diameters, 
                   'Length' : lengths, 
                   #'Azimuth': dict([ (i , rel_orientations[i][0]) for i in VtxList(Scale=3) ]),
                   #'Elevation': dict([ (i , rel_orientations[i][1]) for i in VtxList(Scale=3) ]),
                   #'Roll': dict([ (i , rel_orientations[i][2]) for i in VtxList(Scale=3) ]), 
                   #'GbOrientation' : gb_orientations, 
                   'QtOrientation' : rel_orientations, 
                   'AnchorT': anchorTs }
    return parameters

    
def compute_representation(root, get_parameters, get_sons = Sons, get_father = Father):
    t = PglTurtle()
    vstack = [root]
    while len(vstack) > 0:
        v = vstack.pop()
        l = get_parameters(v,'Length')
        father = get_father(v)
        if not father is None : # there is a father
            t.pop()
            lf = get_parameters(father,'Length')
            if lf > 1e-5:
                t.f(get_parameters(v,'AnchorT')*lf)
        t.setWidth(get_parameters(v,'Diameter')/2)
        if father is None : # there is a no father
            t.startGC()
        if l > 1e-5:
            q = get_parameters(v,'QtOrientation')
            #m2 = Matrix3(*q.getInverseRotationMatrix())
            #t.transform(m2)
            if True : #q.axis().norm() > 1e-5:
                h = Vec(*t.getHeading())
                u = Vec(*t.getUp())
                h = q*h
                u = q*u
                h = Vector3(*h)
                u = Vector3(*u)
                #gh = get_parameters(v,'GbOrientation')[0]
                #gu = get_parameters(v,'GbOrientation')[1]
                #assert norm(h - gh) < 1e-3
                #assert norm(u - gu) < 1e-3
                t.setHead(h,u)
            #p,s = get_parameters(v,'GbOrientation')
            #t.setHead(p,s)
        sons = get_sons(v)
        if len(sons) > 0:
            for s in sons:
                t.push()
                vstack.append(s)
        if l > 1e-5:
            t.setId(v)
            t.F(l)
    return t.getScene()
    

    
    
if __name__ == '__main__':
    mtg_filename = 'walnut.mtg'
    #mtg_filename = 'agraf-small.mtg'
    #mtg_filename = 'test.mtg'
    
    g = MTG(mtg_filename)

    # Compute an AML PlantFrame to have complete geometrical information
    def diam(x) :
        r = Feature(x,'TopDia')
        if r: return r/10
    
    #d = DressingData('agraf.drf')  
    pf = PlantFrame(1,Scale=3,TopDiameter=diam)

    # retrieve geometrical info from plantframe. For this convert orientation into relative orientation
    vtxlist = VtxList(Scale=3)
    parameters = compute_geom_parameters(pf,vtxlist)
    def get_param(v,paramname): return parameters[paramname][v]
    
    sc = compute_representation(Root(vtxlist[0]),get_param)
    Plot(pf)
    Viewer.dialog.question("Initial rep")
    Viewer.display(sc)
    
