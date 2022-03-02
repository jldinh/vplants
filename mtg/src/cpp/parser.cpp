/* A Bison parser, made from parser.y
   by GNU bison 1.35.  */

#define YYBISON 1  /* Identify Bison output.  */

# define	TokCODE	257
# define	TokFORM_A	258
# define	TokFORM_B	259
# define	TokCLASSES	260
# define	TokSYMBOL	261
# define	TokSCALE	262
# define	TokVDECOMP	263
# define	TokINDEXATION	264
# define	TokVDEF	265
# define	TokDESCRIPTION	266
# define	TokLEFT	267
# define	TokRIGHT	268
# define	TokRELTYPE	269
# define	TokMAX	270
# define	TokFEATURES	271
# define	TokFNAME	272
# define	TokFTYPE	273
# define	TokMTG	274
# define	TokENTITYCODE	275
# define	TokReltype	276
# define	TokFType	277
# define	TokString	278
# define	TokFilename	279
# define	TokSymbol	280
# define	TokInteger	281
# define	tabc	282
# define	eol	283
# define	TokError	284

#line 1 "parser.y"
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
 *       $Id: parser.y 5640 2008-10-29 12:51:01Z boudon $
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





#include <stdlib.h>
#include <iostream>
#include <fstream>

#include <assert.h>

#include "tool/util_math.h"


#include "tool/rw_cstring.h"
#include "tool/rw_hdict.h"
#include "tool/rw_vector.h"
#include "tool/rw_list.h"
//#include "tool/rw_zone.h"
//#include "tool/rw_locale.h"
//#include <rw/cstring.h>
//#include <rw/tvslist.h>
//#include <rw/tvhdict.h>
//#include <rw/tvordvec.h>
//#include <rw/zone.h>
//#include <rw/locale.h>

#include "tool/dirnames.h"
// #include "GEOM/geom_geometry.h"
// #include "GEOM/appe_appearance.h"
// #include "GEOM/scne_smbtable.h"
#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_appearance.h"
#include "plantgl/scenegraph/core/smbtable.h"
#include "plantgl/algo/codec/cdc_geom.h"

PGL_USING_NAMESPACE
VPTOOLS_USING_NAMESPACE

#include "tool/util_hashmap.h"

#include <string>

#include "mtg.h"
#include "error.h"
#include "errormsgs.h"
#include "parser_dec.h"
#include "vtxinfo.h"

static const char rcsid[] = "$Id: parser.y 5640 2008-10-29 12:51:01Z boudon $";

#if 0
#define PARSERDEBUG
#endif

typedef RWTValDlist<char> SymbList;
typedef RWTValDlistIterator<char> SymbListIter;
typedef RWTValHashDictionary<RWCString, size_t> StringIntDict;


// #define YYERROR_VERBOSE

#define CHECKIFABORT if (the_errlist->entries() >= the_errlist->maxErrorNb()) YYABORT



// ----------------------------
// Functions used by the parser
// ----------------------------

static void initParsing();
static void cleanParser();
static void REDUCING(char*);
static void STARTING(char*);
static void printAnalysisPercent();
static int createMTG(int scale_nb, ClassDef* cldef, FSetDef* fsetdef);
static void addClassDescription(ClassDef* cldef, char class1, char class2, EType reltype, int val);
static void addFeature(StringArray& featname, FTypeArray& feattype, FeatureSmbTableArray& _smbtable1,
                       char* nameval, FType typeval, void* _smbtable2);
static int findVertexByName_A(char vclass, int index, int loc, EType etype);
static int findVertexByName_B(char vclass, int index, int loc, EType etype);
static int defineVertexByName_A(char vclass_symbol, int index, VId loc, EType et);
static int defineVertexByName_B(char vclass_symbol, int index, VId loc, EType et);
static int vtxprefix(int vtx);
static void addFSet(VId v, Feature* f);
static int storeFeatureValue(int vtx, Feature* fset, int findex);


// -----------------------
// Static Global Variables
// -----------------------

static MTG* the_mtg = 0;
static int file_line_nb = 0;

static VName last_vname;

static ErrorList* the_errlist = 0;

static double old_dec_ratio = 0;

// ----------
// MTG Header
// ----------

static MTGCode mtg_code;              // code form A or B

static int class_nb = 0;
static int scale_nb = 0;

static CharArray* class_symbol = 0;
static IntArray* scale = 0;

static IntArray* vdecomp = 0;
static IntArray* vindexing = 0;
static IntArray* vdef = 0;

static ClassDef* cldef = 0;

static int feature_nb = 0;
static StringArray* featname = 0;
static FTypeArray* feattype = 0;
static FeatureSmbTableArray* smbtable_array = 0;
static FSetDef* fsetdef = 0;

static IntArray* col_name_index = 0; // gives the column nb of the ith feature.
static Feature* fset = 0;            // current set of features

// Hash Dictionary for Alias management

static size_t hashFunc(const RWCString& str) {return str.hash();}
static StringIntDict* alias_dict = 0; // mapping between vertex indexes and their aliases

// Identation management

static IntArray* indent_tbl = 0;      // index i gives the vertex stacked at identation level i
static int previous_indent_level = 0;  // current line identation level
static int current_indent_level = -1;  // current line identation level

static SymbList* symblist = 0;        // Used for storing lists of symbols (chars)

static VtxInfo* vinfo = 0;            // line nbs where a vertex occurs

// Flags positionned on the first error occuring in a certain file section

static AmlBoolean classes_flag_err = FALSE;
static AmlBoolean descrip_flag_err = FALSE;
static AmlBoolean feature_flag_err = FALSE;
static AmlBoolean mtghead_flag_err = FALSE;
static AmlBoolean code_flag_err = FALSE;

static const char* token_name[] = {

  "TokCODE",
  "TokFORM_A",
  "TokFORM_B",

  "TokCLASSES",
  "TokSYMBOL",
  "TokSCALE",
  "TokVDECOMP",
  "TokINDEXATION",
  "TokVDEF",

  "TokDESCRIPTION",
  "TokLEFT",
  "TokRIGHT",
  "TokRELTYPE",
  "TokMAX",

  "TokFEATURES",
  "TokFNAME",
  "TokFTYPE",

  "TokMTG",
  "TokENTITYCODE",

  "TokReltype",
  "TokFType",
  "TokString",
  "TokSymbol",
  "TokInteger",

  "tab",
  "eol",

  "TokError"

};



#line 267 "parser.y"
#ifndef YYSTYPE
typedef union{
  int intval;
  char charval;
  CString stgval;
  void* symblistpt;  // should be of type SymbList*, but this is a parametrized type.
  const EType* etypeval;
  FType ftypeval;
  VName vname;
  Label label;
} yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
#ifndef YYDEBUG
# define YYDEBUG 0
#endif



#define	YYFINAL		267
#define	YYFLAG		-32768
#define	YYNTBASE	37

/* YYTRANSLATE(YYLEX) -- Bison token number corresponding to YYLEX. */
#define YYTRANSLATE(x) ((unsigned)(x) <= 284 ? yytranslate[x] : 106)

/* YYTRANSLATE[YYLEX] -- Bison token number corresponding to YYLEX. */
static const char yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      33,    36,    35,     2,    32,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,    31,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,    34,     2,     2,     2,     2,     2,
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
       6,     7,     8,     9,    10,    11,    12,    13,    14,    15,
      16,    17,    18,    19,    20,    21,    22,    23,    24,    25,
      26,    27,    28,    29,    30
};

#if YYDEBUG
static const short yyprhs[] =
{
       0,     0,     4,     7,     8,    14,    15,    23,    28,    36,
      41,    42,    45,    48,    49,    54,    55,    60,    64,    68,
      74,    82,    94,    98,   110,   111,   112,   113,   114,   131,
     132,   133,   134,   135,   152,   156,   159,   160,   165,   166,
     171,   175,   181,   189,   199,   203,   213,   214,   215,   228,
     230,   234,   238,   239,   243,   245,   250,   251,   256,   260,
     266,   274,   280,   284,   290,   293,   295,   301,   309,   313,
     317,   318,   321,   322,   325,   326,   331,   332,   337,   341,
     347,   355,   356,   362,   366,   370,   371,   374,   376,   378,
     379,   382,   383,   384,   385,   392,   397,   403,   409,   416,
     422,   427,   428,   432,   436,   439,   442,   445,   447,   451,
     454,   455,   457,   461,   465,   466,   470,   473,   476,   478,
     480,   481,   483,   487,   490,   492,   494,   497,   498
};
static const short yyrhs[] =
{
      38,    39,    79,     0,    38,     1,     0,     0,    40,    41,
      45,    59,    68,     0,     0,    42,     3,    31,    28,    43,
      86,    29,     0,    42,    85,     1,    29,     0,    42,     3,
      31,    28,    43,     1,    29,     0,    42,     3,     1,    29,
       0,     0,    44,     4,     0,    44,     5,     0,     0,    46,
      47,    48,    49,     0,     0,     6,    31,    86,    29,     0,
      86,     1,    29,     0,     6,     1,    29,     0,     6,    31,
      86,     1,    29,     0,     6,    31,    86,    29,    86,     1,
      29,     0,     7,    28,     8,    28,     9,    28,    10,    28,
      11,    86,    29,     0,     7,     1,    29,     0,     7,    28,
       8,    28,     9,    28,    10,    28,    11,     1,    29,     0,
       0,     0,     0,     0,    49,    26,    50,    28,    27,    51,
      28,    27,    52,    28,    27,    28,    27,    53,    86,    29,
       0,     0,     0,     0,     0,    58,    26,    54,    28,    27,
      55,    28,    27,    56,    28,    27,    28,    27,    57,    86,
      29,     0,    49,     1,    29,     0,     1,    29,     0,     0,
      60,    61,    62,    63,     0,     0,    12,    31,    86,    29,
       0,    12,     1,    29,     0,    12,    31,    86,     1,    29,
       0,    12,    31,    86,    29,    86,     1,    29,     0,    13,
      28,    14,    28,    15,    28,    16,    86,    29,     0,    13,
       1,    29,     0,    13,    28,    14,    28,    15,    28,    16,
       1,    29,     0,     0,     0,    63,    26,    64,    28,    67,
      28,    22,    28,    27,    86,    65,    29,     0,    66,     0,
      63,     1,    29,     0,    85,     1,    29,     0,     0,    67,
      32,    26,     0,    26,     0,    69,    70,    71,    72,     0,
       0,    17,    31,    86,    29,     0,    17,     1,    29,     0,
      17,    31,    86,     1,    29,     0,    17,    31,    86,    29,
      86,     1,    29,     0,    18,    28,    19,    86,    29,     0,
      18,     1,    29,     0,    18,    28,    19,     1,    29,     0,
      72,    73,     0,    74,     0,    75,    28,    77,    86,    29,
       0,    75,    28,    77,    28,    25,    86,    29,     0,    72,
       1,    29,     0,    85,     1,    29,     0,     0,    76,    24,
       0,     0,    78,    23,     0,     0,    80,    81,    82,    87,
       0,     0,    20,    31,    86,    29,     0,    20,     1,    29,
       0,    20,    31,    86,     1,    29,     0,    20,    31,    86,
      29,    86,     1,    29,     0,     0,    21,    84,    86,    83,
      29,     0,    21,     1,    29,     0,    84,    85,    24,     0,
       0,    85,    28,     0,    28,     0,    85,     0,     0,    87,
      88,     0,     0,     0,     0,    91,    92,    89,    99,    90,
      29,     0,    91,    92,     1,    29,     0,    91,    93,    22,
       1,    29,     0,    91,    92,    22,     1,    29,     0,    91,
      94,    33,    24,     1,    29,     0,    91,    94,    34,     1,
      29,     0,    91,    94,     1,    29,     0,     0,    92,    22,
      97,     0,    93,    22,    97,     0,    93,    35,     0,    94,
      95,     0,    94,    96,     0,    94,     0,    94,     1,    22,
       0,    94,    28,     0,     0,    34,     0,    33,    24,    36,
       0,    33,     1,    36,     0,     0,    26,    98,    27,     0,
       1,    27,     0,    26,     1,     0,   100,     0,   101,     0,
       0,    85,     0,   101,    28,   102,     0,    85,   103,     0,
     103,     0,   104,     0,   105,    24,     0,     0,     0
};

#endif

#if YYDEBUG
/* YYRLINE[YYN] -- source line where rule number YYN was defined. */
static const short yyrline[] =
{
       0,   282,   296,   312,   325,   340,   352,   363,   384,   407,
     428,   436,   446,   458,   471,   494,   502,   506,   520,   534,
     549,   562,   566,   583,   600,   600,   600,   600,   600,   666,
     666,   666,   666,   666,   728,   745,   763,   775,   790,   798,
     802,   817,   832,   847,   851,   867,   884,   884,   884,   986,
     996,  1014,  1034,  1042,  1058,  1082,  1104,  1112,  1116,  1131,
    1146,  1161,  1165,  1182,  1199,  1201,  1210,  1228,  1414,  1433,
    1453,  1461,  1487,  1495,  1508,  1521,  1535,  1543,  1548,  1563,
    1578,  1593,  1593,  1634,  1651,  1695,  1708,  1713,  1720,  1723,
    1730,  1737,  1751,  1751,  1751,  1934,  1958,  1983,  2008,  2032,
    2056,  2080,  2108,  2251,  2327,  2376,  2410,  2443,  2495,  2520,
    2525,  2531,  2535,  2562,  2583,  2583,  2613,  2635,  2674,  2676,
    2679,  2681,  2685,  2692,  2698,  2700,  2703,  2766,  2770
};
#endif


#if (YYDEBUG) || defined YYERROR_VERBOSE

/* YYTNAME[TOKEN_NUM] -- String name of the token TOKEN_NUM. */
static const char *const yytname[] =
{
  "$", "error", "$undefined.", "TokCODE", "TokFORM_A", "TokFORM_B", 
  "TokCLASSES", "TokSYMBOL", "TokSCALE", "TokVDECOMP", "TokINDEXATION", 
  "TokVDEF", "TokDESCRIPTION", "TokLEFT", "TokRIGHT", "TokRELTYPE", 
  "TokMAX", "TokFEATURES", "TokFNAME", "TokFTYPE", "TokMTG", 
  "TokENTITYCODE", "TokReltype", "TokFType", "TokString", "TokFilename", 
  "TokSymbol", "TokInteger", "tabc", "eol", "TokError", "':'", "','", 
  "'('", "'^'", "'*'", "')'", "File", "StartFile", "Header", 
  "StartHeader", "CodeForm", "StartCodeForm", "CodeFormValue", 
  "StartCodeFormValue", "ClassDef", "StartClassDef", "ClassDefTitle", 
  "ClassDefHead", "ClassList", "@1", "@2", "@3", "@4", "@5", "@6", "@7", 
  "@8", "StartClassList", "ClassDescription", "StartClassDescription", 
  "ClassDescriptionTitle", "ClassDescriptionHead", "ClassDescriptionList", 
  "@9", "@10", "StartClassDescriptionList", "SymbolList", "FeatureDef", 
  "StartFeatureDef", "FeatureDefTitle", "FeatureDefHead", 
  "FeatureDefList", "FeatureLine", "StartFeatureDefList", "FName", 
  "StartFName", "FType", "StartFType", "MTGDescription", 
  "StartMTGDescription", "MTGDescriptionTitle", "MTGDescriptionHead", 
  "@11", "AttributeLabels", "Tab", "LambdaTab", "ElementList", "Element", 
  "@12", "@13", "StartElement", "VName", "OutSet", "Indentation", 
  "EscapeMarker", "Alias", "Label", "@14", "FeatureList", 
  "EmptyFeatureList", "FilledFeatureList", "FeatureVal", 
  "FilledFeatureVal", "EmptyFeatureVal", "StartFeatureVal", 0
};
#endif

/* YYR1[YYN] -- Symbol number of symbol that rule YYN derives. */
static const short yyr1[] =
{
       0,    37,    37,    38,    39,    40,    41,    41,    41,    41,
      42,    43,    43,    44,    45,    46,    47,    47,    47,    47,
      47,    48,    48,    48,    50,    51,    52,    53,    49,    54,
      55,    56,    57,    49,    49,    49,    58,    59,    60,    61,
      61,    61,    61,    62,    62,    62,    64,    65,    63,    63,
      63,    63,    66,    67,    67,    68,    69,    70,    70,    70,
      70,    71,    71,    71,    72,    72,    73,    73,    72,    72,
      74,    75,    76,    77,    78,    79,    80,    81,    81,    81,
      81,    83,    82,    82,    84,    84,    85,    85,    86,    86,
      87,    87,    89,    90,    88,    88,    88,    88,    88,    88,
      88,    91,    92,    92,    92,    93,    93,    93,    93,    94,
      94,    95,    96,    96,    98,    97,    97,    97,    99,    99,
     100,   100,   101,   101,   102,   102,   103,   104,   105
};

/* YYR2[YYN] -- Number of symbols composing right hand side of rule YYN. */
static const short yyr2[] =
{
       0,     3,     2,     0,     5,     0,     7,     4,     7,     4,
       0,     2,     2,     0,     4,     0,     4,     3,     3,     5,
       7,    11,     3,    11,     0,     0,     0,     0,    16,     0,
       0,     0,     0,    16,     3,     2,     0,     4,     0,     4,
       3,     5,     7,     9,     3,     9,     0,     0,    12,     1,
       3,     3,     0,     3,     1,     4,     0,     4,     3,     5,
       7,     5,     3,     5,     2,     1,     5,     7,     3,     3,
       0,     2,     0,     2,     0,     4,     0,     4,     3,     5,
       7,     0,     5,     3,     3,     0,     2,     1,     1,     0,
       2,     0,     0,     0,     6,     4,     5,     5,     6,     5,
       4,     0,     3,     3,     2,     2,     2,     1,     3,     2,
       0,     1,     3,     3,     0,     3,     2,     2,     1,     1,
       0,     1,     3,     2,     1,     1,     2,     0,     0
};

/* YYDEFACT[S] -- default rule to reduce with in state S when YYTABLE
   doesn't specify something else to do.  Zero means the default is an
   error. */
static const short yydefact[] =
{
       3,     0,     2,    76,    10,     1,     0,    15,     0,     0,
       0,    38,    89,     0,    87,     0,     0,    89,     0,    91,
      56,     0,     0,     0,    88,     0,     0,     0,     0,    86,
      78,     0,     0,    89,   101,     4,     0,     0,     0,     0,
      89,     0,     0,     0,     9,    13,     7,     0,    77,    83,
      88,    81,    90,   110,     0,     0,     0,    89,     0,    52,
      18,     0,     0,     0,     0,     0,     0,    17,     0,     0,
      79,     0,    84,     0,     0,     0,     0,     0,    89,     0,
      70,    40,     0,     0,     0,     0,    49,     0,     0,    16,
      22,     0,    35,     0,    24,    29,     0,     0,    11,    12,
       0,    82,     0,     0,   120,     0,   104,     0,   109,     0,
       0,   105,   106,    58,     0,     0,     0,     0,    65,     0,
       0,    39,    44,     0,     0,    46,     0,    19,     0,     0,
      34,     0,     0,     8,     6,    80,    95,     0,     0,   102,
     121,    93,   118,   119,     0,   103,   108,   100,     0,     0,
       0,     0,    57,    62,     0,     0,    64,     0,     0,     0,
      41,     0,     0,    50,     0,    51,     0,     0,     0,     0,
     116,    97,   117,     0,   123,     0,     0,   127,    96,   113,
       0,   112,    99,    59,     0,     0,     0,    68,    74,    71,
      69,     0,     0,     0,    20,     0,    25,    30,   115,   126,
      94,   122,   124,   125,    98,     0,    63,    61,    89,     0,
      42,     0,    54,     0,     0,     0,     0,    60,    87,     0,
      73,     0,     0,     0,     0,     0,     0,    89,    66,     0,
       0,     0,    53,     0,    26,    31,     0,    45,    43,     0,
       0,     0,     0,     0,    67,    89,    23,    21,     0,     0,
      47,     0,     0,     0,     0,     0,    48,    27,    32,    89,
      89,     0,     0,    28,    33,     0,     0,     0
};

static const short yydefgoto[] =
{
     265,     1,     3,     4,     7,     8,    68,    69,    11,    12,
      23,    42,    65,   131,   215,   242,   259,   132,   216,   243,
     260,    66,    20,    21,    38,    59,    85,   164,   253,    86,
     213,    35,    36,    55,    80,   117,   156,   118,   157,   158,
     208,   209,     5,     6,    10,    19,    73,    33,    24,    25,
      34,    52,   104,   176,    53,    74,    75,    76,   111,   112,
     139,   173,   141,   142,   143,   201,   174,   203,   175
};

static const short yypact[] =
{
  -32768,    67,-32768,-32768,-32768,-32768,    58,-32768,    84,     2,
      85,-32768,   105,     4,-32768,    63,    -8,    51,    21,-32768,
  -32768,   103,    13,    78,    94,   120,    96,    95,    97,-32768,
  -32768,     5,    98,    51,   129,-32768,   114,    14,   117,   107,
      51,    64,    83,   109,-32768,-32768,-32768,   110,    68,-32768,
       0,-32768,-32768,-32768,    16,   116,   111,    51,    70,    51,
  -32768,    17,   112,   124,   115,    81,   119,-32768,    28,   113,
  -32768,   141,-32768,   118,    26,   -15,     8,   121,    51,    73,
      51,-32768,    57,   122,   132,    82,-32768,    74,   123,    68,
  -32768,   125,-32768,   126,-32768,-32768,   127,   128,-32768,-32768,
     130,-32768,   131,    87,    51,    93,-32768,   -10,-32768,    76,
       3,-32768,-32768,-32768,    61,   133,   135,   104,-32768,    75,
     134,    68,-32768,   136,   137,-32768,   138,-32768,   142,   139,
  -32768,   140,   143,-32768,-32768,-32768,-32768,   -19,    62,-32768,
      86,-32768,-32768,   144,   -16,-32768,-32768,-32768,   145,     1,
     146,   147,    68,-32768,    31,   148,-32768,   150,   149,   151,
  -32768,   157,   154,-32768,   155,-32768,   153,   156,   152,   158,
  -32768,-32768,-32768,   159,-32768,   163,   160,   164,-32768,-32768,
     161,-32768,-32768,-32768,   169,   165,   166,-32768,-32768,-32768,
  -32768,   167,   170,   171,-32768,   182,-32768,-32768,-32768,-32768,
  -32768,-32768,-32768,-32768,-32768,   172,-32768,-32768,   174,   176,
  -32768,   177,-32768,    88,   175,   178,   179,-32768,   180,   183,
  -32768,    38,   186,   185,   189,   187,   188,    51,-32768,   184,
     190,   181,-32768,    52,-32768,-32768,   191,-32768,-32768,   194,
     193,   195,   197,   198,-32768,    51,-32768,-32768,   196,   200,
  -32768,   201,   202,   203,   204,   206,-32768,-32768,-32768,    51,
      51,   205,   207,-32768,-32768,   217,   218,-32768
};

static const short yypgoto[] =
{
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,    -7,   -17,
  -32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,-32768,
      44,-32768,-32768,-32768,-32768,-32768,   -12,-32768,-32768
};


#define	YYLAST		243


static const short yytable[] =
{
      31,    15,   180,    16,   150,    26,    47,   105,   170,   107,
     171,   170,   146,   178,    39,    56,    51,    77,    88,   147,
     106,    30,    32,    61,    72,  -111,    50,   102,    29,    96,
    -107,    71,   185,    17,    48,    27,   108,   181,  -111,   229,
      82,   109,   110,  -107,    40,    57,    89,    78,   103,   -85,
     -85,    97,    87,   240,   -92,   -92,    14,   -89,   120,    14,
     -89,   114,   151,   172,    28,    62,    14,   -89,     2,   -89,
      -5,    83,   128,   119,   115,   126,   159,   148,     9,    14,
      14,   -89,    93,   124,    64,    41,   121,    13,   137,  -114,
     152,    29,    63,   -14,   144,    -5,    14,   140,    84,   -37,
     149,   116,    29,    29,   161,   155,    18,    94,   125,   -36,
    -128,    22,    14,   138,    29,    37,   222,    98,    99,   138,
     223,    43,    29,    45,   -55,    44,    46,    49,   -72,   -75,
      58,    54,    91,    14,    79,   184,    60,   186,    67,    70,
      81,    90,   100,   166,    92,    95,   123,   101,   167,   145,
     113,   122,   127,   129,   154,   130,   133,   134,   191,   135,
     136,     0,   153,   160,   162,   202,   163,   165,   168,   192,
     205,   169,   177,   189,     0,   182,   183,   187,   188,   196,
     190,   179,   194,   193,   195,   197,   198,   199,  -128,   200,
     204,   219,   214,   221,   206,   207,   210,   212,   211,   220,
     233,   217,   218,   224,   230,   227,   225,   226,   231,   239,
     236,   232,   228,   237,   234,   235,   241,   266,   267,   238,
     244,   245,   246,   251,   247,   248,   249,   252,   250,   254,
     255,   257,   256,   258,   263,     0,   264,     0,     0,     0,
       0,     0,   261,   262
};

static const short yycheck[] =
{
      17,     8,     1,     1,     1,     1,     1,    22,    27,     1,
      29,    27,    22,    29,     1,     1,    33,     1,     1,    29,
      35,    29,     1,    40,    24,    22,    33,     1,    28,     1,
      22,    48,     1,    31,    29,    31,    28,    36,    35,     1,
      57,    33,    34,    35,    31,    31,    29,    31,    22,    28,
      29,    68,    59,     1,    28,    29,    28,    29,     1,    28,
      29,    78,     1,     1,     1,     1,    28,    29,     1,     1,
       3,     1,    89,    80,     1,     1,     1,     1,    20,    28,
      28,    29,     1,     1,     1,     7,    29,     3,     1,    27,
      29,    28,    28,    12,     1,    28,    28,   104,    28,    17,
      24,    28,    28,    28,   121,     1,    21,    26,    26,    26,
      24,     6,    28,    26,    28,    12,    28,     4,     5,    26,
      32,     1,    28,    28,    20,    29,    29,    29,    24,     0,
      13,    17,     8,    28,    18,   152,    29,   154,    29,    29,
      29,    29,     1,     1,    29,    26,    14,    29,     9,   105,
      29,    29,    29,    28,    19,    29,    29,    29,     1,    29,
      29,    -1,    29,    29,    28,   177,    29,    29,    28,    15,
       1,    28,    28,    24,    -1,    29,    29,    29,    28,    27,
      29,    36,    29,    28,    28,    27,    27,    24,    24,    29,
      29,   208,    10,    16,    29,    29,    29,    26,    28,    23,
      11,    29,    28,    28,   221,    25,    28,    28,    22,    28,
     227,    26,    29,    29,    27,    27,   233,     0,     0,    29,
      29,    27,    29,    27,    29,    28,    28,    27,   245,    28,
      28,    27,    29,    27,    29,    -1,    29,    -1,    -1,    -1,
      -1,    -1,   259,   260
};
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

case 1:
#line 286 "parser.y"
{

    if (the_errlist->entries()) YYABORT;

#ifdef PARSERDEBUG
    REDUCING("File");
#endif
  ;
    break;}
case 2:
#line 299 "parser.y"
{

    COMPLETEERRORITEM(FILEGENERALSTRUCTURE_0); // used

#ifdef PARSERDEBUG
    REDUCING("File");
#endif

    {YYABORT;}

  ;
    break;}
case 3:
#line 313 "parser.y"
{

  initParsing();

  startStartState(); // for lex init

#ifdef PARSERDEBUG
    STARTING("File");
#endif
;
    break;}
case 4:
#line 331 "parser.y"
{

#ifdef PARSERDEBUG
    REDUCING("Header");
#endif
  ;
    break;}
case 5:
#line 341 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("Header");
#endif
;
    break;}
case 6:
#line 356 "parser.y"
{

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif
  ;
    break;}
case 7:
#line 368 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CODEFORMSTX_0); // used
    CHECKIFABORT;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

    {YYABORT;}

  ;
    break;}
case 8:
#line 390 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;

    yyerrok;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

  ;
    break;}
case 9:
#line 412 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CODEFORMSTX_0); // used
    CHECKIFABORT;

    yyerrok;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

  ;
    break;}
case 10:
#line 429 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("CodeForm");
#endif
;
    break;}
case 11:
#line 439 "parser.y"
{
    mtg_code = FORM_A;

#ifdef PARSERDEBUG
    REDUCING("CodeFormValue_A");
#endif
  ;
    break;}
case 12:
#line 449 "parser.y"
{
    mtg_code = FORM_B;

#ifdef PARSERDEBUG
    REDUCING("CodeFormValue_B");
#endif
  ;
    break;}
case 13:
#line 459 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("CodeFormValue");
#endif
;
    break;}
case 14:
#line 476 "parser.y"
{

    if (classes_flag_err) YYABORT;

    cldef = new ClassDef(class_nb, *class_symbol, *scale, *vdecomp, *vindexing, *vdef);
    assert(cldef);
    for(int i=0; i<class_nb; i++) {
      for(int j=0; j<class_nb; j++)  {
        cldef->plus(i,j).Max() = 0;
        cldef->less(i,j).Max() = 0;
      }
    }
#ifdef PARSERDEBUG
    REDUCING("ClassDef");
#endif
  ;
    break;}
case 15:
#line 495 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("ClassDef");
#endif
;
    break;}
case 17:
#line 508 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX1_0); // used
    CHECKIFABORT;

    {YYABORT;}

  ;
    break;}
case 18:
#line 522 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX1_0); // used
    CHECKIFABORT;

    yyerrok;

  ;
    break;}
case 19:
#line 536 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 20:
#line 551 "parser.y"
{

    COMPLETEERRORITEM(CLASSDEFSTX2_0); // used
    CHECKIFABORT;


    {YYABORT;}

  ;
    break;}
case 22:
#line 570 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 23:
#line 587 "parser.y"
{

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 24:
#line 602 "parser.y"
{

    if (class_symbol->contains(yyvsp[0].charval)) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSDEFUNICITY_0); // used
      CHECKIFABORT;


    }

  ;
    break;}
case 25:
#line 617 "parser.y"
{

    if (ISFALSE(yyvsp[0].intval == (yyvsp[-4].intval) || yyvsp[0].intval == (yyvsp[-4].intval+1) )) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(SCALEORDER_0); // used
      CHECKIFABORT;


    }

  ;
    break;}
case 26:
#line 632 "parser.y"
{

    if (ISFALSE(mtg_code == FORM_A || (mtg_code == FORM_B &&
                                       (yyvsp[0].intval == LESSLINEAR ||
                                        yyvsp[0].intval == NOTCONNECTED ||
                                        yyvsp[0].intval == NONE_D)))){

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FORMBCOND1_0); // used
      CHECKIFABORT;


    }
  ;
    break;}
case 27:
#line 649 "parser.y"
{
    class_nb++;
    class_symbol->insert(yyvsp[-11].charval);
    scale->insert(yyvsp[-8].intval);
    scale_nb = std::max(scale_nb, yyvsp[-8].intval);
    vdecomp->insert(yyvsp[-5].intval);
    vindexing->insert(yyvsp[-2].intval);
    vdef->insert(yyvsp[0].intval);

#ifdef PARSERDEBUG
    //REDUCING("ClassList1");
#endif
  ;
    break;}
case 28:
#line 663 "parser.y"
{
    yyval.intval = yyvsp[-11].intval;
  ;
    break;}
case 29:
#line 669 "parser.y"
{

    // First class which is analysed !

    assert(!class_symbol->contains(yyvsp[0].charval));

  ;
    break;}
case 30:
#line 677 "parser.y"
{

    if (ISFALSE(yyvsp[0].intval == 0)) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(SCALEORDER_0); // used
      CHECKIFABORT;


    }

  ;
    break;}
case 31:
#line 692 "parser.y"
{

    if (ISFALSE(mtg_code == FORM_A || (mtg_code == FORM_B &&
                                       (yyvsp[0].intval == LESSLINEAR ||
                                        yyvsp[0].intval == NOTCONNECTED ||
                                        yyvsp[0].intval == NONE_D)))) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FORMBCOND1_0); // used
      CHECKIFABORT;

    }
  ;
    break;}
case 32:
#line 708 "parser.y"
{

    class_nb++;
    class_symbol->insert(yyvsp[-11].charval);
    scale->insert(yyvsp[-8].intval);
    scale_nb = std::max(scale_nb, yyvsp[-8].intval);
    vdecomp->insert(yyvsp[-5].intval);
    vindexing->insert(yyvsp[-2].intval);
    vdef->insert(yyvsp[0].intval);

#ifdef PARSERDEBUG
    REDUCING("ClassList2");
#endif
  ;
    break;}
case 33:
#line 723 "parser.y"
{
    yyval.intval = yyvsp[-11].intval;
  ;
    break;}
case 34:
#line 732 "parser.y"
{

    class_nb++;

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 35:
#line 748 "parser.y"
{

    class_nb++;

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 36:
#line 764 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("ClassList");
#endif
;
    break;}
case 37:
#line 780 "parser.y"
{

    if (descrip_flag_err) YYABORT;

#ifdef PARSERDEBUG
    REDUCING("ClassDescription");
#endif
  ;
    break;}
case 38:
#line 791 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("ClassDescription");
#endif
;
    break;}
case 40:
#line 804 "parser.y"
{

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDESCSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 41:
#line 819 "parser.y"
{

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 42:
#line 834 "parser.y"
{

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  ;
    break;}
case 44:
#line 855 "parser.y"
{
    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDESCSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 45:
#line 871 "parser.y"
{

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 46:
#line 886 "parser.y"
{
    if (ISFALSE(class_symbol->contains(yyvsp[0].charval))) {

      descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;


    }

  ;
    break;}
case 47:
#line 900 "parser.y"
{

    if (class_symbol->contains(yyvsp[-8].charval)) {

      SymbListIter next(*symblist);

      VClass leftc = cldef->vClass(yyvsp[-8].charval);
      int scaleleft = cldef->scale(leftc);

      while(next()) {

        if (cldef->isValid(next.key())) {

          VClass rightc = cldef->vClass(next.key());
          int scaleright = cldef->scale(rightc);

          if (scaleright != scaleleft) {

            descrip_flag_err = TRUE;

            yyerror(LOGICALERR);
            COMPLETEERRORITEM(TOPOLINKSCALE_0); // used
            CHECKIFABORT;

          }

          int val;

          if (*yyvsp[-3].etypeval == PLUS) val = cldef->plus(cldef->vClass(yyvsp[-8].charval),cldef->vClass(next.key())).Max();
          if (*yyvsp[-3].etypeval == LESS) val = cldef->less(cldef->vClass(yyvsp[-8].charval),cldef->vClass(next.key())).Max();

          if (ISFALSE(val == 0)) {

            RWCString param("(");

            // COMPILATION sous version 4.0 de Silicon : on est oblige de mettre
            // en commentaire les deux lignes suivantes

            param += RWCString(yyvsp[-8].charval);
            param += RWCString(",");
            param += RWCString(next.key());
            param += ",";
            if (*yyvsp[-3].etypeval == PLUS) param += "+";
            if (*yyvsp[-3].etypeval == LESS) param += "<";
            param += ")";

            descrip_flag_err = TRUE;

            yyerror(LOGICALERR);
            COMPLETEERRORITEM1(CLASSDESCUNICITY_1, param.data()); // used
            CHECKIFABORT;


          }
          else {

            if (ISFALSE( mtg_code == FORM_A ||
                        (mtg_code == FORM_B && (*yyvsp[-3].etypeval == PLUS)) ||
                        (mtg_code == FORM_B && (*yyvsp[-3].etypeval == LESS) && yyvsp[-1].intval <= 1))) {

              descrip_flag_err = TRUE;

              yyerror(LOGICALERR);
              COMPLETEERRORITEM(FORMBCOND2_0); // used
              CHECKIFABORT;


            }

            addClassDescription(cldef, yyvsp[-8].charval, next.key(), *yyvsp[-3].etypeval, yyvsp[-1].intval);

          }

        }

      }
    }

    delete symblist;
    symblist = 0;

#ifdef PARSERDEBUG
    REDUCING("ClassDescriptionList2");
#endif
  ;
    break;}
case 49:
#line 989 "parser.y"
{
#ifdef PARSERDEBUG
    REDUCING("ClassDescriptionList1");
#endif
  ;
    break;}
case 50:
#line 1000 "parser.y"
{

    descrip_flag_err = TRUE;

    delete symblist;
    symblist = 0;

    COMPLETEERRORITEM(CLASSDESCLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 51:
#line 1018 "parser.y"
{

    descrip_flag_err = TRUE;

    delete symblist;
    symblist = 0;

    COMPLETEERRORITEM(CLASSDESCLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 52:
#line 1035 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("ClassDescriptionList");
#endif
;
    break;}
case 53:
#line 1044 "parser.y"
{

    if (ISFALSE(class_symbol->contains(yyvsp[0].charval))) {

    descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;

    }

    symblist->append(yyvsp[0].charval);
  ;
    break;}
case 54:
#line 1060 "parser.y"
{

    if (ISFALSE(class_symbol->contains(yyvsp[0].charval))) {

    descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;

    }

    symblist = new SymbList;
    symblist->append(yyvsp[0].charval);

  ;
    break;}
case 55:
#line 1087 "parser.y"
{

    if (feature_flag_err) YYABORT;

    fsetdef = new FSetDef(feature_nb, *featname, *feattype, *smbtable_array);
    assert(fsetdef);

    // a fset is an array of features whose first element
    // contains a line number
    fset = new Feature[feature_nb];

#ifdef PARSERDEBUG
    REDUCING("FeatureDef");
#endif
  ;
    break;}
case 56:
#line 1105 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("FeatureDef");
#endif
;
    break;}
case 58:
#line 1118 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 59:
#line 1133 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 60:
#line 1148 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  ;
    break;}
case 62:
#line 1169 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 63:
#line 1186 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 65:
#line 1203 "parser.y"
{
#ifdef PARSERDEBUG
    REDUCING("FeatureDefList");
#endif
  ;
    break;}
case 66:
#line 1215 "parser.y"
{

    if (!VALID(FSetDef::checkPredefinedFeature(yyvsp[-4].stgval, yyvsp[-2].ftypeval))) {
      feature_flag_err = TRUE;
      CHECKIFABORT;
    }

    feature_nb++;
    addFeature(*featname, *feattype, *smbtable_array, yyvsp[-4].stgval, yyvsp[-2].ftypeval, 0);
#ifdef PARSERDEBUG
    REDUCING("FeatureLine1");
#endif
  ;
    break;}
case 67:
#line 1235 "parser.y"
{

    if (!VALID(FSetDef::checkPredefinedFeature(yyvsp[-6].stgval, yyvsp[-4].ftypeval))) {
      feature_flag_err = TRUE;
      CHECKIFABORT;
    }

    // the name of the file must be interpreted in the local directory
    // of the mtg.

    std::string cwd = get_cwd();

    std::string mtg_name = the_mtg->_filename.data();
    std::string mtg_dir = get_dirname(mtg_name);

    // push the directory of the mtg file

    if (mtg_dir != "") {
      if (!chg_dir(mtg_dir)) std::cerr << "\tchg_dir() returned an error." << std::endl;
    }

    // Computes the symbol table as a result of parsing file whose name is $<ftypeval>5
    void* smbtable = 0;

    switch (yyvsp[-4].ftypeval) {
    case GEOMETRY :
      {

        std::cerr << "Loading Geometric objects from file : " << yyvsp[-2].stgval << " ... " << std::endl;

        SceneObjectSymbolTable* geom_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse(yyvsp[-2].stgval, std::cerr, *geom_table);
        #else
	std::string filename(yyvsp[-2].stgval);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *geom_table, scene, filename);
	#endif

        if (!parse_ok) {
          if (mtg_dir != "")
            if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }

        bool strict_parsing = true;
        GeometryPtr _geom;
        for(SceneObjectSymbolTable::iterator _it = geom_table->begin();
            _it != geom_table->end(); _it++){
            _geom = dynamic_pointer_cast<Geometry>(_it->second);
            if(!_geom){
                // genMessage(WARNINGMSG(INVALID_TYPE_sss),"Geometry",_it->first.c_str(),typeid(*(_i->second)).name());
                strict_parsing = false;
            }
        }

        if(strict_parsing)
            smbtable = geom_table;
        else {
            delete geom_table;
            smbtable = 0;
        }

      }
      break;
    case APPEARANCE:
      {
        std::cerr << "Loading Material objects from file : " << yyvsp[-2].stgval << " ... " << std::endl ;

        SceneObjectSymbolTable* app_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse(yyvsp[-2].stgval, std::cerr, *app_table);
        #else
	std::string filename(yyvsp[-2].stgval);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *app_table, scene, filename);
	#endif

        if (!parse_ok) {
          if (mtg_dir != "")
            if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }

        bool strict_parsing = true;
            AppearancePtr _app;
        for(SceneObjectSymbolTable::iterator _it = app_table->begin();
            _it != app_table->end(); _it++){
            _app = dynamic_pointer_cast<Appearance>(_it->second);
            if(!_app){
                // genMessage(WARNINGMSG(INVALID_TYPE_sss),"Appearance",_it->first.c_str(),typeid(*(_it->second)).name());
                strict_parsing = false;
            }
        }

        if(strict_parsing)
            smbtable = app_table;
        else{
            smbtable = 0;
            delete app_table;
        }
        /*
        std::cerr << std::endl;

        std::cerr << "MATERIAL: List of object loaded : ... " << std::flush;

        Printer pp(std::cerr,std::cerr);

        for (AppearanceSymbolTable::iterator sti = mat_table->begin();
             sti != mat_table->end();
             sti++) {
          std::cerr << sti->first << " = ";
          sti->second->apply(pp);
          std::cerr << std::endl;
        }
        std::cerr << std::endl;
        */
      }
      break;
    case GENERIC:
    {
        std::cerr << "Loading GEOM objects from file : " << yyvsp[-2].stgval << " ... " << std::endl;

        SceneObjectSymbolTable* geom_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse(yyvsp[-2].stgval, std::cerr, *geom_table);
        #else
	std::string filename(yyvsp[-2].stgval);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *geom_table, scene, filename);
	#endif

        if (!parse_ok) {
            if (mtg_dir != "")
                if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }
        smbtable = geom_table;
    }
    break;
    default:
      smbtable = 0;
      break;
    }

    // restores the current work directory

    if (mtg_dir != "")
        if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl;


    feature_nb++;
    addFeature(*featname, *feattype, *smbtable_array, yyvsp[-6].stgval, yyvsp[-4].ftypeval, smbtable);


#ifdef PARSERDEBUG
    REDUCING("FeatureLine2");
#endif
  ;
    break;}
case 68:
#line 1418 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;


#ifdef PARSERDEBUG
    //REDUCING("FeatureDefList");
#endif
  ;
    break;}
case 69:
#line 1437 "parser.y"
{

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

#ifdef PARSERDEBUG
    //REDUCING("FeatureDefList");
#endif
  ;
    break;}
case 70:
#line 1454 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("FeatureDefList");
#endif
;
    break;}
case 71:
#line 1464 "parser.y"
{
    sprintf(yyval.stgval,"%s",yyvsp[0].stgval);

    if (featname->contains(yyvsp[0].stgval)) {

      feature_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FEATURENAMEUNICITY_0); // used
      CHECKIFABORT;


    }

    if (!VALID(FSetDef::checkOrderIfPredefined(featname, yyvsp[0].stgval))) feature_flag_err = TRUE;


#ifdef PARSERDEBUG
    REDUCING("FName");
#endif
  ;
    break;}
case 72:
#line 1488 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("FName");
#endif
;
    break;}
case 73:
#line 1498 "parser.y"
{

    yyval.ftypeval = yyvsp[0].ftypeval;

#ifdef PARSERDEBUG
    REDUCING("FType");
#endif
  ;
    break;}
case 74:
#line 1509 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("FType");
#endif
;
    break;}
case 75:
#line 1526 "parser.y"
{


#ifdef PARSERDEBUG
    REDUCING("MTGDescription");
#endif
  ;
    break;}
case 76:
#line 1536 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("MTGDescription");
#endif
;
    break;}
case 78:
#line 1550 "parser.y"
{

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(MTGSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 79:
#line 1565 "parser.y"
{

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  ;
    break;}
case 80:
#line 1580 "parser.y"
{

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  ;
    break;}
case 81:
#line 1597 "parser.y"
{

    if (ISFALSE(yyvsp[-1].intval == featname->entries())) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FEATNBDIFF_0); // used
      CHECKIFABORT;


      mtghead_flag_err = TRUE;

    }

    if (mtghead_flag_err) YYABORT;

    the_mtg->initMTG(scale_nb, cldef, fsetdef, file_line_nb);

    startCodeState();


    std::cerr << std::endl;


    // index 0 stores the line_number and does not correspond to any column
    /*
    for(int i=0; i<featname->entries(); i++) {

      std::cerr << "featname = " << (*featname)[i] << ", column = " << (*col_name_index)[i] << std::endl;

    }
    */

  ;
    break;}
case 83:
#line 1638 "parser.y"
{

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  ;
    break;}
case 84:
#line 1654 "parser.y"
{
    // check whether this string is in the feature name array
    // find the first index of array name which contains the TokString
    int index = featname->index(yyvsp[0].stgval);

    if (ISFALSE(index != RW_NPOS)) {

      mtghead_flag_err = TRUE;
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(ATTRNAME1_0); // used
      CHECKIFABORT;

    }
    else {                      // index != RW_NPOS

      // cerr << "Trying to find name of feature index = " << $<intval>1 << endl;

      if (ISFALSE( (*featname)[yyvsp[-2].intval] == yyvsp[0].stgval)) {

        mtghead_flag_err = TRUE;
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(ATTRNAME2_0); // used
        CHECKIFABORT;

      }

      //cerr << " ... name found in featname = " << flush;
      //cerr << (*featname)[$<intval>1] << endl;
      //cerr << "with index = " << $<intval>1 << endl;
    }

    // cerr << "defining this name at column " << yyColumnNb() << endl;

    // Store the current column nb in association with this feature name index
    if (index>=0) {
      col_name_index->insertAt(index, yyColumnNb());
    }

    yyval.intval = yyvsp[-2].intval + 1;

  ;
    break;}
case 85:
#line 1697 "parser.y"
{


    col_name_index = new IntArray(featname->entries());
    col_name_index->insertAt(0, 1); // index 0 is index of column 1

    yyval.intval = 0; // counts the attribute labels

  ;
    break;}
case 86:
#line 1710 "parser.y"
{
    yyval.intval = yyvsp[-1].intval + 1;
  ;
    break;}
case 87:
#line 1715 "parser.y"
{
    yyval.intval = 1;
  ;
    break;}
case 88:
#line 1722 "parser.y"
{yyval.intval = yyvsp[0].intval;;
    break;}
case 89:
#line 1725 "parser.y"
{yyval.intval = 0;;
    break;}
case 90:
#line 1732 "parser.y"
{
#ifdef PARSERDEBUG
    //REDUCING("ElementList1");
#endif
  ;
    break;}
case 91:
#line 1738 "parser.y"
{
#ifdef PARSERDEBUG
    REDUCING("ElementList2");
#endif
  ;
    break;}
case 92:
#line 1754 "parser.y"
{

    if (yyvsp[0].vname.ident != CHECKERROR &&
        yyvsp[0].vname.vprefix != CHECKERROR &&
        yyvsp[0].vname.label.symbol != '\0') {

      int index = featname->index("Date");
      if (index == RW_NPOS && yyvsp[0].vname.ident != UNDEF) {
        // this entity has already been defined
        // and we have no Date information => error

        int line_nb = vinfo->findFirstLine(yyvsp[0].vname.ident);

#ifndef STL_EXTENSION
		char stg[20];
		std::ostrstream ost(stg,20);
		ost << line_nb;
		ost << '\0';
    
	    yyerror(LOGICALERR);
	    COMPLETEERRORITEM1(ALREADYDEFINED_1, stg); // used
#else
		std::stringstream ss;
		ss << line_nb << std::ends;
		yyerror(LOGICALERR);
        COMPLETEERRORITEM1(ALREADYDEFINED_1, ss.str().c_str()); // used
#endif
        CHECKIFABORT;

        code_flag_err = TRUE;

        yyval.intval = CHECKERROR;
      }
      else {

        int v;

        if (yyvsp[0].vname.ident != UNDEF) {

          yyval.intval = v = yyvsp[0].vname.ident;

          //cerr << "\nLAST VERTEX 0 = " << v << endl;
        }
        else {

          switch(mtg_code) {

          case FORM_A:
            v = defineVertexByName_A(yyvsp[0].vname.label.symbol,
                                     yyvsp[0].vname.label.index,
                                     yyvsp[0].vname.vprefix,
                                     *yyvsp[0].vname.relation);
            break;

          case FORM_B:
            v = defineVertexByName_B(yyvsp[0].vname.label.symbol,
                                     yyvsp[0].vname.label.index,
                                     yyvsp[0].vname.vprefix,
                                     *yyvsp[0].vname.relation);
            break;

          default:
            break;

          }
        }
        if (VALID(v)) {

#ifdef PARSERDEBUG
          std::cerr << "\n>>>>>>>>>>  Vertex EXPLICIT identifie : ident = " << v
          << ", label = " << yyvsp[0].vname.label.symbol << yyvsp[0].vname.label.index
          << ", true-loc = " << vtxprefix(v)
          << ", relation = " << *yyvsp[0].vname.relation << std::endl;
#endif

          for(int j=0; j<feature_nb; j++) fset[j].i = (unsigned long)LUNDEF;

          yyval.intval = v;

          // cerr << "indent_tbl[" << current_indent_level <<"]= " << v << endl;

          indent_tbl->insertAt(current_indent_level, v);

          last_vname.ident = v;
          last_vname.label = yyvsp[0].vname.label;
          last_vname.relation = yyvsp[0].vname.relation;
          /*
          std::cerr << "\nLAST VERTEX 1 = " << last_vname.ident << std::endl;
          std::cerr << "\nLAST VERTEX 2 = " << $<vname>2.ident << std::endl;
          */
        }
        else {

          yyval.intval = CHECKERROR;
        }

      }

    }
    else {

      yyval.intval = CHECKERROR;

    }

    //startFeatureState();

  ;
    break;}
case 93:
#line 1863 "parser.y"
{

    if (yyvsp[-1].intval != CHECKERROR) {

      // featureList returns the number of matched features on that line
      if (yyvsp[-2].vname.label.symbol != '\0') {

        VClass ic = cldef->vClass(yyvsp[-2].vname.label.symbol);

        if ((*vdef)[ic] == IMPLICIT && yyvsp[0].intval != 0) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(IMPLICITERR_0); // used
          CHECKIFABORT;

          code_flag_err = TRUE;

        }

        int index = featname->index("Date");
        Date date = (unsigned long)LUNDEF;
        if (index != RW_NPOS) {
          date = fset[index].i;
          if ((*vdef)[ic] == EXPLICIT && date == (unsigned long)LUNDEF && code_flag_err == FALSE) {

            yyerror(LOGICALERR);
            COMPLETEERRORITEM(DATEMUSTBEDEFINED_0); // used
            CHECKIFABORT;

            code_flag_err = TRUE;

          }
        }

        vinfo->insert(yyvsp[-1].intval, lineNb());

        EType et = *yyvsp[-2].vname.relation;

        if (et == LESSDOTLESS || et == PLUSDOTPLUS) {
          // E2<.<E5 the feature should be stored on each vtx from E2 to E5

          int index = yyvsp[-2].vname.label.index;
          int loc = yyvsp[-2].vname.vprefix;
          int vtxnb = index - the_mtg->vindex(loc);
          int v = yyvsp[-1].intval;

          for (int i = 0; i <= vtxnb; i++) {

            addFSet(v,fset);
            v = the_mtg->vprefix(v);

          }

        }
        // create an fset only if at least one feature is defined
        else if (yyvsp[0].intval != 0) addFSet(yyvsp[-1].intval, fset);

      }

    }

    //startCodeState();

#ifdef PARSERDEBUG
    REDUCING("Vertex");
#endif
  ;
    break;}
case 95:
#line 1939 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 96:
#line 1964 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 97:
#line 1989 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 98:
#line 2014 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(MISSINGALIASPARENTH_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 99:
#line 2038 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 100:
#line 2061 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  ;
    break;}
case 101:
#line 2081 "parser.y"
{

  code_flag_err = FALSE;

#ifdef DEBUGCHECKERROR
  printAnalysisPercent();
#endif


#ifdef PARSERDEBUG
  std::cerr << "\n***************************************************************" << std::endl;
  std::cerr << "*********************    Line " << lineNb() << "   **************************" << std::endl;
  std::cerr << "***************************************************************" << std::endl;
#endif

#ifdef PARSERDEBUG
  std::cerr << "\n\n";
  STARTING("Element");
#endif
;
    break;}
case 102:
#line 2112 "parser.y"
{

    // A ce moment il faut verifier si le vertex associe
    // a $<vname>$ existe. Si il n'existe pas: erreur
    // sinon, renvoyer l'index de ce vertex, son label, sa position et sa relation

    // vprefix and ident label.symbol and label.index can be erroneous values
    int vprefix = yyvsp[-2].vname.ident;

    if (yyvsp[-2].vname.label.symbol == '\0' ||
        yyvsp[-2].vname.label.index == UNDEF ||
        yyvsp[0].label.symbol == '\0' ||
        yyvsp[0].label.index == UNDEF ||
        vprefix == CHECKERROR ||            // outset error
        yyvsp[-2].vname.vprefix == CHECKERROR) {

      yyval.vname.ident = CHECKERROR;
      yyval.vname.label = yyvsp[0].label;
      yyval.vname.vprefix = vprefix;
      yyval.vname.relation = yyvsp[-1].etypeval;

    }
    else {

      // 1. Treat the case where vprefix is UNDEF: create it

      // case of a vprefix which does not exist yet
      // and which has a valid vprefix

      EType e_type;

      if (*yyvsp[-2].vname.relation == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*yyvsp[-2].vname.relation == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *yyvsp[-2].vname.relation;


      if (vprefix == UNDEF && yyvsp[-2].vname.vprefix >=0 ) {

        switch(mtg_code) {

        case FORM_A:
          vprefix = defineVertexByName_A(yyvsp[-2].vname.label.symbol,
                                          yyvsp[-2].vname.label.index,
                                          yyvsp[-2].vname.vprefix,
                                          e_type);
          break;

        case FORM_B:
          vprefix = defineVertexByName_B(yyvsp[-2].vname.label.symbol,
                                          yyvsp[-2].vname.label.index,
                                          yyvsp[-2].vname.vprefix,
                                          e_type);
          break;

        default:
          break;

        }


#ifdef PARSERDEBUG
        if (VALID(vprefix)) {
          std::cerr << "\n>>>>>>>>>>  Vertex IMPLICIT identifie : ident = " << vprefix
          << ", label = " << yyvsp[-2].vname.label.symbol << yyvsp[-2].vname.label.index
          << ", true-loc = " << vtxprefix(vprefix)
          << ", relation = " << *yyvsp[-2].vname.relation << std::endl;
        }
#endif

      }

#ifdef PARSERDEBUG
      std::cerr << "\n?????? Recherche d'un vertex tq: label = " << yyvsp[0].label.symbol
      << yyvsp[0].label.index << ", loc = " << vprefix
      << ", relation = " << *yyvsp[-1].etypeval << std::flush;
#endif

      int v = CHECKERROR;


      if (*yyvsp[-1].etypeval == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*yyvsp[-1].etypeval == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *yyvsp[-1].etypeval;

      if (vprefix != CHECKERROR) {

        switch(mtg_code) {

        case FORM_A:
          v = findVertexByName_A(yyvsp[0].label.symbol,
                                 yyvsp[0].label.index,
                                 vprefix,
                                 e_type);
          break;

        case FORM_B:
          v = findVertexByName_B(yyvsp[0].label.symbol,
                                 yyvsp[0].label.index,
                                 vprefix,
                                 e_type);
          break;

        default:
          break;

        }

#ifdef PARSERDEBUG
        if (VALID(v)) std::cerr << " ... TROUVE !" << std::endl;
        else std::cerr << " ... PAS TROUVE !" << std::endl;
#endif

      } // end of if vprefix != CHECKERROR

      yyval.vname.ident = v;                  // may be an error CHECKERROR
      yyval.vname.label = yyvsp[0].label;          // label.symbol may be an error '\0'
      yyval.vname.vprefix = vprefix;          // >=0 or CHECKERROR
      yyval.vname.relation = yyvsp[-1].etypeval;

    } // end of else

  ;
    break;}
case 103:
#line 2256 "parser.y"
{

    int vprefix = yyvsp[-2].intval; // may be >=0 or CHECKERROR

    if(vprefix == CHECKERROR || yyvsp[0].label.symbol == '\0' || yyvsp[0].label.index == UNDEF) {

      yyval.vname.ident = CHECKERROR;
      yyval.vname.label = yyvsp[0].label;
      yyval.vname.vprefix = vprefix;
      yyval.vname.relation = yyvsp[-1].etypeval;

    }
    else {

#ifdef PARSERDEBUG
      std::cerr << "\n?????? Recherche d'un vertex tq: "
      << "label = " << yyvsp[0].label.symbol
      << yyvsp[0].label.index << ", loc = " << vprefix
      << ", relation = " << *yyvsp[-1].etypeval
      << std::flush;
#endif

      int v;
      EType e_type;

      if (*yyvsp[-1].etypeval == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*yyvsp[-1].etypeval == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *yyvsp[-1].etypeval;

      switch(mtg_code) {

      case FORM_A:
        v = findVertexByName_A(yyvsp[0].label.symbol,
                               yyvsp[0].label.index,
                               vprefix,
                               e_type);
        break;

      case FORM_B:
        v = findVertexByName_B(yyvsp[0].label.symbol,
                               yyvsp[0].label.index,
                               vprefix,
                               e_type);
        break;

      default:
        break;

      }

#ifdef PARSERDEBUG
      if (VALID(v)) std::cerr << " ... TROUVE !" << std::endl;
      else std::cerr << " ... PAS TROUVE !" << std::endl;
#endif

      yyval.vname.ident = v;                 // may be an error value UNDEF
      yyval.vname.label = yyvsp[0].label;         // label.symbol may be an error '\0'
      yyval.vname.vprefix = vprefix;         // >=0 or CHECKERROR
      yyval.vname.relation = yyvsp[-1].etypeval;

    }

  ;
    break;}
case 104:
#line 2329 "parser.y"
{

  if (previous_indent_level <  current_indent_level) { // pour le cas ou il y a une *

    yyerror(LOGICALERR);
    COMPLETEERRORITEM(IDENTERR1_0); // used
    CHECKIFABORT;

    current_indent_level = previous_indent_level;

    code_flag_err = TRUE;

  }
  else {

    yyval.vname.ident = last_vname.ident;
    yyval.vname.label = last_vname.label;
    yyval.vname.vprefix = last_vname.vprefix;
    yyval.vname.relation = last_vname.relation;
  }
  // cerr << "\nLAST VERTEX = " << last_vname.ident << endl;

;
    break;}
case 105:
#line 2379 "parser.y"
{
    int indent_level = yyvsp[-1].intval;

    if (ISFALSE(indent_level <= current_indent_level)) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(IDENTERR1_0); // used
        YYABORT; // Aborts immediately

        code_flag_err = TRUE;

      }

      yyval.intval = CHECKERROR;

    }
    else { // retreive the last vertex with same identation level
      /*
        std::cerr << "============> indent_level     = " << indent_level << std::endl;
        std::cerr << "============> (*indent_tbl)[indent_level]  = " << (*indent_tbl)[indent_level] << std::endl;
      */
      yyval.intval = (*indent_tbl)[indent_level];

    }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;

  ;
    break;}
case 106:
#line 2413 "parser.y"
{

    /* An alias must be in column 1 */

    int indent_level = yyvsp[-1].intval;

    if (ISFALSE(indent_level == 0)) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(IDENTERR2_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      yyval.intval = CHECKERROR;

    }
    else { // retreive the vertex corresponding to this alias

      yyval.intval = yyvsp[0].intval; // may be an error CHECKERROR

    }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;
  ;
    break;}
case 107:
#line 2445 "parser.y"
{
    int indent_level = yyvsp[0].intval;

      if (ISFALSE(indent_level <= current_indent_level + 1)) {

        if (!code_flag_err) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(IDENTERR3_0); // used
          CHECKIFABORT;

          code_flag_err = TRUE;

        }

        yyval.intval = CHECKERROR;

      }
      else { // retreive the last vertex with lesser (by one) indentation level

        // cerr << "============> indent_level     = " << indent_level << endl;

        if (indent_level > 0) {
          yyval.intval = (*indent_tbl)[indent_level-1];
          // cerr << "============> (*indent_tbl)[indent_level-1]  = " << (*indent_tbl)[indent_level-1] << endl;
        }
        else  yyval.intval = ROOT; // Root is 0

      }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;

/*
    if (index == RW_NPOS) {

    }
    else { // file with feature DATE defined

      // No vertex is defined on this line => return the previous vertex
      $<intval>$ = (*indent_tbl)[current_indent_level];
    }

*/

  ;
    break;}
case 108:
#line 2499 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(NOTACODESTART_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyUnputToken();

    yyerrok;

    yyval.intval = CHECKERROR;

  ;
    break;}
case 109:
#line 2522 "parser.y"
{
    yyval.intval = yyvsp[-1].intval + 1;
  ;
    break;}
case 110:
#line 2526 "parser.y"
{
    yyval.intval = 0;
  ;
    break;}
case 112:
#line 2537 "parser.y"
{
    if (alias_dict->contains(yyvsp[-1].stgval)) {

      yyval.intval = (*alias_dict)[yyvsp[-1].stgval]; // return the corresponding vertex id

    }
    else { /* error, alias not defined */

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(ALIASDONOTEXIST_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      yyval.intval = CHECKERROR;

    }

  ;
    break;}
case 113:
#line 2564 "parser.y"
{

    if (!code_flag_err) {

      COMPLETEERRORITEM(ALIASSTRING_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyval.intval = CHECKERROR;

    yyerrok;

  ;
    break;}
case 114:
#line 2585 "parser.y"
{

    if (ISFALSE(class_symbol->contains(yyvsp[0].charval))) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(CLASSERR_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      yyval.charval = '\0';

    }
    else yyval.charval = yyvsp[0].charval;
  ;
    break;}
case 115:
#line 2605 "parser.y"
{

    yyval.label.symbol = yyvsp[-1].charval; // contains '\0' is case of error
    yyval.label.index = yyvsp[0].intval;   // no error except a syntactic error

  ;
    break;}
case 116:
#line 2616 "parser.y"
{

    yyval.label.symbol = '\0'; // contains '\0' is case of error
    yyval.label.index = yyvsp[0].intval;   // no error except a syntactic error

    if (!code_flag_err) {

      COMPLETEERRORITEM(CLASSERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

  ;
    break;}
case 117:
#line 2638 "parser.y"
{

    if (!code_flag_err) {

      if (yychar != eol && yychar != tabc) {

        COMPLETEERRORITEM(INDEXERR_0); // used

        yyclearin; // clean the bad input which is kept for further scanning otherwise

      }
      else {

        COMPLETEERRORITEM(INDEXMISSING_0); // used

      }

      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyval.label.symbol = yyvsp[-1].charval; // contains '\0' is case of error
    yyval.label.index = UNDEF;   // no error except a syntactic error

    yyerrok;

  ;
    break;}
case 118:
#line 2675 "parser.y"
{yyval.intval = 0;;
    break;}
case 119:
#line 2676 "parser.y"
{yyval.intval = yyvsp[0].intval;;
    break;}
case 122:
#line 2687 "parser.y"
{

    yyval.intval = yyvsp[-2].intval + yyvsp[0].intval;  // counts the nb of none empty featval on the line

  ;
    break;}
case 123:
#line 2693 "parser.y"
{
    yyval.intval = 1;
  ;
    break;}
case 124:
#line 2699 "parser.y"
{yyval.intval = 1;;
    break;}
case 125:
#line 2700 "parser.y"
{yyval.intval = 0;;
    break;}
case 126:
#line 2706 "parser.y"
{

    int current_vertex = (*indent_tbl)[current_indent_level];

    if (strlen(yyvsp[0].stgval) >= MAXSTRINGSIZE) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM1(STRINGSIZETOOBIG_1, itorwcstring(MAXSTRINGSIZE-1).data() );
      CHECKIFABORT;

    }

    int findex = col_name_index->index(columnNb()); // get the index of the feature corresponding to this column nb

    /*
    std::cerr << "findex = " << findex << std::endl;
    std::cerr << "column = " << columnNb() << std::endl;;

    for (int k = 0; k < col_name_index->entries(); k++)
    std::cerr << "index = " << k << ", col = " << (*col_name_index)[k] << std::endl;;
    */

    if (findex == RW_NPOS) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(WRONGFEATCOLUMN_0); // used
      CHECKIFABORT;

    }
    else {

      FFlag nameval = FSetDef::nameFFlag((*featname)[findex]);

      if (nameval == ALIAS_F) {

        // if this name already exists, the new value will overwrite the old one
        // => the definition of an Alias corresponds to its most recent definition in the file thread
        alias_dict->insertKeyAndValue(yyvsp[0].stgval, current_vertex);

      }

      strncpy(fset[findex].s,yyvsp[0].stgval,MAXSTRINGSIZE); // \0 is copied also

      int result = storeFeatureValue(current_vertex, fset, findex);

      if(ISFALSE(result != CHECKERROR)) {

        code_flag_err = TRUE;
        CHECKIFABORT;

      }

    }

#ifdef PARSERDEBUG
    REDUCING("FeatureVal");
#endif
  ;
    break;}
case 128:
#line 2771 "parser.y"
{
#ifdef PARSERDEBUG
    STARTING("FeatureVal");
#endif
;
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
#line 2781 "parser.y"


#ifdef PARSERDEBUG

static int indentcount = 0;

static void REDUCING(char* s)  {

  if (indentcount>0) indentcount--;

  std::cerr << std::endl;
  for(int i=0;i<indentcount;i++) std::cerr << "   ";
  std::cerr << "<== reducing rule: "<< s;
  if (yychar != YYEMPTY) std::cerr << ", LOOK-AHEAD = " << tokenName(yychar) << " (" << yyText() << ")";
  std::cerr << std::endl;

}

static void STARTING(char* s)  {

  std::cerr << std::endl;
  for(int i=0;i<indentcount;i++) std::cerr << "   ";
  std::cerr << "==> starting rule: "<< s;
  if (yychar != YYEMPTY) std::cerr << ", LOOK-AHEAD = " << tokenName(yychar) << " (" << yyText() << ")";
  std::cerr << std::endl;

  indentcount ++;
}

#endif

const char* tokenName(int token) {

  assert(token <= TokError);

  if (token >= TokCODE) return token_name[token-TokCODE];
  else if (token == YYEOF) return "EOF";
  else if (token == YYEMPTY) return "VOID";
  else return "UNKNOWN";

}

const char* tokenVal() {

  return yyText();

}

// These functions return the exact vprefix in terms of line and column of
// the scanning head. This takes into account the possibility of a lookahead
// reading (stored in the variable yychar).

int lineNb() {

  if (yychar != YYEMPTY)
  if (yychar == eol) return yyLineNb() - 1;
  else return yyLineNb();
  else return yyLineNb();

}

int columnNb() {

  if (yychar != YYEMPTY)
  if (yychar == tabc || yychar == eol) return yyPreviousColumnNb();
  else return yyColumnNb();
  else return yyColumnNb();

}

int firstFeatCol() {

  if (featname)
  if (featname->entries()) return (*col_name_index)[0];
  else return -1;
  else return -1;
}


const char* inputLine() {

  static char tmp[MAXLINELENGTH];

  if (yychar != YYEMPTY)
  if (yychar == eol) return yyPreviousLine();
  else if (yychar == tabc) {

    yyUnputToken(); // reject it temporarily in the input stream
    strcpy(tmp, yyCurrentLine());
    yylex(); // read again the current lookahead
    return tmp;

  }
  else return yyCurrentLine();
  else return yyCurrentLine();

}

AmlBoolean lineCodeErrorState() {

  return code_flag_err;

}

static void initParsing() {

  // cerr << "init parsing ..." << endl;

  class_symbol = new CharArray(MAXCLASSNB);
  scale = new IntArray;
  vdecomp = new IntArray;
  vindexing = new IntArray;
  vdef = new IntArray;
  featname = new StringArray(MAXFEATURENB);
  feattype = new FTypeArray(MAXFEATURENB);
  smbtable_array = new FeatureSmbTableArray(MAXFEATURENB);

  /*  Done now by the user

  // definition de la classe 0
  scale_nb++;
  class_nb++;

  class_symbol->insert('$');
  scale->insert(0);
  vdecomp->insert(FREE_D);
  vindexing->insert(FREE_I);
  vdef->insert(IMPLICIT);

  */

  alias_dict = new StringIntDict(hashFunc); // alias table giving the vextex associated to an alias
  indent_tbl = new IntArray; // vextex corresponding to a given indentation

  vinfo = new VtxInfo(file_line_nb);

  current_indent_level = -1;

}

ErrorList* getErrorList() {

  return the_errlist;

}

void cleanErrorList() {

  delete the_errlist;
  the_errlist = 0;

}

static void cleanParser() {

  // the errorList is not reset since it must be available from
  // parser outside

  // cerr << "clean parsing ..." << endl;

  lexAbort();

  the_mtg = 0;
  file_line_nb = 0;
  old_dec_ratio = 0;

  class_nb = 0;
  scale_nb = 0;
  feature_nb = 0;

  classes_flag_err = FALSE;
  descrip_flag_err = FALSE;
  feature_flag_err = FALSE;
  mtghead_flag_err = FALSE;
  code_flag_err = FALSE;

  delete alias_dict;
  delete indent_tbl;
  delete vinfo;
  alias_dict = 0;
  indent_tbl = 0;
  vinfo = 0;


  delete class_symbol;
  delete scale;
  class_symbol = 0;
  scale = 0;

  delete vdecomp;
  delete vindexing;
  delete vdef;
  vdecomp = 0;
  vindexing = 0;
  vdef = 0;

  delete featname;
  delete feattype;
  delete smbtable_array;
  featname = 0;
  feattype = 0;
  smbtable_array = 0;

  delete [] fset;
  delete col_name_index;
  fset = 0;
  col_name_index = 0;

#ifdef PARSERDEBUG
  indentcount = 0;
#endif

}

static void printAnalysisPercent() {

  double ratio = rint((lineNb() / (double) file_line_nb)*10);

  if (ratio > old_dec_ratio) {
    std::cerr << "\x0d" << "Already parsed : " << ((int) ratio)*10 << " % " << std::flush;
    old_dec_ratio = ratio;
  }

}





// ---------------------------------
// Initialisations and header update
// ---------------------------------


static void addClassDescription(ClassDef* cldef, char class1, char class2, EType reltype, int val) {

  int i = cldef->vClass(class1);
  assert(cldef->isValid(i));
  int j = cldef->vClass(class2);
  assert(cldef->isValid(j));

  if (reltype == PLUS) cldef->plus(i,j).Max() = val;
  if (reltype == LESS) cldef->less(i,j).Max() = val;

}

static void addFeature(StringArray& featname, FTypeArray& feattype, FeatureSmbTableArray& smbtable_array,
                char* nameval, FType typeval, void* smbtable) {


  featname.insert(nameval);

  feattype.insert(typeval);

  smbtable_array.insert(smbtable);

}

// ------------------------------------------
// Check for existence and Addition of vertex
// ------------------------------------------


static int vtxprefix(int vtx) {

  return the_mtg->vprefix(vtx);

}


static int findVertexByName_A(char vclass, int index, int loc, EType etype) {

  return the_mtg->findVertexByName_A(vclass, index, loc, etype);

}

static int findVertexByName_B(char vclass, int index, int loc, EType etype) {

  return the_mtg->findVertexByName_B(vclass, index, loc, etype);

}

int defineVertexByName_A(char class_symb, int index, VId loc, EType et) {


  if (et == PLUSDOTPLUS) et = PLUSPLUS;
  else if (et == LESSDOTLESS) et = LESSLESS;


  if (!VALID(the_mtg->isValidClass(class_symb))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }

  if (et == LESSLESS) {

    if (class_symb != the_mtg->classSymbol(the_mtg->vclass(loc))){
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(VTXLISTERR_0);
      return CHECKERROR;
    }

    int vtxnb = index - the_mtg->vindex(loc);

    if (vtxnb <= 0){
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(VTXLIST2ERR_0);
      return CHECKERROR;
    }

    int newvtx = loc;

    for (int i = 1; i <= vtxnb; i++) {

      newvtx = the_mtg->addVertexByName_A(class_symb, index-vtxnb+i, newvtx, LESS);

    }
    return newvtx;

  }
  else if (et == PLUSPLUS) {

    assert(class_symb == the_mtg->classSymbol(the_mtg->vclass(loc)));

    int vtxnb = index - the_mtg->vindex(loc);

    assert(vtxnb > 0);

    int newvtx = loc;

    for (int i = 1; i <= vtxnb; i++) {

      newvtx = the_mtg->addVertexByName_A(class_symb, index-vtxnb+i, newvtx, PLUS);

    }
    return newvtx;

  }
  else return the_mtg->addVertexByName_A(class_symb, index, loc, et);

}

static int defineVertexByName_B(char class_symb, int index, VId loc, EType et) {


  if (!VALID(the_mtg->isValidClass(class_symb))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }

  VId id = the_mtg->addVertexByName_B(class_symb, index, loc, et);

  return id;

}

// ------------------------------------------
//      Checking and updating features
// ------------------------------------------

// Once totally filled, the feature set f[] is stored with its vertex

static void addFSet(VId v, Feature* f) {

  // cerr << "adding fset: vid = " << v << endl;

  the_mtg->addFSet(v, f);

}


static int storeFeatureValue(int vtx, Feature* fset, int findex) {

  int type = the_mtg->fType(findex);
  unsigned long integer;
  float real;

  switch(type) {
  case DDMM:
  case DDMMYY:
  case MMYY:
  case DDMMTIME:
  case DDMMYYTIME:
    {

      integer = encodeDate(fset[findex].s, type);
      fset[findex].i = integer; // the date may be invalid (LUNDEF)

      if (integer == (unsigned long)LUNDEF) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(INVALIDDATE_0);

        return CHECKERROR;
      }
      else return the_mtg->checkFeature(vtx, fset, findex);

    }
  case INTEGER:
    integer = atol(fset[findex].s);
    fset[findex].i = integer;
    return the_mtg->checkFeature(vtx, fset, findex);
  case REAL:
    real = (float) atof(fset[findex].s);
    fset[findex].r = real;
    return the_mtg->checkFeature(vtx, fset, findex);
  case ALPHA:
    return the_mtg->checkFeature(vtx, fset, findex);
  case GEOMETRY:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;

      }

    }

  case GENERIC:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;

      }

    }

  case APPEARANCE:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        // cerr << "Attribut nO: " << findex << " = \"" << fset[findex].s << "\"" << endl;

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;
      }
    }

  }

  return CHECKERROR; // Should return before

}


// --------------
// Parsing Errors
// --------------

static const int MAXERRMESSAGELENGTH = 500;

char* LOGICALERR = "logical error";

/* Remplit line_contents avec le contenu de la ligne courante
   On est oblige d'aller lire la ligne dans le fichier original
   puisque la ligne est en cours d'analyse et n'a peut etre pas
   ete completement analysee a ce moment */

static void getCompleteLine(int number, char* line_contents) {

  register long i, lnbegin;
  long int pos = ftell(yyin);

  fseek(yyin, 0, SEEK_SET);
  for(i=0;i<number;i++) {
    lnbegin = ftell(yyin);
    fgets(line_contents, MAXLINELENGTH, yyin);
  }

  fseek(yyin, pos, SEEK_SET);

}

// creates a new error item containing at least:
// - the type of the error
// - the line and column number of the error
// - the state of the current line when the error occurs

int yyerror(char* errtype) {

  assert(errtype);

  if (!lineCodeErrorState()) { // if not yet any error in this entity-code, create one

    char complete_line[MAXLINELENGTH];

    ErrorType type = GENERAL;

    getCompleteLine(lineNb(), complete_line);

    the_errlist->insert(ErrorItem(
#ifdef DEBUGCHECKERROR
                              NULL,
                              0,
                              yychar,
#endif
                              "Empty Message ...",
                              type,
                              UNDEF,
                              lineNb(),
                              columnNb(),
                              inputLine(),
                              complete_line,
                              UNDEF,
                              UNDEF
                              )
                    );

    if (yychar == 0) { // corresponds to the end of file
      COMPLETEERRORITEM(FILEENDSPREMATURELY_0);
    }

    /*
       std::cerr << "line = " << lineNb() << std::endl;
       cerr << "col  = " << columnNb() << std::endl;
       cerr << "input line = \"" << inputLine() << "\"" << std::endl;
       */

  }
  return 1;

}


// ----------------------
// MTG parser entry point
// ----------------------

ErrorList* parseMTG(MTG* mtg, int line_nb, std::ostream& errfile, int maxerrnb) {

  the_mtg = mtg;
  file_line_nb = line_nb;

  cleanErrorList(); // clean the previous errorlist before creating a new one.
  the_errlist = new ErrorList(err_messages, err_types, errfile, maxerrnb);

  yyparse();
  cleanParser();

  return the_errlist;

}
