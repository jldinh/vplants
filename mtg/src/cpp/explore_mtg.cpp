
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
 *       $Id: explore_mtg.cpp 3258 2007-06-06 13:18:26Z dufourko $
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
#include "tool/rw_time.h"
//#include <rw/rwtime.h>

#include "mtg.h"



//static const char rcsid[] = "$Id: explore_mtg.cpp 3258 2007-06-06 13:18:26Z dufourko $";


// ------------- EXPLORATION DU GTM --------------

VIdList* MTG::findLessSequence(VId firstv) const {

  assert(existsVertex(firstv));

  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  /*
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }

  */

  VIdList* reslist = new VIdList;
  reslist->append(firstv);

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) {
      firstv = nexts.key();
      reslist->append(firstv);
    }

    delete slist;

    slist = topoSons(firstv, ANYLESS);

  }

  delete slist;

  /*
  cerr << "\n/// less sequence(" << firstv << ") = ";
  VIdListIter n(*reslist);
  while (n()) {
    cerr << n.key() << " | " << flush;
  }
  cerr << "." << endl;
  */

  return reslist;

}


VIdList* MTG::findLocalLessSequence(VId firstv) const {

  assert(existsVertex(firstv));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
  VIdList* reslist = new VIdList;
  reslist->append(firstv);

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  VId cf = compoFather(firstv);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) {
      firstv = nexts.key();
      if (compoFather(firstv) == cf) reslist->append(firstv);
      else {
        firstv = UNDEF;
        break;
      }
    }

    delete slist;

    if (firstv != UNDEF) slist = topoSons(firstv, ANYLESS);
    else break;

  }

  if (firstv != UNDEF) delete slist;

  /*
  cerr << "\n/// less sequence(" << firstv << ") = ";
  VIdListIter n(*reslist);
  while (n()) {
    cerr << n.key() << " | " << flush;
  }
  cerr << "." << endl;
  */

  return reslist;

}

VId MTG::findFirstVertexInLocalLessSequence(VId firstv) const {    // checked

  assert(existsVertex(firstv));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */

  VId father = firstv;
  VId vtx;
  VId cf_vtx;
  VId tf_vtx;
  VId cf_tf_vtx;
  EType et = ANYLESS;

  do {

    vtx = father;
    cf_vtx = compoFather(vtx);
    tf_vtx = topoFather(vtx, ANYTOPO);

    if (tf_vtx != UNDEF) {
      cf_tf_vtx = compoFather(tf_vtx);
      et = edgeType(tf_vtx, vtx);
    }

  } while(tf_vtx != UNDEF && cf_tf_vtx == cf_vtx && et == ANYLESS);

  return vtx;

}


VId MTG::findLastVertexInLocalLessSequence(VId firstv) const {  // checked

  assert(existsVertex(firstv));

  /*

  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }

  */

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) firstv = nexts.key();

    delete slist;

    slist = topoSons(firstv, ANYLESS);

  }

  delete slist;

  return firstv;

}

VId MTG::findLabelInLocalLessSequence(VId firstv, VClass csymb, int index) const {   // checked

  assert(existsVertex(firstv));
  assert(isValidClass(csymb));
  assert(isValidIndex(index));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }

  */

  if (vclass(firstv) == csymb && vindex(firstv) == index) return firstv;

  VId cf = compoFather(firstv);

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) {

      firstv = nexts.key();

      if (cf != compoFather(firstv)) {
        delete slist;
        return UNDEF;
      }
      else {
        if (vclass(firstv) == csymb && vindex(firstv) == index) {
          delete slist;
          return firstv;
        }
      }

    }

    delete slist;

    slist = topoSons(firstv, ANYLESS);

  }

  delete slist;

  return UNDEF;

}

VId MTG::findLabelInCarriedLocalLessSequenceAtLoc(VId loc, VClass csymb, int index) const {   // checked

  assert(existsVertex(loc));
  assert(isValidClass(csymb));
  assert(isValidIndex(index));

  int scl = classScale(csymb);

  /*
  // condition explained in mtg.h:
  // all the classes of scale scl must have max(X,Y,<) <= 1
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */

/*
  // condition explained in mtg.h
  for (i=0; i<clnb; i++) {
    assert(_header->plus(vclass(loc),i).max() < 2);
  }
*/

  VId carrier = findCompoAncestorAtScale(loc, scl);
  if (carrier == UNDEF) return UNDEF;

  VId cf = compoFather(carrier);

  VId z = UNDEF;

  VIdList* slist = topoSons(carrier, ANYPLUS);
  assert(slist);

  VIdListIter nexts(*slist);

  while(nexts()) {

    z = nexts.key();

    if (cf != compoFather(z)) {
      delete slist;
      return UNDEF;
    }
    else {
      if (vprefix(z) == loc) { // if one is found it is the sole one
        delete slist;
        // cerr << "Vertex z = " << z << " has been found as the first vertex carried at loc " << loc << endl;
        return findLabelInLocalLessSequence(z, csymb, index);
      }
    }

  }

  delete slist;

  return UNDEF;

}

VId MTG::findInsertionPointInLocalLessSequence(VId firstv, VClass c, int index) const {

  assert(existsVertex(firstv));
  assert(isValidClass(c));
  assert(isValidIndex(index));
  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
  if (vindex(firstv) >= index) return firstv;

  VId cf = compoFather(firstv);

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) {

      firstv = nexts.key();

      if (compoFather(firstv) != cf) {
        delete slist;
        return UNDEF;
      }
      else {
        if (vindex(firstv) >= index) {
          delete slist;
          return firstv;
        }
      }

    }

    delete slist;

    slist = topoSons(firstv, ANYLESS);

  }

  delete slist;

  return UNDEF;

}


VId MTG::findInsertionPointInGlobalLessSequence(VId firstv, VClass c, int index) const {

  assert(existsVertex(firstv));
  assert(isValidClass(c));
  assert(isValidIndex(index));
  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(firstv);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */

  if (vindex(firstv) >= index) return firstv;

  VIdList* slist = topoSons(firstv, ANYLESS);
  assert(slist);

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    while(nexts()) {

      firstv = nexts.key();

      if (vindex(firstv) >= index) {
        delete slist;
        return firstv;
      }

    }

    delete slist;

    slist = topoSons(firstv, ANYLESS);

  }

  delete slist;

  return UNDEF;

}


VId MTG::findInsertionPointInCarriedLocalLessSequenceAtLoc(VId loc, VClass c, int index) const {

  assert(existsVertex(loc));
  assert(isValidClass(c));
  assert(isValidIndex(index));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = classScale(c);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */

/*
  // condition explained in mtg.h
  for (i=0; i<clnb; i++) {
    assert(_header->plus(vclass(loc),i).max() < 2);
  }
*/
  VId carrier = findCompoAncestorAtScale(loc, classScale(c));
  if (carrier == UNDEF) return UNDEF;

  VId cf = compoFather(carrier);

  VId z = UNDEF;

  VIdList* slist = topoSons(carrier, ANYPLUS);
  assert(slist);

  VIdListIter nexts(*slist);

  while(nexts()) {

    z = nexts.key();

    if (compoFather(z) != cf) {
      delete slist;
      return UNDEF;
    }
    else {
      if (vprefix(z) == loc) { // if one is found it is the sole one
        delete slist;
        return findInsertionPointInLocalLessSequence(z, c, index);
      }
    }

  }

  delete slist;

  return UNDEF;

}



VId MTG::findInsertionPointInCarriedGlobalLessSequenceAtLoc(VId loc, VClass c, int index) const {

  assert(existsVertex(loc));
  assert(isValidClass(c));
  assert(isValidIndex(index));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = classScale(c);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
     }
    }
  }
  */
/*
  // condition explained in mtg.h
  for (i=0; i<clnb; i++) {
    assert(_header->plus(vclass(loc),i).max() < 2);
  }
*/
  VId carrier = findCompoAncestorAtScale(loc, classScale(c));
  if (carrier == UNDEF) return UNDEF;

  VId z = UNDEF;

  VIdList* slist = topoSons(carrier, ANYPLUS);
  assert(slist);

  VIdListIter nexts(*slist);

  while(nexts()) {

    z = nexts.key();

    if (vprefix(z) == loc) { // if one is found it is the sole one
      delete slist;
      return findInsertionPointInLocalLessSequence(z, c, index);
    }

  }

  delete slist;

  return UNDEF;

}


VId MTG::findLastVertexInCarriedLocalLessSequenceAtLoc(VId loc, int scl) const {

  assert(existsVertex(loc));
  assert(isValidScale(scl));
  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
/*
  // condition explained in mtg.h
  for (i=0; i<clnb; i++) {
    assert(_header->plus(vclass(loc),i).max() < 2);
  }
*/
  VId carrier = findCompoAncestorAtScale(loc, scl);
  if (carrier == UNDEF) return UNDEF;

  VId cf = compoFather(carrier);

  VId z = UNDEF;

  VIdList* slist = topoSons(carrier, ANYPLUS);
  assert(slist);

  VIdListIter nexts(*slist);

  while(nexts()) {

    z = nexts.key();

    if (compoFather(z) != cf) {
      delete slist;
      return UNDEF;
    }
    else {
      if (vprefix(z) == loc) { // if one is found it is the sole one
        delete slist;
        return findLastVertexInLocalLessSequence(z);
      }
    }

  }

  delete slist;

  return UNDEF;

}


VId MTG::findLastComponent(VId father) const {

  assert(existsVertex(father));
  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(father)+1;
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
  VIdList* clist = findLocalTopoRoots(father);
  assert(clist);

  if (clist->entries() > 1 || clist->entries() == 0) {
    delete clist;
    return UNDEF;
  }

  VId vtx = clist->first();

  delete clist;

  VIdList* slist = topoSons(vtx, ANYLESS);
  assert(slist);

  if (slist->entries() == 0) {
    delete slist;
    return vtx;
  }

  while (slist->entries() != 0) {

    // assert(slist->entries() < 2);

    VIdListIter nexts(*slist);

    nexts();

    father = vtx;
    vtx = nexts.key();

    if (compoFather(vtx) != compoFather(father)) {

      delete slist;
      return father;

    }

    delete slist;

    slist = topoSons(vtx, ANYLESS);
    assert(slist);

  }

  delete slist;

  return vtx;

}

VId MTG::findFirstComponent(VId father) const {

  assert(existsVertex(father));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(father);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
  VIdList* list = findLocalTopoRoots(father);

  int nb = list->entries();

  if (nb == 0 || nb > 1) {

    delete list;

    return UNDEF;

  }
  else {

    VId component = list->first();

    delete list;

    return component;

  }


}

VId MTG::findLastComponentAtScale(VId father, int sc) const {

  assert(existsVertex(father));
  assert(isValidScale(sc));
  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(father);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */
  if (vscale(father) >= sc) return UNDEF;

  VId x = father;

  do {

    x = findLastComponent(father);

    if (x == UNDEF) return UNDEF;

    father = x;

  } while(vscale(x) != sc);

  if (vscale(x) == sc) return x;
  else return UNDEF;

}



VId MTG::findFirstComponentAtScale(VId father, int sc) const {

  assert(existsVertex(father));
  assert(isValidScale(sc));

  /*
  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  int scl = vscale(father);
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    if (classScale(i) == scl) {
      for(register int j=0; j<clnb; j++) {
        if (classScale(j) == scl) assert(_header->less(i,j).max() < 2);
      }
    }
  }
  */

  if (vscale(father) >= sc) return UNDEF;

  VId x = father;

  do {

    x = findFirstComponent(father);

    if (x == UNDEF) return UNDEF;

    father = x;

  } while(vscale(x) != sc);

  if (vscale(x) == sc) return x;
  else return UNDEF;

}


VId MTG::findLastFinestElement(VId vtx) const {

  assert(existsVertex(vtx));

  VIdList* list = findLocalTopoRoots(vtx);
  assert(list);

  int nbroots = list->entries();

  if (nbroots == 0 || nbroots > 1) {
    delete list;
    return vtx;
  }
  else { // nbroots = 1

    assert (nbroots == 1);

    VId root = list->first();
    VId lastvtx = findLastComponent(root);

    delete list;

    if (lastvtx == UNDEF) return root;
    else return findLastFinestElement(lastvtx);

  }

}

// search among the complex ancestors X of loc one, Y,
// which has a successor and such that compoFather(X) == compoFather(Y).

VId MTG::findCoarsestSuccessorAtLoc(VId loc) const {

  assert(existsVertex(loc));

  // condition explained in mtg.h:
  // all the classes of scale scale(firstv) must have max(X,Y,<) <= 1
  /*
  int clnb = classNb();
  for (register int i=0; i<clnb; i++) {
    for(register int j=0; j<clnb; j++) {
      assert(_header->less(i,j).max() < 2);
    }
  }
  */

  VId X = compoFather(loc);

  if (X == mtgRoot()) return UNDEF;

  VIdList* tslist = topoSons(X,ANYLESS);
  assert(tslist);
  assert(tslist->entries() <= 1);

  if (tslist->entries() == 0) {
    delete tslist;
    return findCoarsestSuccessorAtLoc(X);
  }
  else { //  tslist->entries() == 1

    VId Y = tslist->first();

    delete tslist;

    if (compoFather(Y) == compoFather(X)) return Y;
    else findCoarsestSuccessorAtLoc(X);

  }

  return UNDEF;

}


VId MTG::findLocalTopoRoot(VId startv, EType etype) const {

  assert(existsVertex(startv));

  VId father = startv;
  VId cf = UNDEF;
  VId cfstartv = UNDEF;

  do {

    startv = father;
    cfstartv = compoFather(startv); // can be UNDEF
    father = topoFather(startv, etype);
    if (father != UNDEF) cf = compoFather(father);
    else cf = UNDEF;

  } while(father != UNDEF && cf == cfstartv);

  return startv;

}



VId MTG::findGlobalTopoRoot(VId startv, EType etype) const {

  assert(existsVertex(startv));

  VId father = startv;

  do {

    startv = father;
    father = topoFather(startv, etype);

  } while(father != UNDEF);

  return startv;

}


VIdList* MTG::findLocalTopoRoots(VId id) const {

  assert(existsVertex(id));

  VIdList* vlist = new VIdList;
  const VIdList* cslist = vertex(id).compoSons();

  if (cslist == NULL) return vlist;

  *vlist = *cslist;

  return vlist;

}



VIdList* MTG::findLocalTopoRootsAtScale(VId id, int scale) const {

  assert(existsVertex(id));
  assert(isValidScale(scale));

  int idscale = vscale(id);
  if (scale <= idscale) return 0;

  VIdList* reslist = new VIdList;
  assert(reslist);

  VIdList* rootlist = findLocalTopoRoots(id);

  VIdListIter next(*(VIdList*)rootlist);

  while(next()) {

    if (scale == idscale+1) reslist->append(next.key());
    else {

      VIdList* ltson = findLocalTopoRootsAtScale(next.key(), scale);

      VIdListIter nextltson(*ltson);

      while (nextltson()) {

        reslist->append(nextltson.key());

      }

      delete ltson;
    }

  }

  delete rootlist;

  return reslist;

}


VIdList* MTG::findGlobalTopoRootsAtScale(int scale) const {

  assert(isValidScale(scale));

  VIdList* vlist = new VIdList;
  assert(vlist);

  MTGVertexIter next((MTG*)this);

  while(next()) {

    VId vtx = next.key();

    if (vscale(vtx) == scale && topoFather(vtx, ANYTOPO) == UNDEF) {

      vlist->append(vtx);

    }

  }

  return vlist;

}

VId MTG::findCompoAncestorAtScale(VId x, int scale) const {

  assert(existsVertex(x));
  assert(isValidScale(scale));

  int xscale = vscale(x);

  if (xscale < scale) return UNDEF;

  if (xscale == scale) return x;
  else {

    VId compo = compoFather(x);

    if (compo == UNDEF) return UNDEF;
    else return findCompoAncestorAtScale(compo, scale);

  }

}

// Given a vertex v in the GTM, explore the compoancestor family
// of v, starting from compoFather(v) and return the first vertex whose
// vprefix is not its compofather (return the vertex which corresponds
// to the most precise vprefix on the topoFather of x

VId MTG::location(VId x) const {

  assert(existsVertex(x));

  int xscale = vscale(x);
  int xloc = vprefix(x);

  if (xloc == UNDEF) return UNDEF;
  if (isMTGRoot(xloc)) return UNDEF;

  int lscale = vscale(xloc);

  if (xscale <= lscale) return xloc;
  else return location(xloc);

}

VId MTG::findVertexByName_A(char cc, int index, VId loc, EType etype) {

  assert(existsVertex(loc));
  assert(isValidClass(cc));
  assert(isValidIndex(index));

  VClass c = classId(cc);
  int cscale = classScale(c);

  if (etype == SLASH) {

    VIdList* vlist = compoSons(loc);
    assert(vlist);

    VIdListIter vliter(*(VIdList*)vlist);

    while(vliter()) {

      VId son = vliter.key();

      // if (vclass(son) == c && vindex(son) == index) {
      // Modif le 26/8/96 car le test de meme vertex doit etre complete
      if (vclass(son) == c && vindex(son) == index && vprefix(son) == loc) {
        delete vlist;
        return son;
      }

    }

    delete vlist;

  }
  else
  if (etype == PLUS || etype == LESS || etype == PLUSPLUS || etype == LESSLESS)
  {

    // iterate through the list of compoAncestors(loc);
    MTGDepthFirstIter next(this, loc, &MTG::fathers, SLASH);

    while(next()) {

      VId father = next.key();
      int fscale = vscale(father);

      if (fscale < cscale) break;

      if (fscale == cscale) {

        const EIdList* elist = vertex(father).topoDaughters();

        if (elist) {

          EIdListIter eliter(*(EIdList*)elist);

          while(eliter()) {

            EId e = eliter.key();
            VId son = edge(e).son();

            if (edge(e).type() == etype &&
                vclass(son) == c &&
                vindex(son) == index &&
                vprefix(son) == loc)  return son;

          }
        }
      }

    }

  }
  else {

    assert(FALSE);

  }

  return UNDEF;

}


VId MTG::findVertexByName_B(char cc, int index, VId loc, EType etype) {

  assert(isValidClass(cc));
  assert(isValidIndex(index));
  assert(loc != UNDEF);
  assert(etype != LESSLESS && etype != PLUSPLUS);

  VClass c = classId(cc);

  if (etype == SLASH) {

    VIdList* vlist = findLocalTopoRoots(loc);
    assert(vlist);

    /*
       cerr << "\n/// local topo root(" << loc << ") = ";
       VIdListIter n(*vlist);
       while (n()) {
       cerr << n.key() << " | " << flush;
       }
       cerr << "." << endl;
    */

    VIdListIter vliter(*(VIdList*)vlist);

    VId root;

    while(vliter()) {

      root = vliter.key();

      VIdList* less_seq = findLocalLessSequence(root);
      assert(less_seq);

      VIdListIter n(*less_seq);

      VId son;

      while (n()) {
        son = n.key();

        if (vclass(son) == c && vindex(son) == index) {
          delete less_seq;
          delete vlist;
          return son;
        }
      }

      delete less_seq;

    }

    delete vlist;

    return UNDEF;

  }
  else
  if (etype == PLUS) {

    return findLabelInCarriedLocalLessSequenceAtLoc(loc, c, index);
  }
  else {

    return UNDEF;

  }

}

