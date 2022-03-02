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
 *       $Id: vertex.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include "vertex.h"

using namespace std;

// static const char rcsid[] = "$Id: vertex.cpp 17611 2014-10-17 13:20:41Z pradal $";

Vertex::Vertex() {

  _vid = UNDEF;
  _vclass = UNDEF;
  _vindex = UNDEF;

  _topo_mother = UNDEF;
  _topo_daughters = NULL;
  _compo_father = UNDEF;
  _compo_sons = NULL;

  _vprefix = UNDEF;

  _fsetids = NULL;

}


Vertex::Vertex(VId vid,
               VClass vclass,
               int index)
{

  _vid = vid;
  _vclass = vclass;
  _vindex = index;

  _topo_mother = UNDEF;
  _topo_daughters = NULL;
  _compo_father = UNDEF;
  _compo_sons = NULL;

  _vprefix = UNDEF;

  _fsetids = NULL;

}

Vertex::Vertex(const Vertex& v) {

  if (this != &v) {

    _vid = v._vid;
    _vclass = v._vclass;
    _vindex = v._vindex;

    _topo_mother = v._topo_mother;

    if (v._topo_daughters) _topo_daughters = new EIdList(*v._topo_daughters);
    else _topo_daughters = NULL;

    _compo_father = v._compo_father;

    if (v._compo_sons) _compo_sons = new VIdList(*v._compo_sons);
    else _compo_sons = NULL;

    _vprefix = v._vprefix;

    if (v._fsetids) _fsetids = new FSetIdList(*v._fsetids);
    else _fsetids = NULL;

  }

}


Vertex::~Vertex(){

  delete _topo_daughters;

  delete _compo_sons;

  delete _fsetids;

}


int Vertex::binaryStoreSize() const {

  int count = sizeof(_vid) +
  sizeof(_vclass) +
  sizeof(_vindex) +
  sizeof(_topo_mother) +
  sizeof(_topo_daughters) +
  sizeof(_compo_father) +
  sizeof(_compo_sons) +
  sizeof(_vprefix) +
  sizeof(_fsetids);

  // take into account the different lists:

  int cellsize = sizeof(EId*) + sizeof(EId);

  if (_topo_daughters) {
    count += sizeof(*_topo_daughters);
    count += cellsize * _topo_daughters->entries();
  }
  cellsize = sizeof(VId*) + sizeof(VId);

  if (_compo_sons) {
    count += sizeof(*_compo_sons);
    count += cellsize * _compo_sons->entries();
  }
  cellsize = sizeof(EId*) + sizeof(EId);

  if (_fsetids) {
    count += sizeof(*_fsetids);
    count += cellsize * _fsetids->entries();
  }
  return count;

}

Vertex& Vertex::operator=(const Vertex& v) {

  if (this != &v) {

    _vid = v._vid;
    _vclass = v._vclass;
    _vindex = v._vindex;

    _topo_mother = v._topo_mother;

    if (v._topo_daughters) _topo_daughters = new EIdList(*v._topo_daughters);
    else _topo_daughters = NULL;

    _compo_father = v._compo_father;

    if (v._compo_sons) _compo_sons = new VIdList(*v._compo_sons);
    else _compo_sons = NULL;

    _vprefix = v._vprefix;

    if (v._fsetids) _fsetids = new FSetIdList(*v._fsetids);
    else _fsetids = NULL;

  }

  return *this;

}

// Test l'egalite des deux vertex a partir de leur identificateur

AmlBoolean Vertex::operator==(const Vertex& vtx) const {

  if (this == &vtx) return TRUE;
  else if (_vid == vtx._vid) return TRUE;
       else return FALSE;

}

int Vertex::addTopoMother(EId id) {

  if (_topo_mother == UNDEF) {

    if (id != UNDEF) _topo_mother = id;
    return  _topo_mother;

  }
  else return UNDEF;

}

int Vertex::setTopoMother(EId id) {

  _topo_mother = id; // id can be UNDEF for resetting the EDGE
  return  _topo_mother;

}

int Vertex::addTopoDaughter(EId id) {

  if (!_topo_daughters) _topo_daughters = new EIdList;

  _topo_daughters->insert(id);

  return  _topo_daughters->entries();

}


int Vertex::addCompoFather(VId id) {


  if (_compo_father == UNDEF) {

    if (id != UNDEF) {
      _compo_father = id;
      return id;
    }
    return UNDEF;

  }
  else return UNDEF ;

}

int Vertex::addCompoSon(VId id) {

  if (!_compo_sons) _compo_sons = new EIdList;

  _compo_sons->insert(id);

  return  _compo_sons->entries();

}

int Vertex::setVPrefix(VId id) {

  _vprefix = id;
  return id;

}


int Vertex::addFSetId(FSetId id) {

  if (!_fsetids) _fsetids = new FSetIdList;

  _fsetids->insert(id);

  return  _fsetids->entries();

}

void Vertex::removeTopoMother() {

  _topo_mother = UNDEF;

}

void Vertex::removeTopoDaughter(EId eid) {

  if (_topo_daughters) {

    _topo_daughters->remove(eid);

    if (_topo_daughters->isEmpty()) {
      delete _topo_daughters;
      _topo_daughters = NULL;
    }

  }
}

void Vertex::removeCompoSon(VId son) {

  if (_compo_sons) {

    _compo_sons->remove(son);

    if (_compo_sons->isEmpty()) {
      delete _compo_sons;
      _compo_sons = NULL;
    }

  }

}

ostream& Vertex::print(ostream& o) const {

  o << "\tvid = " << _vid << "\tloc = " << _vprefix
  << "\tcomplex = " << _compo_father << endl;

  return o;

}

ostream& Vertex::printAll(ostream& o) const {

  print(o);

  int tm_nb = _topo_mother ? _topo_mother : UNDEF;
  int td_nb = _topo_daughters ? _topo_daughters->entries(): (unsigned int) UNDEF;
  int sm_nb = _compo_father ? _compo_father : UNDEF;
  int sd_nb = _compo_sons ? _compo_sons->entries(): (unsigned int) UNDEF;

  o << "Topo : IN = " << tm_nb << ", OUT = " << td_nb << endl;
  o << "Compo: IN = " << sm_nb << ", OUT = " << sd_nb << endl;

  return o;

}

ostream& operator<<(ostream& o, const Vertex& obj) {

  return obj.print(o);

}
