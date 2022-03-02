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

#include <plantgl/math/util_vector.h>
#include <plantgl/scenegraph/geometry/sor.h>
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/geometry/profile.h>
#include <plantgl/scenegraph/geometry/swung.h>
#include <plantgl/scenegraph/geometry/curve.h>
#include <plantgl/scenegraph/geometry/profile.h>
#include <plantgl/scenegraph/container/geometryarray2.h>

#include <plantgl/python/export_refcountptr.h>
#include <plantgl/python/export_property.h>
#include <plantgl/python/extract_pgl.h>
#include "export_sceneobject.h"

#include <boost/python/make_constructor.hpp>


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

#define bp boost::python

DEF_POINTEE(ProfileInterpolation)

object pi_getSectionAt(ProfileInterpolation * pi, real_t u){
    if (u < pi->getUMin() | u > pi->getUMax())
       throw PythonExc_IndexError();
    if (!pi->check_interpolation()) pi->interpol();
    if (pi->is2DInterpolMode())return object(pi->getSection2DAt(u));
    else return object(pi->getSection3DAt(u));
}

void export_ProfileInterpolation()
{
  
  class_< ProfileInterpolation, ProfileInterpolationPtr,boost::noncopyable >
    ("ProfileInterpolation",init<Curve2DArrayPtr,TOOLS(RealArrayPtr),optional<uint_t,uint_t> >
        ("ProfileInterpolation([Curve2D] profiles,[float] knotList,int degree,int stride",
		(bp::arg("profiles"),
		 bp::arg("knotList"),
		 bp::arg("degree")=ProfileInterpolation::DEFAULT_DEGREE,
		 bp::arg("stride")=ProfileInterpolation::DEFAULT_STRIDE)))
    .def("getSectionAt",&pi_getSectionAt)
    .add_property("umin",&ProfileInterpolation::getUMin)
    .add_property("umax",&ProfileInterpolation::getUMax)
	.DEC_BT_PROPERTY_WDV(degree,   ProfileInterpolation,Degree,          uint_t ,DEFAULT_DEGREE)
	.DEC_BT_PROPERTY_WDV(stride,   ProfileInterpolation,Stride,          uint_t ,DEFAULT_STRIDE)
	.DEC_PTR_PROPERTY(knotList,   ProfileInterpolation,KnotList,         RealArrayPtr)
	.DEC_PTR_PROPERTY(profileList, ProfileInterpolation,ProfileList,     Curve2DArrayPtr)
    .def("interpol",&ProfileInterpolation::interpol)
  ;
}

DEF_POINTEE(Swung)

/*
SwungPtr make_swung( boost::python::list profiles, boost::python::list angles, 
		     uchar_t slices, bool ccw, uint_t degree, uint_t stride ) 
{ 
  Curve2DArrayPtr profilearray= Curve2DArrayPtr(extract_pgllist<Curve2DArray>(profiles)());
  RealArrayPtr anglesarray= RealArrayPtr(extract_pgllist<RealArray>(angles)());
  return SwungPtr(new Swung(profilearray, anglesarray, slices, ccw, degree, stride));
}

SwungPtr make_swung5( boost::python::list profiles, boost::python::list angles, 
		     uchar_t slices, bool ccw, uint_t degree) 
{ 
	return make_swung(profiles,angles,slices,ccw,degree,Swung::DEFAULT_STRIDE);
}
 
SwungPtr make_swung4( boost::python::list profiles, boost::python::list angles, 
		     uchar_t slices, bool ccw) 
{ 
	return make_swung(profiles,angles,slices,ccw,Swung::DEFAULT_DEGREE,Swung::DEFAULT_STRIDE);
}

SwungPtr make_swung3( boost::python::list profiles, 
					  boost::python::list angles, 
					  uchar_t slices) 
{ 
	return make_swung(profiles,angles,slices,Swung::DEFAULT_CCW,Swung::DEFAULT_DEGREE,Swung::DEFAULT_STRIDE);
}

SwungPtr make_swung2( boost::python::list profiles, 
					  boost::python::list angles) 
{ 
	return make_swung(profiles,angles,Swung::DEFAULT_SLICES,Swung::DEFAULT_CCW,Swung::DEFAULT_DEGREE,Swung::DEFAULT_STRIDE);
}
*/

ProfileInterpolationPtr sw_pi(Swung * sw){ return sw->getProfileInterpolation(); }

void export_Swung()
{
    export_ProfileInterpolation();
  
  class_< Swung, SwungPtr, bases< SOR >,boost::noncopyable >
    ("Swung","A surface defined by the revolution and interpolation of several 2D profiles along Z axis.", 
	init<Curve2DArrayPtr,RealArrayPtr,optional<uchar_t,bool,uint_t,uint_t> >
	  ("Swung(profileList,angleList,slices,ccw,degree,stride)",
	  (bp::arg("profileList"),
	   bp::arg("angleList"),
	   bp::arg("slices") = SOR::DEFAULT_SLICES,
	   bp::arg("ccw")    = Swung::DEFAULT_CCW,
	   bp::arg("degree") = Swung::DEFAULT_DEGREE,
	   bp::arg("stride") = Swung::DEFAULT_STRIDE)))
/*    .def( "__init__", make_constructor( make_swung , default_call_policies(), 
                                        args("profiles","angles","slices","ccw","degree","stride")),
                     (const char *)"Swung([Curve2D] profiles,list angles [,slices,ccw,degree,stride])" ) 
    .def( "__init__", make_constructor( make_swung5, default_call_policies(), 
                                        args("profiles","angles","slices","ccw","degree") )) 
    .def( "__init__", make_constructor( make_swung4, default_call_policies(), 
                                        args("profiles","angles","slices","ccw") ) ) 
    .def( "__init__", make_constructor( make_swung3, default_call_policies(), 
                                        args("profiles","angles","slices") ) ) 
    .def( "__init__", make_constructor( make_swung2, default_call_policies(), 
                                        args("profiles","angles") )) */
    .DEF_PGLBASE(Swung)
	.DEC_BT_NR_PROPERTY_WDV(ccw,      Swung,CCW,             bool  ,DEFAULT_CCW )
	.DEC_BT_PROPERTY_WDV(degree,   Swung,Degree,          uint_t ,DEFAULT_DEGREE)
	.DEC_BT_PROPERTY_WDV(stride,   Swung,Stride,          uint_t ,DEFAULT_STRIDE)
	.DEC_PTR_PROPERTY(angleList,   Swung,AngleList,       RealArrayPtr)
	.DEC_PTR_PROPERTY(profileList, Swung,ProfileList,     Curve2DArrayPtr)
    .add_property( "interpolator",&sw_pi);
    ;

  implicitly_convertible< SwungPtr, SORPtr >();
}
