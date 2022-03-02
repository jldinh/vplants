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

#ifndef __CPHYSICS_MECHANICS_UTILS_H__
#define __CPHYSICS_MECHANICS_UTILS_H__

#include <vector>

#include "plantgl/math/util_vector.h"
#include "config.h"

TOOLS_USING_NAMESPACE

namespace physics {
namespace mechanics {
	struct CPHYSICS_EXPORT Particule2D {
	public:
		Vector2 pos;
		Vector2 force;
		double weight;

		Particule2D ()
			: pos(),
			  force(),
			  weight(1.) {}
		
		Particule2D (const Particule2D& p)
		    : pos(p.pos),
		      force(p.force),
		      weight(p.weight) {}
	};

	struct CPHYSICS_EXPORT Particule3D {
	public:
		Vector3 pos;
		Vector3 force;
		double weight;

		Particule3D ()
			: pos(),
			  force(),
			  weight(1.) {}
		
		Particule3D (const Particule3D& p)
		    : pos(p.pos),
		      force(p.force),
		      weight(p.weight) {}
	};

	typedef std::vector<Particule2D> P2D_list;
	typedef std::vector<Particule3D> P3D_list;
	
	void copy_particules (const P2D_list& p1, P2D_list& p2);
	void copy_particules (const P3D_list& p1, P3D_list& p2);

};//mechanics
};//physics
#endif //__CPHYSICS_MECHANICS_UTILS_H__

