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

#include "cphysics/chemistry_actor.h"
using namespace physics;
using namespace chemistry;

#include <boost/python.hpp>
using namespace boost::python;

void export_chemistry_actor () {
	class_<ChemistryActor>("CChemistryActor",init<>())
		;

	class_<Reaction, bases<ChemistryActor> >("CReaction",init<>())
		.def("set_creation",&Reaction::set_creation,"set the alpha constant on a tank")
		.def("set_decay",&Reaction::set_decay,"set the beta constant on a tank")
		;

	class_<ForwardTransport, bases<ChemistryActor> >("CForwardTransport",init<>())
		.def("add_pipe",&ForwardTransport::add_pipe,"add a new pipe between two tanks")
		;
}
