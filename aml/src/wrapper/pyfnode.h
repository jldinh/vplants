/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  $Id: pyfnode.h 3573 2007-09-05 16:59:56Z dufourko $
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


#include <Python.h>
#include "aml/amobj.h"
#include "aml/fnode.h"


class PyFNode : public FNode
{

private:

   PyObject* _func;

public:

   // Constructors 
   PyFNode(PyObject* f,RWCString name, int argnb) : FNode(name,argnb), _func(f)  
   { }

   // Destructors
   ~PyFNode() {_func= 0;}

   // Operators
   virtual AMObj operator()(const AMObjVector& arg) const;

   // Methods
   void setFunc(PyObject* f) { _func= f; }
   PyObject* getFunc() { return _func; }

};

