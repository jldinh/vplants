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
 *       $Id: vertex.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef VERTEX_HEADER
#define VERTEX_HEADER

#include <iostream>

#include "tool/rw_list.h"
//#include <rw/tvslist.h>

#include "aml/defs.h"
#include "edge.h"

typedef RWTValDlist<VId> VIdList;
typedef RWTValDlist<FSetId> FSetIdList;


// Types utilises:
//
// VId        : identificateur d'un vertex
// VIdList    : Liste d'identificateur de vertex
// VClass     : Classe d'un vertex
// VContext   : Contexte d'un vertex
// EType      : type d'une edge
// FSetId     : Feature Set
// FSetIdList : Feature Set list
//

// Les vertex:
//
// Le vertex est un objet autonome qui ne peut etre accede (R|W) qu'au travers
// de son interface externe (meme par les MTG)
//
// d'un point de vue topologique, un vertex a :
// - un pere de meme niveau que lui (dit _topofather) qui peut etre eventuellement
// indefini (cas de la racine de l'arborescence topologique ou d'un
// niveau non-structure)
// le type d'arc reliant ce vertex a son pere topologique est donne par
// le champ _topoedge.
// - des fils de meme niveau que lui, donnes dans leur ordre de definition
// dans la liste _toposons. Cette liste peut etre vide (_toposons == NULL)
// - un pere complexe qui est unique et qui est TOUJOURS defini.
// - enfin un vertex indiquant "la localisation exacte" du vertex courant.
// cette localisation est definie ainsi:
//     . par le vertex le plus precis appartenant a la hierarchie du
//       pere topologique si celui-ci existe. Ce vertex peut etre le
//       pere topologique lui meme ou l'un de ses composants a un niveau
//       plus fin.
//     . Si le pere topologique n'existe pas, alors c'est le pere complexe
//       (qui lui existe toujours) qui constitue la localisation de ce vertex.
//
// Le contexte topologique d'un vertex est constitue:
// - de sa propre classe,
// - du type de l'arc topologique qui le relie a son pere,
// - de sa localisation exacte sur son pere.
// Deux vertex differents ayant meme "contexte topologique" doivent avoir des
// index differents.
//
// Remarque: il n'y a pas de fonction level definie directement sur un vertex
// car cette fonction depend des caracteristiques du graphe
// dans lequel se trouve ce vertex. La fonction level se trouve
// definie sur un vertex au niveau du mtg lui meme.
//
// Remarque: Aucune verification de coherence n'est effectuee sur le
// vertex. Ces verifications devront etre realisees dans la couche superieure
// au niveau du MTG.
//
//

class Vertex {

  friend std::ostream& operator<<(std::ostream&, const Vertex&);

  VId _vid;
  VClass _vclass;
  int _vindex;

  EId      _topo_mother;          // edge topo entrant dans ce vertex
  EIdList* _topo_daughters;       // edge topo sortantes de ce vertex
  VId      _compo_father;         // vertice contenant ce vertex
  VIdList* _compo_sons;           // point d'entree des vertices contenus dans ce vertex

  VId _vprefix;           // localisations exactes de ce vertex sur ses peres topologiques

  FSetIdList* _fsetids;   // Il y a plusieurs ens. d'attributs s'il existe differentes dates

public:

  Vertex();
  Vertex(VId vid,
         VClass vclass,
         int index);
  Vertex(const Vertex&);
  ~Vertex();

  int binaryStoreSize() const;

  Vertex& operator=(const Vertex&);
  AmlBoolean operator==(const Vertex&) const;

  // each time a topo mother edge is added, a vprefix has also to be
  // defined, even if there is no topo edge (id = UNDEF), then loc is
  // a compo father of the vertex

  int addTopoMother(EId id);   // add a new topomother edge
  int setTopoMother(EId id);   // overwrite an old edge
  int addTopoDaughter(EId id);
  int addCompoFather(VId id);
  int addCompoSon(VId id);
  int setVPrefix(VId loc);

  int addFSetId(FSetId id);

  void removeTopoMother();
  void removeTopoDaughter(EId eid);
  void removeCompoSon(VId son);

  VId vid() const {return _vid;}
  VClass vclass() const {return _vclass;}
  int index() const {return _vindex;}

  EId topoMother() const {return _topo_mother;}
  const EIdList* topoDaughters() const {return _topo_daughters;}

  VId compoFather() const {return _compo_father;}
  const VIdList* compoSons() const {return _compo_sons;}

  VId vprefix() {return _vprefix;}

  const FSetIdList* fsetIds() const {return _fsetids;}

  std::ostream& print(std::ostream&) const;
  std::ostream& printAll(std::ostream&) const;

};

std::ostream& operator<<(std::ostream& o, const Vertex& obj);

#endif
