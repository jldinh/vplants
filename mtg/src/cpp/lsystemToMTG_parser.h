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
 *       $Id: lsystemToMTG_parser.h 3258 2007-06-06 13:18:26Z dufourko $
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




#ifndef __LSYSTEMTOMTG_PARSER_HEADER
#define __LSYSTEMTOMTG_PARSER_HEADER

#include <map>
#include <vector>
#include <stack>

typedef std::stack<int> IntStack;
typedef std::list<double> DList;       // to store a set of args
typedef std::pair<char,DList> MPair;   // to store the geometric primitives and its args
typedef std::stack<MPair> ModuleStack; // To stack geometric primitives and their args



struct SyntaxData {

  int nbTopoColumns;
  int featureNb;
  std::map<char, std::vector<int> > mapSymbolArgs; // contains for each l-system symbol, the index of 
                                         // its different arguments in the feature list entries
  
  // data used as global variables by the parser

  int order;         // Order of nesting in the lsystem string
  bool first_symbol; // true at the beginning of the parsing only

  // new_order is true if the order of the previous symbol 
  // in the l-system string (l-string) was
  // one order lesser (only topological symbols are considered)

  int new_order; // true 

  IntStack new_order_stack;

  int nb_of_branches;
  IntStack nb_of_branches_stack; // number of branches starting at a given symbol

  // Each time a topological symbol is read, it can be prefixed
  // in the l-string by a stack of geometric symbols. These
  // are stored in queue 

  ModuleStack mod_stack;  // The actual stack of geometric primitives for each symbol

  std::string discard_symbols;

  // contructor
  SyntaxData(int nbtopocol = 5, int featurenb = 0) {

    nbTopoColumns = nbtopocol;
    featureNb = featurenb;

    order = 0;
    first_symbol = true;
    new_order = true;

	nb_of_branches = 0; 

  }

};

#include "lsystemToMTG_scanner.h"

extern int lsystemToMTG_yyparse(void*);                                                                                          

#endif
