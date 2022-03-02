/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  $Id: aml.cpp 4123 2007-12-20 17:54:28Z dufourko $
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


#include <assert.h>
#include <sstream>
#include <string>

#include "aml.h"

// required for installAMLModules()
#include "aml/install.h"
#include "aml/global.h"
#include "aml/amobjtable.h"
#include "aml/parseraml.h"


using namespace std;


/*********************************************************************************/
/********************************* Retrieve the object ***************************/
/*********************************************************************************/
bool getAMObj( const std::string& name, AMObj& amobj )
{
  AMObj obj;
  bool status= amobjTable()->findValue(name, obj);
  amobj= obj;
  return status;
} 


/*********************************************************************************/
/********************************* Retrieve AML errors ***************************/
/*********************************************************************************/
std::string printErrorList()
{
  std::stringstream oss;

  AMLErrorList* errlist= getAMLErrorList();
  assert(errlist);
  AMLErrorItemListIter next(*errlist);
  while(next())
    {
      next.key().print(oss);
    }
  errlist->clear();
  return oss.str();
}


/*********************************************************************************/
/********************** initialize modules and objects table *********************/
/*********************************************************************************/
void initAML(std::ostream * stream)
{
  // create table for functions and objects 
  createAMObjTable();
  // fill the table
  installAMLModules(); 
  initParser(stream);
}


