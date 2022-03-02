/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR Cirad/Inria/Inra Dap - Virtual Plant Team
 *
 *       File author(s): F. Boudon
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */



#include <plantgl/scenegraph/geometry/nurbspatch.h>
#include <plantgl/scenegraph/container/pointmatrix.h>
#include <plantgl/tool/util_array.h>

#include <plantgl/python/export_refcountptr.h>
#include <plantgl/python/export_property.h>
#include "export_sceneobject.h"

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

#define bp boost::python

DEF_POINTEE(NurbsPatch)

std::string np_repr( NurbsPatch* p )
{
  std::stringstream ss;
  ss << "NurbsPatch(";
  ss << extract<std::string>(str(object(p->getCtrlPoints())))();
  if (!p->isUDegreeToDefault())
      ss << ", udegree = " << p->getUDegree();
  if (!p->isVDegreeToDefault())
      ss << ", vdegree = " << p->getVDegree();
  if (!p->isUKnotListToDefault())
      ss << ", uknotList = " << extract<std::string>(str(object(p->getUKnotList())))();
  if (!p->isVKnotListToDefault())
      ss << ", vknotList = " << extract<std::string>(str(object(p->getVKnotList())))();
  if (!p->isUStrideToDefault())
      ss << ", ustride = " << p->getUStride();
  if (!p->isVStrideToDefault())
      ss << ", vstride = " << p->getVStride();
  if (!p->isCCWToDefault())
      ss << ", ccw = " << (p->getCCW()?"True":"False");
  ss << ")";
  return ss.str();
}

void export_NurbsPatch()
{
  class_< NurbsPatch, NurbsPatchPtr, bases< BezierPatch >,boost::noncopyable >
    ("NurbsPatch", 
	 // "A NURBS Patch represented by 2 degrees, 2 knot vectors and a matrix of control Points.",
    "NurbsPatch describes rational and non rational Bezier surface.\n"
	"It is defined by two degrees n and m and a matrix of control Points Pi,j\n"
	"and using the parametric equation S(u,v) = Sum(i=0,n)Sum(j=0,m)(Ri,n(u)Rj,m(v)Pi,j) with u and v in [0,1]\n"
	"where Ri,n(u) and Ri,m(v) are classical n and m-th degree rational basis function.",
	 init<const Point4MatrixPtr&, optional< RealArrayPtr, RealArrayPtr, uint_t,uint_t,uint_t,uint_t,bool> >
     ("NurbsPatch(Point4Matrix ctrlPointList, RealArray uKnotList,RealArray vKnotList [,uDeg, vDeg,ustride,vstride,ccw])"))
	 .def(init<const Point4MatrixPtr&, uint_t, optional< uint_t,RealArrayPtr, RealArrayPtr, uint_t,uint_t,bool> >
         ("NurbsPatch(Point4Matrix ctrlPointList, udegree, vdegree,"
		  "uknotList, vknotList [,ustride,vstride,ccw])",
		  (bp::arg("ctrlPointList"),
		   bp::arg("udegree") = NurbsPatch::DEFAULT_NURBS_DEGREE,
		   bp::arg("vdegree") = NurbsPatch::DEFAULT_NURBS_DEGREE,
		   bp::arg("uknotList") = TOOLS(RealArrayPtr()),
		   bp::arg("vknotList") = TOOLS(RealArrayPtr()),
		   bp::arg("ustride") = BezierPatch::DEFAULT_STRIDE,
		   bp::arg("vstride") = BezierPatch::DEFAULT_STRIDE,
		   bp::arg("ccw") = Patch::DEFAULT_CCW)))
    .DEF_PGLBASE(NurbsPatch)
     .def( "__repr__", np_repr )
    .DEC_BT_NR_PROPERTY_WD(udegree,NurbsPatch,UDegree,uint_t)
    .DEC_BT_NR_PROPERTY_WD(vdegree,NurbsPatch,VDegree,uint_t)
    .DEC_PTR_PROPERTY_WD(uknotList,NurbsPatch,UKnotList,RealArrayPtr)
    .DEC_PTR_PROPERTY_WD(vknotList,NurbsPatch,VKnotList,RealArrayPtr)
    .add_property( "firstUKnot", &NurbsPatch::getFirstUKnot )
    .add_property( "lastUKnot", &NurbsPatch::getLastUKnot )
    .add_property( "firstVKnot", &NurbsPatch::getFirstVKnot )
    .add_property( "lastVKnot", &NurbsPatch::getLastVKnot )
    .def("setVKnotListToDefault",&NurbsPatch::setVKnotListToDefault)
    .def("setUKnotListToDefault",&NurbsPatch::setUKnotListToDefault)
    .def("getUTangentAt",&NurbsPatch::getUTangentAt,bp::args("u","v"))
    .def("getVTangentAt",&NurbsPatch::getVTangentAt,bp::args("u","v"))
    .def("getNormalAt",&NurbsPatch::getNormalAt,bp::args("u","v"))
    .def("deriveAt",&NurbsPatch::deriveAt,bp::args("u","v","d","uspan","vspan"))
    .def("getDerivativeAt",&NurbsPatch::getDerivativeAt,bp::args("u","v","du","dv"),"Return the derivative at u and v. du and dv specify how many time you want to derive with respect to u and v.")
    .def("getDerivativesAt",&NurbsPatch::getDerivativesAt,bp::args("u","v"))
    ;

  implicitly_convertible< NurbsPatchPtr,BezierPatchPtr >();

}


