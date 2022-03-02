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

#include "cphysics/spring.h"

using namespace physics;
using namespace mechanics;

#include <boost/python.hpp>
using namespace boost::python;

void export_spring () {
	class_<Spring2D>("CSpring2D",init<>())
		;
	class_<Spring3D>("CSpring3D",init<>())
		;

	class_<LinearSpring2D, bases<Spring2D> >("CLinearSpring2D",init<int,int,double,double>())
		;
	class_<LinearSpring3D, bases<Spring3D> >("CLinearSpring3D",init<int,int,double,double>())
		;
}
