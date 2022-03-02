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
 *       $Id: iter_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $
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

//typedef AmlBoolean VertexTester(MTG*, VId, void*);

//static const char rcsid[] = "$Id: iter_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $";


// ---------- Class  MTGVertexIter     -----------

AmlBoolean MTGVertexIter::operator+=(int n) {

  for(int i=0; i<n; i++) _cv++;

  return (_cv < _g->_v.entries());

}

// testFun est une fonction de test qui permet d'evaluer une expression sur un vertex.
// il est necessaire de passer g pour que la fonction puisse utiliser les primitives
// de travail sur un vertex ainsi que testFun
// L'iterateur se place sur le premier element trouve qui verifie la condition
// decrite par testFun. Si aucun element n'est trouve, la fonction renvoie FALSE
// et la position de l'iterateur est indeterminee.
/*
AmlBoolean 
MTGVertexIter::findNext(VertexTester _fun, void* _pdata) {

  // Note: Il semble que la syntaxe if ((*fun)(_g, _cv, pdata)) ... soit egalement
  // permise: c'est teste dans test1

  while((*this)()) if ((*_fun)(_g,_cv, _pdata)) return TRUE;

  return FALSE;

}
*/
// ---------- Class  MTGEdgeIter       -----------

AmlBoolean MTGEdgeIter::operator+=(int n) {

  for(int i=0; i<n; i++) _ce++;

  return (_ce < _g->_e.entries());

}

/*
AmlBoolean MTGEdgeIter::findNext(VertexTester fun, void* pdata) {

  while((*this)()) if ((*fun)(_g, _ce, pdata)) return TRUE;

  return FALSE;

}*/

// ---------- Class  MTGDepthFirstIter -----------

MTGDepthFirstIter::MTGDepthFirstIter(MTG* g, VId vstart, SonListFunc ff, EType type) {

  assert(g);
  _g = g;
  _s.push(vstart);
  _pmf = ff;
  _cv = UNDEF;
  _filter = type;

}

void MTGDepthFirstIter::push(VIdList* vlist) {

  VIdListIter next(*vlist);

  while(next()) {

    _s.push(next.key());

  }

}


// Recherche des ancetres en profondeur d'abord:

AmlBoolean MTGDepthFirstIter::operator()() {

  if (_s.isEmpty()) return FALSE;
  else {
    _cv = _s.pop();

    VIdList* vlist = (_g->*_pmf)(_cv, _filter);
    assert(vlist);

    if (!vlist->isEmpty()) {
      push(vlist);
    }
    delete vlist;
    return TRUE;
  }

}

AmlBoolean MTGDepthFirstIter::operator+=(int n) {

  for(int i=0; i<n; i++) if (!(*this)()) return FALSE;

  return TRUE;

}

/*
AmlBoolean 
MTGDepthFirstIter::findNext(VertexTester fun, void* pdata) {

  while((*this)()) if ((*fun)(_g, _cv, pdata)) return TRUE;

  return FALSE;

}
*/

void MTGDepthFirstIter::reset() {

  _s.clear();
  _cv = UNDEF;

}

// ---------- Class  MTGPostFixIter -----------

MTGPostFixIter::MTGPostFixIter(MTG* g, VId vstart, SonListFunc ff, EType type) {

  assert(g);
  _g = g;
  _s.push(vstart);
  _pmf = ff;
  _cv = UNDEF;
  _filter = type;

}

void MTGPostFixIter::push(VIdList* vlist) {

  VIdListIter next(*vlist);

  while(next()) {

    _s.push(next.key());

  }

}

void MTGPostFixIter::mark(VId x) {

  _used.push(x);

}

AmlBoolean MTGPostFixIter::isMarked(VId x) {

  if (_used.isEmpty()) return FALSE;

  if (_used.top() == x) {
    _used.pop();
    return TRUE;
  }
  return FALSE;

}


// Recherche des ancetres en profondeur d'abord, sous forme postfixee:

AmlBoolean MTGPostFixIter::operator()() {

  if (_s.isEmpty()) return FALSE;
  else {

    VId top = _s.top();

    if (!isMarked(top)) {

      // expansion to the leaves of top of stack

      VIdList* vlist = (_g->*_pmf)(top, _filter);
      assert(vlist);

      while(!vlist->isEmpty()) {
        mark(top);
        push(vlist);
        delete vlist;
        top = _s.top();
        vlist = (_g->*_pmf)(top, _filter);
      }
      delete vlist;
    }

    _cv = _s.pop();

  }
  return TRUE;
}

AmlBoolean MTGPostFixIter::operator+=(int n) {

  for(int i=0; i<n; i++) if (!(*this)()) return FALSE;

  return TRUE;

}

/*
AmlBoolean 
MTGPostFixIter::findNext(VertexTester fun, void* pdata) {

  while((*this)()) if ((*fun)(_g,_cv, pdata)) return TRUE;

  return FALSE;

}*/

void MTGPostFixIter::reset() {

  _s.clear();
  _used.clear();
  _cv = UNDEF;

}

/*
// ---------- Class  MTGBreadthFirstIter -----------

MTGBreadthFirstIter::MTGBreadthFirstIter(MTG* g, VId vstart, SonListFunc ff, EType type) {

  assert(g);
  _g = g;
  _q.insert(vstart);
  _pmf = ff;
  _cv = UNDEF;
  _filter = type;

}

void MTGBreadthFirstIter::push(VIdList* vlist) {

  VIdListIter next(*vlist);

  while(next()) {

    _q.insert(next.key());

  }

}


// Recherche des ancetres en profondeur d'abord:

AmlBoolean MTGBreadthFirstIter::operator()() {

  if (_q.isEmpty()) return FALSE;
  else {
    _cv = _q.get();

    VIdList* vlist = (_g->*_pmf)(_cv, _filter);
    assert(vlist);

    if (!vlist->isEmpty()) {
      push(vlist);
    }
    delete vlist;
    return TRUE;
  }

}
AmlBoolean MTGBreadthFirstIter::operator+=(int n) {

  for(int i=0; i<n; i++) if (!(*this)()) return FALSE;

  return TRUE;

}

AmlBoolean MTGBreadthFirstIter::findNext(VertexTester fun, void* pdata) {

  while((*this)()) if ((*fun)(_g,_cv, pdata)) return TRUE;

  return FALSE;

}


void MTGBreadthFirstIter::reset() {

  _q.clear();
  _cv = UNDEF;

}

*/
