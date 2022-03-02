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
 *       $Id: lsystemToMTG_parser.y 17608 2014-10-17 07:46:31Z pradal $
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


/*
 *  Template parser2 for AMAPmod. Illustrates the use of two parsers
 *  within the same program.
 *
 *  To be able to do this the following steps are required:
 *
 *  1. create a file .h cooresponding to the .l and change the scanner file
 *  (see template_scanner2.[hl])
 *
 *  2. create a file .h cooresponding to the .y and change the parser file.
 *  it must be slightly updated as shown below. The parts updated
 *  are put between string brackets as follows:
 *  ################################
 *       changes ...
 *  #################################
 *
 *  3. change the makefile so that the right new prefix can be added to the "yyfunctions"
 *  (see the compilation of template_scanner2.C and template_parser2.C)
 *
 *  4. From the place where the parser/lexer are called, you must include
 *  both files template_scanner2.h and template_parser2.h.
 *  (see file call_parser2.C)
 */

%{

#include <iostream>
#include <string>
// #include "tool/tools_namespace.h"
// TOOLS_USING_NAMESPACE

#include <list>
#include <stack>

using namespace std;

/*################################*/
#include "lsystemToMTG_scanner.h"
/*#################################*/

/*################################*/
  // yyerror must be redefined since the default value is supplied as yyerror().
  // copy this macro as is, just chaging its name so that it coincides with
  // the prefix in use.
#ifndef SYSTEM_IS__CYGWIN
#define lsystemToMTG_yyerror(parser,_msg){		\
        yyerrok;\
        yyclearin;\
	GenericParser<SMB_TABLE_TYPE> p = *(GenericParser<SMB_TABLE_TYPE> *)parser; \
        p.handleError(std::string(_msg), yychar, yytname[YYTRANSLATE((yychar>=0?yychar:-yychar))]);\
        postream(p) << std::endl; }
/*#################################*/
#else
#define lsystemToMTG_yyerror(parser,_msg){		\
        yyerrok;\
        yyclearin;\
	GenericParser<SMB_TABLE_TYPE> p = *(GenericParser<SMB_TABLE_TYPE> *)parser; \
        p.handleError(std::string(_msg), yychar, "");\
	postream(p) << std::endl;}
#endif

#include "lsystemToMTG_parser.h"

#include "tool/gparser.h"

#include <limits.h>
#include <cfloat>

  // macros parser(p) and smbtable(p,t) enable you to define the
  // parser p an its symbol table t from within
  // the action part of the grammar rules use.
  // However, before, the type of the symbol table used must be set here.
  // here the parser is of type GenericParser<float> and then:

#define SMB_TABLE_TYPE float

  // definition of an undefined value (used locally in this file)
  // corresponding to the returned type (float) of an action.

#define UNDEF_FLOAT FLT_MAX
#define ISDEFINED(x) (((x)!=UNDEF_FLOAT)?true:false)

#define colsep '\t'

// If the order increases in the l-string, then the new order state
// must be pushed onto the stack and the new order variable should
// be reset.

static void increase_order(SyntaxData* sd) {

  sd->new_order_stack.push(sd->new_order);
  sd->new_order = 0;
  sd->order++;

  // Treatment of nb of branching points at this point

  sd->nb_of_branches_stack.push(sd->nb_of_branches);
  sd->nb_of_branches = 0;

}

static void decrease_order(SyntaxData* sd) {

  sd->new_order_stack.pop();

  if (sd->new_order_stack.empty())
    sd->new_order = 0;
  else
    sd->new_order = sd->new_order_stack.top();

  sd->order--;

  // Treatment of nb of branching points of the father element

  if (!sd->nb_of_branches_stack.empty())
    sd->nb_of_branches = sd->nb_of_branches_stack.top() + 1;

  // When returning to the father element the top of the stack should point
  // to the father of the father

  sd->nb_of_branches_stack.pop();

}


static void indent_code(std::ostream& o, SyntaxData* sd) {
  for (int i = 0; i< sd->order; i++) o << colsep;
}

static void fill_space_to_feature_columns(std::ostream& o, int startCol, SyntaxData* sd)
{
  // just after the column containing the topo code (column order, starting at 0)
  // columns must be filled with tabs until the first column of features.

  for(int i=sd->order;i<startCol; i++) o << colsep << std::flush;

}

bool geometric_symbol(char symbol) {

  switch (symbol) {

  // geometric symbols
  case '+':
  case '-':
  case '#':
  case ';':
    // case of geom directives for the next symbol
        // must be pushed onto the stack
        // the arglist is copied onto the stack
        // and should be deleted latter on.
        return true;
  default:
    return false;

  }

}


static void write_geometric_primitves_as_features(std::ostream& o, SyntaxData* sd) {

    o << "# ";

        while (!(sd->mod_stack.empty())) {

          MPair& p = sd->mod_stack.top();

          o << p.first << std::flush;
      o << "(";
          for (DList::iterator l=p.second.begin();l!=p.second.end();l++)
            o << *l << " ";
          o << ")" << std::flush;

      switch (p.first) {

      // geometric symbols
      case '+':

            break;
      case '-':
            break;
      case '#':
            break;
      case ';':
            break;

      default:
                break;
      }

      sd->mod_stack.pop();

    }

}

static void write_arguments(std::ostream& o, char symbol,
                                                        std::list<double>* arglist, SyntaxData* sd) {


    if (arglist && sd) {

          // Retreives the list of indexes corresponding to symbol

          std::cerr << "indexlist in parser for symbol : " << symbol;

          std::map<char, std::vector<int> >::iterator pindexlist = sd->mapSymbolArgs.find(symbol);

      if (pindexlist != sd->mapSymbolArgs.end()) {

            for (std::vector<int>::iterator pp = pindexlist->second.begin(); pp!=pindexlist->second.end();pp++)
              std::cerr << " " << *pp;
        std::cerr <<std::endl;

		/*
	    for (vector<int>::iterator pp = pindexlist->second.begin(); pp!=pindexlist->second.end();pp++)
	      cerr << " " << *pp;
        cerr << endl;
        */

            // Creates a vector containing the feature values corresponding to symbol
        std::vector<double>* featlist = new std::vector<double>(sd->featureNb);

            // All elements in vector are initialized with DBL_MAX
        for(int j=0; j<sd->featureNb; j++) {
               (*featlist)[j] = DBL_MAX;
        }

       // Goes through the list of args
        int i = 0;
        for(std::list<double>::iterator pd=arglist->begin(); pd!=arglist->end(); pd++) {

               // the ith arg in list arglist should be stored in vector
                   int index = (pindexlist->second)[i] - 1;

                   if (index >= 0 && index < sd->featureNb) {
                     (*featlist)[index] = *pd;
                     // cerr << "index = " << index << " val = " << *pd << endl;
           }
           i++;

        }

            // cerr << endl << "featureNB = " << i << endl;

        for(std::vector<double>::iterator p=featlist->begin(); p!=featlist->end();p++) {

              if (*p != DBL_MAX)
            o << *p << colsep << std::flush; // the double in written
          else
            o << colsep << std::flush;       // the column is skipped

        }

        // write the computed vector of features

        delete featlist;

      }
          else {
            std::cerr << "not defined : " << std::endl;

          }

    }

}
 
bool discard(char symbol, SyntaxData* sd) {

  std::string discard_st = sd->discard_symbols;

  if (discard_st!="") {

    bool found = false;

    for (int i=0; i<discard_st.length(); i++) 
      if (symbol == discard_st[i]) {
	found = true;
	break;
      }

    return found;
    
  }
  else return false;

}

// Writes in a MTG format what was detected in the l-string as a
// features of a topological module, i.e. something of the form Symbol(arglist).
// Here features=arglist=*pl
// Note: it may exist geometric features in the Module stack that
// should be added to the arglist.

static void write_symbol_line(char symbol, std::list<double>* pl, std::ostream& o, SyntaxData* sd)
{

  if (!(sd->first_symbol == true && sd->order > 0)) {

    if (geometric_symbol(symbol)) {
      // push the symbol and its features on the stack
      sd->mod_stack.push(MPair(symbol,(*pl)));
	
    }
    else {
    
      bool discard_symbol = discard(symbol, sd);

      // if this symbol is the first topological symbol
      // at this order(i.e. not a geometric directive),
      // it must be preceded by a +
      // otherwise by a ^<

      if (! discard_symbol) {

	indent_code(o, sd);
	
	if (sd->new_order == 0) {
	  
	  // In this case, the symbol is the first topological symbol
	  // at this order.
	  
	  if (sd->first_symbol == true) {
	    o << "/"; // for the first symbol, a decomposition sign is required
	    sd->first_symbol = false;
	  }
	  else o << "+";
	  
	  // look at the current nb of branching points of the father element
	  int inc_index = 0;
	  if (!sd->nb_of_branches_stack.empty())
	    inc_index = sd->nb_of_branches_stack.top();
	  
	  o << symbol << sd->order + inc_index << std::flush;
	  
	  // Now at this order, the other symbols are not the first ones
	  sd->new_order = 1;
	  
	}
	else {
	  o << "^<";
	  o << symbol << sd->order << std::flush;
	}
	
	
	fill_space_to_feature_columns(o, sd->nbTopoColumns, sd);
	
	write_arguments(o, symbol, pl, sd);
	
	// should also empty the stack of geom directives
	// -> iterate on the stack and transform the directives
	// into Features
	
	write_geometric_primitves_as_features(o, sd);
	
	o << std::endl;
      }
    }
  }
  else {
    o << "# symbols between [ ] at the beginning of the l-system string have been skipped" << std::endl;
  }

}


%}

%pure_parser                    /* asks for a reentrant parser: don't remove ! */
%token_table                    /* generates a token table (names of the tokens) */
%name-prefix "lsystemToMTG_yy"
%parse-param {void * parser}
%lex-param {GENERIC_LEXER * YYLEX_PARAM }

/* possible types of tokens returned by the lexer */

%union {
  int                   integer;
  double                real;
  char                  character;
  std::list<double>* doublelist;
}


/* association of types to tokens and non terminals */

%token <integer>   TokInt
%token <real>      TokReal
%token <character> TokChar
%token <character> TokQuery

%token '['
%token ']'
%token '('
%token ')'
%token ','
%token ';'
%token '#'
%token '-'
%token '+'

%token TokError

%type <real>       Arg
%type <doublelist> Arglist


%start LString

%%


LString :
   LString Module
 | Module
 | LString error
   {
     parser(p);
     postream(p) << "*** LSYSTEM-TO-MTG PARSER: OK: Resynchronized on input at ";
     postream(p) << p._plexer->YYText() << std::endl;
   }
;

Module :
   TokChar
     {
        parser(p);
            SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
            write_symbol_line($1, NULL, postream(p), sd);
         }
 | TokChar '(' Arglist ')'
     {
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           write_symbol_line($1, $<doublelist>3, postream(p), sd);
           delete $3;
         }
 | TokQuery '(' Arglist ')'
     {
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           write_symbol_line($1, $<doublelist>3, postream(p), sd);
           delete $3;
         }
 |'['
   {
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
       increase_order(sd);
   }
   LString
  ']'
   {
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           decrease_order(sd);
   }
;

Arglist :
   Arglist ',' Arg
     {
           $<doublelist>1->push_back($3);
           $<doublelist>$=$<doublelist>1;
         }
 | Arg
     {
       $<doublelist>$ = new std::list<double>;
           $<doublelist>$->push_back($1);
     }
;

Arg :
   TokReal {$$ = (double) $1;}
 | TokInt {$$ = (double) $1;}
;


%%

static void writeMTGheader(std::ostream& o) {


}



