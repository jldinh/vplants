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

#include <plantgl/scenegraph/function/function.h>

#include <plantgl/python/export_refcountptr.h>
#include <plantgl/python/export_property.h>
#include "export_sceneobject.h"
#include <plantgl/python/export_list.h>
#include <plantgl/python/exception.h>


using namespace boost::python;

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

DEF_POINTEE(QuantisedFunction)

object func_findX(QuantisedFunction * func, real_t y)
{
    bool found = false;
    real_t x = func->findX(y,found);
    if (!found) return object();
    else return object(x);
}

object func_findX2(QuantisedFunction * func, real_t y, real_t startingx)
{
    bool found = false;
    real_t x = func->findX(y,found,startingx);
    if (!found) return object();
    else return object(x);
}

real_t Func_getValue(QuantisedFunction * func, real_t x)
{
   if (func->getClamped() && (func->getFirstX() > x  || x > func->getLastX()))
      throw PythonExc_IndexError();
   else return func->getValue(x);
}

object Func_getSamples(QuantisedFunction * func)
{ return make_list(func->getSamples())(); }

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(isMonotonous_overloads, isMonotonous, 0, 1)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(isIncreasing_overloads, isIncreasing, 0, 1)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(isDecreasing_overloads, isDecreasing, 0, 1)

void export_Function()
{
  class_< QuantisedFunction, QuantisedFunctionPtr, boost::noncopyable >
    ("QuantisedFunction","A 2D quantised injective function (homomorphism) defined on the range [firstx,lastx].", init<const Curve2DPtr& , optional<uint_t> >
     (args("curve","sampling"),
     "QuantisedFunction(curve[,sampling,clamped]) : Quantised 2D function.\n"
     "If clamped parameter is set to False, if a x value is out of range, first or last value is returned.\n"
     "Otherwise an exception is raised."))
      .def(init<const Point2ArrayPtr& , optional<uint_t> >(args("points","sampling"),"Function(points [,sampling])"))
      // .def(init<const Point2ArrayPtr& , optional<uint_t> >())
      .def("__call__",&Func_getValue,args("x"))
      .def("getValue",&Func_getValue,args("x"))
      .def("findX",&func_findX,args("y"))
      .def("findX",&func_findX2,args("y","startingX"),"findX(y[,startingX]) : find the first x value such as f(x) = y.")
      .def("isMonotonous",&QuantisedFunction::isMonotonous,isMonotonous_overloads())
      .def("isIncreasing",&QuantisedFunction::isIncreasing,isIncreasing_overloads())
      .def("isDecreasing",&QuantisedFunction::isDecreasing,isDecreasing_overloads())
      .def("isValid",&QuantisedFunction::isValid)
      .def("inverse",&QuantisedFunction::inverse)
      .def("build",(bool(QuantisedFunction::*)(const Curve2DPtr&, uint_t))&QuantisedFunction::build,args("curve","sampling"))
      .def("build",(bool(QuantisedFunction::*)(const Curve2DPtr&))&QuantisedFunction::build)
      .add_property("sampling",&QuantisedFunction::getSampling)
      .add_static_property("DEFAULT_SAMPLING",make_getter(&QuantisedFunction::DEFAULT_SAMPLING))
      .add_property("firstx",&QuantisedFunction::getFirstX)
      .add_property("lastx",&QuantisedFunction::getLastX)
      .DEC_BT_NR_PROPERTY_WDV(clamped,QuantisedFunction,Clamped,bool,DEFAULT_CLAMPED)
      .def("_getSamples",&Func_getSamples)
      .def("checkQuantisableFunction",&QuantisedFunction::check)
      .staticmethod("checkQuantisableFunction");
    ;

  // implicitly_convertible< FontPtr, SceneObjectPtr >();
}
