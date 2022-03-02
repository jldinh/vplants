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
 *       $Id: artist.cpp 3258 2007-06-06 13:18:26Z dufourko $
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
#include <math.h>
#include <stdlib.h>

#include "artist.h"

using namespace std;

//static const char rcsid[] = "$Id: artist.cpp 3258 2007-06-06 13:18:26Z dufourko $";

MTGArtist::MTGArtist(MTG* the_mtg): _mtg(the_mtg) {

}

void MTGArtist::drawSubXtreeMtg(VId v) {

  static int depth = 0;

  int vclass = _mtg->vclass(v);

  for(int i=0;i<depth;i++) _file << "\t";

  _file << _mtg->classSymbol(vclass) << _mtg->vindex(v) << endl;;

  depth++;

  VIdList* vsonlist = _mtg->topoSons(v, ANYTOPO);
  assert(vsonlist);

  VIdListIter next(*vsonlist);

  while( next() ) {

    VId x = next.key();

    drawSubXtreeMtg(x);

  }

  delete vsonlist;

  depth--;

}

int MTGArtist::drawXtreeMtg(int scale, const char* file) {

  assert(file);

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".xtree");
    // cerr << "name = " << name << endl;

  }
  else {

    name += ".xtree";
    // cerr << "name = " << name << endl;
  }

  _file.open(name.data());

  if (!_file) {
    cerr << "Cannot open file for writing : "
         << name
         << endl;
    return 0;
  }

  VIdList* root_list = _mtg->findGlobalTopoRootsAtScale(scale);

  if (root_list) {

    VIdListIter next(*root_list);

    while (next()) {

      drawSubXtreeMtg(next.key());

    }
    delete root_list;

  }

  cerr << "File created : " << name << endl;

  _file.close();

  return 1;

}


int MTGArtist::drawXtreeMtg(const char* file) {

  int scale_nb = _mtg->scaleNb();

  assert(file);

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".xtree");
    // cerr << "name = " << name << endl;

  }
  else {

    name += ".xtree";
    // cerr << "name = " << name << endl;
  }

  _file.open(name.data());

  if (!_file) {
    cerr << "Cannot open file for writing : "
         << name
         << endl;
    return 0;
  }

  for (int i=1; i<=scale_nb; i++) {

    VIdList* root_list = _mtg->findGlobalTopoRootsAtScale(i);

    if (root_list) {

      VIdListIter next(*root_list);

      while (next()) {

        drawSubXtreeMtg(next.key());

      }
      delete root_list;

    }

  }

  cerr << "File created : " << name << endl;

  _file.close();

  return 1;

}

int MTGArtist::drawEdgeMtg(const char* file) {

  int scale_nb = _mtg->scaleNb();

  assert(file);

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".edge");
    // cerr << "name = " << name << endl;

  }
  else {

    name += ".edge";
    // cerr << "name = " << name << endl;
  }

  _file.open(name.data());

  if (!_file) {
    cerr << "Cannot open file for writing : "
         << name
         << endl;
    return 0;
  }


  _file << "graph: {" << endl;

  _file << "orientation: left_to_right" << endl;

  // List of nodes
  MTGVertexIter nextn(_mtg);
  while (nextn()) {

    VId node = nextn.key();

    int sc = _mtg->vscale(node);

    _file << "node: { title: \"" << node
          << "\" label: \"" << _mtg->classSymbol(_mtg->vclass(node)) << _mtg->vindex(node)
          << "\" borderwidth: " << _mtg->vscale(node) + 2
          << " bordercolor: \"" << (char*) ( sc-(sc/2)*2 ? "black" : "grey")
          << "\" }" << endl;

  }

  // List of topoEdges
  MTGEdgeIter nexte(_mtg);
  while (nexte()) {

    VId edge = nexte.key();
    VId father = _mtg->edge(edge).father();
    VId son = _mtg->edge(edge).son();
    const char* elab = _mtg->edgeLabel(edge);

    if (father != UNDEF && son != UNDEF && elab != NULL) { // check whether this edge can be printed
      _file << "edge: { label: \"" << elab
      << "\" sourcename: \"" << father
      << "\" targetname: \"" << son
      << "\" }" << endl;
    }

  }

  // List of compoEdges
  nextn.reset();
  while (nextn()) {

    VId node = nextn.key();
    const VIdList* sonlist = _mtg->vertex(node).compoSons();

    if (sonlist) {

      VIdListIter nexts(*(VIdList*)sonlist);

      while (nexts()) {

        VId son = nexts.key();

        _file << "edge: { label: \"" << "/"
        << "\" sourcename: \"" << node
        << "\" targetname: \"" << son
        << "\" linestyle: dotted"
        << " }" << endl;

      }

    }

  }

  _file << "}" << endl;


  cerr << "File created : " << name << endl;

  _file.close();

  return 1;

}


static const float ANGLE = 1.;

void MTGArtist::drawSubLtreeMtg(VId v, EType e, VGeom vg) {

  static int order = 0;
  static int oldrank = 0;
  static int rank = 0;

  int vclass = _mtg->vclass(v);

  // print segment v of line tree
  LtreeRecord ltr;

  ltr.symb = 1;    // entre-noeud
  ltr.detail = 4;  // on dessine tout (pas de simplification)
  ltr.bouf1 = 0;
  ltr.bouf2 = 0;
  int j;
  for(j=0; j<3; j++) ltr.mat[j][0] = ((float*) &vg.p)[j];

  for(j=0; j<3; j++) ltr.mat[j][1] = ((float*) &vg.q)[j];
  for(j=0; j<3; j++) ltr.mat[j][2] = ((float*) &vg.r)[j];
  for(j=0; j<3; j++) ltr.mat[j][3] = ((float*) &vg.o)[j];

  cerr.precision(2);
  for(int i=0;i<3;i++) {
    for(int j=0;j<4;j++) cerr << ltr.mat[i][j] << " ";
    cerr << endl;
  }
  cerr << endl << endl;

  ltr.diamb = .05;
  ltr.diamh = .05;
  ltr.bouf3 = 0;

  _file.write((const char*) &ltr, sizeof(ltr));

  if (e == PLUS) {
    order++;
    oldrank=rank;
    rank=0;
  }
  else {
    rank++;
  }


  VIdList* vsonlist = _mtg->topoSons(v, ANYTOPO);
  assert(vsonlist);

  VIdListIter next(*vsonlist);

  while( next() ) {

    VId x = next.key();

    EType etype = _mtg->edgeType(v,x);

    VGeom xg;
    double alpha = (randomDouble()>.5)?-randomDouble()*ANGLE:randomDouble()*ANGLE;

    if (etype == PLUS) {

      vecsomme(1., 1., &vg.o, &vg.p, &xg.o);
      rotation_axe((float*) &vg.r, (float*) &vg.p, alpha, (float*) &xg.p);
      rotation_axe((float*) &vg.r, (float*) &vg.q, alpha, (float*) &xg.q);
      vecaffecte(&vg.r, &xg.r);

    }
    else {

      vecsomme(1., 1., &vg.o, &vg.p, &xg.o);
      vecaffecte(&vg.p, &xg.p);
      vecaffecte(&vg.q, &xg.q);
      vecaffecte(&vg.r, &xg.r);
    }

    drawSubLtreeMtg(x, etype, xg);

  }

  delete vsonlist;

  if (e == PLUS) {
    order--;
    rank = oldrank;
  }
  else rank--;

}


int MTGArtist::writeInfo (const char* file, float age, int nbb, int graine, int simplification, float *max, float *min)
{
  int  nb;

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".inf");

  }
  else {

    name += ".inf";

  }

  ofstream info(name.data());

  if (!info) {
    cerr << "Cannot open file for writing : "
    << name
    << endl;
    return 0;
  }

  nb = 1;

  info << "File : 1amapmod\n";
  info.precision(5);
  info << "Age : " << age << "   " << nb << " pattern(s)  number of branches " << nbb << endl;
  info << "Random_seed " << graine << "  Simplification " << simplification << endl;

  info.precision(6);
  info << max[0] << " " << max[1] << " " << max[2] << endl;
  info << min[0] << " " << min[1] << " " << min[2] << endl;

  info << "entre-noeud  1       entn105 1" << endl;

  info.close();

  cerr << "File created : " << name << endl;

  return (1);
}

int MTGArtist::drawLtreeMtg(int scale, const char* file) {

  assert(file);

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".lig");
    // cerr << "name = " << name << endl;

  }
  else {

    name += ".lig";
    // cerr << "name = " << name << endl;
  }

  _file.open(name.data());

  if (!_file) {
    cerr << "Cannot open file for writing : "
         << name
         << endl;
    return 0;
  }

  ifstream header("/usr/people/bin/binv4/ENTETE");

  if (!header) {
    cerr << "Cannot open file for writing : "
         << "/usr/people/bin/binv4/ENTETE"
         << endl;
    return 0;
  }

  char tmp[80];

  header.read(tmp, 80);

  header.close();

  _file.write(tmp, 80);

  VIdList* rootlist = _mtg->findGlobalTopoRootsAtScale(scale);

  VId topo_root;

  if (rootlist->entries() != 0) topo_root = rootlist->first();

  VGeom initg;
  initg.o.x = 0.0;
  initg.o.y = 0.0;
  initg.o.z = 0.0;
  initg.p.x = 0.0;
  initg.p.y = 0.0;
  initg.p.z = 1.5;
  initg.q.x = 0.0;
  initg.q.y = 1.0;
  initg.q.z = 0.0;
  initg.r.x = 1.0;
  initg.r.y = 0.0;
  initg.r.z = 0.0;

  float age = 10;
  int nbb = 10;
  int graine = 3;
  int simplification = 0;
  float max[3] = {10., 10., 10.};
  float min[3] = {-10, -10., 0.};

  writeInfo(name.data(), age, nbb, graine, simplification, max, min);

#ifdef _WIN32
  srand(2);
#else
  srandom(2);
#endif

  drawSubLtreeMtg(topo_root, PLUS, initg);

  cerr << "File created : " << name << endl;

  _file.close();

  return 1;

}


void MTGArtist::writeMTGheader(const MTGHeader* header) {

  int clnb = header->classNb();

  _file << "CODE:" << '\t';
  _file << "FORM-A" << endl;

  _file << endl;
  _file << "CLASSES:" << endl;
  _file << "SYMBOL\tSCALE\tDECOMPOSITION\tINDEXATION\tDEFINITION" << endl;

  for(int i1=1; i1<clnb; i1++) {

    RWCString decomp_st;
    RWCString indexing_st;
    RWCString vdef_st;

    switch (header->vdecomp(i1)) {

    case FREE_D:
      decomp_st = "FREE";
      break;
    case LESSLINEAR:
      decomp_st = "<-LINEAR";
      break;
    case PLUSLINEAR:
      decomp_st = "+-LINEAR";
      break;
    case LINEAR:
      decomp_st = "LINEAR";
      break;
    case CONNECTED:
      decomp_st = "CONNNECTED";
      break;
    case NOTCONNECTED:
      decomp_st = "NOTCONNNECTED";
      break;
    case NONE_D:
      decomp_st = "NONE";
      break;

    }

    switch (header->vindexing(i1)) {

    case FREE_I:
      indexing_st = "FREE";
      break;
    case CONSECUTIVE:
      indexing_st = "CONSECUTIVE";
      break;

    }

    switch (header->vdef(i1)) {

    case EXPLICIT:
      vdef_st = "EXPLICIT";
      break;
    case IMPLICIT:
      vdef_st = "IMPLICIT";
      break;

    }

    _file << header->symbol(i1) << '\t' << header->scale(i1) << '\t'
          << decomp_st  << '\t'
          << indexing_st << '\t'
          << vdef_st << endl;

  }

  _file << endl;
  _file << "CLASSDEF:" << endl;
  _file << "LEFT\tRIGHT\tRELTYPE\tMAX" << endl;

  for(int i=0; i<clnb; i++) {

    for (int j=0; j<clnb; j++) {

      if (header->less(i,j).Max()!=0 || header->plus(i,j).Max()!= 0) {

        if (header->less(i,j).Max()!=0) {
          _file << header->symbol(i) << "\t" << header->symbol(j);
          _file << "\t<\t";
          if (header->less(i,j).Max()==MAXINT) _file << '?' << endl;
          else _file << header->less(i,j).Max() << endl;
        }
        if (header->plus(i,j).Max()!= 0) {
          _file << header->symbol(i) << "\t" << header->symbol(j);
          _file << "\t+\t";
          if (header->plus(i,j).Max()==MAXINT) _file << '?' << endl;
          else _file << header->plus(i,j).Max() << endl;
        }
      }
    }

  }

  _file << endl;
  _file << "FEATURES:" << endl;
  _file << "NAME\tTYPE" << endl;


  int fnb = header->fNb();

  for(int i2=1; i2<fnb; i2++) {

    _file << header->fName(i2) << "\t";
    switch (header->fType(i2)) {
    case INTEGER:
      _file << "INT";
      break;
    case ALPHA:
      _file << "ALPHA";
      break;
    default:
      _file << "UNKNOWN";
      break;
    }

    if ((header->fSmbTable(i2)) != 0) _file << "\t" << header->fSmbTable(i2) << endl;
    else _file << endl;

  }

  _file << endl;

}

void MTGArtist::findCodeFromRoot(VId v) {

  static int depth = 0;

  RWCString* stg;

  VId father = _mtg->topoFather(v, ANYTOPO);

  if (father == UNDEF) father = _mtg->mtgRoot();

  EType etype = _mtg->edgeType(father,v);
  int delta_index = _mtg->vindex(v) - _mtg->vindex(father);

  if (etype == PLUS) depth++;
  if (etype == PLUSPLUS) depth += delta_index;

  for(int i=0;i<depth;i++) _file << "\t";

  if (etype == LESS || etype == LESSLESS) _file << '^';


  stg = _mtg->relativeName(father, v);

  assert(stg);


  _file << stg->data() << endl;

  delete stg;

  VIdList* vsonlist = _mtg->topoSons(v, PLUS);
  assert(vsonlist);

  VIdListIter next(*vsonlist);

  while (next()) {

    VId vtx = next.key();

    findCodeFromRoot(vtx);

  }

  delete vsonlist;

  vsonlist = _mtg->topoSons(v, LESS);

  next.reset(*vsonlist);
  while (next()) {

    VId vtx = next.key();

    findCodeFromRoot(vtx);

  }

  delete vsonlist;

  if (etype == PLUS) depth--;
  if (etype == PLUSPLUS) depth -= delta_index;

}

int MTGArtist::createMTGCode(const char* file) {

  assert(file);

  RWCString name(file);

  int pos = name.last('.');

  if (pos != RW_NPOS) {

    name.replace(pos, name.length(),".a");

  }
  else {

    name += ".a";

  }

  _file.open(name.data());

  if (!_file) {
    cerr << "Cannot open file for writing : "
         << name
         << endl;
    return 0;
  }

  writeMTGheader(_mtg->header());

  _file << endl;
  _file << "MTG:" << endl;

  int fnb = _mtg->header()->fNb();

  _file << "ENTITY-CODE" << "\t\t\t\t\t";

  for(int i=1; i<fnb; i++) { // i=0 is used to store a line number

    _file << "\t" << _mtg->header()->fName(i);

  }

  VIdList* root_list = _mtg->findGlobalTopoRootsAtScale(2);

  if (root_list) {

    VIdListIter next(*root_list);

    while (next()) {

      _file << endl;
      findCodeFromRoot(next.key());

    }
    delete root_list;

  }


  _file.close();


  return 1;

}
