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
 *       $Id: array.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef ARRAY_HEADER
#define ARRAY_HEADER


extern const char *Plot_prefix;
extern const char* SYSTEMCHAR; // prefix of all system command names

#include <fstream>

#include "set.h"
#include "fnode.h"

typedef RWTValDlist<VId> VIdList;
typedef RWTValDlistIterator<VId> VIdListIter;

typedef RWTValDlist<AMObj> AMObjList; // type AMObjList has already been used elsewhere
typedef RWTValDlistIterator<AMObj> AMObjListIter;

// ------------------------
// Iterators on collections
// ------------------------

class ArrayIter {

public:

  virtual ~ArrayIter() {};

  virtual AmlBoolean operator++() = 0;
  virtual AmlBoolean operator()()  = 0;

  virtual void reset() = 0;

  virtual AMObj key() const = 0;

};


class SLArrayIter : public ArrayIter {

  AMObjListIter _next;

public:

  SLArrayIter(AMObjList* list) : _next(*list) {};
  virtual ~SLArrayIter() {}

  AMObjList* container() const {return _next.container();}

  virtual AmlBoolean operator++() {return ++_next;}
  virtual AmlBoolean operator()() {return _next();}

  virtual void reset() {_next.reset();}

  virtual AMObj key() const {return _next.key();}

};

// -----------
//    Arrays
// -----------

class Array : public AMModel {

protected:

  int nestedDepth() const;

  AmlBoolean _state;

  AMObj* _an_element;

public:

  Array() {_an_element = 0; _state = TRUE;}
  virtual ~Array() {delete _an_element;}

  virtual int entries() const = 0;
  virtual int isValid() const {return (int)_state;}

  virtual ArrayIter* iterator() const = 0;

  virtual AmlBoolean contains(const Array& array) const = 0;
  virtual AmlBoolean contains(const AMObj& obj) const = 0;
  virtual AmlBoolean operator==(const Array& array) const = 0;

  virtual Array& operator+=(const Array*) = 0;
  virtual Array& operator+=(const AMObj&) = 0;
  virtual Array& operator-=(const AMObj&) = 0;

  virtual void remove(int start, int end) = 0;
  virtual void insert(int index, const AMObj&) = 0;

  const AMObj* anElement() const {return _an_element;}

  AmlBoolean checkDefined() const;

  AMObjType surfaceType() const {
    if (_an_element) return _an_element->tag();
    else return AMObjType::ANY;
  }
  AmlBoolean matchesArrayType(const AMObj& obj) const {
    if (_an_element) return obj && (*_an_element);
    else return TRUE; // the array is empty and any type matches the array type
  }

  virtual const AMObj head() const = 0; // an AMObj
  virtual const AMObj tail() const = 0; // a array of AMObj
  virtual int index(const AMObj&) const = 0;  // first index of an object
  virtual const AMObj at(int) const = 0;

  virtual std::ostream& display(std::ostream&, size_t maxbytes = 0) const;
  virtual std::ostream& displayOneLine(std::ostream&) const;
  virtual AMObj display(std::ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}
  virtual std::ostream& displaySpreadSheet(std::ostream& o, int level, const char* sep) const;

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj plot(GP_window&, const AMObjVector& args) const = 0;

};

class SLArray : public Array, public AMObjList {


  int plotWrite(const char* prefix,
                const char* title,
                const char* xtitle,
                const char* ytitle,
                Array* titles,
                const char* style,
                int mode,
                int xaxis,
                double xoutset,
                double xstep,
                double xmin,
                double xmax,
                double ymin,
                double ymax
                ) const;
  int saveWrite(const AMObj& array, const char* prefix) const;


public:

  SLArray(): Array() {}
  SLArray(const VIdList*);
  SLArray(const Array*, const PFNode*, const AMObj*);
  SLArray(const SLArray& array) : AMObjList(array) {}
  SLArray(const char*, int, const int*); // lecture d'un tableau multidimensionel
  SLArray(const char*); // lecture d'un tableau quelconque
  SLArray(const Set* set);

  virtual ~SLArray() {}
  virtual int entries() const {return AMObjList::entries();}

  virtual ArrayIter* iterator() const {return new SLArrayIter((AMObjList*)this);}

  virtual AmlBoolean contains(const Array& array) const;
  virtual AmlBoolean contains(const AMObj& obj) const;
  virtual AmlBoolean operator==(const Array& array) const;

  virtual Array& operator+=(const AMObj&);
  virtual Array& operator-=(const AMObj&);
  Array& operator+=(const Array* parray);

  virtual void remove(int start, int end);
  virtual void insert(int index, const AMObj&);

  virtual const AMObj head() const {
    if (AMObjList::entries()) return first();
    else return AMObj(AMObjType::UNDEF);
  }

  virtual const AMObj tail() const {
    if (AMObjList::entries()) {
      SLArray* _tail = new SLArray(*this);
      _tail->removeFirst();
      return AMObj(AMObjType::ARRAY, _tail);
    }
    else return AMObj(AMObjType::ARRAY, new SLArray);
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

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual AMObj save(const AMObjVector& args) const;

};


#endif
