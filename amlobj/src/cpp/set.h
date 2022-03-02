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
 *       $Id: set.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef SET_HEADER
#define SET_HEADER

//#include <rw/tvhset.h>


#include "tool/rw_hset.h"
#include "fnode.h"

typedef RWTValDlist<VId> VIdList;
typedef RWTValDlistIterator<VId> VIdListIter;

typedef RWTValHashSet<AMObj> AMObjSet;
typedef RWTValHashTableIterator<AMObj> AMObjSetIter; // an RWTValHashSet<T> is an RWTValHashTable<T>

// ------------------------
// Iterators on collections
// ------------------------

class SetIter {

public:

  virtual ~SetIter() {};

  virtual AmlBoolean operator++() = 0;
  virtual AmlBoolean operator()()  = 0;

  virtual void reset() = 0;

  virtual AMObj key() const = 0;

};


class HashSetIter : public SetIter {

  AMObjSetIter _next;

public:

  HashSetIter(AMObjSet* set) : _next(*set) {};
  virtual ~HashSetIter() {}

  RWTValHashTable<AMObj>* container() const {return _next.container();}

  virtual AmlBoolean operator++() {return ++_next;}
  virtual AmlBoolean operator()() {return _next();}

  virtual void reset() {_next.reset();}

  virtual AMObj key() const {return _next.key();}

};

// -----------
//    Sets
// -----------

class Set : public AMModel {

protected:

  AmlBoolean _state;

  AMObj* _an_element;

public:

  Set() {_an_element = 0; _state = TRUE;}
  virtual ~Set() {delete _an_element;}

  void clearAndDestroy() {if (_an_element) delete _an_element;}

  Set& operator=(const Set& set) {
    if (this != &set) {
      clearAndDestroy();
      (*(AMModel*)this) = ((AMModel&)set);
      _an_element = new AMObj(*set._an_element);
    }
    return *this;
  }

  virtual int entries() const = 0;
  virtual int isValid() const {return _state;}
  virtual SetIter* iterator() const = 0;

  virtual AmlBoolean contains(const Set& set) const = 0;
  virtual AmlBoolean contains(const AMObj& obj) const = 0;
  virtual AmlBoolean operator==(const Set& set) const = 0;

  virtual Set& operator+=(const Set*) = 0;
  virtual Set& operator+=(const AMObj&) = 0;
  virtual Set& operator-=(const AMObj&) = 0;

  const AMObj* anElement() const {return _an_element;}

  AmlBoolean checkDefined() const;

  AMObjType surfaceType() const {
    if (_an_element) return _an_element->tag();
    else return AMObjType::ANY;
  }
  AmlBoolean matchesSetType(const AMObj& obj) const {
    if (_an_element) return obj && (*_an_element);
    else return TRUE; // the set is empty and any type matches the set type
  }

  virtual std::ostream& display(std::ostream&, int maxbytes = 0) const;
  virtual std::ostream& displayOneLine(std::ostream&) const;
  virtual AMObj display(std::ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

class HashSet : public Set, public AMObjSet {

  int saveWrite(const AMObj& set, const char* prefix) const;

public:

  HashSet() : AMObjSet(hashAMObj, HASHAMOBJCONST) {}
  HashSet(const VIdList*);
  HashSet(const Set*, const PFNode*, const AMObj*);
  HashSet(const HashSet& set) : Set(), AMObjSet(set) { }
  virtual ~HashSet() {}

  virtual int entries() const {return AMObjSet::entries();}
  virtual SetIter* iterator() const {return new HashSetIter((AMObjSet*)this);}

  virtual AmlBoolean contains(const Set& set) const;
  virtual AmlBoolean contains(const AMObj& obj) const;
  virtual AmlBoolean operator==(const Set& set) const;

  virtual Set& operator+=(const AMObj&);
  virtual Set& operator+=(const Set* pset);
  virtual Set& operator-=(const AMObj&);

  virtual AMObj save(const AMObjVector& args) const;
};


#endif
