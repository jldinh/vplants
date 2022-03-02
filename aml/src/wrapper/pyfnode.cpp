/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  $Id: pyfnode.cpp 3300 2007-06-08 12:51:44Z pradal $
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

//#define PyFUNC_CALL
//#define GLOBAL_TRACK

/*********************************************************************************/
/************************************* Libraries *********************************/
/*********************************************************************************/

#include "pyfnode.h"
#include "amlPymodule.h"

/*********************************************************************************/
/*********************************** Class pyfnode *******************************/
/*********************************************************************************/

// Operators
AMObj PyFNode::operator()(const AMObjVector& arg) const
  {
#ifdef GLOBAL_TRACK
    cout << " PyFNode::operator()\n";
#endif
    int mode= getMode();
    setMode(1);
    
PyObject* args = PyTuplefromAMObjVect(arg);
    PyObject* pyobj = PyObject_CallObject(_func, args);
    AMObject  amresult = PytoAMObject(pyobj);
#ifdef PyFUNC_CALL
    cout << "PyFunction called is";
    PyObject_Print(_func, stdout,0);
    cout << "\nPyFunction args is:";
    PyObject_Print(args, stdout,0);
    cout << "\nPyFunction called returns:";
    amresult.amobj.print(cout);
#endif
    setMode(mode);
    return (amresult.amobj);
  }

