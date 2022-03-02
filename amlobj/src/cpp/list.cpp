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
 *       $Id: list.cpp 17611 2014-10-17 13:20:41Z pradal $
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

#include "list.h"

#include "array.h"
#include "kernel_err.h"

#define min(x,y) ((x<y)?(x):(y))

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Kernel"

using namespace std;

ostream& List::display(ostream& o, int maxbytes) const {

  if (!maxbytes) return displayOneLine(o);

  ListIter* pnext = iterator();
  ListIter& next = *pnext;

  if (maxbytes < 5) maxbytes = 5;

  int nbel = entries();

  // Computes the number of bytes allocated to one element

  int commas = nbel?nbel-1:0; // nb of commas used in the expression
  int fillchars = 5; // to account for chars : '[' '...' and ']'

  int reserved = fillchars + commas;
  int available = maxbytes - reserved;

  if (available < 0) available = 0;

  int elem_size = nbel?available/nbel:0;

#ifndef STL_EXTENSION
  char* tmp = new char[maxbytes+1];
  for (int h=0;h<=maxbytes;h++) tmp[h]=0;
  ostrstream os(tmp,maxbytes);
#else
  ostringstream os;
#endif
  
  o << "[" ;

  int first = TRUE;

  while(next()) {

    if (!first) os << ",";
    else first = FALSE;

    next.key().printValue(os, elem_size);

  }

  delete pnext;

#ifndef STL_EXTENSION
  RWCString elemstg(tmp,min(strlen(tmp),maxbytes));
#else
  RWCString elemstg= string(os.str(), 0,maxbytes);
#endif  
/*
  cerr << "tmp       = " << tmp << endl;
  cerr << "maxbytes = " << maxbytes << endl;
  cerr << "elemstg   = " << elemstg << endl;
  cerr << "elemstg.ln= " << elemstg.length() << endl;
*/
  if ( int( elemstg.length() ) >= maxbytes-2) { // -2 for '[' and ']'

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


ostream& List::displayOneLine(ostream& o) const {

  ListIter* pnext = iterator();
  ListIter& next = *pnext;

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

SLList::SLList(const List* list, const PFNode* pred, const AMObj* arg) {

  ListIter* pnext = list->iterator();
  ListIter& next = *pnext;

  AMObj obj;
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
      _valid = FALSE;
      break;

    }
    else if (obj.tag() != AMObjType::VOID) {
      AMObjList::insert(obj);
    }

    k++;

  }

  delete pnext;

}


AmlBoolean SLList::contains(const AMObj& obj) const {

  return AMObjList::contains(obj);

}

AmlBoolean SLList::contains(const List& list) const {

  AmlBoolean result = TRUE;

  ListIter* pnext = list.iterator();
  ListIter& next = *pnext;

  while(next()) {

    if (!AMObjList::contains(next.key())) {
      result = FALSE;
      break;
    }

  }

  delete pnext;

  return result;

}

AmlBoolean SLList::operator==(const List& list) const {

  if (list.entries() != entries()) return FALSE;

  AmlBoolean result = TRUE;

  ListIter* pnext = iterator();
  ListIter* pnext2 = list.iterator();
  ListIter& next = *pnext;
  ListIter& next2 = *pnext2;

  while(next() && next2()) {

    if (next.key() != next2.key()) {
      result = FALSE;
      break;
    }

  }

  delete pnext;
  delete pnext2;

  return result;

}


List& SLList::operator+=(const AMObj& obj) {

  AMObjList::insert(obj);

  return *this;

}

List& SLList::operator-=(const AMObj& obj) {

  AMObjList::remove(obj);

  return *this;

}

List& SLList::operator+=(const List* plist) {

  assert(plist);

  ListIter* pnext = plist->iterator();
  ListIter& next = *pnext;

  while(next()) {

    AMObjList::insert(next.key());

  }

  delete pnext;

  return *this;

}

void SLList::remove(int start, int end) {

  assert(start>=0);
  assert(end>=start);
  assert(end<entries());

#ifdef RWOUT
  removeIn(start,end);
#else
  for (int i=start; i<=end; i++) {

    removeAt(i);

  }
#endif

}

void SLList::insert(int index, const AMObj& val) {

  assert(index>=0);
  assert(index<entries());

  insertAt(index, val);

}
