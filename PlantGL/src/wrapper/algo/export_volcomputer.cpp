/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon, DDS et al.
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

#include <plantgl/algo/base/volcomputer.h>
#include <plantgl/algo/base/discretizer.h>
#include <plantgl/scenegraph/scene/scene.h>

/* ----------------------------------------------------------------------- */

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

/* ----------------------------------------------------------------------- */

real_t vol_geom(Geometry * obj){
    Discretizer d;
    VolComputer sf(d);
    obj->apply(sf);
	return sf.getVolume();
}

real_t vol_sh(Shape * obj){
    Discretizer d;
    VolComputer sf(d);
    obj->apply(sf);
	return sf.getVolume();
}

/* ----------------------------------------------------------------------- */

void export_VolComputer()
{
  class_< VolComputer, bases<Action>, boost::noncopyable >
    ("VolComputer", init<Discretizer&>("VolComputer() -> compute the object volume"))
    .def("process", (bool (VolComputer::*)(const ScenePtr))&VolComputer::process) 
    .add_property("volume", &VolComputer::getVolume, "Return the volume of the shape")
    .add_property("result",  &VolComputer::getVolume)
    ;
  def("volume",(real_t(*)(const ScenePtr))&sceneVolume,"Compute volume of a scene");
  def("volume",&vol_geom,"Compute volume of a geometry");
  def("volume",&vol_sh,"Compute volume of a shape");

}
