/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): C. godin (godin@cirad.fr)
 *
 *       $Source$
 *       $Id: mtg_interface.cpp 3258 2007-06-06 13:18:26Z dufourko $
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


#include "mtg.h"

using namespace std;

VId MTG::si_mtgRoot() const {

  return mtgRoot();

}

VId MTG::si_complex(VId v, int s ) const { // s = scale

  if (!existsVertex(v)) return -1;
  if (!isValidScale(s)) return -1;

  return compoFather(v, s);

}

VId MTG::si_father(VId v, int s ) const {

  if (!existsVertex(v)) return -1;
  if (!isValidScale(s)) return -1;

  VId father;

  if (s == -1) {

    father = topoFather(v, ANYTOPO);

  }
  else {

    int loc = location(v);

    if (loc != -1)
       father = findCompoAncestorAtScale(loc, s);
    else father = -1;

    if (father == findCompoAncestorAtScale(v, s)) father = -1;

  }

  return father;

}

// VtxList is the STL counterpart of VIdList
// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_sons(VId v, int s , EType edgetype ) const {

  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  int argscale = vscale(v);

  if (s == -1 || argscale == s) {

    VIdList* sonlist = topoSons(v, edgetype);

    VIdListIter next(*sonlist);

    while (next()) {

      list->push_back(next.key());

    }
    delete sonlist;

  }
  else { // s > -1 && argscale != s

    if (argscale > s) {

      VId complex = findCompoAncestorAtScale(v, s);
      VIdList* sonlist = topoSons(complex, edgetype);

      // puis on filtre ceux qui n'ont pas la bonne location

      VIdListIter next(*sonlist);

      int loc;
      while (next()) {

        loc = location(next.key());

        if (loc != -1)
          complex = findCompoAncestorAtScale(loc, argscale);
        else complex = -1;

        if (complex == v) list->push_back(next.key());

      }
      delete sonlist;

    }
    else { // argscale < s

      VIdList* componentlist;
      VIdList* sonlist;

      componentlist = compoSons(v, s);

      assert(componentlist);

      VIdListIter next(*componentlist);

      while (next()) {

        sonlist = topoSons(next.key(), edgetype);
        if (sonlist) {
          VIdListIter next2(*sonlist);
          while (next2()) {
            if (findCompoAncestorAtScale(next2.key(), argscale)!=v)
              list->push_back(next2.key());
          }
          delete sonlist;
        }
      }

      delete componentlist;

    }

  }

  return list;

}


// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_ancestors(VId v) const {

  if (!existsVertex(v)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  VIdList* sonlist = topoAncestors(v, ANYTOPO);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}

// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_descendants(VId v, int s) const {

  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned


  VIdList* sonlist = topoDescendants(v, ANYTOPO);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}

// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_extremities(VId v, int s ) const {

  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  VIdList* sonlist = topoExtremities(v, ANYTOPO);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}

// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_components(VId v, int s) const {

  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  VIdList* sonlist = compoSons(v, s);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}


// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_componentRoots(VId v, int s) const {


  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  if (vscale(v) == s) {

    list->push_back(v);
    return list;

  }

  VIdList* sonlist;
  if (s == -1) sonlist = findLocalTopoRoots(v);
  else sonlist = findLocalTopoRootsAtScale(v, s);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}

// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_path(VId v1, VId v2) const {

  if (!existsVertex(v1)) return NULL;
  if (!existsVertex(v2)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  VIdList* sonlist = path(v1, v2);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}

// returns NULL if an error occured. Otherwise, returns a valid
// (may be empty) list

VtxList* MTG::si_axis(VId v, int s ) const {

  if (!existsVertex(v)) return NULL;
  if (!isValidScale(s)) return NULL;

  VtxList* list = new VtxList; // list of sons to be returned

  VId firstv = findGlobalTopoRoot(v, LESS);

  int vs = vscale(v);

  if (s != -1 && vs != s) {

    if (s < vs) firstv = findCompoAncestorAtScale(firstv, s);
    else firstv = findFirstComponentAtScale(firstv, s);

  }

  if (!existsVertex(firstv)) return NULL;

  VIdList* sonlist = findLessSequence(firstv);

  VIdListIter next(*sonlist);

  while (next()) {

    list->push_back(next.key());

  }
  delete sonlist;

  return list;

}


char MTG::si_class(VId v) const {

  if (!existsVertex(v)) return '\0';

  return symbol(v);

}

int MTG::si_index(VId v) const {

  if (!existsVertex(v)) return -1;

  return vindex(v);

}

int MTG::si_scale(VId v) const {

  if (!existsVertex(v)) return -1;

  return vscale(v);

}


char MTG::si_edgeType(VId v1, VId v2) const {

  if (!existsVertex(v1)) return '\0';
  if (!existsVertex(v2)) return '\0';

  return edgeSymbol(edgeType(v1, v2));

}


// FIndex is an index defined in defs.h
// which defines to the ith attribute defined in a MTG

const Feature* MTG::si_feature(VId v, FIndex i) const {

  if (!existsVertex(v)) return NULL;

  return feature(v, i, LUNDEF);

}

// Any attribute can also be accessed throught its name:

const Feature* MTG::si_feature(VId v, string fname) const {

  if (!existsVertex(v)) return NULL;

  /// finds the feature index of the feature with name name. UNDEF if not found.
  int i = fNameIndex(fname.c_str());

  if (i == UNDEF) return NULL;

  return feature(v, i, LUNDEF);

}


const bool MTG::si_isDefined(Feature* f) const {

  assert(f != NULL);

  if (f->i == -1) return false;
  else return true;

}


  // FType is an enum defining the type of a feature
  // defined in defs.h
  //
  // typedef enum {
  // ALPHA, INTEGER, REAL,
  // DDMM, DDMMYY, MMYY, DDMMTIME, DDMMYYTIME,
  // GEOMETRY,
  // APPEARANCE,
  // GENERIC
  // } FType;

const FType MTG::si_fType(FIndex i) const {

  if (!existsFIndex(i)) return (FType)-1;

  return fType(i);

}

int MTG::si_order(VId v) const {

  if (!existsVertex(v)) return -1;

  VId v1 = findGlobalTopoRoot(v, ANYTOPO);

  return pathEdgeNb(v1, v, PLUS);

}

int MTG::si_rank(VId v) const {

  if (!existsVertex(v)) return -1;

  VId v1 = findGlobalTopoRoot(v, LESS);

  return pathLength(v1, v, LESS);

}



VId MTG::si_defineSubTreeRoot(VId vtx, int scale) const {

  VId ret = -1;

  if (existsVertex(vtx) == TRUE) {

    if (scale==-1)
    {
      scale=vscale(vtx)+1;
    }

    VtxList* rootlist = si_componentRoots(vtx,scale);

    if (rootlist) {

      if (rootlist->size() != 1) {

        cerr << "Non unique vertex component of " << vtx << " at scale " << scale << " ..." << endl;
        delete rootlist;

      }
      else ret = (*rootlist)[0];
      delete rootlist;


    }
    else {
      cerr << " An error occured while computing the roots of " << vtx << " at scale " << scale << " ..." << endl;
      delete rootlist;
    }

  }
  else {
    cerr << " Vertex " << vtx << " does not exist ..." << endl;
  }

  return ret;

}



