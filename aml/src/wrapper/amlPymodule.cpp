/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *  AMLPy package.
 *
 *  File author(s): Christophe Pradal, Cyril Bonnard
 *
 *  Implementation of the module '_amlPy' and the 'AMObj' type.
 *
 *  $Id: amlPymodule.cpp 15669 2014-02-04 16:05:56Z gbaty $
 *
  ----------------------------------------------------------------------------
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

// ACTIVE DEBUG TRACE
// #define PyFUNC_CALL
// #define ARGUMENTS
// #define GLOBAL_TRACK

/*********************************************************************************/
/************************************* Libraries *********************************/
/*********************************************************************************/

#include <sstream>

#include "py_ostreambuf.h"
#include "amlPymodule.h"
#include "pyfnode.h"
#include "aml.h"

#include "compile.h"
#include "funcobject.h"

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif


using namespace std;


/*********************************************************************************/
/************************************** GLOBAL ***********************************/
/*********************************************************************************/

static int CONVMODE=1;
std::string errormsg;

/*********************************************************************************/
/************************************ AMException ********************************/
/*********************************************************************************/

// A new exception
PyObject* amlPyException;

/*********************************************************************************/
/******************************* New PyTypeObject   ******************************/
/*********************************************************************************/

AMObject* AMObj_new(AMObj amobj, int convmode);


/*********************************************************************************/
/**********************************  AML to Py conversion ************************/
/*********************************************************************************/

PyObject* AMLtoPy(AMObj amobj)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nAMLtoPy()\n"<<std::endl;
#endif

  AMObject* amobject;
  switch(amobj.type()())
    {
    case AMObjType::SET:
      return PyListfromSet((HashSet*)amobj.val.p);
    case AMObjType::ARRAY:
      return PyListfromArray((SLArray*)amobj.val.p);
    case AMObjType::LIST:
      return PyTuplefromList((SLList*)amobj.val.p);

    case AMObjType::STRING:
      return PyString_FromString(((AMString*)amobj.val.p)->c_str());
    case AMObjType::BOOL:
      return PyBool_FromLong((long)amobj.val.i);
    case AMObjType::INTEGER:
      return PyInt_FromLong((long)amobj.val.i);
    case AMObjType::REAL:
      return PyFloat_FromDouble((double)amobj.val.r);
    case AMObjType::CHAR:
      return PyString_FromStringAndSize(&(amobj.val.c), 1);
      //    case AMObjType::DATE:
      //      return PyLong_FromUnsignedLong(amobj.val.d);
    case AMObjType::VTX:
      return PyInt_FromLong((long)amobj.val.i);
    case AMObjType::UNDEF:
    case AMObjType::VOID:
      Py_INCREF(Py_None);
      return Py_None;

    case AMObjType::ERROR:
      errormsg = printErrorList();
      PyErr_SetString(amlPyException,errormsg.c_str());
      return NULL;

    default:
      amobject = AMObj_new(amobj,0);
      PyObject* res = (PyObject*)amobject;
      return res;
    }
}

/*********************************************************************************/
/***************************  Choose the right conversion ************************/
/*********************************************************************************/

PyObject* convert(AMObj o)
{
  // CONVERSION MODE IS 1
  if (CONVMODE==1)
  {
    PyObject* pyres = AMLtoPy(o);
    return pyres;
  }
  // CONVERSION MODE IS 0
  else
  {
    AMObj amobj= o;
    switch(amobj.type()())
    {
    case AMObjType::STRING:
      return PyString_FromString(((AMString*)amobj.val.p)->c_str());
    case AMObjType::BOOL:
      return PyBool_FromLong((long)amobj.val.i);
    case AMObjType::INTEGER:
      return PyInt_FromLong((long)amobj.val.i);
    case AMObjType::REAL:
      return PyFloat_FromDouble((double)amobj.val.r);
    case AMObjType::CHAR:
      return PyString_FromStringAndSize(&(amobj.val.c), 1);
      //    case AMObjType::DATE:
      //      return PyLong_FromUnsignedLong(amobj.val.d);
    case AMObjType::VTX:
      return PyInt_FromLong((long)amobj.val.i);

    case AMObjType::ERROR:
      errormsg = printErrorList();
      PyErr_SetString(amlPyException,errormsg.c_str());
      return NULL;

    default:
      return (PyObject*) AMObj_new(o, 0);
    }
  }
}
/*********************************************************************************/
/**********************************  Py to AML conversion ************************/
/*********************************************************************************/

AMObject PytoAMObject(PyObject* argobj)
{
  AMObj amlarg;
  AMObject r;

  if ( argobj == NULL )
    {
      cerr << "NULL arg object" << endl;
      amlarg = AMObj(AMObjType::ERROR);
      return r;
    }
  if (PyBool_Check(argobj))
    {
      amlarg = AMObj(AMObjType::BOOL, (int)PyInt_AsLong(argobj));
    }
  else
  if( argobj == Py_None )
    amlarg = AMObj(AMObjType::UNDEF);
  else
  if (PyInt_Check(argobj))
    {
      amlarg = AMObj(AMObjType::INTEGER, (int)PyInt_AsLong(argobj));
    }
  else if (PyFloat_Check(argobj))
    {
      amlarg = AMObj(AMObjType::REAL, PyFloat_AsDouble(argobj));
    }
  else if (PyLong_Check(argobj))
    {
      amlarg = AMObj(AMObjType::INTEGER, PyLong_AsLong(argobj));
    }
  else if (PyString_Check(argobj))
    {
      string s = PyString_AsString(argobj);
      amlarg =  AMObj(AMObjType::STRING, new AMString(s.c_str()));
    }
  else if (Char_Check(argobj))
    {
      amlarg = AMObj(AMObjType::CHAR, PyStringasChar(argobj));
    }
  else if (PyTuple_Check(argobj))
    {
    if (containsDifferentTypes(argobj)) {
      if(containsDoubledValues(argobj))
        amlarg = AMObj(AMObjType::LIST, PyTupleasList(argobj));
      else
        amlarg = AMObj(AMObjType::SET, PyTupleasSet(argobj));
    }
    else
      amlarg = AMObj(AMObjType::ARRAY, PyTupleasArray(argobj));
    }
  else if (PyList_Check(argobj))
    {
      if (containsDifferentTypes(argobj)){
        if(containsDoubledValues(argobj))
          amlarg = AMObj(AMObjType::LIST, PyListasList(argobj));
      else
          amlarg = AMObj(AMObjType::SET, PyListasSet(argobj));
      }
      else {
        amlarg = AMObj(AMObjType::ARRAY, PyListasArray(argobj));
      }
    }
  else if (AMObject_Check(argobj))
  {
    amlarg = ((AMObject*)argobj)->amobj;
    }
  else if (PyCallable_Check(argobj))
    {
      //co->co_argcount;
      // Retrieving function name
      char* str = PyString_AsString(PyObject_Repr(argobj));
      AMString repr(str);
      std::string::size_type pos = repr.find_last_of(" ");
      AMString name(repr.substr(10,pos-13));
      // Retrieving args number
      PyObject* code = PyFunction_GetCode(argobj);
      int argsnumber = 0;
      if (PyCode_Check(code))
         {
         argsnumber = ((PyCodeObject*)code)->co_argcount;
         PyFNode* pyf= new PyFNode(argobj, name, argsnumber);
         amlarg = AMObj(AMObjType::FNODE, pyf);
         ++amlarg;
         }
      else
         {
         PyErr_BadInternalCall();
         amlarg = AMObj(AMObjType::ERROR);
         }
#ifdef PyFUNC_CALL
      //      std::cout<< "pyfnode is:"<<std::endl;
      //      std::cout << *pyf << std::endl;
      std::cout << "\nPyFunction called is:";
      std::cout << name << "\n";
#endif
    }
  else
    {
      PyErr_Clear();
      PyErr_Format(amlPyException, "Cannot convert from type '%s'",
           argobj->ob_type->tp_name);
      amlarg = AMObj(AMObjType::ERROR);
    }

  r.amobj=amlarg;
  return r;
}



/*********************************************************************************/
/***************************  Getting arguments and keywords *********************/
/*********************************************************************************/

AMObjVector * getArguments( PyObject *args, int argsnumber)
{
#ifdef GLOBAL_TRACK
  std::cout << "\ngetArguments()\n";
#endif
  AMObject amlarg;
  AMObj argamobj;
  int i;
  AMObjVector * _amobjvect = new AMObjVector(argsnumber);
  AMObjVector& amobjvect = *_amobjvect;

  //Returns the arg at position i in the tuple pointed to by args.
  for (i=0; i<argsnumber; i++)
    {
#ifdef ARGUMENTS 
      std::cout << "arg " << i << " :"<< endl;
#endif
      // get and convert arguments args from aml.function(args)
      amlarg = PytoAMObject(PyTuple_GetItem(args, i));
#ifdef ARGUMENTS
      std::cout <<"...converted\n";
      amlarg.amobj.print(std::cout);
      std::cout << endl;
#endif
      amobjvect[i] = amlarg.amobj;
    }
#ifdef ARGUMENTS
  std::cout <<"Arguments ...converted\n";
#endif
  return _amobjvect;
}

AMObjVector * getKeywords( PyObject *kwds, int kwdsnumber)
{
  AMObject kamlkwd;
  AMObject vamlkwd;

  int i;
  PyObject *kvitems = NULL;
  PyObject *kvitem  = NULL;

  AMObjVector * _amobjvect = new AMObjVector(2*kwdsnumber);
  AMObjVector& amobjvect = *_amobjvect;
  kvitems = PyMapping_Items(kwds);
#ifdef GLOBAL_TRACK
  std::cout << "\ngetKeywords()\n";
#endif
  //Returns the kwd at position j in the tuple pointed to by args.
   for (i=0; i<kwdsnumber; i++)
     {
       kvitem = PySequence_GetItem(kvitems, i);

       vamlkwd = PytoAMObject(PyTuple_GetItem(kvitem, 1));
       kamlkwd = PytoAMObject(PyTuple_GetItem(kvitem, 0));
       kamlkwd.amobj.tag = AMObjType::OPTION;
#ifdef ARGUMENTS      
       std::cout << "kwd "<< i << " :" <<std::endl;
       std::cout << "Value is:"; vamlkwd.amobj.print(std::cout); std::cout << std::endl;
       std::cout << "Key is:"; kamlkwd.amobj.print(std::cout); std::cout << std::endl;
#endif
       amobjvect[2*i] = kamlkwd.amobj;
       amobjvect[2*i+1] = vamlkwd.amobj;
     }

#ifdef ARGUMENTS
  std::cout <<"Keyword ...converted\n";
#endif
   return _amobjvect;
}




/*********************************************************************************/
/************************* Slots of AMObjType Table ******************************/
/*********************************************************************************/

// Get the the name and args of the AML function when invoking AMObj from Python
static PyObject* AMObj_call(PyObject *self, PyObject *args, PyObject *kwds)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nAMObj_call()\n";
#endif

  int argsnumber = 0;
  int kwdsnumber = 0;

  if (args)
    argsnumber = PyObject_Length(args);

  if (kwds)
    kwdsnumber = PyObject_Length(kwds);
  if ((argsnumber<0) || (kwdsnumber<0))
    return NULL;

  AMObjVector * amobjvect = NULL;
  AMObjVector * kwdsvect = NULL;

  if (args)
    amobjvect = getArguments(args, argsnumber);
  if (kwds){
    kwdsvect = getKeywords(kwds, kwdsnumber);
  }
#ifdef ARGUMENTS
  int j;
  if(amobjvect && !amobjvect->empty()){
  std::cout << "Arguments vector is:\n";
  for( j=0; j< amobjvect->size(); j++)
    {
      (*amobjvect)[j].print(std::cout);
    }
  std::cout << std::endl;
  }
  if(kwdsvect && !kwdsvect->empty()){
  std::cout << "Keywords vector is:\n";
  for( j=0; j< kwdsvect->size(); j++)
    {
      (*kwdsvect)[j].print(std::cout);
    }
  std::cout << std::endl;
  }
#endif
   if(!amobjvect || !kwdsvect)
      {
      if(!amobjvect)
         amobjvect = kwdsvect;
      }
   else 
      {
      for( AMObjVector::const_iterator _it = kwdsvect->begin();
           _it != kwdsvect->end(); _it++)
         {
         amobjvect->push_back(*_it);
         }
      delete kwdsvect;
     }

#ifdef ARGUMENTS 
  if(amobjvect){
  std::cout << "Total arguments vector is:\n";
  for(j=0; j< amobjvect->size(); j++)
    {
      (*amobjvect)[j].print(std::cout);
    }
  std::cout << std::endl;
  }
#endif

   AMObj function = ((AMObject*)self)->amobj;
   AMObj res;
   if (function.isaAMModel())
      {
      if (function.type() == AMObjType::FNODE)
         {
         FNode* fnode = (FNode*) (function.val.p);
         //call an evaluation of the corresponding aml function
         if(amobjvect)res= (*fnode)(*amobjvect);
         else res= (*fnode)(AMObjVector());
         if(amobjvect) delete amobjvect;
         if ( res.tag == AMObjType::ERROR)
            {
            errormsg = printErrorList();
            PyErr_SetString(amlPyException,errormsg.c_str());
            return NULL;
            }
         }
      else
         {
         PyErr_SetString(PyExc_ValueError, "Object entered is not a function"); 
         return NULL;
         }
      }
   else
      {
      PyErr_SetString(PyExc_ValueError, "Object entered is not a model");
      return NULL;
      }

  return convert(res);

}

/* corresponds to the tp_new slot */
static PyObject* AMObj_tpnew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nAMObj_tpnew()\n";
#endif
  PyObject *self;
  self = type->tp_alloc(type, 0);
  return self;
}

/*********************************************************************************/
/***********************************   Destruction   *****************************/
/*********************************************************************************/

// Handling deallocation when refcount=0
static void AMObj_dealloc(PyObject* self)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nAMObj_dealloc()\n";
#endif
  PyObject_Del(self);
}


/*********************************************************************************/
/*********************************   Print AMObject   ****************************/
/*********************************************************************************/

static int AMObj_print(PyObject* obj, FILE *fp, int flags)
{
  if ( PyErr_Occurred() != 0 )
    {
      PyErr_Print();
      PyErr_Clear();
    }
  else
    {
      ((AMObject*)obj)->amobj.print(std::cout) << std::endl;
      if (((AMObject*)obj)->amobj.type()== AMObjType::ERROR)
    {
    PyErr_SetString(amlPyException,errormsg.c_str());
    PyErr_Print();
    }
    }
  return 0;
}

/*********************************************************************************/
/*********************************   str AMObject   ****************************/
/*********************************************************************************/

static PyObject* AMObj_str(PyObject* obj)
{
  if ( PyErr_Occurred() != 0 )
    {
      PyErr_Print();
      PyErr_Clear();
      return PyString_FromString("");
    }

  if (((AMObject*)obj)->amobj.type()== AMObjType::ERROR)
    {
      PyErr_SetString(amlPyException,errormsg.c_str());
      PyErr_Print();
      PyErr_Clear();
      return PyString_FromString("");
    }

  std::stringstream ss;
  ((AMObject*)obj)->amobj.print(ss);

  return PyString_FromString( ss.str().c_str());

}

/*********************************************************************************/
/********************************   Compare AMObjects   **************************/
/*********************************************************************************/
static int AMObj_compare(PyObject* obj1, PyObject* obj2)
{
    int result= -1;

    if(AMObject_Check(obj1) && AMObject_Check(obj2))
      {
    if (((AMObject*)obj1)->amobj == ((AMObject*)obj2)->amobj)
      result = 0;
    else
      result = -1;
      }
    else
      {
    AMObj amobj;
    PyObject* obj;
    if(AMObject_Check(obj1))
      {
      amobj= ((AMObject*)obj1)->amobj;
      obj= obj2;
      }
    else
    if(AMObject_Check(obj2))
      {
      amobj= ((AMObject*)obj2)->amobj;
      obj= obj1;
      }
    else return -1;


    if (amobj.type()==AMObjType::UNDEF && obj==Py_None )
      return 0;
    AMObject amobj2= PytoAMObject(obj);

    if (amobj == amobj2.amobj)
      result = 0;
    else
      result = -1;
      }

    return result;
}
/*********************************************************************************/
/********************************  AMObjects Iterators  **************************/
/*********************************************************************************/
static AMObject* AMObj_getiter(AMObject* a)
{
  AMObj amobj = a->amobj;
  Py_INCREF(a);

  switch(amobj.type()())
    {
    case AMObjType::SET:
      a->it = (SetIter*)((Set*)amobj.val.p)->iterator();
      break;
    case AMObjType::ARRAY:
      a->it = (ArrayIter*)((Array*)amobj.val.p)->iterator();
      break;
    case AMObjType::LIST:
      a->it = (ListIter*)((List*)amobj.val.p)->iterator();
      break;
    default:
      PyErr_SetString(amlPyException, "Not an iterator object");
      return NULL;
    }
  return a;
}

template < class T > AMObject* nextIt( T* pnext )
{
  AMObj nextobj;
  T& next= *pnext;
  if (next())
    {
      nextobj = pnext->key();
      return AMObj_new(nextobj,0);
    }
  PyErr_SetObject(PyExc_StopIteration, Py_None);
  return NULL;
}

static AMObject* AMObj_next(AMObject* a)
{
  SetIter* pnext1;
  ArrayIter* pnext2;
  ListIter* pnext3;
  switch(a->amobj.type()())
    {
    case AMObjType::SET:
      pnext1 = (SetIter*)(a->it);
      return nextIt(pnext1);
      break;
    case AMObjType::ARRAY:
      pnext2 = (ArrayIter*)(a->it);
      return nextIt(pnext2);
      break;
    case AMObjType::LIST:
      pnext3 = (ListIter*)(a->it);
      return nextIt(pnext3);
      break;
    default:
      PyErr_SetString(amlPyException, "Not an iterator object");
      return NULL;
    }

}


/*********************************************************************************/
/****************************** AMObjectType table   *****************************/
/*********************************************************************************/
// AMObjectType table
static PyTypeObject AMObj_Type = {
  PyObject_HEAD_INIT(&PyType_Type)
  0,                    /*ob_size*/
  "AML",        /*tp_name*/
  sizeof(AMObject), /*tp_basicsize*/
  0,            /*tp_itemsize*/
  (destructor)AMObj_dealloc, /*tp_dealloc*/
  0,        /*tp_print*/
  0,
  0,
  AMObj_compare,    /*tp_compare*/
  AMObj_str,            /*tp_repr*/
  0,            /*tp_as_number*/
  0,//&Robj_as_sequence,/*tp_as_sequence*/
  0,            /*tp_as_mapping*/
  0,            /*tp_hash*/
  (ternaryfunc)AMObj_call,/*tp_call*/
  AMObj_str,              /*tp_str*/
  PyObject_GenericGetAttr,/*tp_getattro*/
  0,                      /*tp_setattro*/
  0,                      /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/*tp_flags*/
  0,                      /*tp_doc*/
  0,                      /*tp_traverse*/
  0,                      /*tp_clear*/
  0,                      /*tp_richcompare*/
  0,                      /*tp_weaklistoffset*/
  (getiterfunc)AMObj_getiter,/*tp_iter*/
  (iternextfunc)AMObj_next,/*tp_iternext*/
  0,//AMObj_methods,           /*tp_methods*/
  0,                      /*tp_members*/
  0,                      /*tp_getset*/
  0,                      /*tp_base*/
  0,                      /*tp_dict*/
  0,                      /*tp_descr_get*/
  0,                      /*tp_descr_set*/
  0,                      /*tp_dictoffset*/
  0,                      /*tp_init*/
  PyType_GenericAlloc,    /*tp_alloc*/
  AMObj_tpnew,            /*tp_new*/
  0,                      /*tp_free*/
  0,                      /*tp_is_gc*/
};


/*********************************************************************************/
/*********************************** Creation ************************************/
/*********************************************************************************/

// Creates a new AMObject
AMObject* AMObj_new(AMObj amobj, int convmode)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nAMObj_new()\n";
#endif
  AMObject* amobject;
  //allocates the memory, initializes the object, sets the refcount to one
  amobject = PyObject_New(AMObject, &AMObj_Type);
  if (!amobject)
    return NULL;

  amobject->amobj.tag = AMObjType::UNDEF;
  amobject->amobj = AMObj(amobj);
  amobject->conversion = convmode;

  return amobject;
}


/*********************************************************************************/
/************************************ Type checking ******************************/
/*********************************************************************************/

bool AMObject_Check(PyObject* pobj)
{
  if (pobj->ob_type == &AMObj_Type)
    return TRUE;
  else
    return FALSE;
}

bool Char_Check(PyObject* pobj)
{
    char *buffer;
    Py_ssize_t length;
    if(!PyString_Check(pobj))
      return FALSE;
    else if(-1==PyString_AsStringAndSize(pobj, &buffer, &length))
      return FALSE;
    else if(length!=1)
      return FALSE;
    else
      return TRUE;
}


/*********************************************************************************/
/********************************** Type conversions *****************************/
/*********************************************************************************/
char PyStringasChar(PyObject* pobj)
{
    char *buffer;
    Py_ssize_t length;
    if(!PyString_Check(pobj))
      return EOF;
    if(-1 == PyString_AsStringAndSize(pobj, &buffer, &length))
      return EOF;
    if(length!=1)
      return EOF;
    return *buffer;
}

AMModel* PyTupleasSet(PyObject* pobj)
{
  Set* set = 0;
  set = new HashSet;
  int size = PyTuple_Size(pobj);
  for(int i=0;i<size;i++)
    {
      AMObj element = (PytoAMObject(PyTuple_GetItem(pobj,i))).amobj;
      *set+=element;
    }
  return (AMModel*)set;
}
AMModel* PyTupleasArray(PyObject* pobj)
{
  Array* array = 0;
  array = new SLArray;
  int size = PyTuple_Size(pobj);
  for(int i=0;i<size;i++)
    {
      AMObj element = (PytoAMObject(PyTuple_GetItem(pobj,i))).amobj;
      *array+=element;
    }
  return (AMModel*)array;
}
AMModel* PyTupleasList(PyObject* pobj)
{
  List* list = 0;
  list = new SLList;
  int size = PyTuple_Size(pobj);
  for(int i=0;i<size;i++)
    {
      AMObj element = (PytoAMObject(PyTuple_GetItem(pobj,i))).amobj;
      *list+=element;
    }
  return (AMModel*)list;
}

AMModel* PyListasList(PyObject* pobj)
{
  List* list = 0;
  list = new SLList;
  int size = PyList_Size(pobj);
  for(int i=0; i<size; i++)
    {
      AMObj element = (PytoAMObject(PyList_GetItem(pobj,i))).amobj;
      *list+=element;
    }
  return (AMModel*)list;
}
AMModel* PyListasSet(PyObject* pobj)
{
  Set* set = 0;
  set = new HashSet;
  int size = PyList_Size(pobj);
  for(int i=0;i<size;i++)
    {
      AMObj element = (PytoAMObject(PyList_GetItem(pobj,i))).amobj;
      //printf("element n�%d\n", i);
      //element.print(cout);
      *set+=element;
    }
  return (AMModel*)set;
}
AMModel* PyListasArray(PyObject* pobj)
{
  Array* array = 0;
  array = new SLArray;
  int size = PyList_Size(pobj);
  for(int i=0;i<size;i++)
    {
      AMObj element = (PytoAMObject(PyList_GetItem(pobj,i))).amobj;
      *array+=element;
    }
  return (AMModel*)array;
}

PyObject* PyTuplefromList(SLList* liste)
{
  int len = liste->size();
  PyObject* tuple = PyTuple_New(len);
  SLListIter it = SLListIter(liste);
  int i=0;
  while (++it)
    {
      if (PyTuple_SetItem(tuple,i,AMLtoPy(it.key())))
    {
      PyErr_SetString(PyExc_ValueError, "List to Tuple conversion failed\n");
      return NULL;
    }
      i++;
    }
  return tuple;
}

PyObject* PyTuplefromArray(SLArray* array)
{
  int len = array->size();
  PyObject* tuple = PyTuple_New(len);
  for(int i=0;i<len;i++)
    {
      if (PyTuple_SetItem(tuple,i,AMLtoPy(array->at(i))))
    {
      PyErr_SetString(PyExc_ValueError, "Array to Tuple conversion failed\n");
      return NULL;
    }
    }
  return tuple;
}

PyObject* PyListfromList(SLList* liste)
{
  int len = liste->size();
  PyObject* list = PyList_New(len);
  SLListIter it = SLListIter(liste);
  int i=0;
  while (++it)
    {
      if (PyList_SetItem(list,i,AMLtoPy(it.key())))
    {
      PyErr_SetString(PyExc_ValueError, "List to Tuple conversion failed\n");
      return NULL;
    }
      i++;
    }
  return list;
}
PyObject* PyListfromArray(SLArray* array)
{
  int len = array->size();
  PyObject* list = PyList_New(len);
  for(int i=0;i<len;i++)
    {
      if (PyList_SetItem(list,i,AMLtoPy(array->at(i))))
    {
      PyErr_SetString(PyExc_ValueError, "Array to List conversion failed\n");
      return NULL;
    }
    }
  return list;
}

PyObject* PyListfromSet(HashSet* set)
{
  int len = set->size();
  HashSetIter it =  HashSetIter(set);
  PyObject* list = PyList_New(len);
  int i=0;
  while (++it)
    {
      if (PyList_SetItem(list,i,AMLtoPy(it.key())))
    {
      PyErr_SetString(PyExc_ValueError, "Set to List conversion failed\n");
      return NULL;
    }
      i++;
    }
  return list;
}

PyObject* PyTuplefromSet(HashSet* set)
{
  int len = set->size();
  HashSetIter it =  HashSetIter(set);
  PyObject* tuple = PyTuple_New(len);
  int i=0;
  while (++it)
    {
      if (PyList_SetItem(tuple,i,AMLtoPy(it.key())))
    {
      PyErr_SetString(PyExc_ValueError, "Set to List conversion failed\n");
      return NULL;
    }
      i++;
    }
  return tuple;
}

PyObject* PyTuplefromAMObjVect(const AMObjVector& vect)
{

  int len =vect.size();
  PyObject* tuple = PyTuple_New(len);
  for(int i=0;i<len;i++)
    {
      if (PyTuple_SetItem(tuple,i,AMLtoPy(vect[i])))
    {
      PyErr_SetString(PyExc_ValueError, "AMObjVect to Tuple conversion failed");
      std::cout << std::endl;
      return NULL;
    }
    }
    return tuple;
}

// assuming pobj is a python sequence
bool containsDifferentTypes(PyObject* pobj)
{
  int size = PySequence_Size(pobj);
  for(int i=0;i<size-1;i++)
    {
      if(PyObject_Compare(PyObject_Type(PySequence_GetItem(pobj,i)),
              PyObject_Type(PySequence_GetItem(pobj,i+1))))
    return TRUE;
    }
  return FALSE;

}

// assuming pobj is a python sequence
bool containsDoubledValues(PyObject* pobj)
{
  int size = PySequence_Size(pobj);
  for(int i=0;i<size-1;i++)
    {
      if(PyObject_Compare(PySequence_GetItem(pobj,i),
              PySequence_GetItem(pobj,i+1)))
    return TRUE;
    }
  return FALSE;

}

/*********************************************************************************/
/******************************* Module functions  *******************************/
/*********************************************************************************/

/* Can be called from Python: _amlPy.functionName*/

// Catch the name of the AML object, get the corresponding AML object, convert it to a
// new AMObj.

static PyObject* aml_get(PyObject *self, PyObject *args, PyObject *kwds)
{
  char* obj_str;
  AMObj amobj;

  static char *kwlist[] = {"name", 0};
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s:get", kwlist, &obj_str))
    return NULL;

  std::string funcname = ":" + std::string(obj_str);
#ifdef GLOBAL_TRACK
  std::cout << "\nget()\n";
  std::cout << funcname <<std::endl;
#endif

  //function which makes Python linked to AML
  if (!getAMObj(funcname, amobj))
    {
      PyErr_Clear();
      PyErr_Format(amlPyException, "Object%s is not an AML function",funcname.c_str());
      return NULL;
    }
  return convert(amobj);
}

bool setMode(int mode)
{
  if( mode < -1 || mode > 1 )
    return false;

  CONVMODE= mode;
  return true;
}

int getMode()
{
  return CONVMODE;
}

static PyObject* set_mode(PyObject *self, PyObject *args)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nset_mode()\n";
#endif
  int mode = -1;
  if (!PyArg_ParseTuple(args, "i:set_mode", &mode))
    return NULL;
  if (mode<-1 || mode>1)
    {
      PyErr_SetString(PyExc_ValueError, "Wrong mode");
      return NULL;
    }
  else
    CONVMODE = mode;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* get_mode(PyObject *self, PyObject *args)
{
#ifdef GLOBAL_TRACK
  std::cout << "\nget_mode()\n";
#endif
  if (!PyArg_ParseTuple(args, ":get_mode"))
    return NULL;
  return PyInt_FromLong(CONVMODE);
}

/*********************************************************************************/
/*********************  List of functions defined in the module  *****************/
/*********************************************************************************/

static PyMethodDef amlPy_methods[] =
 {
   {"get", (PyCFunction)(aml_get), METH_KEYWORDS},
   {"set_mode", (PyCFunction)set_mode, METH_VARARGS},
   {"get_mode", (PyCFunction)get_mode, METH_VARARGS},
   {NULL, NULL}
 };


//_declspec(dllexport)
/*********************************************************************************/
/********************** Initialization function for the module *******************/
/*********************************************************************************/
std::streambuf* old_cout_buf, *old_cerr_buf;


#ifdef __cplusplus
extern "C" {
#endif

void AtExit()
{
   std::cout.rdbuf(old_cout_buf);
   std::cerr.rdbuf(old_cerr_buf);
}

DL_EXPORT(void)
init_amlPymodule(void)
{
  // Redirect STDOUT
  PyObject* sys = PyImport_ImportModule("sys");
  PyObject* dict = PyModule_GetDict( sys );
  PyObject* sys_stdout = PyDict_GetItemString(dict, "stdout");
  PyObject* sys_stderr = PyDict_GetItemString(dict, "stderr");
  
  old_cout_buf = std::cout.rdbuf();
  old_cerr_buf = std::cerr.rdbuf();

  if (PyObject_HasAttrString( sys_stdout, "write")) {
    std::cout.rdbuf( new python::py_ostreambuf(sys_stdout) );
	}
  
  if (PyObject_HasAttrString( sys_stderr, "write")) {
    std::cerr.rdbuf( new python::py_ostreambuf(sys_stderr) );
	}

  std::cout << "Loading AML...";

  CONVMODE=0;
  AMObj_Type.ob_type = &PyType_Type;
  PyObject* m = Py_InitModule("_amlPymodule", amlPy_methods);

  // Retreive the module dictionnary
  PyObject* d = PyModule_GetDict(m);
  // Create the new exception
  amlPyException = PyErr_NewException("amlPy.Exception", NULL, NULL);
  if (amlPyException)
    PyDict_SetItemString(d, "AMException", amlPyException);

  // Load AML
  initAML(&std::cout);
  std::cout << "OK\n";
  
  Py_AtExit(&AtExit);
  
}

#ifdef __cplusplus
}
#endif


