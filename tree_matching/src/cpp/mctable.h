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
 *       $Id: mctable.h 3258 2007-06-06 13:18:26Z dufourko $
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


#ifndef SB_MATCHING_CONNECTED_TABLE
#define SB_MATCHING_CONNECTED_TABLE

#include "definitions.h"
#include "nodecost.h"
#include "mnodecost.h"
#include "wnodecost.h"
#include "inttable.h"
/**
 *\class MatchingConnectedTable
 *\brief 
 *\author Pascal ferraro
 *\date 1999
 */

class MatchingConnectedTable
{
  friend class Matching;
  friend class MatchPath;

  public :
  MatchingConnectedTable(){};
  MatchingConnectedTable(TreeGraph& ,TreeGraph& );
  ~MatchingConnectedTable(){};
  void make(TreeGraph& ,TreeGraph&);
  int getNBC(int ,int ) const ;
  void putNBC(int ,int ,int);
  int getNBCF(int ,int ) const ;
  void putNBCF(int ,int ,int);
  void openIntVector(int);
  void closeIntVector(int);

  //Initialisation
  IntTable* getConnectedTable() {return(&_treeConnectedTable);};

  private :
  TreeGraph* T1;
  TreeGraph* T2;

  protected :
  IntTable _treeConnectedTable;
  IntTable _forestConnectedTable;
};

#endif 






