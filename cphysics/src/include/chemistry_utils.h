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

#ifndef __CPHYSICS_CHEMISTRY_UTILS_H__
#define __CPHYSICS_CHEMISTRY_UTILS_H__

#include <vector>

#include "config.h"

namespace physics {
namespace chemistry {
	struct CPHYSICS_EXPORT Tank {
	public:
		double volume;
		double level;

		Tank ()
			: volume(0.),
			  level(0.) {}
		Tank (double volume, double level=0.)
			: volume(volume),
			  level(level) {}
	};

	typedef std::vector<Tank*> tank_list;

};//chemistry
};//physics
#endif //__CPHYSICS_CHEMISTRY_UTILS_H__

