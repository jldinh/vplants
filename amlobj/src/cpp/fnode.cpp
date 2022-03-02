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
 *       $Id: fnode.cpp 3259 2007-06-06 13:40:30Z dufourko $
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




#include <assert.h>

#include "fnode.h"
#include "parseraml.h"
#include "set.h"
#include "array.h"
#include "list.h"

#include "erroraml.h"
#include "kernel_err.h"

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Kernel"

using namespace std;

// ---------------
// Class FNode
// ---------------

// Builds an invalid FNode, which can be patched afterwards to become valid

FNode::FNode(RWCString name, int argnb) {

  _name = name;

  _argnb = argnb;
  _argtype = new AMObjType[_argnb];
  _rettype = AMObjType::ANY;

  for(int k=0; k<_argnb; k++) _argtype[k] = AMObjType::ANY;

  _headtype = FNode::FNODE;
  _fnhead = 0;

  _hargnb = 0;
  _hargtype = 0;  // Value which defines this FNode as being invalid
  _harg = 0;

  _valid = FALSE;

}

// build a FNode from a head Fnode and a list of arguments
// - The FNode given as the head is locked
// - Arguments may be of 3 types :
//      FNodes
//      ATOMS
//      Variables
//

FNode::FNode(RWCString name, FNode* head, const StringList* varlist, const FAMObjPtrList* args) {

  assert(head);
  assert(varlist);
  assert(args);

  _name = name;

  _valid = TRUE;

  // cerr << "FNode name = " << name << endl;
  // cerr << "FNode head = " << head->name() << endl;

  if (head->name() == ":IfThenElse") _headtype = FNode::IFCTRL;
  else if (head->name() == ":Switch") _headtype = FNode::SWITCHCTRL;
  else _headtype = FNode::FNODE;
  _fnhead = head;
  lockHead();
  _rettype = head->retType();
  _argnb = varlist->entries();
  //assert(_argnb);

  _argtype = new AMObjType[_argnb];
  for(int k=0; k<_argnb; k++) _argtype[k] = AMObjType::ANY;

  int headargnb = _fnhead->argNb();
  // assert(headargnb <= args->entries());
  // because of functions which can have varying number of args.

  _hargnb = args->entries();
  _hargtype = new HeadArgType[_hargnb];
  _harg = new AMObj[_hargnb];

  // Now go through the list of instanciated head arguments and make
  // the head list of arguments used at evaluation

  FAMObjPtrListIter next(*(FAMObjPtrList*)(args));

  int i = 0;                    // ith head argument

  while (next()) { // loop on arguments head args

//    if (!isValid()) break;

    FAMObj* farg = next.key();

    switch(farg->tag.type) {

    case AMObjType::VAR:
      {
        assert(varlist->contains(*(AMString*)(farg->val.p)));
        int varindex = varlist->index(*(AMString*)(farg->val.p));
        if (i < headargnb) _argtype[varindex] = head->_argtype[i]; // case where optional parma exist
        else _argtype[varindex] = AMObjType::ANY;
        _hargtype[i] = FNode::VAR;
        if (i < headargnb) _harg[i].tag = head->_argtype[i];
        else _harg[i].tag = AMObjType::ANY;
        _harg[i].val.i = varindex;
      }
      break;
    case AMObjType::FNODE:
      {
        // create a PFNODE !!
        // PFNode(FNode* head, int argnb, int* argref);

        FNode* fun = (FNode*) farg->val.p;
        assert(fun);
        int* argref = new int[fun->argNb()];

        if (!farg->arglist) {

          // Cas d'une fonction (sans arguments) passee comme argument dans une autre fonction
          // _valid = FALSE;
          // genAMLError(ERRORMSG(K_F_ARG_TYPE2_ERR_sdss), name.data(), i+1, "FUNC", "a function");

        }
        else {
          assert(!farg->arglist->isEmpty());

          int j = 0;
          StringListIter nextvar(*farg->arglist); // loop on var list of farg
          while(nextvar()) {
            RWCString varstg = nextvar.key();
            assert(varlist->contains(varstg));
            argref[j] = varlist->index(varstg);

            if (_argtype[argref[j]] == AMObjType::ANY)
            _argtype[argref[j]] = fun->argType(j);
            else {
              _argtype[argref[j]] =  (_argtype[argref[j]] & fun->argType(j));
            }
            j++;
          }
          _hargtype[i] = FNode::PFNODE;
          _harg[i].tag = AMObjType::UNDEF; // this value is used during copies of this amobj
          _harg[i].val.pt = (void*) new PFNode(fun, fun->argNb(), argref);

        }

        delete [] argref;

      }
      break;
    default: // All AMObjTypes except FNODE and VAR treated above
      _hargtype[i] = FNode::ATOM;
      _harg[i] = *farg;
      if (i < headargnb) _harg[i].tag = (head->_argtype[i] & farg->tag);
      // no use : else _harg[i].tag = farg->tag;
      break;
    }
    i++;
  }

  // cerr << endl;

}


// constructor for iterators

FNode::FNode(RWCString name, FNode* head, const StringList* varlist, RWCString tiedvar, const FAMObjPtrList* args) {

  assert(head);
  assert(varlist);
  assert(args);

  _name = name;
  _valid = TRUE;

  _headtype = FNode::ITERATOR;
  _fnhead = head;
  lockHead();
  _rettype = head->retType();
  _argnb = varlist->entries();
  _argtype = new AMObjType[_argnb];
  for(int k=0; k<_argnb; k++) _argtype[k] = AMObjType::ANY;

  _hargnb = _fnhead->argNb();
  _hargtype = new HeadArgType[_hargnb];
  _harg = new AMObj[_hargnb];

  assert(_hargnb == int(args->entries()));

  // Now go through the list of instanciated head arguments and make
  // the head list of arguments used at evaluation

  FAMObjPtrListIter next(*(FAMObjPtrList*)(args));

  int i = 0;                    // ith head argument

  while (next()) { // loop on arguments args

//    if (!isValid()) break;

    FAMObj* farg = next.key();

    switch(farg->tag.type) {

    case AMObjType::VAR:
      {
        if (varlist->contains(*(AMString*)(farg->val.p))) {
          int varindex = varlist->index(*(AMString*)(farg->val.p));
          _argtype[varindex] = head->_argtype[i];
          _hargtype[i] = FNode::VAR;
          _harg[i].tag = AMObjType::ANY;
          _harg[i].val.i = varindex;
        }
        else {                          // A VERIFIER !!!!!!!!
          _hargtype[i] = FNode::VAR;
          _harg[i].tag = AMObjType::ANY;
          _harg[i].val.i = -1;
        }
      }
      break;
    case AMObjType::FNODE:
      {
        // create a PFNODE !!
        // PFNode(FNode* head, int argnb, int* argref);

        FNode* fun = (FNode*) farg->val.p;
        assert(fun);
        int* argref = new int[fun->argNb()];

        if (!farg->arglist) {

          _valid = FALSE;
          genAMLError(ERRORMSG(K_F_ARG_TYPE2_ERR_sdss), name.data(),i+1, "FUNC", "a function");

        }
        else {

          assert(!farg->arglist->isEmpty());

          int j = 0;
          StringListIter nextvar(*farg->arglist); // loop on var list of farg
          while(nextvar()) {
            RWCString varstg = nextvar.key();
            if (varstg == tiedvar) {
              argref[j] = -1;
            }
            else {
              argref[j] = varlist->index(varstg);
              if (_argtype[argref[j]] == AMObjType::ANY)
              _argtype[argref[j]] = fun->argType(j); // synthetize the argument type
              else {
                _argtype[argref[j]] =  (_argtype[argref[j]] & fun->argType(j));
              }
            }
            j++;
          }
          _hargtype[i] = FNode::PFNODE;
          _harg[i].tag = AMObjType::UNDEF;
          _harg[i].val.pt = (void*) new PFNode(fun, fun->argNb(), argref);

        }

        delete [] argref;

      }
      break;
    default: // All AMObjTypes except FNODE and VAR treated above
      _hargtype[i] = FNode::ATOM;
      _harg[i] = *farg;
      _harg[i].tag = (head->_argtype[i] & farg->tag);
      break;
    }
    i++;
  }

  // cerr << endl;

}


FNode::FNode(RWCString name, PFUN head, int hargnb, AMObj* harg, AMObjType rettype) :
 _harg(0)
{

  // assert(harg);

  _name = name;

  _valid = TRUE;

  _argnb = hargnb;
  _argtype = new AMObjType[_argnb];
  _rettype = rettype;

  for (register int k=0; k<_argnb; k++) _argtype[k] = AMObjType::ANY;
  for (register int i=0; i<_argnb; i++)  _argtype[i] = harg[i].tag;

  _headtype = FNode::PFUNC;
  _pfhead = head;

  _hargnb = hargnb;
  _hargtype = new HeadArgType[_hargnb];
  _harg = harg;

  for (int i2=0; i2<_hargnb; i2++)  _hargtype[i2] = FNode::VAR; // Should never be used !!!

}


FNode::FNode(const FNode& node):
 _harg(0) {

  _name = node._name;

  _valid = node._valid;

  int nb = node._argnb;

  _argnb = nb;

  _argtype = new AMObjType[nb];
  for(register int i=0; i<nb; i++) _argtype[i] = node._argtype[i];

  _rettype = node._rettype;

  _headtype = node._headtype;
  switch(_headtype) {
  case FNode::PFUNC:
    _pfhead = node._pfhead;
    break;
  case FNode::FNODE:
    _fnhead = node._fnhead;
    if (_fnhead) lockHead();
    break;
  default:
    assert(FALSE);
  }

  nb = node._hargnb;
  _hargnb = nb;
  _hargtype = new HeadArgType[nb];
  _harg = new AMObj[nb];

  for (int i2=0; i2<nb; i2++) {
    _hargtype[i2] = node._hargtype[i2];
    if (_hargtype[i2] == FNode::PFNODE)
    _harg[i2] = AMObj(AMObjType::UNDEF, (void*)new PFNode(*(PFNode*)node._harg[i2].val.pt)); // duplicates the pfnode
    else _harg[i2] = node._harg[i2];
  }

}


FNode::~FNode() {

  clearAndDestroy();

}


void FNode::clearAndDestroy() {

  if (_argtype) delete [] _argtype;
  _argtype = 0;
  _argnb = 0;

  if (_headtype == FNode::FNODE ||
      _headtype == FNode::ITERATOR ||
      _headtype == FNode::IFCTRL ||
      _headtype == FNode::SWITCHCTRL ) {
    if (_fnhead) {
      unlockHead();
    }
  }

  // delete its FNode sons before deleting itself

  for (register int i=0; i<_hargnb; i++) {

    // deletes the PFNode which in turn deletes its FNode if this one has an undefined name
    if (_hargtype[i] == FNode::PFNODE) delete (PFNode*)_harg[i].val.pt;

  }

  _hargnb = 0; // avoid several destructions on recursive functions

  if (_harg) {
          delete [] _harg; // allocated externally
  }
  if (_hargtype) {
          delete [] _hargtype; // allocated externally
  }
  _harg= 0;
  _hargtype = 0;

  _valid = FALSE;

}

FNode& FNode::operator=(const FNode& node) {

  if (this == &node) return *this;

  if (!isValid()) *(AMModel*)this = (AMModel&)node;

  clearAndDestroy();

  // must not be copied if the fnode is valid since it is used only in the parseraml.y
  // to overwrite a function stored in the amobjtable (to allow recurrence definition of funcs)

  _name = node._name;

  int nb = node._argnb;

  _argnb = nb;
  _argtype = new AMObjType[nb];
  for(register int i=0; i<nb; i++) _argtype[i] = node._argtype[i];

  _rettype = node._rettype;

  _headtype = node._headtype;

  switch(_headtype) {
  case FNode::PFUNC:
    _pfhead = node._pfhead;
    break;
  case FNode::FNODE:
    _fnhead = node._fnhead;
    if (_fnhead) lockHead();
    break;
  default:
    _fnhead = node._fnhead; // ITERATORS: _fnhead is an FNode
    if (_fnhead) lockHead();
  }

  nb = node._hargnb;
  _hargnb = nb;
  _hargtype = new HeadArgType[nb];
  _harg = new AMObj[nb];

  for (int i2=0; i2<nb; i2++) {
    _hargtype[i2] = node._hargtype[i2];
    if (_hargtype[i2] == FNode::PFNODE && node._harg[i2].val.pt != NULL)
    _harg[i2] = AMObj(AMObjType::UNDEF, (void*)new PFNode(*(PFNode*)node._harg[i2].val.pt)); // duplicates the fnode
    else _harg[i2] = node._harg[i2];
  }

  _valid = node._valid;

  return *this;

}

AMObj FNode::evalNthArg(HeadArgType type, const AMObj& arg, const AMObjVector& arglist) const {

  switch(type) {

  case FNode::PFNODE:
    {
      PFNode* son = (PFNode*)arg.val.pt;
	  if(son == NULL) return arg;
      AMObjVector sonarglist(son->_argnb);
      for (register int j=0; j<son->_argnb; j++) {
        sonarglist[j] = arglist[son->_argref[j]];
      }
      return (*(((FNode*)(son->_fn.val.p))))(sonarglist);
    }
  case FNode::VAR:
    return arglist[arg.val.i]; // matching of variables
  case FNode::ATOM:
    return arg;
 default:
   return arg;
  }

}

AMObj FNode::apply(const AMObjVector& arg) const{
  return operator()(arg);
}

AMObj FNode::operator()(const AMObjVector& arg) const {

  AMObj ret;

  switch (_headtype) {

  case FNode::PFUNC:
    // cerr << "PFUN eval" << endl;
    assert(_pfhead);
    ret = (*_pfhead)(arg);
    break;
  case FNode::FNODE:
    {
      // First close the argument list

      AMObjVector closed_list(_hargnb); // a function can be overloaded with no argument cf Activate()

      for (register int i=0; i<_hargnb; i++) {

        closed_list[i] = evalNthArg(_hargtype[i],_harg[i],arg);

      }

      // Second evaluates the head function on this closed list

      ret = (*_fnhead)(closed_list);

    }
    break;

  case FNode::IFCTRL:
    {
      AMObj test;

      // First Eval first argument

      test = evalNthArg(_hargtype[0], _harg[0], arg);

      // Then compute the FExp corresponding to the predicate result (FExp1 if TRUE, FExp2 if FALSE)

      int i;

      if (test.val.i) i = 1;
      else i = 2;

      ret = evalNthArg(_hargtype[i], _harg[i], arg);

    }
    break;

  case FNode::SWITCHCTRL:
    {
      AMObj test;

      // args[] = SwitchExp CaseExp1 Exp1 CaseExp2 Exp2 ... DefaultExp
      // here: _hargnb = 1 + 2*n + 1 (n may be 0,1,2,...)

      // First Eval first argument

      test = evalNthArg(_hargtype[0], _harg[0], arg);

      // Loop on the Case and Default Exps identical to the Switch Exp;

      for(int k=1; k<_hargnb; k+=2) {

        if (k+1 == _hargnb) ret = evalNthArg(_hargtype[k],_harg[k],arg);
        else if (test == evalNthArg(_hargtype[k],_harg[k],arg)) {

          ret = evalNthArg(_hargtype[k+1],_harg[k+1],arg);
          break;

        }
      }

    }

    break;

  case FNode::ITERATOR:
    {

      AMObj setobj;

      // cerr << "Evaluation du FNode dont le _headtype == FNode::ITERATOR" << endl;

      // cerr << "Evaluation de l'argument 0" << endl;
      // First Eval first argument which is the collection to iterate through

      if (_hargtype[0] != ATOM && _hargtype[0] != PFNODE && _hargtype[0] != VAR) {

          genAMLError(ERRORMSG(K_ITER_ARG_TYPE_ERR_sdss), _name.data(), 1, setobj.tag.string().data(), "ARRAY or SET");
            return AMObjType(AMObjType::ERROR);

      }

      setobj = evalNthArg(_hargtype[0], _harg[0], arg);

      // cerr << "Boucle de Selection sur : " << setobj;
      // Then Loop on the collection using the second argument

      if (_fnhead->_name == ":Foreach") {

        if (setobj.tag == AMObjType::SET) {

          Set* objret;

          switch(_hargtype[1]) {

          case FNode::PFNODE:
            objret = new HashSet((Set*) setobj.val.p, (PFNode*)_harg[1].val.pt, arg.data());
            break;
          case FNode::VAR:
            objret = new HashSet;
            {
              SetIter* pnext = ((Set*)setobj.val.p)->iterator();
              SetIter& next = *pnext;

              while(next()) {
                *objret += next.key();
              }

              delete pnext;

            }
            break;
          case FNode::ATOM:
            objret = new HashSet;
            {
              SetIter* pnext = ((Set*)setobj.val.p)->iterator();
              SetIter& next = *pnext;

              while(next()) {
                *objret += _harg[1];
              }
              delete pnext;
            }
            break;
          }

          if (objret->isValid()) ret = AMObj(AMObjType::SET, objret);
          else {
            delete objret;
            ret = AMObj(AMObjType::ERROR);
          }

        }
        else if (setobj.tag == AMObjType::ARRAY) {

          Array* objret;

          switch(_hargtype[1]) {

          case FNode::PFNODE:
            objret = new SLArray((Array*) setobj.val.p, (PFNode*)_harg[1].val.pt, arg.data());
            break;
          case FNode::VAR:
            objret = new SLArray;
            {
              ArrayIter* pnext = ((Array*)setobj.val.p)->iterator();
              ArrayIter& next = *pnext;

              while(next()) {
                *objret += next.key();
              }

              delete pnext;

            }
            break;
          case FNode::ATOM:
            objret = new SLArray;
            {
              ArrayIter* pnext = ((Array*)setobj.val.p)->iterator();
              ArrayIter& next = *pnext;

              while(next()) {
                *objret += _harg[1];
              }
              delete pnext;
            }
            break;

          }

          if (objret->isValid()) ret = AMObj(AMObjType::ARRAY, objret);
          else {
            delete objret;
            ret = AMObj(AMObjType::ERROR);
          }
        }
        else if (setobj.tag == AMObjType::LIST) {

          List* objret;

          switch(_hargtype[1]) {

          case FNode::PFNODE:
            objret = new SLList((List*) setobj.val.p, (PFNode*)_harg[1].val.pt, arg.data());
            break;
          case FNode::VAR:
            objret = new SLList;
            {
              ListIter* pnext = ((List*)setobj.val.p)->iterator();
              ListIter& next = *pnext;

              while(next()) {
                *objret += next.key();
              }

              delete pnext;

            }
            break;
          case FNode::ATOM:
            objret = new SLList;
            {
              ListIter* pnext = ((List*)setobj.val.p)->iterator();
              ListIter& next = *pnext;

              while(next()) {
                *objret += _harg[1];
              }
              delete pnext;
            }
            break;
          }

          if (objret->isValid()) ret = AMObj(AMObjType::LIST, objret);
          else {
            delete objret;
            ret = AMObj(AMObjType::ERROR);
          }

        }
        else {

          genAMLError(ERRORMSG(K_ITER_ARG_TYPE_ERR_sdss), _name.data(), 2, setobj.tag.string().data(), "LIST, ARRAY or SET");
          ret = AMObjType(AMObjType::ERROR);

        }

      }
      else assert(FALSE);


    }
    break;

  }

  return ret;

}

void FNode::giveName(RWCString name, int argnb, const int* index_match) {

  assert(index_match);

  _name = name; // give a name to this fnode

  if (argnb > _argnb) { // expression of the form f(_x,_y,_z) = g(_x, _z)

    AMObjType* oldtype = _argtype;
    _argtype = new AMObjType[argnb];

    for(register int k=0; k<argnb; k++) _argtype[k] = AMObjType::ANY;

    for (int k2=0; k2<_argnb; k2++) {

      _argtype[index_match[k2]] = oldtype[k2];

    }

    delete [] oldtype;

    _argnb = argnb;

  }

  // change the variable mapping in _harg

  for (int i=0; i<_hargnb; i++) {

    switch (_hargtype[i]) {

    case FNode::PFNODE:
      {
        PFNode* son = (PFNode*)_harg[i].val.pt;
		if(son)
        for (int j=0; j<son->_argnb; j++) {
          // exclude tied variables from matching
          if (son->_argref[j] >= 0 ) son->_argref[j] = index_match[son->_argref[j]];

        }
      }
      break;
    case FNode::VAR:
      _harg[i].val.i = index_match[_harg[i].val.i];
      break;
    case FNode::ATOM:
      break;
    }

  }

}

#define _var_(k) ((char)(((k)>=0)?('a'+(k)):('0'-((k)+1))))

ostream& FNode::_displayOneLine(ostream& o, int argnb, int* argref, int depth) const {

  assert(depth>=0);

  if (depth == 0) {

    RWCString fname(_name);

    o << _rettype << "<-- " << fname.strip(RWCString::leading, ':') << "(";
    int* arg = new int[_argnb];

    for(register int k=0; k<_argnb; k++) {
      if (k == _argnb-1) o << _argtype[k].string() << "_" << _var_(k);
      else o << _argtype[k].string() << "_" << _var_(k) << ",";
      arg[k] = k;
    }
    o << ")";

    _displayOneLine(o, _argnb, arg, depth+1);
    delete [] arg;

  }
  else {

    if (_headtype != FNode::PFUNC) {

      if(isValid()) {

        if (depth == 1) o << " = ";

        if (!(_fnhead->_name.isNull())) {

          RWCString fname = _fnhead->_name;

          o << fname.strip(RWCString::leading, ':');

        }

        o << "(";

        for (register int i=0; i<_hargnb; i++) {

          switch(_hargtype[i]) {

          case FNode::PFNODE:
            {
              PFNode* son = (PFNode*)_harg[i].val.pt;
              assert(son);
              int* arg = new int[son->_argnb];
              for (int j=0; j<son->_argnb; j++) {
                if (son->_argref[j] >= 0) {
                  arg[j] = argref[son->_argref[j]];
                }
                else {
                  arg[j] = son->_argref[j]-depth+1;
                }
              }
              ((FNode*)(son->_fn.val.p))->_displayOneLine(o, son->_argnb, arg, depth+1);
              delete [] arg;
            }
            break;
          case FNode::VAR:
            if (_harg[i].val.i < argnb) o << "_" << _var_(argref[_harg[i].val.i]);
            else o << "_?";
            break;
          case FNode::ATOM:
            _harg[i].printValue(o, 50);
            break;

          }

          if (i!= _hargnb-1) o << ",";

        }

        o << ")";

      }
      else {

        o << "Invalid Fnode()";

      }
    }

  }

  return o;

}


ostream& FNode::_print(ostream& o) const {

  o << "<FNODE> : ";
  if (_name.isNull()) o << "lambda";
  else o << _name;
  o << "(";
  for(register int k=0; k<_argnb; k++)
  if (k == _argnb-1) o << "_" << k;
  else o << "_" << k << ",";
  o << ")";

  o << " with signature : ";
  printSignature(o) << endl;

  o << "  Head name  : ";
  if (_headtype == FNODE) {
    if (_fnhead->_name.isNull()) o << "lambda";
    else o << _fnhead->_name;
  }
  else o << "pfun";

  o << "(" <<  _hargnb << " arguments) :" << endl;

  for (int i=0; i<_hargnb; i++) {

    switch(_hargtype[i]) {

    case FNode::PFNODE:
      {
        PFNode* son = (PFNode*)_harg[i].val.pt;
        o << "  * Function :" << son << " " << ((FNode*)(son->_fn.val.p))->name() << "(";
        for(int j=0; j<son->_argnb; j++) cerr << "_" << son->_argref[j] << " ";
        cerr << ")" << endl;
      }
      break;
    case FNode::VAR:
      o << "  * Variable _" << _harg[i].val.i << endl;
      break;
    case FNode::ATOM:
      o << "  * Value" << endl;
      break;

    }

  }

  return o;

}


ostream& FNode::printSignature(ostream& o) const {

  o << _rettype << " <-- ";

  if (_argnb) assert(_argtype);

  for (int i=0; i<_argnb; i++) {

    o << _argtype[i];

    if (i!=_argnb-1) o << " . ";

  }

  return o;

}

ostream& FNode::display(ostream& o, int maxbytes) const {

  if (maxbytes) {

    if (maxbytes<5) maxbytes = 5;

#ifndef STL_EXTENSION
    char* tmp = new char[maxbytes+1];
    ostrstream os(tmp,maxbytes-3); // for "..."

    _displayOneLine(os);

    o << os.str();
    if (strlen(tmp) >= maxbytes-3)  o << "...";

    delete [] tmp;
#else
    ostringstream os; // for "..."

    _displayOneLine(os);

    o << os.str();
    if ( int(os.str().size()) >= maxbytes-3)  o << "...";

#endif
  }
  else _displayOneLine(o);

  return o;

}

ostream& FNode::printAll(ostream& o, int tabnb) const {

  assert(tabnb>=0);

  char* stuff = new char[tabnb+1];

  for (int i1=0; i1<tabnb; i1++) stuff[i1] = '\t';
  stuff[tabnb] = '\0';

  o << stuff << "<FNODE> : ";
  if (_name.isNull()) o << "lambda";
  else o << _name;
  o << "(";
  for(register int k=0; k<_argnb; k++)
  if (k == _argnb-1) o << "_" << k;
  else o << "_" << k << ",";
  o << ")";

  o << " with signature : ";
  printSignature(o) << endl;

  o << stuff << "  Head name  : ";
  if (_headtype == FNODE) {
    if (_fnhead->_name.isNull()) o << "lambda";
    else o << _fnhead->_name;
  }
  else o << "pfun";

  o << "(" <<  _hargnb << " arguments) :" << endl;

  for (int i=0; i<_hargnb; i++) {

    switch(_hargtype[i]) {

    case FNode::PFNODE:
      {
        PFNode* son = (PFNode*)_harg[i].val.pt;
        o << stuff << "  * Function (";
        for (int j=0; j<son->_argnb; j++) o << "_" << son->_argref[j] << " ";
        o << ")" << endl;
        ((FNode*)(son->_fn.val.p))->printAll(o, tabnb+1);
      }
      break;
    case FNode::VAR:
      o << stuff << "  * Variable _" << _harg[i].val.i << endl;
      break;
    case FNode::ATOM:
      o << stuff << "  * Value" << endl;
      break;

    }

  }

  delete [] stuff;

  return o;

}



// ---------------
// Class PFNode
// ---------------

PFNode::PFNode(FNode* head, int argnb, const int* argref) :_fn(AMObjType::FNODE,head){

  _argnb = argnb;
  _argref = new int[argnb];

  for(register int i = 0; i<argnb; i++) _argref[i] = argref[i];

}

PFNode::PFNode(const PFNode& pf) : _fn(pf._fn) {

  _argnb = pf._argnb;
  _argref = new int[_argnb];

  for (register int i=0; i<_argnb; i++) _argref[i] = pf._argref[i];

}

const PFNode& PFNode::operator=(const PFNode& pf) {

  if (this == &pf) return *this;

  clearAndDestroy();

  _fn = pf._fn;

  _argnb = pf._argnb;
  _argref = new int[_argnb];
  for (register int i=0; i<_argnb; i++) _argref[i] = pf._argref[i];

  return *this;

}

ostream& operator<<(ostream& o, const FNode& fnode) {

  return fnode.printSignature(o);

}
