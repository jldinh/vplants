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
 *       $Id: fnode.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef FNODE_HEADER
#define FNODE_HEADER

#include "tool/rw_cstring.h"
//#include <rw/cstring.h>

#include "ammodel.h"
#include "amstring.h"

// Within a FuncNode, the description of the arguments of a function should
// say how to compute the function: arguments of type INT, BOOL, STRING, etc
// are available directly in the argument list. Their type is also available
// directly (INT, BOOL, ...). For arguments of type PFNODE, values should be
// taken from the associated FNodeNode son pointed to by the corresponding value.
// The type of this argument is the type of the return value of the pointed node.
// Finally arguments of type VAR should be taken from the FNode evaluator
// (class FNodeNodeEval) which is called for a certain value of a VId. Type is VTX.
// And the integer value associated to VAR gives a reference to one among many
// variables.

class FNode : public AMModel {

  enum HeadType {FNODE, PFUNC, IFCTRL, SWITCHCTRL, ITERATOR};
  enum HeadArgType {PFNODE, ATOM, VAR};

  RWCString _name;

  int _argnb;
  AMObjType* _argtype;          // only contains positive values
  AMObjType _rettype;

  HeadType _headtype;
  union{                        // pointer function used at that node (type FNode* or PFUN)
    PFUN _pfhead;               // it cannot be const since this function can itself be an FExp
    FNode* _fnhead;
  };

  int _hargnb;                  // head arg nb
  HeadArgType* _hargtype;       // may contain negative values
  AMObj* _harg;         // this list should be closed before being passed to _head for evaluation

  AmlBoolean _valid;

  void lockHead() {
    assert(_headtype != FNode::PFUNC);
    assert(_fnhead);
    _fnhead->lock();
#ifdef DEBUGREFCOUNT
  std::cerr << "refcount++ (" <<_fnhead->isLocked() << ") sur : ";
    _fnhead->displayOneLine(std::cerr);
  std::cerr << std::endl;
#endif
  }

  void unlockHead() {
    assert(_headtype != FNode::PFUNC);
    assert(_fnhead);
    if (_fnhead->isLocked()) { //"if" instead of "assert" because of recursive functions
      _fnhead->unlock();
#ifdef DEBUGREFCOUNT
      std::cerr << "refcount-- (" << _fnhead->isLocked() << ") sur : ";
      _fnhead->displayOneLine(std::cerr);
#endif
      if (!_fnhead->isLocked()) {
#ifdef DEBUGREFCOUNT
        std::cerr << "=> *** Destruction ***";
#endif
        delete _fnhead;
        _fnhead = 0;
      }
#ifdef DEBUGREFCOUNT
      std::cerr << std::endl;
#endif
    }
  }

  AMObj evalNthArg(HeadArgType type, const AMObj& arg, const AMObjVector& arglist) const;

  std::ostream& _displayOneLine(std::ostream& o, int argnb = 0, int* argref = 0, int depth = 0) const;

public:

  FNode(RWCString name, int argnb);
  FNode(RWCString name, FNode* head, const StringList* varlist, const FAMObjPtrList* args);
  FNode(RWCString name, FNode* head, const StringList* varlist, RWCString tiedvar, const FAMObjPtrList* args);
  FNode(RWCString name, PFUN head, int hargnb, AMObj* harg, AMObjType rettype);
  FNode(const FNode& node);

  virtual ~FNode();

  // signature of the function associated with this node
  int argNb() const {return _argnb;}
  const AMObjType* argTypes() const {return _argtype;}
  AMObjType argType(int i) const {assert(i>=0 && i<_argnb); return _argtype[i];}
  AMObjType retType() const {return _rettype;}
  RWCString name() const {return _name;}

  AmlBoolean isPredicate() const {return retType() == AMObjType::BOOL;}
  virtual void clearAndDestroy();

  FNode& operator=(const FNode& node);

  AmlBoolean isValid() const {return _valid;}

  void giveName(RWCString name, int argnb, const int* index_match);

  virtual AMObj operator()(const AMObjVector& arg) const;
  AMObj apply(const AMObjVector& arg) const;

  std::ostream& _print(std::ostream&) const;
  std::ostream& printAll(std::ostream& o, int tabnb = 0) const;
  std::ostream& printSignature(std::ostream&) const;

  virtual std::ostream& display(std::ostream& o, int maxbytes = 0) const;
  virtual AMObj display(std::ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}
  virtual std::ostream& displayOneLine(std::ostream& o) const {return display(o);}

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

class PFNode {                  // pointer to an FNode

  friend class FNode;

  AMObj _fn;                    // AMObj containing the fnode
  int _argnb;                   // number of arguments of _pfn
  int* _argref;                 // for each argument where can i find the instantiated value in the referencee FNode

public:

  PFNode(FNode* head, int argnb, const int* argref);
  PFNode(const PFNode& pf);
  ~PFNode() {clearAndDestroy();}

  void clearAndDestroy() {delete [] _argref; _argref = 0;}

  int argNb() const {return _argnb;}
  int argRef(int i) const {return _argref[i];}
  const FNode* fnode() const {assert(isValid()); return (FNode*)_fn.val.p;}

  AmlBoolean isValid() const {return _fn.tag == AMObjType::FNODE;}

  const PFNode& operator=(const PFNode& pf);

};

std::ostream& operator<<(std::ostream& o, const FNode& fnode);

#endif
