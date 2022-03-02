/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): N. Dones (dones@clermont.inra.fr)
 *                       UMR PIAF INRA-UBP Clermont-Ferrand
 *
 *       $Source$
 *       $Id: electrical_model.h 15687 2014-02-05 10:15:41Z gbaty $
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

#ifndef __flux_h__
#define __flux_h__

#include <vector>

#include "plantgl/tool/util_hashmap.h"
#include "plantgl/tool/util_array.h"

#include "mtg/mtg.h"
#include "aml/fnode.h"


TOOLS_USING_NAMESPACE
/*----------------------------------------------------------------------*/

struct eqint
{
  bool operator()(const VId i1, const VId i2) const
  {
    return i1==i2;
  }
};

#ifndef WIN32_STL_EXTENSION
typedef pgl_hash_map<VId, int, hash<VId>, eqint> VtxHMap;
#else
typedef pgl_hash_map<VId, int> VtxHMap;
#endif
/*---------------------------------------------------------------------*/

/**
    \class ElectricalModel
    \brief The Class of the flux computer
*/

class ElectricalModel {

protected:

  /// The mtg
  MTG* _g;
  /// The root of the sub graph studied
  VId _id;
  /// The base potential
  double _base_potential;

  /// List of the vId using for the flux computation
  VtxList* _vlist;

 /// A Hash Map used to give the vlist index corresponding to a VId
  VtxHMap _vIdHTab;

  ///
  RealArray* _resistance_array;
  RealArray* _flux_array;
  RealArray* _potential_array;

protected:
  /// The valid return code
  bool _isValid;

  int _nb_desc;

public:

  ///Computation of the ElectricalModel
  void computeEM();

  /// Computation of the flux.
  RealArray* clcFlux();

  /// Computation of the water potential.
  RealArray* clcPotential(RealArray* flux_array);


public:

  ///Return if the ElectricalModel is Valid
  bool isValid() {return _isValid;}

  /// Constructors.
  //  ElectricalModel(MTG* g, VId v, int scale, FNode* LA_fun, FNode* resist_fun, FNode* trans_fun);
  ElectricalModel(MTG* g, VId root, double base_pot);
  ElectricalModel(MTG* g, VId root, RealArray*  resistance, RealArray* flux, RealArray* potential,double base_pot);

  // Destructor.
  virtual ~ElectricalModel();

  ///Correspondance between the vtx (VId) and the index of the vlist
  int vtxToIndex(VId v) {return _vIdHTab[v];}
  VId indexToVtx(int i) {return (*_vlist)[i];}

  virtual std::ostream& displayOneLine(std::ostream& o) const;
  virtual std::ostream& display(std::ostream& o) const;
};


// __flux_h__
#endif

