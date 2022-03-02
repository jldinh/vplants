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
 *       $Id: list.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef LIST_HEADER
#define LIST_HEADER

//#include <rw/tvhset.h>

#include "fnode.h"

typedef RWTValDlist<AMObj> AMObjList; // type AMObjList has already been used elsewhere
typedef RWTValDlistIterator<AMObj> AMObjListIter;

// ------------------------
// Iterators on collections
// ------------------------

class ListIter {

public:

  virtual ~ListIter() {};

  virtual AmlBoolean operator++() = 0;
  virtual AmlBoolean operator()()  = 0;

  virtual void reset() = 0;

  virtual AMObj key() const = 0;

};


class SLListIter : public ListIter {

  AMObjListIter _next;

public:

  SLListIter(AMObjList* list) : _next(*list) {};
  virtual ~SLListIter() {}

  AMObjList* container() const {return _next.container();}

  virtual AmlBoolean operator++() {return ++_next;}
  virtual AmlBoolean operator()() {return _next();}

  virtual void reset() {_next.reset();}

  virtual AMObj key() const {return _next.key();}

};

// -----------
//    Lists
// -----------

class List : public AMModel {

protected:

  int _valid;

public:

  List() {_valid = TRUE;}
  virtual ~List() {}

  virtual int entries() const = 0;
  virtual int isValid() const {return _valid;}
  virtual ListIter* iterator() const = 0;

  virtual AmlBoolean contains(const List& list) const = 0;
  virtual AmlBoolean contains(const AMObj& obj) const = 0;
  virtual AmlBoolean operator==(const List& list) const = 0;

  virtual List& operator+=(const List*) = 0;
  virtual List& operator+=(const AMObj&) = 0;
  virtual List& operator-=(const AMObj&) = 0;

  virtual void remove(int start, int end) = 0;
  virtual void insert(int index, const AMObj&) = 0;

  virtual const AMObj head() const = 0; // an AMObj
  virtual const AMObj tail() const = 0; // a list of AMObj
  virtual int index(const AMObj&) const = 0;  // first index of an object
  virtual const AMObj at(int) const = 0;

  virtual std::ostream& display(std::ostream&, int maxbytes = 0) const;
  virtual std::ostream& displayOneLine(std::ostream&) const;

  virtual AMObj display(std::ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

class SLList : public List, public AMObjList {

public:

  SLList(): List() {}
  SLList(const List*, const PFNode*, const AMObj*);
  SLList(const SLList& list) : AMObjList(list) {}

  virtual ~SLList() {}
  virtual int entries() const {return AMObjList::entries();}

  virtual ListIter* iterator() const {return new SLListIter((AMObjList*)this);}

  virtual AmlBoolean contains(const List& list) const;
  virtual AmlBoolean contains(const AMObj& obj) const;
  virtual AmlBoolean operator==(const List& list) const;

  virtual List& operator+=(const AMObj&);
  virtual List& operator-=(const AMObj&);
  List& operator+=(const List* plist);

  virtual void remove(int start, int end);
  virtual void insert(int index, const AMObj&);

  virtual const AMObj head() const {
    if (AMObjList::entries()) return first();
    else return AMObj(AMObjType::UNDEF);
  }

  virtual const AMObj tail() const {
    if (AMObjList::entries()) {
      SLList* _tail = new SLList(*this);
      _tail->removeFirst();
      return AMObj(AMObjType::LIST, _tail);
    }
    else return AMObj(AMObjType::LIST,new SLList);
  }

  virtual int index(const AMObj& obj) const {

    if (AMObjList::entries()) {
      size_t pos = AMObjList::index(obj);
      if (pos != RW_NPOS) return pos;
      else return UNDEF;
    }
    else return UNDEF;

  }

  virtual const AMObj at(int i) const {return AMObjList::at(i);}

};


#endif
