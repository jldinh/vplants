/* A Bison parser, made from lsystemToMTG_parser.y
   by GNU bison 1.35.  */

#define YYBISON 1  /* Identify Bison output.  */

#define yyparse lsystemToMTG_yyparse
#define yylex lsystemToMTG_yylex
#define yyerror lsystemToMTG_yyerror
#define yylval lsystemToMTG_yylval
#define yychar lsystemToMTG_yychar
#define yydebug lsystemToMTG_yydebug
#define yynerrs lsystemToMTG_yynerrs
# define	TokInt	257
# define	TokReal	258
# define	TokChar	259
# define	TokQuery	260
# define	TokError	261

#line 62 "lsystemToMTG_parser.y"


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
#define lsystemToMTG_yyerror(_msg){		\
        yyerrok;\
        yyclearin;\
        parser(p);\
        p.handleError(std::string(_msg), yychar, yytname[YYTRANSLATE((yychar>=0?yychar:-yychar))]);\
        postream(p) << std::endl; }
/*#################################*/
#else
#define lsystemToMTG_yyerror(_msg){		\
        yyerrok;\
        yyclearin;\
        parser(p);\
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



#line 413 "lsystemToMTG_parser.y"
#ifndef YYSTYPE
typedef union {
  int                   integer;
  double                real;
  char                  character;
  std::list<double>* doublelist;
} yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
#ifndef YYDEBUG
# define YYDEBUG 0
#endif



#define	YYFINAL		23
#define	YYFLAG		-32768
#define	YYNTBASE	17

/* YYTRANSLATE(YYLEX) -- Bison token number corresponding to YYLEX. */
#define YYTRANSLATE(x) ((unsigned)(x) <= 261 ? yytranslate[x] : 22)

/* YYTRANSLATE[YYLEX] -- Bison token number corresponding to YYLEX. */
static const char yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,    13,     2,     2,     2,     2,
       9,    10,     2,    15,    11,    14,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,    12,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     7,     2,     8,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     3,     4,     5,
       6,    16
};

#if YYDEBUG
static const short yyprhs[] =
{
       0,     0,     3,     5,     8,    10,    15,    20,    21,    26,
      30,    32,    34
};
static const short yyrhs[] =
{
      17,    18,     0,    18,     0,    17,     1,     0,     5,     0,
       5,     9,    20,    10,     0,     6,     9,    20,    10,     0,
       0,     7,    19,    17,     8,     0,    20,    11,    21,     0,
      21,     0,     4,     0,     3,     0
};

#endif

#if YYDEBUG
/* YYRLINE[YYN] -- source line where rule number YYN was defined. */
static const short yyrline[] =
{
       0,   449,   451,   452,   460,   467,   474,   481,   481,   496,
     502,   509,   511
};
#endif

#define YYNTOKENS 17
#define YYNNTS 5
#define YYNRULES 12
#define YYNSTATES 24
#define YYMAXUTOK 261

/* YYTNAME[TOKEN_NUM] -- String name of the token TOKEN_NUM. */
static const char *const yytname[] =
{
  "$", "error", "$undefined.", "TokInt", "TokReal", "TokChar", "TokQuery", 
  "'['", "']'", "'('", "')'", "','", "';'", "'#'", "'-'", "'+'", 
  "TokError", "LString", "Module", "@1", "Arglist", "Arg", 0
};
/* YYTOKNUM[YYLEX] -- Index in YYTNAME corresponding to YYLEX. */
static const short yytoknum[] =
{
       0,   256,     2,   257,   258,   259,   260,    91,    93,    40,
      41,    44,    59,    35,    45,    43,   261,    -1
};
/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives. */
static const short yyr1[] =
{
       0,    17,    17,    17,    18,    18,    18,    19,    18,    20,
      20,    21,    21
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN. */
static const short yyr2[] =
{
       0,     2,     1,     2,     1,     4,     4,     0,     4,     3,
       1,     1,     1
};

/* YYDEFACT[S] -- default rule to reduce with in state S when YYTABLE
   doesn't specify something else to do.  Zero means the default is an
   error. */
static const short yydefact[] =
{
       0,     4,     0,     7,     0,     2,     0,     0,     0,     3,
       1,    12,    11,     0,    10,     0,     0,     5,     0,     6,
       8,     9,     0,     0
};

static const short yydefgoto[] =
{
       4,     5,     8,    13,    14
};

static const short yypact[] =
{
      -2,    14,    15,-32768,     1,-32768,     7,     7,    -2,-32768,
  -32768,-32768,-32768,     9,-32768,    11,     8,-32768,     7,-32768,
  -32768,-32768,    17,-32768
};

static const short yypgoto[] =
{
      10,    -4,-32768,    18,    12
};


#define	YYLAST		30


static const short yytable[] =
{
      10,    22,     9,     1,     2,     3,     1,     2,     3,     9,
      11,    12,    10,     1,     2,     3,    20,    23,    16,    17,
      18,    19,    18,     6,     7,    15,     0,     0,     0,     0,
      21
};

static const short yycheck[] =
{
       4,     0,     1,     5,     6,     7,     5,     6,     7,     1,
       3,     4,    16,     5,     6,     7,     8,     0,     8,    10,
      11,    10,    11,     9,     9,     7,    -1,    -1,    -1,    -1,
      18
};
#define YYPURE 1

/* -*-C-*-  Note some compilers choke on comments on `#line' lines.  */
#line 3 "bison.simple"

/* Skeleton output parser for bison,

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002 Free Software
   Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330,
   Boston, MA 02111-1307, USA.  */

/* As a special exception, when this file is copied by Bison into a
   Bison output file, you may use that output file without restriction.
   This special exception was added by the Free Software Foundation
   in version 1.24 of Bison.  */

/* This is the parser code that is written into each bison parser when
   the %semantic_parser declaration is not specified in the grammar.
   It was written by Richard Stallman by simplifying the hairy parser
   used when %semantic_parser is specified.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

#if ! defined (yyoverflow) || defined (YYERROR_VERBOSE)

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# if YYSTACK_USE_ALLOCA
#  define YYSTACK_ALLOC alloca
# else
#  ifndef YYSTACK_USE_ALLOCA
#   if defined (alloca) || defined (_ALLOCA_H)
#    define YYSTACK_ALLOC alloca
#   else
#    ifdef __GNUC__
#     define YYSTACK_ALLOC __builtin_alloca
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's `empty if-body' warning. */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
# else
#  if defined (__STDC__) || defined (__cplusplus)
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   define YYSIZE_T size_t
#  endif
#  define YYSTACK_ALLOC malloc
#  define YYSTACK_FREE free
# endif
#endif /* ! defined (yyoverflow) || defined (YYERROR_VERBOSE) */


#if (! defined (yyoverflow) \
     && (! defined (__cplusplus) \
	 || (YYLTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  short yyss;
  YYSTYPE yyvs;
# if YYLSP_NEEDED
  YYLTYPE yyls;
# endif
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAX (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# if YYLSP_NEEDED
#  define YYSTACK_BYTES(N) \
     ((N) * (sizeof (short) + sizeof (YYSTYPE) + sizeof (YYLTYPE))	\
      + 2 * YYSTACK_GAP_MAX)
# else
#  define YYSTACK_BYTES(N) \
     ((N) * (sizeof (short) + sizeof (YYSTYPE))				\
      + YYSTACK_GAP_MAX)
# endif

/* Copy COUNT objects from FROM to TO.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if 1 < __GNUC__
#   define YYCOPY(To, From, Count) \
      __builtin_memcpy (To, From, (Count) * sizeof (*(From)))
#  else
#   define YYCOPY(To, From, Count)		\
      do					\
	{					\
	  register YYSIZE_T yyi;		\
	  for (yyi = 0; yyi < (Count); yyi++)	\
	    (To)[yyi] = (From)[yyi];		\
	}					\
      while (0)
#  endif
# endif

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack)					\
    do									\
      {									\
	YYSIZE_T yynewbytes;						\
	YYCOPY (&yyptr->Stack, Stack, yysize);				\
	Stack = &yyptr->Stack;						\
	yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAX;	\
	yyptr += yynewbytes / sizeof (*yyptr);				\
      }									\
    while (0)

#endif


#if ! defined (YYSIZE_T) && defined (__SIZE_TYPE__)
# define YYSIZE_T __SIZE_TYPE__
#endif
#if ! defined (YYSIZE_T) && defined (size_t)
# define YYSIZE_T size_t
#endif
#if ! defined (YYSIZE_T)
# if defined (__STDC__) || defined (__cplusplus)
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# endif
#endif
#if ! defined (YYSIZE_T)
# define YYSIZE_T unsigned int
#endif

#define yyerrok		(yyerrstatus = 0)
#define yyclearin	(yychar = YYEMPTY)
#define YYEMPTY		-2
#define YYEOF		0
#define YYACCEPT	goto yyacceptlab
#define YYABORT 	goto yyabortlab
#define YYERROR		goto yyerrlab1
/* Like YYERROR except do call yyerror.  This remains here temporarily
   to ease the transition to the new meaning of YYERROR, for GCC.
   Once GCC version 2 has supplanted version 1, this can go.  */
#define YYFAIL		goto yyerrlab
#define YYRECOVERING()  (!!yyerrstatus)
#define YYBACKUP(Token, Value)					\
do								\
  if (yychar == YYEMPTY && yylen == 1)				\
    {								\
      yychar = (Token);						\
      yylval = (Value);						\
      yychar1 = YYTRANSLATE (yychar);				\
      YYPOPSTACK;						\
      goto yybackup;						\
    }								\
  else								\
    { 								\
      yyerror ("syntax error: cannot back up");			\
      YYERROR;							\
    }								\
while (0)

#define YYTERROR	1
#define YYERRCODE	256


/* YYLLOC_DEFAULT -- Compute the default location (before the actions
   are run).

   When YYLLOC_DEFAULT is run, CURRENT is set the location of the
   first token.  By default, to implement support for ranges, extend
   its range to the last symbol.  */

#ifndef YYLLOC_DEFAULT
# define YYLLOC_DEFAULT(Current, Rhs, N)       	\
   Current.last_line   = Rhs[N].last_line;	\
   Current.last_column = Rhs[N].last_column;
#endif


/* YYLEX -- calling `yylex' with the right arguments.  */

#if YYPURE
# if YYLSP_NEEDED
#  ifdef YYLEX_PARAM
#   define YYLEX		yylex (&yylval, &yylloc, YYLEX_PARAM)
#  else
#   define YYLEX		yylex (&yylval, &yylloc)
#  endif
# else /* !YYLSP_NEEDED */
#  ifdef YYLEX_PARAM
#   define YYLEX		yylex (&yylval, YYLEX_PARAM)
#  else
#   define YYLEX		yylex (&yylval)
#  endif
# endif /* !YYLSP_NEEDED */
#else /* !YYPURE */
# define YYLEX			yylex ()
#endif /* !YYPURE */


/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)			\
do {						\
  if (yydebug)					\
    YYFPRINTF Args;				\
} while (0)
/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
#endif /* !YYDEBUG */

/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef	YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   SIZE_MAX < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#if YYMAXDEPTH == 0
# undef YYMAXDEPTH
#endif

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif

#ifdef YYERROR_VERBOSE

# ifndef yystrlen
#  if defined (__GLIBC__) && defined (_STRING_H)
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
static YYSIZE_T
#   if defined (__STDC__) || defined (__cplusplus)
yystrlen (const char *yystr)
#   else
yystrlen (yystr)
     const char *yystr;
#   endif
{
  register const char *yys = yystr;

  while (*yys++ != '\0')
    continue;

  return yys - yystr - 1;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined (__GLIBC__) && defined (_STRING_H) && defined (_GNU_SOURCE)
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
#   if defined (__STDC__) || defined (__cplusplus)
yystpcpy (char *yydest, const char *yysrc)
#   else
yystpcpy (yydest, yysrc)
     char *yydest;
     const char *yysrc;
#   endif
{
  register char *yyd = yydest;
  register const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif
#endif

#line 315 "bison.simple"


/* The user can define YYPARSE_PARAM as the name of an argument to be passed
   into yyparse.  The argument should have type void *.
   It should actually point to an object.
   Grammar actions can access the variable by casting it
   to the proper pointer type.  */

#ifdef YYPARSE_PARAM
# if defined (__STDC__) || defined (__cplusplus)
#  define YYPARSE_PARAM_ARG void *YYPARSE_PARAM
#  define YYPARSE_PARAM_DECL
# else
#  define YYPARSE_PARAM_ARG YYPARSE_PARAM
#  define YYPARSE_PARAM_DECL void *YYPARSE_PARAM;
# endif
#else /* !YYPARSE_PARAM */
# define YYPARSE_PARAM_ARG
# define YYPARSE_PARAM_DECL
#endif /* !YYPARSE_PARAM */

/* Prevent warning if -Wstrict-prototypes.  */
#ifdef __GNUC__
# ifdef YYPARSE_PARAM
int yyparse (void *);
# else
int yyparse (void);
# endif
#endif

/* YY_DECL_VARIABLES -- depending whether we use a pure parser,
   variables are global, or local to YYPARSE.  */

#define YY_DECL_NON_LSP_VARIABLES			\
/* The lookahead symbol.  */				\
int yychar;						\
							\
/* The semantic value of the lookahead symbol. */	\
YYSTYPE yylval;						\
							\
/* Number of parse errors so far.  */			\
int yynerrs;

#if YYLSP_NEEDED
# define YY_DECL_VARIABLES			\
YY_DECL_NON_LSP_VARIABLES			\
						\
/* Location data for the lookahead symbol.  */	\
YYLTYPE yylloc;
#else
# define YY_DECL_VARIABLES			\
YY_DECL_NON_LSP_VARIABLES
#endif


/* If nonreentrant, generate the variables here. */

#if !YYPURE
YY_DECL_VARIABLES
#endif  /* !YYPURE */

int
yyparse (YYPARSE_PARAM_ARG)
     YYPARSE_PARAM_DECL
{
  /* If reentrant, generate the variables here. */
#if YYPURE
  YY_DECL_VARIABLES
#endif  /* !YYPURE */

  register int yystate;
  register int yyn;
  int yyresult;
  /* Number of tokens to shift before error messages enabled.  */
  int yyerrstatus;
  /* Lookahead token as an internal (translated) token number.  */
  int yychar1 = 0;

  /* Three stacks and their tools:
     `yyss': related to states,
     `yyvs': related to semantic values,
     `yyls': related to locations.

     Refer to the stacks thru separate pointers, to allow yyoverflow
     to reallocate them elsewhere.  */

  /* The state stack. */
  short	yyssa[YYINITDEPTH];
  short *yyss = yyssa;
  register short *yyssp;

  /* The semantic value stack.  */
  YYSTYPE yyvsa[YYINITDEPTH];
  YYSTYPE *yyvs = yyvsa;
  register YYSTYPE *yyvsp;

#if YYLSP_NEEDED
  /* The location stack.  */
  YYLTYPE yylsa[YYINITDEPTH];
  YYLTYPE *yyls = yylsa;
  YYLTYPE *yylsp;
#endif

#if YYLSP_NEEDED
# define YYPOPSTACK   (yyvsp--, yyssp--, yylsp--)
#else
# define YYPOPSTACK   (yyvsp--, yyssp--)
#endif

  YYSIZE_T yystacksize = YYINITDEPTH;


  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;
#if YYLSP_NEEDED
  YYLTYPE yyloc;
#endif

  /* When reducing, the number of symbols on the RHS of the reduced
     rule. */
  int yylen;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY;		/* Cause a token to be read.  */

  /* Initialize stack pointers.
     Waste one element of value and location stack
     so that they stay on the same level as the state stack.
     The wasted elements are never initialized.  */

  yyssp = yyss;
  yyvsp = yyvs;
#if YYLSP_NEEDED
  yylsp = yyls;
#endif
  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed. so pushing a state here evens the stacks.
     */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyssp >= yyss + yystacksize - 1)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
	/* Give user a chance to reallocate the stack. Use copies of
	   these so that the &'s don't force the real ones into
	   memory.  */
	YYSTYPE *yyvs1 = yyvs;
	short *yyss1 = yyss;

	/* Each stack pointer address is followed by the size of the
	   data in use in that stack, in bytes.  */
# if YYLSP_NEEDED
	YYLTYPE *yyls1 = yyls;
	/* This used to be a conditional around just the two extra args,
	   but that might be undefined if yyoverflow is a macro.  */
	yyoverflow ("parser stack overflow",
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),
		    &yyls1, yysize * sizeof (*yylsp),
		    &yystacksize);
	yyls = yyls1;
# else
	yyoverflow ("parser stack overflow",
		    &yyss1, yysize * sizeof (*yyssp),
		    &yyvs1, yysize * sizeof (*yyvsp),
		    &yystacksize);
# endif
	yyss = yyss1;
	yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyoverflowlab;
# else
      /* Extend the stack our own way.  */
      if (yystacksize >= YYMAXDEPTH)
	goto yyoverflowlab;
      yystacksize *= 2;
      if (yystacksize > YYMAXDEPTH)
	yystacksize = YYMAXDEPTH;

      {
	short *yyss1 = yyss;
	union yyalloc *yyptr =
	  (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
	if (! yyptr)
	  goto yyoverflowlab;
	YYSTACK_RELOCATE (yyss);
	YYSTACK_RELOCATE (yyvs);
# if YYLSP_NEEDED
	YYSTACK_RELOCATE (yyls);
# endif
# undef YYSTACK_RELOCATE
	if (yyss1 != yyssa)
	  YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;
#if YYLSP_NEEDED
      yylsp = yyls + yysize - 1;
#endif

      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
		  (unsigned long int) yystacksize));

      if (yyssp >= yyss + yystacksize - 1)
	YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:

/* Do appropriate processing given the current state.  */
/* Read a lookahead token if we need one and don't already have one.  */
/* yyresume: */

  /* First try to decide what to do without reference to lookahead token.  */

  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* yychar is either YYEMPTY or YYEOF
     or a valid token in external form.  */

  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = YYLEX;
    }

  /* Convert token to internal form (in yychar1) for indexing tables with */

  if (yychar <= 0)		/* This means end of input. */
    {
      yychar1 = 0;
      yychar = YYEOF;		/* Don't call YYLEX any more */

      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yychar1 = YYTRANSLATE (yychar);

#if YYDEBUG
     /* We have to keep this `#if YYDEBUG', since we use variables
	which are defined only if `YYDEBUG' is set.  */
      if (yydebug)
	{
	  YYFPRINTF (stderr, "Next token is %d (%s",
		     yychar, yytname[yychar1]);
	  /* Give the individual parser a way to print the precise
	     meaning of a token, for further debugging info.  */
# ifdef YYPRINT
	  YYPRINT (stderr, yychar, yylval);
# endif
	  YYFPRINTF (stderr, ")\n");
	}
#endif
    }

  yyn += yychar1;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != yychar1)
    goto yydefault;

  yyn = yytable[yyn];

  /* yyn is what to do for this token type in this state.
     Negative => reduce, -yyn is rule number.
     Positive => shift, yyn is new state.
       New state is final state => don't bother to shift,
       just return success.
     0, or most negative number => error.  */

  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrlab;

  if (yyn == YYFINAL)
    YYACCEPT;

  /* Shift the lookahead token.  */
  YYDPRINTF ((stderr, "Shifting token %d (%s), ",
	      yychar, yytname[yychar1]));

  /* Discard the token being shifted unless it is eof.  */
  if (yychar != YYEOF)
    yychar = YYEMPTY;

  *++yyvsp = yylval;
#if YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  yystate = yyn;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     `$$ = $1'.

     Otherwise, the following line sets YYVAL to the semantic value of
     the lookahead token.  This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];

#if YYLSP_NEEDED
  /* Similarly for the default location.  Let the user run additional
     commands if for instance locations are ranges.  */
  yyloc = yylsp[1-yylen];
  YYLLOC_DEFAULT (yyloc, (yylsp - yylen), yylen);
#endif

#if YYDEBUG
  /* We have to keep this `#if YYDEBUG', since we use variables which
     are defined only if `YYDEBUG' is set.  */
  if (yydebug)
    {
      int yyi;

      YYFPRINTF (stderr, "Reducing via rule %d (line %d), ",
		 yyn, yyrline[yyn]);

      /* Print the symbols being reduced, and their result.  */
      for (yyi = yyprhs[yyn]; yyrhs[yyi] > 0; yyi++)
	YYFPRINTF (stderr, "%s ", yytname[yyrhs[yyi]]);
      YYFPRINTF (stderr, " -> %s\n", yytname[yyr1[yyn]]);
    }
#endif

  switch (yyn) {

case 3:
#line 453 "lsystemToMTG_parser.y"
{
     parser(p);
     postream(p) << "*** LSYSTEM-TO-MTG PARSER: OK: Resynchronized on input at ";
     postream(p) << p._plexer->YYText() << std::endl;
   ;
    break;}
case 4:
#line 462 "lsystemToMTG_parser.y"
{
        parser(p);
            SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
            write_symbol_line(yyvsp[0].character, NULL, postream(p), sd);
         ;
    break;}
case 5:
#line 468 "lsystemToMTG_parser.y"
{
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           write_symbol_line(yyvsp[-3].character, yyvsp[-1].doublelist, postream(p), sd);
           delete yyvsp[-1].doublelist;
         ;
    break;}
case 6:
#line 475 "lsystemToMTG_parser.y"
{
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           write_symbol_line(yyvsp[-3].character, yyvsp[-1].doublelist, postream(p), sd);
           delete yyvsp[-1].doublelist;
         ;
    break;}
case 7:
#line 482 "lsystemToMTG_parser.y"
{
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
       increase_order(sd);
   ;
    break;}
case 8:
#line 489 "lsystemToMTG_parser.y"
{
       parser(p);
           SyntaxData* sd = (SyntaxData*)(p._data_for_parsing);
           decrease_order(sd);
   ;
    break;}
case 9:
#line 498 "lsystemToMTG_parser.y"
{
           yyvsp[-2].doublelist->push_back(yyvsp[0].real);
           yyval.doublelist=yyvsp[-2].doublelist;
         ;
    break;}
case 10:
#line 503 "lsystemToMTG_parser.y"
{
       yyval.doublelist = new std::list<double>;
           yyval.doublelist->push_back(yyvsp[0].real);
     ;
    break;}
case 11:
#line 510 "lsystemToMTG_parser.y"
{yyval.real = (double) yyvsp[0].real;;
    break;}
case 12:
#line 511 "lsystemToMTG_parser.y"
{yyval.real = (double) yyvsp[0].integer;;
    break;}
}

#line 705 "bison.simple"


  yyvsp -= yylen;
  yyssp -= yylen;
#if YYLSP_NEEDED
  yylsp -= yylen;
#endif

#if YYDEBUG
  if (yydebug)
    {
      short *yyssp1 = yyss - 1;
      YYFPRINTF (stderr, "state stack now");
      while (yyssp1 != yyssp)
	YYFPRINTF (stderr, " %d", *++yyssp1);
      YYFPRINTF (stderr, "\n");
    }
#endif

  *++yyvsp = yyval;
#if YYLSP_NEEDED
  *++yylsp = yyloc;
#endif

  /* Now `shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTBASE] + *yyssp;
  if (yystate >= 0 && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTBASE];

  goto yynewstate;


/*------------------------------------.
| yyerrlab -- here on detecting error |
`------------------------------------*/
yyerrlab:
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;

#ifdef YYERROR_VERBOSE
      yyn = yypact[yystate];

      if (yyn > YYFLAG && yyn < YYLAST)
	{
	  YYSIZE_T yysize = 0;
	  char *yymsg;
	  int yyx, yycount;

	  yycount = 0;
	  /* Start YYX at -YYN if negative to avoid negative indexes in
	     YYCHECK.  */
	  for (yyx = yyn < 0 ? -yyn : 0;
	       yyx < (int) (sizeof (yytname) / sizeof (char *)); yyx++)
	    if (yycheck[yyx + yyn] == yyx)
	      yysize += yystrlen (yytname[yyx]) + 15, yycount++;
	  yysize += yystrlen ("parse error, unexpected ") + 1;
	  yysize += yystrlen (yytname[YYTRANSLATE (yychar)]);
	  yymsg = (char *) YYSTACK_ALLOC (yysize);
	  if (yymsg != 0)
	    {
	      char *yyp = yystpcpy (yymsg, "parse error, unexpected ");
	      yyp = yystpcpy (yyp, yytname[YYTRANSLATE (yychar)]);

	      if (yycount < 5)
		{
		  yycount = 0;
		  for (yyx = yyn < 0 ? -yyn : 0;
		       yyx < (int) (sizeof (yytname) / sizeof (char *));
		       yyx++)
		    if (yycheck[yyx + yyn] == yyx)
		      {
			const char *yyq = ! yycount ? ", expecting " : " or ";
			yyp = yystpcpy (yyp, yyq);
			yyp = yystpcpy (yyp, yytname[yyx]);
			yycount++;
		      }
		}
	      yyerror (yymsg);
	      YYSTACK_FREE (yymsg);
	    }
	  else
	    yyerror ("parse error; also virtual memory exhausted");
	}
      else
#endif /* defined (YYERROR_VERBOSE) */
	yyerror ("parse error");
    }
  goto yyerrlab1;


/*--------------------------------------------------.
| yyerrlab1 -- error raised explicitly by an action |
`--------------------------------------------------*/
yyerrlab1:
  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
	 error, discard it.  */

      /* return failure if at end of input */
      if (yychar == YYEOF)
	YYABORT;
      YYDPRINTF ((stderr, "Discarding token %d (%s).\n",
		  yychar, yytname[yychar1]));
      yychar = YYEMPTY;
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */

  yyerrstatus = 3;		/* Each real token shifted decrements this */

  goto yyerrhandle;


/*-------------------------------------------------------------------.
| yyerrdefault -- current state does not do anything special for the |
| error token.                                                       |
`-------------------------------------------------------------------*/
yyerrdefault:
#if 0
  /* This is wrong; only states that explicitly want error tokens
     should shift them.  */

  /* If its default is to accept any token, ok.  Otherwise pop it.  */
  yyn = yydefact[yystate];
  if (yyn)
    goto yydefault;
#endif


/*---------------------------------------------------------------.
| yyerrpop -- pop the current state because it cannot handle the |
| error token                                                    |
`---------------------------------------------------------------*/
yyerrpop:
  if (yyssp == yyss)
    YYABORT;
  yyvsp--;
  yystate = *--yyssp;
#if YYLSP_NEEDED
  yylsp--;
#endif

#if YYDEBUG
  if (yydebug)
    {
      short *yyssp1 = yyss - 1;
      YYFPRINTF (stderr, "Error: state stack now");
      while (yyssp1 != yyssp)
	YYFPRINTF (stderr, " %d", *++yyssp1);
      YYFPRINTF (stderr, "\n");
    }
#endif

/*--------------.
| yyerrhandle.  |
`--------------*/
yyerrhandle:
  yyn = yypact[yystate];
  if (yyn == YYFLAG)
    goto yyerrdefault;

  yyn += YYTERROR;
  if (yyn < 0 || yyn > YYLAST || yycheck[yyn] != YYTERROR)
    goto yyerrdefault;

  yyn = yytable[yyn];
  if (yyn < 0)
    {
      if (yyn == YYFLAG)
	goto yyerrpop;
      yyn = -yyn;
      goto yyreduce;
    }
  else if (yyn == 0)
    goto yyerrpop;

  if (yyn == YYFINAL)
    YYACCEPT;

  YYDPRINTF ((stderr, "Shifting error token, "));

  *++yyvsp = yylval;
#if YYLSP_NEEDED
  *++yylsp = yylloc;
#endif

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

/*---------------------------------------------.
| yyoverflowab -- parser overflow comes here.  |
`---------------------------------------------*/
yyoverflowlab:
  yyerror ("parser stack overflow");
  yyresult = 2;
  /* Fall through.  */

yyreturn:
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
  return yyresult;
}
#line 515 "lsystemToMTG_parser.y"


static void writeMTGheader(std::ostream& o) {


}



