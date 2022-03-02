#ifndef PYTHON_PY_OSTREAMBUF_HPP
#define PYTHON_PY_OSTREAMBUF_HPP

#include <Python.h>
#include <string>
#include <streambuf>

namespace python {

struct PythonInterpreterAcquirer {
public:
    PythonInterpreterAcquirer() 
    { 
        /** It seems mandatory to acquire the GIL to call python 
            from C++ internal (during GUI process for instance) */
        gstate = PyGILState_Ensure(); 
    }
    ~PythonInterpreterAcquirer()
    { 
        PyGILState_Release(gstate); 
    }

protected:
    PyGILState_STATE gstate;
};


class py_ostreambuf : public std::streambuf
{
 private:
    PyObject* file;
    bool have_flush;

 public:
    py_ostreambuf(PyObject* file_object)
      : file( file_object)
    {
        have_flush = PyObject_HasAttrString( file, "flush");
    }
	
	

 protected:
    virtual int_type overflow( int_type c)
    {
		PythonInterpreterAcquirer a;
	PyObject* write_method = PyString_FromString( "write" );
	char cc = static_cast<char>(c);
	const char * str = std::string(&cc,1).c_str();
	PyObject* pystr = PyString_FromString(str); 
        PyObject_CallMethodObjArgs(file, write_method, pystr, NULL);
	return c;
    }

    virtual std::streamsize xsputn(const char_type* s, std::streamsize n)
    {
		PythonInterpreterAcquirer a;
        const char * str = std::string( s, n).c_str();
        PyObject* pystr = PyString_FromString(str); 
 	PyObject* write_method = PyString_FromString( "write" ); 
	PyObject_CallMethodObjArgs(file, write_method, pystr, NULL); 
        return n;
    }
    
    virtual int sync()
    {
        if (have_flush) {
	  
		PythonInterpreterAcquirer a;
		PyObject* write_method = PyString_FromString( "flush" );
		PyObject_CallMethodObjArgs(file, write_method, NULL);
        }
        return 0;
    }
};

} // !namespace python

#endif // !defined
