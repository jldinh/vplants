/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: amobj.h 17611 2014-10-17 13:20:41Z pradal $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */




#ifndef AMOBJ_HEADER
#define AMOBJ_HEADER

#include "tool/config.h"

#ifndef SYSTEM_IS__IRIX
#include <string.h>
#ifdef _WIN32
#  define   bzero(a,b)      memset(a,0,b)
#endif
#else // IRIX
#include <strings.h>
#endif


#include <iostream>

#ifdef STL_EXTENSION
        #include <sstream>
#else
        #include <strstream>
#endif


#include <assert.h>

#ifndef SYSTEM_IS__IRIX
#include "tool/rw_cstring.h"
#include "tool/rw_list.h"
#include "tool/rw_vector.h"
#else
#include <rw/cstring.h>
#include <rw/tvslist.h>
#include <rw/tpslist.h>
#include <rw/tvvector.h>
#endif

#include "defs.h"

#if 0
#define DEBUGREFCOUNT
#endif

typedef RWTValDlist<RWCString> StringList;
typedef RWTValDlistIterator<RWCString> StringListIter;

#ifdef _WIN32
#ifdef ERROR
#undef ERROR
#endif
#ifdef VOID
#undef VOID
#endif
#endif
#ifdef ANY
#undef ANY
#endif
struct AMObjType {

public:

  enum AMOBJTYPE {

#ifdef _WIN32
    ERROR,
    UNDEF,
    ANY,
#else
    ERROR =-2,
    UNDEF =-1,
    ANY= 0,
#endif

    BOOL,
    INTEGER,
    REAL,
    CHAR,
    DATE,
    VTX,
    MTG,
    TREEMATCHING,
    PLANTFRAME,
    LINETREE,
    VIRTUAL_PATTERN,
    DRESSING_DATA,

    FREQUENCY_DISTRIBUTION,
    DISTRIBUTION,
    DISCRETE_MIXTURE,
    DISCRETE_MIXTURE_DATA,
    CONVOLUTION,
    CONVOLUTION_DATA,
    COMPOUND,
    COMPOUND_DATA,

    VECTORS,
    REGRESSION,
    MIXTURE,
    MIXTURE_DATA,

    VECTOR_DISTANCE,

    DISTANCE_MATRIX,
    CLUSTERS,

    RENEWAL,
    RENEWAL_DATA,
    TIME_EVENTS,

    VARIABLE_ORDER_MARKOV,
    HIDDEN_VARIABLE_ORDER_MARKOV,
    VARIABLE_ORDER_MARKOV_DATA,
    SEMI_MARKOV,
    HIDDEN_SEMI_MARKOV,
    SEMI_MARKOV_DATA,
    NONHOMOGENEOUS_MARKOV,
    NONHOMOGENEOUS_MARKOV_DATA,
    SEQUENCES,
    MARKOVIAN_SEQUENCES,
    CORRELATION,

    TOPS,
    TOP_PARAMETERS,

    STRING,
    OPTION,
    VAR,

    WINDOW,
    FNODE,

    SET,
    ARRAY,
    LIST,

    ELECTRICAL_MODEL,

    OCTREE,
    MSVOXEL,
        GEOMSCENE,

    VOID



  };

AMOBJTYPE type;

public:

  AMObjType() {type = UNDEF;}
  AMObjType(const AMObjType& t) {type = t.type;}
  AMObjType(AMOBJTYPE t) {type = t;}
  AMObjType(int i) {type = (AMOBJTYPE)i;}

  AMObjType& operator=(const AMObjType& t) {if (this != &t) type = t.type; return *this;}
  AMObjType& operator=(AMOBJTYPE t) {type = t; return *this;}

  AMObjType operator&(AMObjType t) const;

  AmlBoolean operator==(const AMObjType& t) const {
    if (this == &t) return TRUE;
    else if (t.type == UNDEF || type == UNDEF) return TRUE; // UNDEF is of anytype
    else return type == t.type;
  }

  AmlBoolean operator!=(const AMObjType& t) const {return !(*this == t);}
  AmlBoolean operator==(AMOBJTYPE t) const {return type == t;}
  AmlBoolean operator!=(AMOBJTYPE t) const {return type != t;}

  AMOBJTYPE operator()() const {return type;}

  RWCString string() const;
  std::ostream& print(std::ostream& o) const;

};

class AMModel;

std::ostream& operator<<(std::ostream& o, AMObjType t);

typedef union {
  AmlBoolean b;    // BOOL
  int t;        // TYPE
  int v;        // VTX
  int i;        // INT
  unsigned long d;      // DATE
  double r;     // REAL
  char c;       // CHAR
  void* pt;     // STRING
  AMModel* p;   // pointers to models and complexe type objects such as ARRAY, SET, LIST...
} AMObjVal;


// Type checking is done both statically and dynamically:
// - statically when a function is built to catch whenever possible wrong argument types
// - dynamically whenever a function can take several argument types (polymmorphism)

struct AMObj {

  friend class AMObjTable;
  friend size_t hashAMObj(const AMObj& v);

private:

  int unionLength() const {return sizeof(val);}

public:

  AMObjType tag;
  AMObjVal val;

  AMObj() {tag = AMObjType::UNDEF; bzero((void*)&val.b, unionLength());}

  AMObj(AMObjType t)            {tag = t; bzero((void*)&val.b, unionLength());}
  AMObj(AMObjType t, int i)     {assert(t==AMObjType::INTEGER ||
                                        t==AMObjType::BOOL ||
                                        t==AMObjType::VTX);
                                 tag = t; val.i = i;}
  AMObj(AMObjType t, long l)    {assert(t==AMObjType::DATE);tag = t; val.d = l;}
  AMObj(AMObjType t, double r)  {assert(t==AMObjType::REAL);tag = t; val.r = r;}
  AMObj(AMObjType t, char c)    {assert(t==AMObjType::CHAR);
                                 tag = t; val.c = c;}
  AMObj(AMObjType t, void* pt)   {assert(t==AMObjType::UNDEF); // used only in FNode for storing PFNodes
                                 tag = t; val.pt = pt;}

  AMObj(AMObjType t, AMModel* p);

  AMObj(const AMObj& rec);

  virtual ~AMObj();

  void clearAndDestroy();

  AMObj& operator=(const AMObj& rec);

  AmlBoolean operator==(const AMObj& rec) const;
  AmlBoolean operator<(const AMObj& rec) const;

  AmlBoolean operator!=(const AMObj& rec) const {
    return !(operator==(rec));
  }

  AmlBoolean isaAMModel() const;
  int isLocked() const;

  void operator++();
  void operator--();

  std::ostream& print(std::ostream& o) const;
  std::ostream& printTag(std::ostream& o) const;
  std::ostream& printValue(std::ostream& o, int line_size = 0) const; // By default the entire object is printed

  AmlBoolean isValid() const {return tag.type != AMObjType::ERROR;}
  AMObjType type() const {return tag;}

};


struct FAMObj : public AMObj {

  StringList* arglist;

  FAMObj() {arglist=0;}
  FAMObj(AMObjType t): AMObj(t) {arglist=0;}
  FAMObj(const FAMObj& rec): AMObj(rec) {arglist = new StringList(*rec.arglist);}
  FAMObj(const AMObj& rec): AMObj(rec) {arglist = 0;}
  FAMObj(const AMObj& rec, StringList* list): AMObj(rec) {arglist = list;}

  void clearAndDestroy() {delete arglist; arglist = 0;}

  ~FAMObj() {clearAndDestroy();}

  FAMObj& operator=(const FAMObj& rec) {
    if (this != &rec) {
      AMObj::clearAndDestroy();
      clearAndDestroy();
      *(AMObj*)this = (AMObj&)rec;
      arglist = new StringList(*rec.arglist);
    }
    return *this;
  }

  // two FAMObj match whatever their arglist
  AmlBoolean operator==(const FAMObj& rec) const {
    if (this != &rec) {
      if ( *(AMObj*)this == (AMObj&)rec ){
        return TRUE;
      }
      else return FALSE;
    }
    else return TRUE;
  }

  const char* varname() const;

  std::ostream& print(std::ostream& o) const;

};

// compares types of arguments and returns TRUE if they are structurally equivalent:
AmlBoolean operator&&(const AMObj&, const AMObj&);

std::ostream& operator<<(std::ostream&, const AMObj&);
std::ostream& operator<<(std::ostream&, const FAMObj&);

typedef RWTValVector<AMObj> AMObjVector;

typedef RWTPtrDlist<FAMObj> FAMObjPtrList;
typedef RWTPtrDlistIterator<FAMObj> FAMObjPtrListIter;

typedef AMObj (*PFUN)(const AMObjVector&);

const int HASHAMOBJCONST = 100;
size_t hashAMObj(const AMObj& v);

#endif
