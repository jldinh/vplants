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

#ifndef __CPHYSICS_SPRING_H__
#define __CPHYSICS_SPRING_H__

#include "mechanics_utils.h"

namespace physics {
namespace mechanics {
	class CPHYSICS_EXPORT Spring2D {
	public:
		Spring2D () {}

		virtual void assign_forces (P2D_list& particules) {}
	};

	class CPHYSICS_EXPORT Spring3D {
	public:
		Spring3D () {}

		virtual void assign_forces (P3D_list& particules) {}
	};

	class CPHYSICS_EXPORT LinearSpring2D : public Spring2D {
	private:
		int _pid1;
		int _pid2;
		double _stiffness;
		double _ref_length;
	public:
		LinearSpring2D (int pid1, int pid2, double stiffness, double ref_length)
			: Spring2D(),
			  _pid1(pid1),
			  _pid2(pid2),
			  _stiffness(stiffness),
			  _ref_length(ref_length) {}

		double strain (P2D_list& particules);
		double stress (P2D_list& particules);
		void assign_forces (P2D_list& particules);
	};

	class CPHYSICS_EXPORT LinearSpring3D : public Spring3D {
	private:
		int _pid1;
		int _pid2;
		double _stiffness;
		double _ref_length;
	public:
		LinearSpring3D (int pid1, int pid2, double stiffness, double ref_length)
			: Spring3D(),
			  _pid1(pid1),
			  _pid2(pid2),
			  _stiffness(stiffness),
			  _ref_length(ref_length) {}

		double strain (P3D_list& particules);
		double stress (P3D_list& particules);
		void assign_forces (P3D_list& particules);
	};

};//mechanics
};//physics
#endif //__CPHYSICS_SPRING_H__

