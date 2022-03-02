/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  $Id: amlPymodule.h 3573 2007-09-05 16:59:56Z dufourko $
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


#ifdef _DEBUG
#undef _DEBUG
#include <Python.h>
#define _DEBUG
#else
#include <Python.h>
#endif
#include "aml/list.h"
#include "aml/array.h"
#include "aml/set.h"

/*********************************************************************************/
/************************************* AMObject **********************************/
/*********************************************************************************/

// Emulate an AML object
typedef struct
{
  PyObject_HEAD // a refcount and a pointer to a type object
  AMObj amobj;  // a real AMObj
  void* it;

  int conversion;
} AMObject;


/*********************************************************************************/
/************************************* Functions *********************************/
/*********************************************************************************/

AMObject PytoAMObject(PyObject* argobj);
bool AMObject_Check(PyObject* pobj);
bool Char_Check(PyObject* pobj);
char PyStringasChar(PyObject* pobj);
AMModel* PyTupleasSet(PyObject* pobj);
AMModel* PyListasList(PyObject* pobj);
AMModel* PyTupleasList(PyObject* pobj);
AMModel* PyTupleasArray(PyObject* pobj);
AMModel* PyListasArray(PyObject* pobj);
AMModel* PyListasSet(PyObject* pobj);
bool containsDifferentTypes(PyObject* pobj);
bool containsDoubledValues(PyObject* pobj);
PyObject* PyTuplefromList(SLList* liste);
PyObject* PyTuplefromArray(SLArray* array);
PyObject* PyListfromList(SLList* liste);
PyObject* PyListfromArray(SLArray* array);
PyObject* PyListfromSet(HashSet* set);
PyObject* PyTuplefromSet(HashSet* set);
PyObject* PyTuplefromAMObjVect(const AMObjVector& vect);
bool setMode(int mode);
int getMode();

