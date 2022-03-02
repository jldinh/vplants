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

#include <plantgl/math/util_matrix.h>
#include <plantgl/scenegraph/geometry/boundingbox.h>

#include <plantgl/algo/base/discretizer.h>
#include <plantgl/algo/base/bboxcomputer.h>
#include <plantgl/scenegraph/geometry/geometry.h>
#include <plantgl/scenegraph/scene/scene.h>

#include <string>

#include <plantgl/python/export_refcountptr.h>
#include <plantgl/python/export_property.h>
#include "export_sceneobject.h"
#include <boost/python/make_constructor.hpp>


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;
#define bp boost::python

DEF_POINTEE(BoundingBox)

std::string bbox_str(BoundingBox * bbox){
  std::stringstream ss;
  const Vector3& v = bbox->getLowerLeftCorner();
  const Vector3& w = bbox->getUpperRightCorner();
  ss << "BoundingBox(Vector3(" << v.x() << "," << v.y() << "," << v.z() << "),Vector3(" << w.x() << "," << w.y() << "," << w.z() << "))";
  return ss.str();
}

bool contains_bbox(BoundingBox * bbox, BoundingBox * bbox2){
	return bbox->include(*bbox2);
}

bool contains_v3(BoundingBox * bbox, Vector3 v){
	return intersection(*bbox,v);
}

bool intersect_bbox(BoundingBox * bbox, BoundingBox * bbox2){
	return bbox->intersect(*bbox2);
}

void extend_bbox(BoundingBox * bbox, BoundingBox * bbox2){
	bbox->extend(*bbox2);
}

void extend_bbox_v3(BoundingBox * bbox, Vector3 v){
	bbox->extend(v);
}

real_t distance_to_bbox(BoundingBox * bbox, BoundingBox * bbox2){
	return bbox->distance(*bbox2);
}

real_t distance_to_bbox_v3(BoundingBox * bbox, Vector3 v){
	return bbox->distance(v);
}


BoundingBoxPtr  bbx_fromobj( boost::python::object o ) 
{ 
	extract<Scene> e(o);
	if(!e.check()){
		Discretizer d;
		BBoxComputer bbc(d);
		SceneObject * geom = extract<SceneObject *>(o)();
		geom->apply(bbc);
//		boost::python::call_method<bool>(o.ptr(),"apply", bbc );
		return bbc.getBoundingBox();
	}
	else {
		Discretizer d;
		BBoxComputer bbc(d);
		bbc.process(e());
		return bbc.getBoundingBox();
	}
}

void export_BoundingBox()
{
  class_< BoundingBox, BoundingBoxPtr, bases<RefCountObject> , boost::noncopyable >
    ("BoundingBox", "An axis aligned box represented by 2 opposite corners.", init< optional < const Vector3&, const Vector3& > > 
     ( "BoundingBox(Vector3 lowerLeft, Vector3 upperRight) " 
       "Constructs a BoundingBox with the 2 opposing corners lowerLeft and upperRight.",
	   (bp::arg("lowerLeft")= TOOLS(Vector3::ORIGIN),bp::arg("upperRight")=TOOLS(Vector3::ORIGIN))
	   ) )
    .def( "__init__", make_constructor( bbx_fromobj ), "BoundingBox(geometry|scene) Constructs a BoundingBox from some geometries.") 
	.DEC_CT_PROPERTY(lowerLeftCorner,BoundingBox,LowerLeftCorner,Vector3)
	.DEC_CT_PROPERTY(upperRightCorner,BoundingBox,UpperRightCorner,Vector3)
    .def("set",&BoundingBox::set,"set(lowerLeft,upperRight)")
    .def("change",&BoundingBox::change,"change(center)")
	.def("getCenter",&BoundingBox::getCenter)
	.def("getSize",&BoundingBox::getSize,
	 "size of the half diagonal of self along the x-axis, y-axis and z-axis. ")	 
    .def("getXRange",&BoundingBox::getXRange)
    .def("getYRange",&BoundingBox::getYRange)
    .def("getZRange",&BoundingBox::getZRange)
    .def("getXMin",&BoundingBox::getXMin)
    .def("getYMin",&BoundingBox::getYMin)
    .def("getZMin",&BoundingBox::getZMin)
    .def("getXMax",&BoundingBox::getXMax)
    .def("getYMax",&BoundingBox::getYMax)
    .def("getZMax",&BoundingBox::getZMax)
 	.def("__str__",&bbox_str)	 
	.def("__repr__",&bbox_str)	 
	.def("transform",(void (BoundingBox::*)(const Matrix4&))&BoundingBox::transform)
	.def("transform",(void (BoundingBox::*)(const Matrix3&))&BoundingBox::transform)
	.def("translate",&BoundingBox::translate)	 
	.def("scale",&BoundingBox::scale)	 
    .def( self == self )
    .def( self != self )
    .def( self + self )
    .def( self + other< Vector3 >() )
    .def( self | self )
    .def( self | other< Vector3 >() )
    .def( self & self )
	.def("contains",&contains_bbox)	 
	.def("contains",&contains_v3)
	.def("intersect",&intersect_bbox) 
	.def("extend",&extend_bbox) 
	.def("extend",&extend_bbox_v3) 
	.def("distance",&distance_to_bbox) 
	.def("distance",&distance_to_bbox_v3) 
    .def("getId",&RefCountObject::uid) 
	 ;

}



