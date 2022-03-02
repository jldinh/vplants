/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): P. Ferraro (pascal.ferraro@cirad.fr)
 *
 *       $Source$
 *       $Id: aml_treematch.h 8157 2010-02-18 10:07:05Z guedon $
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









#ifndef SB_AML_TREEMATCH_HEADER
#define SB_AML_TREEMATCH_HEADER

#include <iostream>
#include <fstream>

#include "mtg/mtg.h"

#include "aml/ammodel.h"
#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/erroraml.h"
#include "aml/array.h"
#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "aml/amobj.h"
//#include "STAT/vectors.h"

#include "tree_matching/definitions.h"
#include "tree_matching/treematch.h"
#include "tree_matching/treematchext.h"
#include "tree_matching/unordered_treematch.h"
#include "tree_matching/ordered_treematch.h"
#include "tree_matching/pordered_treematch.h"


class AML_TreeMatch : public TreeMatch, public AMModel
{
  public :

  AML_TreeMatch( ):TreeMatch(),AMModel() {;};

  AML_TreeMatch( MTG& mtg, Array* roots):TreeMatch(mtg,roots) {;};
  AML_TreeMatch( MTG& mtg,
                 Array* roots,
                 Array* local_functions,
                 AMString matching_type,
                 AMString ordered_type,
                 int self_similarity,
                 VectorDistance& vect_dist,
                 double coeff):TreeMatch(mtg,roots,local_functions,matching_type,ordered_type,self_similarity,vect_dist,coeff) {;};

  virtual std::ostream& displayOneLine(std::ostream& o) const;
  std::ostream& viewAllMatching(std::ostream& o) const {return(TreeMatch::viewAllMatching(o));};
  std::ostream& viewOneMatching(std::ostream& o, int itree, int rtree) const {return(TreeMatch::viewOneMatching(o,itree,rtree));};
  virtual AMObj print(const AMObjVector& args) const { assert(&args);return(AMObj(AMObjType::VOID)); };
  virtual AMObj save(const AMObjVector& args) const;
};
class AML_TreeMatch_U : public TreeMatch_U, public AMModel
{
  public :

  AML_TreeMatch_U( ):TreeMatch_U(),AMModel() {;};

  AML_TreeMatch_U( MTG& mtg, Array* roots):TreeMatch_U(mtg,roots) {;};

  AML_TreeMatch_U( MTG& mtg,
                 Array* roots,
                 Array* local_functions,
                 AMString matching_type,
                 AMString mapping_type,
                 AMString mapping,
                 AMString scale_type,
                 VectorDistance& vect_dist,
                 double coeff):TreeMatch_U(mtg,roots,local_functions,matching_type,mapping_type,mapping,scale_type,vect_dist,coeff) {;};

  virtual std::ostream& displayOneLine(std::ostream& o) const;
  std::ostream& viewAllMatching(std::ostream& o) const {return(TreeMatch_U::viewAllMatching(o));};
  std::ostream& viewOneMatching(std::ostream& o, int itree, int rtree) const {return(TreeMatch_U::viewOneMatching(o,itree,rtree));};
  virtual AMObj print(const AMObjVector& args) const { assert(&args);return(AMObj(AMObjType::VOID)); };
  virtual AMObj save(const AMObjVector& args) const;
};
class AML_TreeMatch_O : public TreeMatch_O, public AMModel
{
  public :

  AML_TreeMatch_O( ):TreeMatch_O(),AMModel() {;};

  AML_TreeMatch_O( MTG& mtg, Array* roots):TreeMatch_O(mtg,roots) {;};

  AML_TreeMatch_O( MTG& mtg,
                 Array* roots,
                 Array* local_functions,
                 AMString matching_type,
                 AMString mapping_type,
                 AMString mapping,
                 AMString scale_type,
                 VectorDistance& vect_dist,
                 double coeff):TreeMatch_O(mtg,roots,local_functions,matching_type,mapping_type,mapping,scale_type,vect_dist,coeff) {;};

  virtual std::ostream& displayOneLine(std::ostream& o) const;
  std::ostream& viewAllMatching(std::ostream& o) const {return(TreeMatch_O::viewAllMatching(o));};
  std::ostream& viewOneMatching(std::ostream& o, int itree, int rtree) const {return(TreeMatch_O::viewOneMatching(o,itree,rtree));};
  virtual AMObj print(const AMObjVector& args) const { assert(&args);return(AMObj(AMObjType::VOID)); };
  virtual AMObj save(const AMObjVector& args) const;
};
class AML_TreeMatch_PO : public TreeMatch_PO, public AMModel
{
  public :

  AML_TreeMatch_PO( ):TreeMatch_PO(),AMModel() {;};

  AML_TreeMatch_PO( MTG& mtg, Array* roots):TreeMatch_PO(mtg,roots) {;};

  AML_TreeMatch_PO( MTG& mtg,
                 Array* roots,
                 Array* local_functions,
                 AMString matching_type,
                 AMString mapping_type,
                 AMString mapping,
                 AMString scale_type,
                 VectorDistance& vect_dist,
                 double coeff):TreeMatch_PO(mtg,roots,local_functions,matching_type,mapping_type,mapping,scale_type,vect_dist,coeff) {;};

  virtual std::ostream& displayOneLine(std::ostream& o) const;
  std::ostream& viewAllMatching(std::ostream& o) const {return(TreeMatch_PO::viewAllMatching(o));};
  std::ostream& viewOneMatching(std::ostream& o, int itree, int rtree) const {return(TreeMatch_PO::viewOneMatching(o,itree,rtree));};
  virtual AMObj print(const AMObjVector& args) const { assert(&args);return(AMObj(AMObjType::VOID)); };
  virtual AMObj save(const AMObjVector& args) const;
};

#endif
