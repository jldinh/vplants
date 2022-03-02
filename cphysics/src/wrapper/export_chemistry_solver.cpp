/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.container: utils package                                     
 *                                                                              
 *        Copyright 2006 INRIA - CIRAD - INRA                      
 *                                                                              
 *        File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>         
 *                                                                              
 *        Distributed under the Cecill-C License.                               
 *        See accompanying file LICENSE.txt or copy at                          
 *            http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html       
 *                                                                              
 *        OpenAlea WebSite : http://openalea.gforge.inria.fr                    
 *       
 *                                                                       
 *-----------------------------------------------------------------------------*/

#include "cphysics/chemistry_solver.h"
using namespace physics;
using namespace chemistry;

#include <boost/python.hpp>
using namespace boost::python;

void export_chemistry_solver () {
	class_<ForwardEuler>("CCForwardEuler",init<>())
		.def("volume",&ForwardEuler::volume,"return tank volume")
		.def("set_volume",&ForwardEuler::set_volume,"change tank volume")
		.def("level",&ForwardEuler::level,"return tank level")
		.def("set_level",&ForwardEuler::set_level,"change tank level")
		.def("set_boundary_function",&ForwardEuler::set_boundary_function,"set the boundary function")
		.def("boundary",&ForwardEuler::boundary,"boundary")
		.def("add_tank",&ForwardEuler::add_tank,"add a new tank")
		.def("add_actor",&ForwardEuler::add_actor,"add a new actor")
		.def("react",&ForwardEuler::react,"compute reactions")
		;
}
