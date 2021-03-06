/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): P.ferraro (pascal.ferraro@cirad.fr)
 *
 *       $Source$
 *       $Id: amlnodefunction.h 3264 2007-06-06 14:22:22Z dufourko $
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


#ifndef SB_NODE_FUNCTION_HEADER
#define SB_NODE_FUNCTION_HEADER

#include "definitions.h"
#include "aml/fnode.h"

class NodeFunction
{
public :
  NodeFunction() {}
  NodeFunction(std::string name,FNode *f,DistanceType default_value=DIST_UNDEF);
  std::string getName() const { return(_name); }
  void putName(std::string name) { _name=name; }
  FNode* getFun() const { return(_function);}
  DistanceType operator() (VId );
  DistanceType operator() (VId,VId );

private :
  std::string _name;
  DistanceType _defaultValue;
  FNode* _function;
};

const NodeFunction FUN_UNDEF("FUN_UNDEF",(FNode*) 0);

#endif

