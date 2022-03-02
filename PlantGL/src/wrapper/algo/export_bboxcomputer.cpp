/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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
 
#include <boost/python.hpp>

#include <plantgl/algo/base/bboxcomputer.h>
#include <plantgl/algo/base/discretizer.h>
#include <plantgl/scenegraph/geometry/boundingbox.h>
#include <plantgl/scenegraph/scene/scene.h>

/* ----------------------------------------------------------------------- */

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

/* ----------------------------------------------------------------------- */

BoundingBoxPtr d_getBBox( BBoxComputer* b )
{ return b->getBoundingBox(); }

bool p_scene( BBoxComputer * b, ScenePtr s){
	return b->process(s);
}

/* ----------------------------------------------------------------------- */

void export_BBoxComputer()
{
  class_< BBoxComputer,bases< Action >,boost::noncopyable >
    ("BBoxComputer", init<Discretizer&>("BBoxComputer() -> Compute the objects bounding box" ))
    .def("clear",&BBoxComputer::clear)
    .def("process",&p_scene)
    .add_property("boundingbox",d_getBBox,"Return the last computed Bounding Box.")
    .add_property("result",d_getBBox)
    ;
}

/* ----------------------------------------------------------------------- */
