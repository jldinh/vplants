/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  $Id: aml.h 4123 2007-12-20 17:54:28Z dufourko $
 *
 *  ----------------------------------------------------------------------------
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *  ----------------------------------------------------------------------------
 */

/*********************************************************************************/
/************************************* Libraries *********************************/
/*********************************************************************************/

#include <string>
#include "aml/amobj.h"


/*********************************************************************************/
/************************************* Functions *********************************/
/*********************************************************************************/



std::string printErrorList();
void initAML(std::ostream* stream = 0);
bool getAMObj( const std::string& name, AMObj& amobj);

