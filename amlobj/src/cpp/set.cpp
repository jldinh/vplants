
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
 *       $Id: set.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include "tool/config.h"
#ifdef STL_EXTENSION
        #include <sstream>
#else
        #include <strstream>
#endif

#include "set.h"

#include "array.h"
#include "kernel_err.h"

#define min(x,y) ((x<y)?(x):(y))

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Kernel"

using namespace std;

ostream& Set::display(ostream& o, int maxbytes) const {

  if (!maxbytes) return displayOneLine(o);

  SetIter* pnext = iterator();
  SetIter& next = *pnext;

  if (maxbytes < 5) maxbytes = 5;

  int nbel = entries();

  // Computes the number of bytes allocated to one element

  int commas = nbel?nbel-1:0; // nb of commas used in the expression
  int fillchars = 5; // to account for chars : '[' '...' and ']'

  int reserved = fillchars + commas;
  int available = maxbytes - reserved;

  if (available < 0) available = 0;

  int elem_size = nbel?available/nbel:0;

#ifdef STL_EXTENSION
  ostringstream os;
#else
  ostrstream os;
#endif

  o << "[" ;

  int first = TRUE;

  while(next()) {

    if (!first) os << ",";
    else first = FALSE;

    next.key().printValue(os, elem_size);

  }

  delete pnext;
  os << ends;

#ifdef STL_EXTENSION
  RWCString elemstg= string(os.str(),0,maxbytes);

#else
  char* tmp = os.str();

  RWCString elemstg(tmp,min(strlen(tmp),maxbytes));
  elemstg[min(strlen(tmp),maxbytes)] = '\0';
#endif
/*
  cerr << "tmp       = " << tmp << endl;
  cerr << "maxbytes = " << maxbytes << endl;
  cerr << "elemstg   = " << elemstg << endl;
  cerr << "elemstg.ln= " << elemstg.length() << endl;
*/
  if (elemstg.length() >= maxbytes-2) { // -2 for '[' and ']'

    if (maxbytes-fillchars >=0) {
      elemstg.remove(maxbytes-fillchars); // '[' "..." and ']'
    }
    elemstg.append("...");

  }

  o << elemstg;

  o << "]" ;

#ifndef STL_EXTENSION
  delete [] tmp;
#endif
  return o;

}

ostream& Set::displayOneLine(ostream& o) const {

  SetIter* pnext = iterator();
  SetIter& next = *pnext;

  o << "[" ;

  int first = TRUE;

  while(next()) {

    if (!first) o << ",";
    else first = FALSE;

    next.key().printValue(o);

  }

  delete pnext;

  o << "]" ;

  return o;

}

AmlBoolean Set::checkDefined() const {
  if (surfaceType() == AMObjType::ARRAY) {
    return ((Array*)(_an_element->val.p))->checkDefined();
  }
  else if (surfaceType() == AMObjType::SET) {
    return ((Set*)(_an_element->val.p))->checkDefined();
  }
  else if (surfaceType() == AMObjType::UNDEF) return FALSE;
  else return TRUE;
}



HashSet::HashSet(const VIdList* list) : AMObjSet(hashAMObj, HASHAMOBJCONST) {

  VIdListIter next(*(VIdList*)list);

  while (next()) {

    if (!_an_element) _an_element = new AMObj(AMObjType::VTX,next.key());

    this->AMObjSet::insert(AMObj(AMObjType::VTX,next.key()));

  }

}

HashSet::HashSet(const Set* set, const PFNode* pred, const AMObj* arg) : AMObjSet(hashAMObj, HASHAMOBJCONST) {

  SetIter* pnext = set->iterator();
  SetIter& next = *pnext;

  AMObj obj(set->surfaceType());
  AMObjVector predarglist(pred->argNb());

  int k = 0;

  while(next()) {

    obj = next.key();

    for (register int j=0; j<pred->argNb(); j++) {

      if (pred->argRef(j) == -1) {
        predarglist[j] = obj;
      }
      else {
        predarglist[j] = arg[pred->argRef(j)];
      }

    }

    obj = (*(pred->fnode()))(predarglist);


    if (obj.tag() == AMObjType::ERROR) {

      genAMLError(ERRORMSG(K_ITER_EVAL_ERR_sd), (const char*)(pred->fnode()->name()), k+1);
      delete _an_element;
      _an_element = 0;
      _state = FALSE;
      break;

    }
    else if (obj.tag() != AMObjType::VOID) {
      if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(obj);
      if (_an_element->tag == obj.tag) AMObjSet::insert(obj);
      else {

        genAMLError(ERRORMSG(K_ITER_EVAL_ERR_sd), (const char*)(pred->fnode()->name()), k+1);
        delete _an_element;
        _an_element = 0;
        _state = FALSE;
        break;

      }

     }

    k++;

  }

  delete pnext;

}

AmlBoolean HashSet::contains(const AMObj& obj) const {

  return AMObjSet::contains(obj);

}

AmlBoolean HashSet::contains(const Set& set) const {

  AmlBoolean result = TRUE;

  SetIter* pnext = set.iterator();
  SetIter& next = *pnext;

  while(next()) {

    if (!AMObjSet::contains(next.key())) {
      result = FALSE;
      break;
    }

  }

  delete pnext;

  return result;

}

AmlBoolean HashSet::operator==(const Set& set) const {

  if (contains(set) && set.contains(*this)) return TRUE;
  else return FALSE;

}

Set& HashSet::operator+=(const AMObj& obj) {

  if (matchesSetType(obj)) {
    AMObjSet::insert(obj);
    if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(obj);
  }

  return *this;

}

Set& HashSet::operator-=(const AMObj& obj) {

  if (matchesSetType(obj)) {
    AMObjSet::remove(obj);
    if (!AMObjSet::entries()) {
      delete _an_element;
      _an_element = 0;
    }
  }

  return *this;
}

Set& HashSet::operator+=(const Set* pset) {

  assert(pset);

  if (pset->anElement()) {

    SetIter* pnext = pset->iterator();
    SetIter& next = *pnext;

    if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(*(pset->anElement())); // if the current set is empty;

    while(next()) {

      AMObjSet::insert(next.key());

    }

    delete pnext;

  }

  return *this;

}

AMObj HashSet::save(const AMObjVector& args) const {

  int len = args.length();

  const char *fileprefix;

  // 2 arguments obligatoires

  CHECKCONDVA(len >= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Save" , 2));

  CHECKCONDVA(args[0].tag() == AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 1, args[0].tag.string().data(), "SET"));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Save", 2, args[1].tag.string().data(), "STRING"));

  fileprefix = ((AMString*)(args[1].val.p))->data();

  CHECKCONDVA(strlen(fileprefix) != 0,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "Save", 2, "an empty string"));



  SLArray* array = new SLArray((Set*)args[0].val.p);

  // On transforme le SET en array pour les besoins de l'impression

  AMObjVector args2 = args;

  args2[0] = AMObj(AMObjType::ARRAY, array);

  array->save(args2);

  return AMObj(AMObjType::VOID);

}
