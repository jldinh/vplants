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

#include "cphysics/mass_spring_solver.h"
using namespace physics;
using namespace mechanics;

#include <boost/python.hpp>
using namespace boost::python;

double export_deform3D (MSSolver3D& solver, double dt) {
	return solver.deform(solver.particules(),dt);
}

void export_mass_spring_solver () {
	class_<MSSolver2D>("CMSSolver2D",init<>())
		.def("weight",&MSSolver2D::weight,"return point weight")
		.def("set_weight",&MSSolver2D::set_weight,"change point weight")
		.def("boundary",&MSSolver2D::boundary,"boundary")
		.def("set_boundary_function",&MSSolver2D::set_boundary_function,"set the boundary function")
		.def("add_particule",&MSSolver2D::add_particule,"add a new particule")
		.def("position",&MSSolver2D::position,"position coordinates of a particule")
		.def("set_position",&MSSolver2D::set_position,"change coordinates of a particule")
		.def("force",&MSSolver2D::force,"force applied on a particule")
		.def("set_force",&MSSolver2D::set_force,"set the force on a particule")
		.def("add_spring",&MSSolver2D::add_spring,"add a new spring")
		.def("deform",&MSSolver2D::deform,"compute deformation")
		.def("deform_to_equilibrium",&MSSolver2D::deform_to_equilibrium,"compute deformation up to equilibrium")
		;

	class_<MSSolver3D>("CMSSolver3D",init<>())
		.def("weight",&MSSolver3D::weight,"return point weight")
		.def("set_weight",&MSSolver3D::set_weight,"change point weight")
		.def("boundary",&MSSolver3D::boundary,"boundary")
		.def("set_boundary_function",&MSSolver3D::set_boundary_function,"set the boundary function")
		.def("add_particule",&MSSolver3D::add_particule,"add a new particule")
		.def("position",&MSSolver3D::position,"position coordinates of a particule")
		.def("set_position",&MSSolver3D::set_position,"change coordinates of a particule")
		.def("force",&MSSolver3D::force,"force applied on a particule")
		.def("set_force",&MSSolver3D::set_force,"set the force on a particule")
		.def("add_spring",&MSSolver3D::add_spring,"add a new spring")
		.def("deform",&export_deform3D,"compute deformation")
		.def("deform_to_equilibrium",&MSSolver3D::deform_to_equilibrium,"compute deformation up to equilibrium")
		;

	class_<ForwardEuler2D, bases<MSSolver2D> >("CForwardEuler2D",init<>())
		;
	class_<ForwardEuler3D, bases<MSSolver3D> >("CForwardEuler3D",init<>())
		;

	class_<ForwardMarching2D, bases<MSSolver2D> >("CForwardMarching2D",init<>())
		;
	class_<ForwardMarching3D, bases<MSSolver3D> >("CForwardMarching3D",init<>())
		;

}
