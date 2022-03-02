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
 *       $Id: amobj.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include <iostream>
#include <iomanip>

#include "date.h"

#include "amobj.h"
#include "amobjtable.h"
#include "global.h"
#include "fnode.h"
#include "set.h"
#include "list.h"
#include "array.h"
#include "amstring.h"

#include "tool/config.h"
#ifdef STL_EXTENSION
        #include <sstream>
#else
        #include <strstream>
#endif

#ifdef _WIN32
#define bcopy(src,dest,len) memcpy(dest,src,len)
#define bcmp memcmp
#endif

using namespace std;

RWCString AMObjType::string() const {

  RWCString stg;

  switch(type) {

  case AMObjType::ERROR:
    stg = "ERROR";
    break;
  case AMObjType::VAR:
    stg = "VAR";
    break;
  case AMObjType::ANY:
    stg = "ANY";
    break;
  case AMObjType::UNDEF:
    stg = "UNDEF";
    break;
  case AMObjType::BOOL:
    stg = "BOOL";
    break;
  case AMObjType::INTEGER:
    stg = "INT";
    break;
  case AMObjType::REAL:
    stg = "REAL";
    break;
  case AMObjType::STRING:
    stg = "STRING";
    break;
  case AMObjType::WINDOW:
    stg = "WINDOW";
    break;
  case AMObjType::OPTION:
    stg = "OPTION";
    break;
  case AMObjType::CHAR:
    stg = "CHAR";
    break;
  case AMObjType::DATE:
    stg = "DATE";
    break;
  case AMObjType::VTX:
    stg = "VTX";
    break;
  case AMObjType::FNODE:
    stg = "FUNC";
    break;
  case AMObjType::SET:
    stg = "SET";
    break;
  case AMObjType::ARRAY:
    stg = "ARRAY";
    break;
  case AMObjType::LIST:
    stg = "LIST";
    break;
  case AMObjType::MTG:
    stg = "MTG";
    break;
  case AMObjType::TREEMATCHING:
    stg = "TREEMATCHING";
    break;
  case AMObjType::PLANTFRAME:
    stg = "PLANTFRAME";
    break;
  case AMObjType::LINETREE:
    stg = "LINETREE";
    break;
  case AMObjType::VIRTUAL_PATTERN:
    stg = "VIRTUAL_PATTERN";
    break;
  case AMObjType::DRESSING_DATA:
    stg = "DRESSING_DATA";
    break;

  case AMObjType::FREQUENCY_DISTRIBUTION:
    stg = "FREQUENCY_DISTRIBUTION";
    break;
  case AMObjType::DISTRIBUTION:
    stg = "DISTRIBUTION";
    break;
  case AMObjType::DISCRETE_MIXTURE:
    stg = "DISCRETE_MIXTURE";
    break;
  case AMObjType::DISCRETE_MIXTURE_DATA:
    stg = "DISCRETE_MIXTURE_DATA";
    break;
  case AMObjType::CONVOLUTION:
    stg = "CONVOLUTION";
    break;
  case AMObjType::CONVOLUTION_DATA:
    stg = "CONVOLUTION_DATA";
    break;
  case AMObjType::COMPOUND:
    stg = "COMPOUND";
    break;
  case AMObjType::COMPOUND_DATA:
    stg = "COMPOUND_DATA";
    break;

  case AMObjType::VECTORS:
    stg = "VECTORS";
    break;
  case AMObjType::REGRESSION:
    stg = "REGRESSION";
    break;
  case AMObjType::MIXTURE:
    stg = "MIXTURE";
    break;
  case AMObjType::MIXTURE_DATA:
    stg = "MIXTURE_DATA";
    break;

  case AMObjType::VECTOR_DISTANCE:
    stg = "VECTOR_DISTANCE";
    break;

  case AMObjType::DISTANCE_MATRIX:
    stg = "DISTANCE_MATRIX";
    break;
  case AMObjType::CLUSTERS:
    stg = "CLUSTERS";
    break;

  case AMObjType::RENEWAL:
    stg = "RENEWAL";
    break;
  case AMObjType::RENEWAL_DATA:
    stg = "RENEWAL_DATA";
    break;
  case AMObjType::TIME_EVENTS:
    stg = "TIME_EVENTS";
    break;

  case AMObjType::VARIABLE_ORDER_MARKOV:
    stg = "VARIABLE_ORDER_MARKOV";
    break;
  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV:
    stg = "HIDDEN_VARIABLE_ORDER_MARKOV";
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA:
    stg = "VARIABLE_ORDER_MARKOV_DATA";
    break;
  case AMObjType::SEMI_MARKOV:
    stg = "SEMI-MARKOV";
    break;
  case AMObjType::HIDDEN_SEMI_MARKOV:
    stg = "HIDDEN_SEMI-MARKOV";
    break;
  case AMObjType::SEMI_MARKOV_DATA:
    stg = "SEMI-MARKOV_DATA";
    break;
  case AMObjType::NONHOMOGENEOUS_MARKOV:
    stg = "NONHOMOGENEOUS_MARKOV";
    break;
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA:
    stg = "NONHOMOGENEOUS_MARKOV_DATA";
    break;
  case AMObjType::SEQUENCES:
    stg = "SEQUENCES";
    break;
  case AMObjType::MARKOVIAN_SEQUENCES:
    stg = "MARKOVIAN_SEQUENCES";
    break;
  case AMObjType::CORRELATION:
    stg = "CORRELATION";
    break;

  case AMObjType::TOPS:
    stg = "TOPS";
    break;
  case AMObjType::TOP_PARAMETERS:
    stg = "TOP_PARAMETERS";
    break;

  case AMObjType::OCTREE:
    stg = "OCTREE";
    break;

  case AMObjType::MSVOXEL:
    stg = "MSVOXEL";
    break;

  case AMObjType::GEOMSCENE:
    stg = "GEOMSCENE";
    break;

  case AMObjType::ELECTRICAL_MODEL:
    stg = "ELECTRICAL_MODEL";
    break;

  case AMObjType::VOID:
    stg = "VOID";
    break;
  }
/*
  stg.prepend("(");
  stg.append(")");
*/
  return stg;

}



ostream& AMObjType::print(ostream& o) const {

  o << string().data();

  return o;

}

ostream& operator<<(ostream& o, AMObjType t) {

  return t.print(o);

}

//
// Intersection of two types:
//
// ANY is the neutral element: for any t, ANY & t = t
// UNDEF is the absorbing element: for any t, UNDEF & t = UNDEF
// An object of type UNDEF is of any type but refers to a undefined value of that type
//

AMObjType AMObjType::operator&(AMObjType t) const {

  switch(type) {

  case AMObjType::ANY:
    return t.type;

  default:
    switch(t.type) {

    case AMObjType::ANY:
      return type;
    default:
      if (type == t.type) return type;
      if (type == AMObjType::INTEGER && t.type == AMObjType::REAL) return AMObjType::REAL;
      if (type == AMObjType::REAL && t.type == AMObjType::INTEGER) return AMObjType::REAL;
      if (type == AMObjType::VTX && t.type == AMObjType::INTEGER) return AMObjType::VTX;
      if (type == AMObjType::INTEGER && t.type == AMObjType::VTX) return AMObjType::VTX;
      if (type == AMObjType::INTEGER && t.type == AMObjType::BOOL) return AMObjType::BOOL;
      if (type == AMObjType::BOOL && t.type == AMObjType::INTEGER) return AMObjType::BOOL;
      if (type == AMObjType::DATE && t.type == AMObjType::INTEGER) return AMObjType::DATE;
      if (type == AMObjType::DATE && t.type == AMObjType::DATE) return AMObjType::INTEGER;
      return AMObjType::UNDEF;

    }

  }

}


// -----------
// class AMObj
// -----------

AMObj::AMObj(AMObjType t, AMModel* p) {

  assert(t==AMObjType::OPTION ||
         t==AMObjType::VAR ||
         t==AMObjType::STRING ||

         t==AMObjType::FNODE ||
         t==AMObjType::WINDOW ||
         t==AMObjType::SET ||
         t==AMObjType::ARRAY||
         t==AMObjType::LIST ||
         t==AMObjType::MTG ||
         t==AMObjType::TREEMATCHING ||
         t==AMObjType::PLANTFRAME ||
         t==AMObjType::LINETREE ||
         t==AMObjType::VIRTUAL_PATTERN ||
         t==AMObjType::DRESSING_DATA ||

         t==AMObjType::FREQUENCY_DISTRIBUTION ||
         t==AMObjType::DISTRIBUTION ||
         t==AMObjType::DISCRETE_MIXTURE ||
         t==AMObjType::DISCRETE_MIXTURE_DATA ||
         t==AMObjType::CONVOLUTION ||
         t==AMObjType::CONVOLUTION_DATA ||
         t==AMObjType::COMPOUND ||
         t==AMObjType::COMPOUND_DATA ||

         t==AMObjType::VECTORS ||
         t==AMObjType::REGRESSION ||
         t==AMObjType::MIXTURE ||
         t==AMObjType::MIXTURE_DATA ||

         t==AMObjType::VECTOR_DISTANCE ||

         t==AMObjType::DISTANCE_MATRIX ||
         t==AMObjType::CLUSTERS ||

         t==AMObjType::RENEWAL ||
         t==AMObjType::RENEWAL_DATA ||
         t==AMObjType::TIME_EVENTS ||

         t==AMObjType::VARIABLE_ORDER_MARKOV ||
         t==AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV ||
         t==AMObjType::VARIABLE_ORDER_MARKOV_DATA ||
         t==AMObjType::SEMI_MARKOV ||
         t==AMObjType::HIDDEN_SEMI_MARKOV ||
         t==AMObjType::SEMI_MARKOV_DATA ||
         t==AMObjType::NONHOMOGENEOUS_MARKOV ||
         t==AMObjType::NONHOMOGENEOUS_MARKOV_DATA ||
         t==AMObjType::SEQUENCES ||
         t==AMObjType::MARKOVIAN_SEQUENCES ||
         t==AMObjType::CORRELATION ||

         t==AMObjType::TOPS ||
         t==AMObjType::TOP_PARAMETERS ||

         t==AMObjType::OCTREE ||
         t==AMObjType::MSVOXEL ||
         t==AMObjType::GEOMSCENE ||

         t==AMObjType::ELECTRICAL_MODEL
         );

  if (   t==AMObjType::SET) {
    if (!((Set*)p)->checkDefined())
    tag = AMObjType::UNDEF;
    else {
      tag = t;
      val.p = p;
      operator++();
    }
  }
  else if (   t==AMObjType::ARRAY) { // to make [[Undef]] = Undef
    if (!((Array*)p)->checkDefined())
    tag = AMObjType::UNDEF;
    else {
      tag = t;
      val.p = p;
      operator++();
    }
  }
  else {
    tag = t;
    val.p = p;
    operator++();
  }

}

AMObj::AMObj(const AMObj& rec) {

  tag = rec.tag;

  if (rec.isaAMModel()) {
    val.p = rec.val.p;
    operator++();
  }
  else {
    bcopy((void*)&(rec.val.b), (void*)&val.b, unionLength());
  }

}

AmlBoolean AMObj::operator==(const AMObj& rec) const {
  if (this != &rec) {
    AMObjType tmin = (tag & rec.tag);
    //cerr << tag << "&" << rec.tag << " = " << tmin << endl;
    if (tmin() != AMObjType::UNDEF) {
      switch(tmin()) {
      case AMObjType::BOOL:
        if (rec.val.b == FALSE && val.b == FALSE) return TRUE;
        if (rec.val.b == TRUE && val.b == TRUE) return TRUE;
        else return FALSE;
      case AMObjType::INTEGER:
      case AMObjType::VTX:
        if (rec.val.i == val.i) return TRUE;
        else return FALSE;
      case AMObjType::REAL:
        if (rec.val.r == val.r) return TRUE;
        else return FALSE;
      case AMObjType::CHAR:
        if (rec.val.c == val.c) return TRUE;
        else return FALSE;
      case AMObjType::DATE:
        if (rec.val.d == val.d) return TRUE;
        else return FALSE;
      case AMObjType::SET:
        if (*(Set*)rec.val.p == *(Set*)val.p) return TRUE;
        else return FALSE;
      case AMObjType::ARRAY:
        if (*(Array*)rec.val.p == *(Array*)val.p) return TRUE;
        else return FALSE;
      case AMObjType::LIST:
        if (*(List*)rec.val.p == *(List*)val.p) return TRUE;
        else return FALSE;

      case AMObjType::STRING:
      case AMObjType::OPTION:
      case AMObjType::VAR:

        if (*(AMString*)rec.val.p == *(AMString*)val.p) return TRUE;
        else return FALSE;

      case AMObjType::FNODE:
      case AMObjType::WINDOW:
      case AMObjType::MTG:
      case AMObjType::TREEMATCHING:
      case AMObjType::PLANTFRAME:
      case AMObjType::LINETREE:
      case AMObjType::VIRTUAL_PATTERN:
      case AMObjType::DRESSING_DATA:

      case AMObjType::FREQUENCY_DISTRIBUTION:
      case AMObjType::DISTRIBUTION:
      case AMObjType::DISCRETE_MIXTURE:
      case AMObjType::DISCRETE_MIXTURE_DATA:
      case AMObjType::CONVOLUTION:
      case AMObjType::CONVOLUTION_DATA:
      case AMObjType::COMPOUND:
      case AMObjType::COMPOUND_DATA:

      case AMObjType::VECTORS:
      case AMObjType::REGRESSION:
      case AMObjType::MIXTURE:
      case AMObjType::MIXTURE_DATA:

      case AMObjType::VECTOR_DISTANCE:

      case AMObjType::DISTANCE_MATRIX:
      case AMObjType::CLUSTERS:

      case AMObjType::RENEWAL:
      case AMObjType::RENEWAL_DATA:
      case AMObjType::TIME_EVENTS:

      case AMObjType::VARIABLE_ORDER_MARKOV:
      case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV:
      case AMObjType::VARIABLE_ORDER_MARKOV_DATA:
      case AMObjType::SEMI_MARKOV:
      case AMObjType::HIDDEN_SEMI_MARKOV:
      case AMObjType::SEMI_MARKOV_DATA:
      case AMObjType::NONHOMOGENEOUS_MARKOV:
      case AMObjType::NONHOMOGENEOUS_MARKOV_DATA:
      case AMObjType::SEQUENCES:
      case AMObjType::MARKOVIAN_SEQUENCES:
      case AMObjType::CORRELATION:

      case AMObjType::TOPS:
      case AMObjType::TOP_PARAMETERS:

      case AMObjType::OCTREE:
      case AMObjType::MSVOXEL:
      case AMObjType::GEOMSCENE:
      case AMObjType::ELECTRICAL_MODEL:

        if (rec.val.p == val.p) return TRUE;
        else return FALSE;
      default:
        if (bcmp(&rec.val.i, &val.i, unionLength())) return TRUE;
        else return FALSE;
      }
    }
    else {
      if (tag() == rec.tag()) return TRUE; // case Undef == Undef
      else return FALSE;
    }
  }
  else return TRUE;
}

AmlBoolean AMObj::operator<(const AMObj& rec) const {
  if (this != &rec) {
    AMObjType tmin = (tag & rec.tag);
    if (tmin() != AMObjType::UNDEF) {
      switch(tmin()) {
      case AMObjType::BOOL:
        return FALSE;
      case AMObjType::INTEGER:
      case AMObjType::VTX:
        return (val.i < rec.val.i);
      case AMObjType::REAL:
        return (val.r < rec.val.r);
      case AMObjType::CHAR:
        return (val.c < rec.val.c);
      case AMObjType::DATE:
        return (val.d < rec.val.d);
      case AMObjType::STRING:
        return (*(AMString*)val.p < *(AMString*)rec.val.p);

      default:
        return FALSE;
      }
    }
    else {
      return FALSE;
    }
  }
  else return FALSE;
}

AmlBoolean AMObj::isaAMModel() const {

    switch(tag()) {

    case AMObjType::ERROR:
    case AMObjType::UNDEF:
    case AMObjType::ANY:
    case AMObjType::BOOL:
    case AMObjType::INTEGER:
    case AMObjType::REAL:
    case AMObjType::CHAR:
    case AMObjType::DATE:
    case AMObjType::VTX:
    case AMObjType::VOID:
      return FALSE;
    default: // AMModels ...
      return TRUE;
    }

}

int AMObj::isLocked() const {

  assert(isaAMModel());
  if (val.p) return val.p->isLocked();
  else return TRUE;

}

AMObj::~AMObj() {

  clearAndDestroy();

}

void AMObj::clearAndDestroy() {

  if (isaAMModel()) --(*this);

}

AMObj& AMObj::operator=(const AMObj& rec) {

  if (this != &rec) {

    clearAndDestroy();

    tag = rec.tag;

    if (rec.isaAMModel()) {
      val.p = rec.val.p;
      ++(*this);
    }
    else {
      bcopy((void*)&(rec.val.b), (void*)&val.b, unionLength());
    }

  }

  return *this;

}

void AMObj::operator++() {
  assert(isaAMModel());

  if(val.p) {
    val.p->lock();
#ifdef DEBUGREFCOUNT
    cerr << "refcount++ (" << val.p->isLocked() << ") sur : ";
    val.p->displayOneLine(cerr);
    cerr << endl;
#endif
  }

}

void AMObj::operator--() {
  assert(isaAMModel());
  if (val.p) { // if au lieu d'un assert car a la definition les fnodes declarent des types d'arg (ex STRING) ayant une valeur nulle
    if (val.p->isLocked()) {  // should be an assert !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      val.p->unlock();
#ifdef DEBUGREFCOUNT
      cerr << "refcount-- (" << val.p->isLocked() << ") sur : ";
      val.p->displayOneLine(cerr);
#endif
      if (!val.p->isLocked()) {
#ifdef DEBUGREFCOUNT
        cerr << "=> *** Destruction *** ";
#endif
        delete val.p;
        val.p = 0;
      }
#ifdef DEBUGREFCOUNT
      cerr << endl;
#endif
    }
  }
}

ostream& AMObj::printTag(ostream& o) const {

  if (tag.type == AMObjType::ARRAY) {

    o << tag << "(";

    const AMObj* elem = ((Array*)val.p)->anElement();

    if (elem) elem->printTag(o);
    else o << "ANY";

    o << ")";
  }
  else if (tag.type == AMObjType::SET) {

    o << tag << "(";

    const AMObj* elem = ((Set*)val.p)->anElement();

    if (elem) elem->printTag(o);
    else o << "ANY";

    o << ")";
  }
  else if (tag.type == AMObjType::LIST) {

    o << tag << "(";

    ListIter* pnext = ((List*)val.p)->iterator();
    ListIter& next = *pnext;

    int begin = TRUE;

    while(next()) {

      if (begin) begin = FALSE;
      else o << ",";

      next.key().printTag(o);

    }

    delete pnext;

    o << ")";
  }
  else o << tag;

  return o;

}

ostream& AMObj::print(ostream& o) const {

  static const int LINESIZE = 200;

  if (tag.type != AMObjType::VOID) {

    //o << setiosflags(ios::left) << setw(9);

    o << "<";
    printTag(o);
    o << ">";

    o << " : ";

    printValue(o, LINESIZE);

  }

  return o;

}

ostream& AMObj::printValue(ostream& o, int line_size) const {

  switch(tag.type) {

  case AMObjType::ERROR:
    o << "Error";
    break;
  case AMObjType::ANY:
    o << "ANY";
    break;
  case AMObjType::UNDEF:
    o << "Undef";
    break;
  case AMObjType::BOOL:
    (val.b?o << "TRUE":o<<"FALSE") ;
    break;
  case AMObjType::INTEGER:
    o << val.i;
    break;
  case AMObjType::REAL:
    o << setiosflags(ios::showpoint) << val.r;
    break;
  case AMObjType::CHAR:
    o << val.c;
    break;
  case AMObjType::DATE:
    {
      FType datetype = (FType)-1;
      AMObj format;
      amobjTable()->findValue(":DateFormat", format);
      if (*(AMString*)format.val.p == "DDMM") datetype = DDMM;
      else if (*(AMString*)format.val.p == "DDMMYY") datetype = DDMMYY;
      else if (*(AMString*)format.val.p == "MMYY") datetype = MMYY;
      else if (*(AMString*)format.val.p == "DDMMTIME") datetype = DDMMTIME;
      else if (*(AMString*)format.val.p == "DDMMYYTIME") datetype = DDMMYYTIME;

      if (datetype != (FType)-1)
        o << printDate(val.d, datetype);
      else o << printDate(val.d);
    }
    break;
  case AMObjType::VTX:
    o << val.v;
    break;

  case AMObjType::STRING:
  case AMObjType::VAR:
  case AMObjType::OPTION:
    if (val.p) val.p->displayOneLine(o);
    else o << "NULL object";
    break;

  case AMObjType::FNODE:
    o << "Function";
    break;
  case AMObjType::MTG:
    if (val.p) val.p->display(o, line_size);
    else o << "NULL object";
    break;

  case AMObjType::SET:
    if (val.p) ((Set*)val.p)->display(o, line_size);
    else o << "NULL object";
    break;
  case AMObjType::ARRAY:
    if (val.p) ((Array*)val.p)->display(o, line_size);
    else o << "NULL object";
    break;
  case AMObjType::LIST:
    if (val.p) ((List*)val.p)->display(o, line_size);
    else o << "NULL object";
    break;


  case AMObjType::WINDOW:
  case AMObjType::TREEMATCHING:
  case AMObjType::PLANTFRAME:
  case AMObjType::LINETREE:
  case AMObjType::VIRTUAL_PATTERN:
  case AMObjType::DRESSING_DATA:

  case AMObjType::FREQUENCY_DISTRIBUTION:
  case AMObjType::DISTRIBUTION:
  case AMObjType::DISCRETE_MIXTURE:
  case AMObjType::DISCRETE_MIXTURE_DATA:
  case AMObjType::CONVOLUTION:
  case AMObjType::CONVOLUTION_DATA:
  case AMObjType::COMPOUND:
  case AMObjType::COMPOUND_DATA:

  case AMObjType::VECTORS:
  case AMObjType::REGRESSION:
  case AMObjType::MIXTURE:
  case AMObjType::MIXTURE_DATA:

  case AMObjType::VECTOR_DISTANCE:

  case AMObjType::DISTANCE_MATRIX:
  case AMObjType::CLUSTERS:

  case AMObjType::RENEWAL:
  case AMObjType::RENEWAL_DATA:
  case AMObjType::TIME_EVENTS:

  case AMObjType::VARIABLE_ORDER_MARKOV:
  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV:
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA:
  case AMObjType::SEMI_MARKOV:
  case AMObjType::HIDDEN_SEMI_MARKOV:
  case AMObjType::SEMI_MARKOV_DATA:
  case AMObjType::NONHOMOGENEOUS_MARKOV:
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA:
  case AMObjType::SEQUENCES:
  case AMObjType::MARKOVIAN_SEQUENCES:
  case AMObjType::CORRELATION:

  case AMObjType::TOPS:
  case AMObjType::TOP_PARAMETERS:

  case AMObjType::OCTREE:
  case AMObjType::MSVOXEL:
  case AMObjType::GEOMSCENE:
  case AMObjType::ELECTRICAL_MODEL:

#ifdef DEBUGREFCOUNT
    if (val.p) o << "(refcount=" << val.p->isLocked() << ") ";
#endif
    if (val.p) val.p->displayOneLine(o);
    else o << "NULL object";
    break;
  case AMObjType::VOID:
    o << "Void";
    break;
  }

  o << flush;

  return o;

}

// ------------
// class FAMObj
// ------------

const char* FAMObj::varname() const {

  assert(arglist);

  return arglist->first().data();

}


ostream& FAMObj::print(ostream& o) const {

  AMObj::print(o);
  o << endl;

  o << "FAMObj.arglist : ";

  if (arglist) {

    StringListIter next(*arglist);

    while(next()) {

      o << next.key() << endl;

    }

  }
  else {

    o << "None" << endl;

  }

  return o;

}


ostream& operator<<(ostream& o, const AMObj& r) {

  return r.print(o);

}

ostream& operator<<(ostream& o, const FAMObj& r) {

  return r.print(o);

}


size_t hashAMObj(const AMObj& v) {

  switch(v.tag()) {

  case AMObjType::ERROR:
  case AMObjType::VAR:
  case AMObjType::ANY:
  case AMObjType::UNDEF:
    return 0;

  case AMObjType::STRING:
  case AMObjType::OPTION:
    if (v.val.p) return ((AMString*)v.val.p)->hash();
    else return 0;

  case AMObjType::BOOL:
  case AMObjType::INTEGER:
  case AMObjType::VTX:
    return (size_t) v.val.i % HASHAMOBJCONST;

  case AMObjType::DATE:
    return (size_t) v.val.d % HASHAMOBJCONST;

  case AMObjType::CHAR:
    return (size_t) v.val.c % HASHAMOBJCONST;

  case AMObjType::REAL:
    {
#ifdef STL_EXTENSION
      stringstream tmp;
      tmp << v.val.r;
      unsigned int hashval = RWCString(tmp.str()).hash();
#else
      strstream tmp;
      tmp << v.val.r;
      char* realstg = tmp.str();
      unsigned int hashval = RWCString(realstg).hash();
      delete [] realstg;
#endif
      return hashval;
    }

  case AMObjType::SET:
    if (v.val.p) return ((Set*)v.val.p)->entries();
    else return 0;
  case AMObjType::ARRAY:
    if (v.val.p) return ((Array*)v.val.p)->entries();
    else return 0;
  case AMObjType::LIST:
    if (v.val.p) return ((List*)v.val.p)->entries();
    else return 0;

  case AMObjType::FNODE:
  case AMObjType::MTG:
  case AMObjType::WINDOW:
  case AMObjType::TREEMATCHING:
  case AMObjType::PLANTFRAME:
  case AMObjType::LINETREE:
  case AMObjType::VIRTUAL_PATTERN:
  case AMObjType::DRESSING_DATA:

  case AMObjType::FREQUENCY_DISTRIBUTION:
  case AMObjType::DISTRIBUTION:
  case AMObjType::DISCRETE_MIXTURE:
  case AMObjType::DISCRETE_MIXTURE_DATA:
  case AMObjType::CONVOLUTION:
  case AMObjType::CONVOLUTION_DATA:
  case AMObjType::COMPOUND:
  case AMObjType::COMPOUND_DATA:

  case AMObjType::VECTORS:
  case AMObjType::REGRESSION:
  case AMObjType::MIXTURE:
  case AMObjType::MIXTURE_DATA:

  case AMObjType::VECTOR_DISTANCE:

  case AMObjType::DISTANCE_MATRIX:
  case AMObjType::CLUSTERS:

  case AMObjType::RENEWAL:
  case AMObjType::RENEWAL_DATA:
  case AMObjType::TIME_EVENTS:

  case AMObjType::VARIABLE_ORDER_MARKOV:
  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV:
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA:
  case AMObjType::SEMI_MARKOV:
  case AMObjType::HIDDEN_SEMI_MARKOV:
  case AMObjType::SEMI_MARKOV_DATA:
  case AMObjType::NONHOMOGENEOUS_MARKOV:
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA:
  case AMObjType::SEQUENCES:
  case AMObjType::MARKOVIAN_SEQUENCES:
  case AMObjType::CORRELATION:

  case AMObjType::TOPS:
  case AMObjType::TOP_PARAMETERS:

  case AMObjType::OCTREE:
  case AMObjType::MSVOXEL:
  case AMObjType::GEOMSCENE:
  case AMObjType::ELECTRICAL_MODEL:

    if (v.val.p) return (size_t) v.val.p % HASHAMOBJCONST;
    else return 0;
  case AMObjType::VOID:
    return 0;
  default:
    return 0; // Should not be used
  }

}

AmlBoolean operator&&(const AMObj& x, const AMObj& y) {

  if (x.tag == y.tag) {

    if (x.tag() == AMObjType::SET) {

      if (y.tag() == AMObjType::SET) {

        assert(x.val.p);
        assert(y.val.p);

        const AMObj* p1 = ((Set*)x.val.p)->anElement();
        const AMObj* p2 = ((Set*)y.val.p)->anElement();

        if (p1 && p2) return *p1 && *p2;
        else return TRUE;

      }
      else return TRUE;

    }
    else if (x.tag() == AMObjType::ARRAY) {

      if (y.tag() == AMObjType::ARRAY) {

        assert(x.val.p);
        assert(y.val.p);

        const AMObj* p1 = ((Array*)x.val.p)->anElement();
        const AMObj* p2 = ((Array*)y.val.p)->anElement();

        if (p1 && p2) return *p1 && *p2;
        else return TRUE;

      }
      else return TRUE;

    }
    else if (x.tag() == AMObjType::LIST) {

      if (y.tag() == AMObjType::LIST) {

        assert(x.val.p);
        assert(y.val.p);

        ListIter* pnextx = ((List*)x.val.p)->iterator();
        ListIter& nextx = *pnextx;
        ListIter* pnexty = ((List*)y.val.p)->iterator();
        ListIter& nexty = *pnexty;

        int result = TRUE;

        while(nextx() && nexty()) {

          if (!(nextx.key() && nexty.key())) {

            result = FALSE;
            break;

          };

        }

        delete pnextx;
        delete pnexty;

        return result;
      }
      else return TRUE;

    }
    else if (x.tag() == AMObjType::FNODE) {

      if (y.tag() == AMObjType::FNODE) return TRUE;
      else {
        cerr << "Not yet implemented" << endl;
        return FALSE;
      }

    }
    else return TRUE; // This includes INT && UNDEF -> True

  }
  else return FALSE;

}
