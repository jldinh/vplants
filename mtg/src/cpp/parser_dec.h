#define CPL
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
 *       $Id: parser_dec.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef PARSER_HEADER
#define PARSER_HEADER

#include <stdio.h>

#ifndef CPL
#include "aml/defs.h"
#else
#include "bitvec.h"
#endif

#include "error.h"
#include "scanner.h"

typedef struct {
  char symbol;
  int index;
} Label;

typedef struct {
  int ident;
  int vprefix;
  const EType* relation;
  Label label;
} VName;

class MTG;

extern int yychar;
extern ErrorList* parseMTG(MTG* mtg, int line_nb,std::ostream& errstream,int maxerrornb);
extern void cleanErrorList(); // the only variable which is not cleaned by the parser is cleaned by this function
extern ErrorList* getErrorList();

// These functions return the exact vprefix in terms of line and column of
// the scanning head. This takes into account the possibility of a lookahead
// reading (stored in the variable yychar).

extern const char* tokenName(int token);
extern const char* tokenVal();
extern int lineNb();
extern int columnNb();
extern int firstFeatCol();
extern const char* inputLine();
extern AmlBoolean lineCodeErrorState();

extern int yyerror(char* errtype); // creates a error item with correct line and column nbs

#endif
