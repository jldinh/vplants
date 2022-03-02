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
 *       $Id: mtg.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include <stdlib.h>
#include <math.h>

#include <strstream>

#include <fstream>

#include "tool/rw_tokenizer.h"
//#include <rw/ctoken.h>

#include "error.h"
#include "mtg.h"
#include "parser_dec.h"

// OLD INCLUDES
//#include "GEOM/geom_geometry.h"
//#include "GEOM/scne_shape.h"
#include "plantgl/pgl_geometry.h"
PGL_USING_NAMESPACE


#if 0
#define DEBUGMTG
#endif

#ifdef _WIN32
#define srandom srand
#endif

using namespace std;

//-----------------------------------------
//---------------- MTG --------------------
//-----------------------------------------

int MTG::binaryStoreSize() const {

  register int count = sizeof(_header) +
  sizeof(_v) +
  sizeof(_e) +
  sizeof(_fs);

  // arrays

  for (register int i1=0; i1<_v.length(); i1++) {

    count += vertex(i1).binaryStoreSize();

  }
  for (register int i=0; i<_e.length(); i++) {

    count += edge(i).binaryStoreSize();

  }

  count += sizeof(Vertex) * (_v.entries()-_v.length());
  count += sizeof(Edge) * (_e.entries() - _e.length());

  count += sizeof(Feature) * _fs.featNbPerFSet() * _fs.entries();

  return count;

}

// ------------ Private members ------------


EId MTG::topoMother(VId id, EType filter) const {

  assert(existsVertex(id));

  EId me = vertex(id).topoMother();

  if (me != UNDEF) {
    if(filter == ANYTOPO) return me;
    else
    if (*(edge(me).type() & filter)) return me;
    else return UNDEF;
  }
  else return UNDEF;

}


EIdList* MTG::topoDaughters(VId id, EType filter) const {

  assert(existsVertex(id));

  const EIdList* dlist = vertex(id).topoDaughters();

  EIdList* elist = new EIdList;

  if (dlist == NULL) return elist;

  // cast away const because of the RW Iterator Constructor !!!!
  EIdListIter next(*(EIdList*)dlist);

  assert(elist);

  while (next()) {
    if(filter != ANYTOPO) {
      if(*(edge(next.key()).type() & filter)) elist->append(next.key());
    }
    else elist->append(next.key());
  }
  return elist;

}

void MTG::addCompoSon(VId complex, VId son) {

  assert(existsVertex(complex));
  assert(existsVertex(son));

  const VIdList* cslist = vertex(complex).compoSons();

  if (cslist) {
    if (!(cslist->contains(son))) {
      vertex(complex).addCompoSon(son);
    }
  }
  else vertex(complex).addCompoSon(son);

}

void MTG::removeCompoSon(VId complex, VId son) {

  assert(existsVertex(complex));
  assert(existsVertex(son));

  // No check is done for the existence of son in this composonlist
  // No error is reported if it fails.

  vertex(complex).removeCompoSon(son);

}

void MTG::removeEdge(VId id1, VId id2) {

  assert(existsVertex(id1));
  assert(existsVertex(id2));

  EId eid = topoEdge(id1, id2);

  vertex(id2).removeTopoMother();
  vertex(id1).removeTopoDaughter(eid);

  VId cf1 = compoFather(id1);
  VId cf2 = compoFather(id2);

  if (cf1 == cf2) addCompoSon(cf1, id2);

#ifdef DEBUGFORMB

  EType et = edge(eid).type();

  if (et == PLUS) cerr << "\n----> + edge removed : (" << id1 << "," << id2 << ")" << endl;
  else if (et == LESS) cerr << "\n----> + edge removed : (" << id1 << "," << id2 << ")" << endl;
  else if (et == PLUSPLUS) cerr << "\n----> + edge removed : (" << id1 << "," << id2 << ")" << endl;
  else if (et == LESSLESS) cerr << "\n----> + edge removed : (" << id1 << "," << id2 << ")" << endl;
  else assert(FALSE);

#endif

  // freeEdgeStackAdd(eid);

}


// if vertex id1 and id2 are connected, then they can be
// disconnected by cutting any edge between location(id2)
// and their corresponding topoSon down to scale = scale(id1)


void MTG::cutVertexConnection(VId id1, VId id2) {

  assert(existsVertex(id1));
  assert(existsVertex(id2));

#ifdef DEBUGFORMB
  cerr << "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><" << endl;
  cerr << "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><" << endl;
  cerr << "     Cutting connection: " << id1 << "," << id2 << endl;
#endif

  int sc1 = vscale(id1);
  int sc2 = vscale(id2);

  assert(sc1 == sc2);

  EType et = edgeType(id1, id2);

  assert(et != LESSLESS && et != PLUSPLUS);

  if (et != NONE) {

    VId loc = location(id2);
    assert(vscale(loc) >= sc1);

    VIdList* slist;

    for (VId vtx = loc; vscale(vtx) >= sc1; vtx = compoFather(vtx)) {

      slist = topoSons(vtx, et);
      assert(slist);

      VIdListIter next(*slist);
      VId son;

      while(next()) {

        son = next.key();

        if (isCompoAncestorOf(id2, son)) {
          removeEdge(vtx, son);
          break; // only one edge by scale has to be removed
        }

      }
      delete slist;
    }
  }
#ifdef DEBUGFORMB
  cerr << "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><" << endl;
  cerr << "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><" << endl;
#endif

}


// ----------------
// MTG Constructors
// ----------------

void MTG::initMTG(int scale_nb,
                  ClassDef* cldef,
                  FSetDef* fsetdef,
                  int line_nb)
{

  assert(cldef);
  assert(fsetdef);

  _fs.resize(line_nb, fsetdef->fNb());

  _header = new MTGHeader(scale_nb, cldef, fsetdef, this);
  assert(_header);

  // add the root vertex as vertex 0;
  // vertex of class 0 and index 0

  VClass vcl = classId('$');
  VId root = addVertex(vcl, 0);
  if (isDefFeature(DATE_F)) {
    Feature* f = new Feature[featureNb()];
    for(int i=0; i<featureNb(); i++) f[i].i = (unsigned long)LUNDEF;
    f[fIndex(DATE_F)].i = 0; // 01/01/1900
    addFSet(0,f);
    delete [] f;
  }

  // This must be the first vertex in the graph
  assert(root == 0);

}

MTG::MTG(const char* filename, int vtxsize, ostream& errstream, int maxerrornb, int resize) {

  int nb_of_lines = 0;

  char tmp[MAXLINELENGTH];
  FILE* input;

  /* Refaire cette partie en C++ */

  assert(filename != NULL);

  _filename = filename;
  _header = 0;

  input = fopen(filename, "r");

  if (!input) {
    cerr << "Cannot read file : "
    << filename
    << endl;
    _error_nb = 1;
  }
  else {

    long int pos = ftell(input); /* sauvegarde de la position courante ds input */

    fseek(input, 0, SEEK_SET);
    while (fgets(tmp, MAXLINELENGTH, input)) {
      nb_of_lines++;
    }

    fprintf(stderr, "\nLoading File %s (%d lines)\n\n", filename, nb_of_lines);

    /* on restitue la position initiale de input */
    fseek(input, pos, SEEK_SET);

    _estimated_size = vtxsize > 0 ? vtxsize :  nb_of_lines * 5;

    // If the _estimated_size is exceeded, the arrays are resized automatically
    // but this process is usually unefficient
    _v.resize(_estimated_size);
    _e.resize(_estimated_size);

    yyin = input;
    ErrorList* errlist = parseMTG(this, nb_of_lines,errstream,maxerrornb); // call the parser
    assert(errlist);

    _error_nb = errlist->entries();

    if (_error_nb == 0) {

      cerr << "Parsing completed Ok" << endl;
      cerr << "Adjusting MTG size ... " << flush;

      // stretch the mtg at its optimum size
      if (resize) {

        _v.resize(_v.entries());
        _e.resize(_e.entries());
        _fs.resize(_fs.entries());

        cerr << "Ok" << endl;
      }

    }
    else {

#ifdef DEBUGCHECKERROR
      cerr << "... Parsing aborted with " << _error_nb << " errors :" << endl;
#endif

    }

    cleanErrorList();

    fclose(input);
  }
}


MTG::~MTG() {

  delete _header;

}


MTG::MTG(char* filename, int nodenb, int seed) {

  ofstream filest(filename);

  if(!filest) {
    cerr << "cannot open file " << filename << endl;
    _error_nb = 1;
  }
  else {

    filest << "CODE:" << '\t';
    filest << "FORM-A" << endl;

    filest << "\nCLASSES:" << endl;
    filest << "SYMBOL\tSCALE\tDECOMPOSITION\tINDEXATION\tDEFINITION" << endl;

    filest << "A\t1\tFREE\tFREE\tEXPLICIT" << endl;
    filest << endl;

    filest << "DESCRIPTION:" << endl;
    filest << "LEFT\tRIGHT\tRELTYPE\tMAX" << endl;

    filest << "A\tA\t+\t?" << endl;
    filest << "A\tA\t<\t1" << endl;
    filest << endl;

    filest << "FEATURES:" << endl;
    filest << "NAME\tTYPE" << endl;
    filest << endl;

    filest << "MTG:" << endl;

    filest << "ENTITY-CODE" << endl;

    srandom(seed);

    for (int i=1; i<nodenb; i++) {

      long newfathernode = randomNbInRange(0,i-1);

      filest << "v" << i << "\tv" << newfathernode << "\t+\tA" << i << endl;

    }

    cerr << "File created : " << filename << endl;

    filest.close();

  }

}

// ---------------- General public members  ------------------

char MTG::edgeSymbol(EType e) const {

  if (e == PLUS || e == PLUSPLUS) return '+';
  if (e == LESS || e == LESSLESS) return '<';
  if (e == SLASH) return '/';

  return '?';

}

// test si father est un ascendant complex de x (vrai si father == x)

AmlBoolean MTG::isCompoAncestorOf(VId father, VId x) const {

  if (existsVertex(father) && existsVertex(x)) {
    if (x == father) return TRUE;
    VId f = compoFather(x);
    if (isCompoAncestorOf(father, f)) return TRUE;
  }
  return FALSE;

}

// test si son est un descendant topologique de x (vrai si son == x)

AmlBoolean MTG::isCompoDescendantOf(VId son, VId x) const {

  if (existsVertex(son) && existsVertex(x)) {

    if (x == son) return TRUE;

    VIdList* flist = compoSons(x);
    VIdListIter next(*flist);

    while (next()) {
      if (isCompoDescendantOf(son, next.key())) {
        delete flist;
        return TRUE;
      }
    }

    delete flist;
    return FALSE;
  }
  return FALSE;

}

// test si father est un ascendant topologique de x (vrai si father == x)

AmlBoolean MTG::isTopoAncestorOf(VId father, VId x, EType filter) const {

  if (existsVertex(father) && existsVertex(x)) {

    if (x == father) return TRUE;

    VId f = topoFather(x, filter);

    if (isTopoAncestorOf(father, f, filter)) return TRUE;

  }
  return FALSE;

}

// test si son est un descendant topologique de x (vrai si son == x)

AmlBoolean MTG::isTopoDescendantOf(VId son, VId x, EType filter) const {

  if (existsVertex(son) && existsVertex(x)) {

    if (x == son) return TRUE;

    VIdList* flist = topoSons(x, filter);
    VIdListIter next(*flist);

    while (next()) {
      if (isTopoDescendantOf(son, next.key(), filter)) {
        delete flist;
        return TRUE;
      }
    }

    delete flist;
    return FALSE;
  }
  return FALSE;

}

// is id root at scale scale(id) ?
AmlBoolean MTG::isGlobalTopoRoot(VId id) const {

  if (existsVertex(id)) {

    if (isMTGRoot(id)) return TRUE;

    VId f = topoFather(id, ANYTOPO);

    if (f != UNDEF) return FALSE;
    else return TRUE;

  }
  else return FALSE;

}

// is id root of its compoFather ?
AmlBoolean MTG::isLocalTopoRoot(VId id) const {

  if (existsVertex(id)) {

    VId f = topoFather(id, ANYTOPO);

    if (compoFather(id) != compoFather(f)) return TRUE;
    else return FALSE;

  }
  else return FALSE;

}



// --------- Les Vertex ----------

EId MTG::topoEdge(VId v1, VId v2) const {

  assert(existsVertex(v1) && existsVertex(v2));

  int s1 = vscale(v1);
  int s2 = vscale(v2);

  if (s1==s2 || s2==0) {

    VId f = topoFather(v2, ANYTOPO);

    if(f == v1) return topoMother(v2, ANYTOPO);
    else return UNDEF;

  }
  else return UNDEF;

}

EType MTG::edgeType(VId v1, VId v2) const {

  assert(existsVertex(v1) && existsVertex(v2));

  EId e = topoEdge(v1,v2);

  if (existsEdge(e)) return edge(e).type();
  else if (scaleEdge(v1,v2)) return SLASH;

  return NONE;

}

AmlBoolean MTG::scaleEdge(VId v1, VId v2) const {

  if (existsVertex(v1) && existsVertex(v2)) {

    int s1 = vscale(v1);
    int s2 = vscale(v2);

    if (s1 != 0 && s1 == s2-1) { // Compo edge

      if (topoFather(s2, ANYTOPO) == s1) return TRUE;
      else return FALSE;

    }
    else return FALSE;

  }
  else return FALSE;

}

VId MTG::topoFather(VId id, EType filter) const {

  assert(existsVertex(id));

  EId me = topoMother(id, filter);
  //cerr << "topoMother(" << id << "," << filter << ") = " << me << endl;

  if (me != UNDEF) return edge(me).father();
  else return UNDEF;

}

VId MTG::localTopoFather(VId id, EType filter) const {

  assert(existsVertex(id));

  VId tf = topoFather(id, filter);

  if (tf != UNDEF && (compoFather(id) != compoFather(tf))) tf = UNDEF;

  return tf;

}

VIdList* MTG::topoSons(VId id, EType filter) const {

  assert(existsVertex(id));

  EIdList* elist = topoDaughters(id, filter);
  assert(elist);

  EIdListIter next(*(EIdList*) elist);
  VIdList* vlist = new VIdList;
  assert(vlist);

  while(next()) {
    vlist->append(edge(next.key()).son());
  }
  delete elist;

  return vlist;

}


VIdList* MTG::localTopoSons(VId id, EType filter) const {

  assert(existsVertex(id));

  VId cf = compoFather(id);

  EIdList* elist = topoDaughters(id, filter);
  assert(elist);

  EIdListIter next(*(EIdList*) elist);
  VIdList* vlist = new VIdList;
  assert(vlist);

  // cerr << "\n possible sons(" << id << ": ";

  while(next()) {

    // cerr << edge(next.key()).son() << "," ;

    if (compoFather(edge(next.key()).son()) == cf) vlist->append(edge(next.key()).son());
  }
  delete elist;

  // cerr << endl;

  return vlist;

}

VIdList* MTG::topoDescendants(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  newlist->append(id);

  VIdList* lslist = topoSons(id, filter);
  assert(lslist);

  VIdListIter next(*lslist);

  while(next()) {

    VIdList* list = topoDescendants(next.key(), filter);
    assert(list);

    VIdListIter nextcat(*list);
    while(nextcat()) {
      newlist->append(nextcat.key());
    }
    delete list;
  }

  delete lslist;

  return newlist;

}

VIdList* MTG::topoExtremities(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  VIdList* lslist = topoSons(id, filter);
  assert(lslist);

  if (lslist->entries() == 0) newlist->append(id);

  else {

    VIdListIter next(*lslist);

    while(next()) {

      VIdList* list = topoExtremities(next.key(), filter);
      assert(list);

      VIdListIter nextcat(*list);
      while(nextcat()) {
        newlist->append(nextcat.key());
      }
      delete list;
    }
  }

  delete lslist;

  return newlist;

}

VIdList* MTG::localTopoExtremities(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  VIdList* lslist = localTopoSons(id, filter);
  assert(lslist);

  if (lslist->entries() == 0) newlist->append(id);

  else {

    VIdListIter next(*lslist);

    while(next()) {

      VIdList* list = localTopoExtremities(next.key(), filter);
      assert(list);

      VIdListIter nextcat(*list);
      while(nextcat()) {
        newlist->append(nextcat.key());
      }
      delete list;
    }
  }

  delete lslist;

  return newlist;

}

VIdList* MTG::topoAncestors(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  newlist->append(id);

  VId vtx = id;

  while (existsVertex(vtx = topoFather(vtx, filter))) newlist->append(vtx);

  return newlist;

}

VIdList* MTG::localTopoDescendants(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  newlist->append(id);

  VIdList* lslist = localTopoSons(id, filter);
  assert(lslist);

  // cerr << "\n/// localTopoSon(" << id << ") = ";

  VIdListIter next(*lslist);

  while(next()) {

    // cerr << next.key() << " | " << flush;

    VIdList* list = localTopoDescendants(next.key(), filter);
    assert(list);

    VIdListIter nextcat(*list);
    while(nextcat()) {
      newlist->append(nextcat.key());
    }
    delete list;
  }

  // cerr << endl;

  delete lslist;

  return newlist;

}

VIdList* MTG::localTopoAncestors(VId id, EType filter) const {

  assert(existsVertex(id));

  VIdList* newlist = new VIdList;
  assert(newlist);

  newlist->append(id);

  VId vtx = id;

  while (existsVertex(vtx = localTopoFather(vtx, filter))) newlist->append(vtx);

  return newlist;

}

VIdList* MTG::topoSonsWithClass(VId id, VClass cl, EType filter) const {

  assert(existsVertex(id));

  EIdList* elist = topoDaughters(id, filter);
  assert(elist);

  EIdListIter next(*(EIdList*) elist);
  VIdList* vlist = new VIdList;
  assert(vlist);

  while(next()) {
    VId son = edge(next.key()).son();
    if (cl == vclass(son)) vlist->append(son);
  }
  delete elist;

  return vlist;

}

// return the list of vertex between v1 and v2: which is not empty
// only if v1 is a topoancestor of v2
// path(v1,v1) --> {v1}
// path(v1,v4) --> {v1,v2,v3,v4}
// path(v1,w0) --> {}              where v1 is not an ancestor of w0

VIdList* MTG::path(VId v1, VId v2) const {

  assert(existsVertex(v1));
  assert(existsVertex(v2));

  VIdList* vlist = new VIdList;
  assert(vlist);

  register VId father = v2;
  vlist->append(v2);

  while(father != v1) {

    father = topoFather(father,ANYTOPO);

    if (father != UNDEF) vlist->prepend(father);
    else { // UNDEF is encoutered and v1 has not been reached
      vlist->clear();
      break;
    }

  }

  // turn the list

  return vlist;

}

int MTG::pathLength(VId v1, VId v2, EType filter) const {

  assert( *(ANYTOPO & filter));

  VId f = v2;

  int dist = 0;

  if (v1 == v2) return 0;

  while(f != UNDEF) {

    f = topoFather(f, filter);
    dist++;
    if (f == v1) return dist;

  }

  return UNDEF;

}


int MTG::algPathLength(VId v1, VId v2, EType filter) const {

  int posdist = pathLength(v1,v2,filter);

  if (posdist == UNDEF) {
    int negdist = pathLength(v2,v1,filter);
    if (negdist == UNDEF) return UNDEF;
    else return -(negdist);     // returns a negative value
  }
  else return posdist;

}


int MTG::pathEdgeNb(VId v1, VId v2, EType filter) const {

  assert( *(ANYTOPO & filter));

  register VId f2 = v2;
  register VId f1;

  int dist = 0;

  if (v1 == v2) return 0;

  while(f2 != UNDEF) {

    f1 = topoFather(f2, ANYTOPO);

    if (f1 == UNDEF) break;

    if (edgeType(f1,f2) == filter) dist++;

    if (f1 == v1) return dist;

    f2 = f1;

  }

  return UNDEF;

}


int MTG::algPathEdgeNb(VId v1, VId v2, EType filter) const {

  int posorder = pathEdgeNb(v1,v2,filter);

  if (posorder == UNDEF) {
    int negorder = pathEdgeNb(v2,v1,filter);
    if (negorder == UNDEF) return UNDEF;
    else return -(negorder);    // returns a negative value
  }
  else return posorder;

}


VId MTG::compoFather(VId id) const {

  assert(existsVertex(id));

  return vertex(id).compoFather();

}

VId MTG::compoFather(VId id, int scale) const {

  assert(existsVertex(id));

  do {

    id = compoFather(id);

  }
  while (existsVertex(id) && vscale(id) != scale);

  return id;

}

// the list of composons contained in id is the list
// of all components of id which have no topofather
// This list has to be expanded before returning
// the complete list of compoSons(id)

VIdList* MTG::compoSons(VId id) const {

  assert(existsVertex(id));

  const VIdList* rootlist = vertex(id).compoSons();

  VIdList* reslist = new VIdList;
  assert(reslist);

  if (rootlist) {

    VIdListIter next(*(VIdList*)rootlist);

    while(next()) {

      VIdList* ltson = localTopoDescendants(next.key(), ANYTOPO);
      assert(ltson);

      VIdListIter nextltson(*ltson);

      while (nextltson()) {

        reslist->append(nextltson.key());

      }

      delete ltson;

    }
  }
/*
  cerr << "\n/// compoSons(" << id << ") = ";
  VIdListIter n(*reslist);
  while (n()) {
    cerr << n.key() << " | " << flush;
  }
  cerr << "." << endl;
*/

  return reslist;

}



VIdList* MTG::compoSons(VId id, int scale) const {

  assert(existsVertex(id));

  int idscale = vscale(id);
  if (scale <= idscale) return new VIdList;

  VIdList* reslist = new VIdList;
  assert(reslist);

  VIdList* compolist = compoSons(id);

  if (compolist) {

    VIdListIter next(*(VIdList*)compolist);

    while(next()) {

      if (scale == idscale+1) reslist->append(next.key());
      else {

        VIdList* ltson = compoSons(next.key(), scale);
        assert(ltson);

        if (ltson->entries()) {

          VIdListIter nextltson(*ltson);

          while (nextltson()) {

            reslist->append(nextltson.key());

          }

        }

        delete ltson;

      }

    }

    delete compolist;

  }

  return reslist;

}



VIdList* MTG::fathers(VId id, EType filter) const {

  assert(existsVertex(id));
  assert( filter == SLASH || *(~(filter & SLASH))); // cannot be both topo and compo

  VIdList* flist = new VIdList;
  VId v;

  if (*(filter & ANYTOPO)) {

    v = topoFather(id, filter);
    if (v != UNDEF) flist->append(v); // liste a un seul element

  }
  else {
    if (*(filter & SLASH)) {

      v = compoFather(id);
      if (v != UNDEF) flist->append(v); // liste a un seul element

    }
  }

  return flist; // 1 or 0 elements

}

VIdList* MTG::sons(VId id, EType filter) const {

  assert(existsVertex(id));



  if (*(filter & ANYTOPO)) {
    return topoSons(id, filter);
  }
  if (*(filter & SLASH)) {
    return compoSons(id);
  }

  return new VIdList; // empty VIdList by default

}


VId MTG::vprefix(VId id) const {

  assert(existsVertex(id));

  return vertex(id).vprefix();

}

static void reverseStringTokens(const RWCString& s_in, RWCString& s_out) {

  StringStack tokstack; // pile de tokens

  RWCTokenizer next(s_in);

  RWCString token;

  while (!(token = next()).isNull()) tokstack.push(token);

  while(!tokstack.isEmpty()) s_out += tokstack.pop();

}

const char* MTG::edgeLabel(EId fe) const {

  EType et = edge(fe).type();

  if (et == PLUS) return "+";
  else if (et == LESS) return "<";
  else if (et == PLUSPLUS) return "++";
  else if (et == LESSLESS) return "<<";
  else return NULL;

}

//
// this function builds the string of characters describing the vertex
// id from the origine id0. If id0 belongs to the loc ancestors of id
// the relative name of id wrt id0 is returned. Else, the absolute name
// of id in the MTG is returned.
//
//
// A vertex name is made as follows:
//
// let x be the vertex at hand,
// let y be a vprefix of x (y = loc(x))
// let e be the edge between x and z
//
//      name(x) = name(y).name(type(e)).name(label(x))
//
//      with
//
//      name(label(x)) = name(vclass(x)).name(index(x));

RWCString* MTG::relativeName(VId id0, VId id) const {

  assert(existsVertex(id));
  assert(existsVertex(id0));

  RWCString tmp_name;

  VId mtgroot = mtgRoot();
  if (id == mtgroot) return NULL; // no name for the global mtg itself

  VId loc;

  do {

    loc = vprefix(id);

    int scale = vscale(loc);
    if (vscale(id) == vscale(loc)+1) {
      tmp_name += "/";
    }
    else {

      if (vscale(id) > vscale(loc)+1) return NULL;

      EId fe = topoMother(id, ANYTOPO);

      if (fe == UNDEF) {

        return NULL;

      }
      else {

        const char* elab = edgeLabel(fe);
        if (elab) tmp_name += elab;
        else return NULL;

      }
    }


    // vclass and index have to be added to the name

    // vclass
    char c = classSymbol(vclass(id));
    tmp_name.append(&c, 1);

    // index
    char stg[10];
    ostrstream ost(stg,10);
    ost << vindex(id);
    ost << " "; // a blanc is added as a token separator in tmp_name;
    ost << '\0';

    tmp_name += stg;

    id = loc;

  } while (loc != mtgroot && loc != id0);

  RWCString* name = new RWCString;

  reverseStringTokens(tmp_name, *name);

  return name;

}

// --------------- FONCTIONS DE VISUALISATION -----------


ostream& MTG::printTopoSons(ostream& o, VId i) const {

  if(existsVertex(i)) {

    VIdList* slist = topoSons(i, ANYTOPO);
    assert(slist);

    VIdListIter next(*slist);

    if (slist) {
      o << "\tsons --> ";
      while (next()) {

        o << vertex(next.key()) << endl;

      }

      delete slist;
      return o;
    }
    else return o << "\tsons --> ANY";
  }

  return o;
}

ostream& MTG::printTopoFather(ostream& o, VId i) const {

  if (existsVertex(i)) {

    VId f = topoFather(i, ANYTOPO);

    if (existsVertex(f)) {
      o << "\ttopological father ("<< i << ") --> " << vertex(f);
    }
    else {
      o << "\ttopological father ("<< i << ") --> " << ANY;
    }

    o << endl;

  }

  return o;

}

ostream& MTG::printCompoFather(ostream& o, VId i) const {

  if (existsVertex(i)) {

    VId f = compoFather(i);

    if (existsVertex(f)) {
      o << "\tcomplex     father ("<< i << ") --> " << vertex(f);
    }
    else {
      o << "\tcomplex     father ("<< i << ") --> " << ANY;
    }

    o << endl;

  }


  return o;

}

ostream& MTG::printVertex(ostream& o) const {

  for(int i=0; i< _v.entries(); i++) {

    o << "vertex #" << i << " (" << classSymbol(vclass(i)) << vindex(i) << "): " << endl;
    o << vertex(i);

    int fnb = featureNb();
    FSetId fset = firstFSet(i);

    if (existsFSetId(fset)) {

      o << "\tfset      = ";

      for (int j=0; j<fnb; j++) {

        switch(fType(j)) {

        case INTEGER:
          if (feature(fset,j).i == (unsigned long)LUNDEF) o << " ";
          else o << feature(fset,j).i << " ";
          break;

        case REAL:
          if (feature(fset,j).i == (unsigned long)LUNDEF) o << " ";
          else o << feature(fset,j).r << " ";
          break;

        case ALPHA:
          if (feature(fset,j).i == (unsigned long)LUNDEF) o << " ";
          else o << feature(fset,j).s << " ";
          break;
/*
        case DATE:
          o << feature(fset,j).i << " ";
          break;
*/

        case GEOMETRY:
        case APPEARANCE:
        case GENERIC:
          if (feature(fset,j).i == (unsigned long)LUNDEF) o << " ";
          else o << feature(fset,j).p << " ";
          break;
        default:
          if (feature(fset,j).i == (unsigned long)LUNDEF) o << " ";
          else o << feature(fset,j).i << " ";
          break;

        }

      }

      o << endl;

    }


    VIdList* sons = topoSons(i, ANYTOPO);
    assert(sons);

    if (sons->entries()==0) {
      delete sons;
      continue;
    }

    o << "\ttopo sons =";
    VIdListIter next(*sons);

    while(next()) o << " " << next.key();

    o << endl << endl;

    delete sons;

  }

  return o;

}

ostream& MTG::printEdge(ostream& o) const {

  for(int i=0; i< _e.entries(); i++) {
    o << "edge #" << i << " : " << edge(i) << endl;
  }

  return o;
}

ostream& MTG::printStat(ostream& o) const {

  o << "\n\nMTG STATs:" << endl;
  o << "sizeof(mtg)    = " << binaryStoreSize() << " Bytes" << endl;
  o << "sizeof(Empty Vertex) = " << sizeof(Vertex) << " Bytes" << endl;
  o << "sizeof(Empty Edge)   = " << sizeof(Edge) << " Bytes" << endl;
  o << "sizeof(FSet)         = " << sizeof(Feature) * _fs.featNbPerFSet() << " Bytes" <<
  "\t nb of features per FSet : " << _fs.featNbPerFSet() << endl << endl;

  o << "Nb vertex      = " << _v.entries() << "\tentries = " << _v.entries() << " vertex" << endl;
  o << "Nb edges       = " << _e.entries() << "\tentries = " << _e.entries() << " edges" << endl;
  o << "Nb featsets    = " << _fs.fsetLength() << "\tentries = " << _fs.entries() << " feature sets" << endl;

  o << endl;

  return o;

}

ostream& MTG::displayOneLine(ostream& o) const {

  o << "vtxnb=" << _v.entries() <<
  ", edgenb=" << _e.entries() <<
  ", levelnb=" << scaleNb() <<
  ", featurenb=" << _fs.fsetLength() <<
  ", bytesize=" << binaryStoreSize();

  return o;

}

ostream& MTG::print(ostream& o) const {

  _header->print(o);

  printVertex(o);
  printEdge(o);

  return o;

}

ostream& MTG::printAll(ostream& o) const {

  printStat(o);
  print(o);

  return o;

}


ScenePtr MTG::shape(int scale, VId root) const {

  assert(isValidScale(scale));

  // cerr << "Root  = " << root << endl;
  // cerr << "Scale = " << scale<< endl;

  if (!existsVertex(root)) root = mtgRoot(); // the whole graphe is considered if not specified otherwise

  ScenePtr scene(new Scene);  // to store the resulting shape list
  //ShapeList shapelist;

  FIndex findex = -1;

  // finds the index of the first feature being of type GEOMETRY. UNDEF if not found.
  FIndex geom_ind = fTypeIndex(GEOMETRY);
  // cerr << "attribut GEOMETRY " << geom_ind << endl;

  // finds the index of the first feature being of type SHAPE. UNDEF if not found.
  FIndex shape_ind = fTypeIndex(GENERIC);

  FIndex mat_ind = fTypeIndex(APPEARANCE);
  // cerr << "attribut APPEARANCE " << mat_ind << endl;

  // if no GEOMETRY attribute is defined, the shape list will be empty
  if (geom_ind != UNDEF || (shape_ind != UNDEF && geom_ind < shape_ind)) {

    VIdList* vtxlist = compoSons(root, scale);

    if (vtxlist) {

      VIdListIter next(*vtxlist);

      VId vtx;

      AppearancePtr default_mat(new Material("Default_Mtg_1",Color3(255,204,204),
                                             0.5,
                                             Color3((uchar_t)0),
                                             Material::DEFAULT_EMISSION,
                                             0,
                                             0));
      default_mat->setName("MTGDefault");
      GeometryPtr pgeom;
      AppearancePtr pmat = default_mat;

      //Printer pp;
      //Printer pp(cerr,cerr,cerr);

      while(next()) {

        // gets the GEOMETRY and the MATERIAL Attributes of the vertex
        vtx = next.key();

        const Feature* pf = feature(vtx, geom_ind, LUNDEF);

        if (pf && pf->i == (unsigned long)LUNDEF) continue;
        else if (pf) {
          pgeom = dynamic_pointer_cast<Geometry>(*(SceneObjectPtr*)pf->p); // replace void* by the correct type

          if(pgeom){
              const Feature* pf2 = feature(vtx, mat_ind, LUNDEF);

              if (pf2 && mat_ind != UNDEF &&
                  pf2->i != (unsigned long)LUNDEF) {
                  AppearancePtr pmat2 = dynamic_pointer_cast<Appearance>(*(SceneObjectPtr*)pf2->p);
                  if(pmat2)scene->add(ShapePtr(new Shape(pgeom,pmat2,vtx)));
                  else scene->add(ShapePtr(new Shape(pgeom,pmat,vtx)));
              }
              else
                  scene->add(ShapePtr(new Shape(pgeom,pmat,vtx)));
          }
        }

      }

      delete vtxlist;

    }

  }
  else if(shape_ind != UNDEF){
      VIdList* vtxlist = compoSons(root, scale);

      if (vtxlist) {

          VIdListIter next(*vtxlist);

          VId vtx;

          AppearancePtr default_mat(new Material("Default_MTG_2",Color3(255,204,204),
                                                 0.5,
                                                 Color3((uchar_t)0),
                                                 Material::DEFAULT_EMISSION,
                                                 0,
                                                 0));
          default_mat->setName("MTGDefault");
          ShapePtr pgeom;
          AppearancePtr pmat = default_mat;

          //Printer pp;
          //Printer pp(cerr,cerr,cerr);

          while(next()) {

              // gets the SHAPE Attribute of the vertex
              vtx = next.key();

              const Feature* pf = feature(vtx, shape_ind, LUNDEF);

              if (pf && pf->i == (unsigned long)LUNDEF) continue;
              else if (pf) {
                  pgeom = dynamic_pointer_cast<Shape>(*(SceneObjectPtr*)pf->p); // replace void* by the correct type

                  if(pgeom){
                      pgeom->id = vtx;
                      if(!pgeom->appearance)
                          pgeom->appearance = default_mat;
                      scene->add(ShapePtr(new Shape(*pgeom)));
                  }
              }

          }

          delete vtxlist;

      }

  }

  return scene;

}



ostream& operator<<(ostream& o, const MTG& obj){

  return obj.print(o);

}
