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
 *       $Id: kernel_funs.cpp 5100 2008-06-13 15:00:23Z boudon $
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
#include <iomanip>
#include <string>
#include "tool/util_math.h"
#include "tool/timer.h"
#include <climits>

#include "tool/rw_locale.h"
#include "tool/rw_vector.h"
//#include <rw/tvsrtvec.h>
//#include <rw/locale.h>

#include "aml/erroraml.h"
#include "aml/parseraml.h"
#include "aml/fnode.h"

#include "mtg/utils.h"
#include "aml/date.h"

#include "tool/dirnames.h"

#include "aml/gnuplot.h"

#include "aml/set.h"
#include "aml/array.h"
#include "aml/list.h"

#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "aml/global.h"

#include "stat_tool/stat_tools.h"
#include "stat_tool/curves.h"
#include "stat_tool/markovian.h"
#include "sequence_analysis/sequences.h"
#include "aml/stat_module.h"

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Kernel"

#ifdef SYSTEM_IS__Linux
// AML2
// Apparament, il y a un probleme avec la fonction truncate,
// qui pourtant est bien defini dans mathcall.h inclu par math.h
// Je ne sais pas faire mieux que de la definir "a la main".
extern "C" double   trunc(double);
#endif

extern const char *Plot_prefix;
extern const char* SYSTEMCHAR;
/*
KernelEnv::KernelEnv() {

  _dateformat = DDMMYY;

}
*/

// -------------------------
// General Numeric Operators
// -------------------------

static AMObj K_SetMinus(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SetMinus", 2));

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  if (args[0].tag() == AMObjType::ARRAY) {

    CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "\\", args[0].tag.string().data(), "ARRAY"));

    Array* array1 = (Array*) args[0].val.p;
    Array* array2 = (Array*) args[1].val.p;

    Array* array3 = new SLArray(*(SLArray*)array1);

    ArrayIter* pnext = array2->iterator();
    ArrayIter& next = *pnext;

    while(next()) {

      *array3 -= next.key();

    }

    delete pnext;


    return AMObj(AMObjType::ARRAY, array3);

  }
  else if (args[0].tag() == AMObjType::SET) {


    CHECKCONDVA(args[0].tag() ==AMObjType::SET,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "\\", args[0].tag.string().data(), "SET"));

    Set* set1 = (Set*) args[0].val.p;
    Set* set2 = (Set*) args[1].val.p;

    Set* set3 = new HashSet(*(HashSet*)set1);

    SetIter* pnext = set2->iterator();
    SetIter& next = *pnext;

    while(next()) {

      *set3 -= next.key();

    }

    delete pnext;


    return AMObj(AMObjType::SET, set3);

  }
  else CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "\\", args[0].tag.string().data(), "SET or ARRAY"));

}


static AMObj K_Union(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Union", 2));

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  if (args[0].tag() == AMObjType::ARRAY) {

    CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "|", args[0].tag.string().data(), "ARRAY"));

    Array* array1 = (Array*) args[0].val.p;
    Array* array2 = (Array*) args[1].val.p;

    Array* array3 = new SLArray(*(SLArray*)array1);// WARNING: if array1 is not a SLArray, this is an error !!!

    ArrayIter* pnext = array2->iterator();
    ArrayIter& next = *pnext;

    while(next()) {

      *array3 += next.key();

    }

    delete pnext;

    return AMObj(AMObjType::ARRAY, array3);

  }
  else if (args[0].tag() == AMObjType::SET) {


    CHECKCONDVA(args[0].tag() ==AMObjType::SET,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "|", args[0].tag.string().data(), "SET"));

    Set* set1 = (Set*) args[0].val.p;
    Set* set2 = (Set*) args[1].val.p;

    Set* set3 = new HashSet(*(HashSet*)set1); // WARNING: if set1 is not a HashSet, this is an error !!!

    SetIter* pnext = set2->iterator();
    SetIter& next = *pnext;

    while(next()) {

      *set3 += next.key();

    }

    delete pnext;


    return AMObj(AMObjType::SET, set3);

  }
  else CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "|", args[0].tag.string().data(), "SET or ARRAY"));

}

static AMObj K_Inter(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Inter", 2));

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  if (args[0].tag() == AMObjType::ARRAY) {

    CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "&", args[0].tag.string().data(), "ARRAY"));

    Array* array1 = (Array*) args[0].val.p;
    Array* array2 = (Array*) args[1].val.p;

    Array* array3 = new SLArray;

    ArrayIter* pnext = array2->iterator();
    ArrayIter& next = *pnext;

    while(next()) {

      if (array1->contains(next.key())) *array3 += next.key();

    }

    delete pnext;


    return AMObj(AMObjType::ARRAY, array3);

  }
  else if (args[0].tag() == AMObjType::SET) {


    CHECKCONDVA(args[0].tag() ==AMObjType::SET,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "&", args[0].tag.string().data(), "SET"));

    Set* set1 = (Set*) args[0].val.p;
    Set* set2 = (Set*) args[1].val.p;

    Set* set3 = new HashSet;

    SetIter* pnext = set2->iterator();
    SetIter& next = *pnext;

    while(next()) {

      if (set1->contains(next.key())) *set3 += next.key();

    }

    delete pnext;


    return AMObj(AMObjType::SET, set3);

  }
  else CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "&", args[0].tag.string().data(), "SET or ARRAY"));

}

static AMObj K_PLUS(const AMObjVector& args) {


  if (args[0].tag() == AMObjType::ARRAY) { // No copy is made of the array: it is modified !!!

    /*
    CHECKCONDVA(args[1].tag() != AMObjType::ARRAY,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"+",args[0].tag.string().data(),"ARRAY(T) and T. To merge ARRAYs use |"));
    AMObjType elemtype = ((Array*)args[0].val.p)->surfaceType();
                */

    CHECKCONDVA(args[1] && ((Array*)args[0].val.p)->head(),
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"+",args[0].tag.string().data(),"ARRAY(T) and T"));

    ((Array*)args[0].val.p)->operator+=(args[1]);

    return args[0];

  }
  else if (args[0].tag() == AMObjType::SET) {

    if (((Set*)args[0].val.p)->anElement()) { // The set is not empty

      CHECKCONDVA(args[1] && *((Set*)args[0].val.p)->anElement(),
                  genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"+", args[0].tag.string().data(), "SET(T) and T"));
    }

    ((Set*)args[0].val.p)->operator+=(args[1]);

    return args[0];

  }
  else if (args[0].tag() == AMObjType::LIST) {

    ((List*)args[0].val.p)->operator+=(args[1]);

    return args[0];

  }
  else if (args[0].tag() == AMObjType::DATE) {

    CHECKCONDVA(args[1].tag == AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"+", 2, args[1].tag.string().data(), "INT"));

    AMObj unit;
    amobjTable()->findValue(":DateUnit", unit);

    AMObj d(AMObjType::DATE);

    d.val.d = args[0].val.d + unit.val.i * args[1].val.i;

    //cerr << args[0].val.d << endl;
    //cerr << unit.val.i << endl;
    //cerr << args[1].val.i << endl;

    return d;

  }
  else if (args[0].tag() == AMObjType::STRING) {

    CHECKCONDVA(args[1].tag == AMObjType::STRING || args[1].tag == AMObjType::CHAR,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"+", 2, args[1].tag.string().data(), "STRING"));
	RWCString cat;
	if(args[1].tag == AMObjType::CHAR)cat = *(AMString*)(args[0].val.p) + args[1].val.c;
    else cat = *(AMString*)(args[0].val.p) + *(AMString*)(args[1].val.p);

    return AMObj(AMObjType::STRING, new AMString(cat.data()));

  }
  else {

    AMObjType argtype = (args[0].tag & args[1].tag);

    if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"+", argtype.string().data(), "INT or REAL"));

    AMObj d(argtype);

    if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i + args[1].val.i;
    else {

      register double d0;
      if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
      else d0 = (double) args[0].val.i;

      register double d1;
      if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
      else d1 = (double) args[1].val.i;

      d.val.r = d0 + d1;

    }

    return d;

  }

}


static AMObj K_MINUS(const AMObjVector& args) {

  if (args[0].tag() == AMObjType::ARRAY) {

    if (args[1].tag() == AMObjType::ARRAY) return K_SetMinus(args);

    AMObjType elemtype = ((Array*)args[0].val.p)->surfaceType();

    CHECKCONDVA(args[1].tag == elemtype,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"-", args[0].tag.string().data(),"ARRAY(T) and T"));

    ((Array*)args[0].val.p)->operator-=(args[1]);

    return args[0];

  }
  else if (args[0].tag() == AMObjType::SET) {

    if (args[1].tag() == AMObjType::SET) return K_SetMinus(args);

    AMObjType elemtype = ((Set*)args[0].val.p)->surfaceType();

    CHECKCONDVA(args[1].tag != elemtype,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"-", args[1].tag.string().data(),"SET(T) and T"));

    ((Set*)args[0].val.p)->operator-=(args[1]);

    return args[0];

  }
  else if (args[0].tag() == AMObjType::DATE) {

    CHECKCONDVA(args[1].tag == AMObjType::INTEGER || args[1].tag == AMObjType::DATE,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"-", 2, args[1].tag.string().data(), "INT or DATE"));


    AMObj unit;
    amobjTable()->findValue(":DateUnit", unit);

    CHECKCONDVA(unit.val.i > 0,
                genAMLError(ERRORMSG( K_F_FUN_ERR_ss),"-", "DateUnit is not valid"));


    if (args[1].tag == AMObjType::INTEGER) {

      AMObj d(AMObjType::DATE);

      d.val.d = args[0].val.d - args[1].val.i * unit.val.i;

      return d;
    }
    else {

      AMObj d(AMObjType::INTEGER);

      d.val.i = (int)(args[0].val.d - args[1].val.d) / unit.val.i;

      return d;
    }

  }
  else {

    AMObjType argtype = (args[0].tag & args[1].tag);

    if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"-", argtype.string().data(), "INT or REAL"));

    AMObj d(argtype);

    if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i - args[1].val.i;
    else {

      register double d0;
      if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
      else d0 = (double) args[0].val.i;

      register double d1;
      if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
      else d1 = (double) args[1].val.i;

      d.val.r = d0 - d1;

    }

    return d;

  }
}



static AMObj K_UNARYMINUS(const AMObjVector& args) {

  AMObjType argtype = args[0].tag();

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"-", argtype.string().data(), "INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i =  - args[0].val.i;
  else d.val.r = - args[0].val.r;

  return d;

}



static AMObj K_TIMES(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"*", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i * args[1].val.i;
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    d.val.r = d0 * d1;

  }

    return d;

}

static AMObj K_DIVIDED(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"/", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) {
    CHECKDEFINECOND(args[1].val.i != 0, "Division by zero");
    d.val.i = args[0].val.i / args[1].val.i;
  }
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    CHECKDEFINECOND(d1 != 0.0, "Division by zero");

    d.val.r = d0 / d1;

  }

  return d;

}


static AMObj K_POWER(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"^", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  register double d1;
  if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
  else d1 = (double) args[1].val.i;

  CHECKDEFINECOND(!(d0 < 0 && fmod(d1,1) != 0), "x^y not defined for x<0 and y not integer"); // x^y : forbidden x<0 and y integer

  d.val.r = pow(d0,d1);

  return d;

}

static AMObj K_Sqrt(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Sqrt", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Sqrt", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0 >= 0, "The argument of Sqrt should be non-negative");

  d.val.r = sqrt(d0);

  return d;

}

static AMObj K_Exp(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Exp", 1));
  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Exp", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  d.val.r = exp(d0);

  return d;

}

static AMObj K_Log(const AMObjVector& args) {


  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Log", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Log", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0 > 0, "The argument of Log should be positive");

  d.val.r = log(d0);

  return d;

}

static AMObj K_Log10(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Log", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Log", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0 > 0, "The argument of Log10 should be positive");

  d.val.r = log10(d0);

  return d;

}

static AMObj K_MOD(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Mod", argtype.string().data(),"INT"));

  AMObj d(argtype);

  d.val.i = args[0].val.i % args[1].val.i;

  return d;

}

static AMObj K_Abs(const AMObjVector& args) {


  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Abs", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Abs", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i >= 0 ? args[0].val.i : -args[0].val.i;
  else d.val.r = fabs(args[0].val.r);

  return d;

}

static AMObj K_Floor(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Floor", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Floor", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i;
  else d.val.r = floor(args[0].val.r);

  return d;

}

static AMObj K_Ceil(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Ceil", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Ceil", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i;
  else d.val.r = ceil(args[0].val.r);

  return d;

}


static AMObj K_Truncate(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Truncate", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Truncate", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i;
  else d.val.r = trunc(args[0].val.r);

  return d;

}

static AMObj K_Rint(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Rint", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Rint", argtype.string().data(),"INT or REAL"));

  AMObj d(argtype);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i;
  else d.val.r = rint(args[0].val.r);

  return d;

}


static AMObj K_ToInt(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToInt", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::VTX || argtype == AMObjType::DATE || argtype == AMObjType::REAL || argtype == AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"ToInt", argtype.string().data(),"INT, VTX, DATE, REAL or STRING"));

  AMObj d(AMObjType::INTEGER);

  if (argtype == AMObjType::INTEGER) d.val.i = args[0].val.i;
  else if (argtype == AMObjType::STRING){
	int res = atoi(((AMString *)(args[0].val.p))->data());
	d.val.i = res;
  }
  else if (argtype == AMObjType::VTX) d.val.i = args[0].val.i;
  else if (argtype == AMObjType::DATE) d.val.i = (int) args[0].val.d;
  else if (fabs(args[0].val.r) <= (double) INT_MAX) d.val.i = (int)args[0].val.r;
  else d = AMObj(AMObjType::UNDEF);

  return d;

}



static AMObj K_ToReal(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToReal", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL || argtype == AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"ToReal", argtype.string().data(),"INT, REAL or STRING"));

  AMObj d(AMObjType::REAL);

  if (argtype == AMObjType::STRING){
	float res = atof(((AMString *)(args[0].val.p))->data());
	d.val.r = res;
  }
  if (argtype == AMObjType::REAL) d.val.r = args[0].val.r;
  else d.val.r = (double) args[0].val.i;

  return d;

}

static AMObj K_ToString(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToString", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER ||
              argtype == AMObjType::VTX ||
              argtype == AMObjType::DATE ||
              argtype == AMObjType::REAL ||
              argtype == AMObjType::CHAR,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"ToString", argtype.string().data(),"INT, VTX, DATE, CHAR or REAL"));

  AMObj d;

  if (argtype == AMObjType::INTEGER || argtype == AMObjType::VTX) {
    RWLocaleSnapshot english;
    RWCString conv = english.asString((long)args[0].val.i);
    d = AMObj(AMObjType::STRING, new AMString(conv.data()));
  }
  else if (argtype == AMObjType::REAL) {
    RWLocaleSnapshot english;
    RWCString conv = english.asString(args[0].val.r);
    d = AMObj(AMObjType::STRING, new AMString(conv.data()));
  }
  else if (argtype == AMObjType::DATE) d = AMObj(AMObjType::STRING, new AMString(printDate(args[0].val.d).data()));
  else if (argtype == AMObjType::CHAR) d = AMObj(AMObjType::STRING, new AMString(args[0].val.c));
  else d = AMObj(AMObjType::UNDEF);

  return d;

}

static AMObj K_SubString(const AMObjVector& args) {
  CHECKCONDVA(args.length() >= 2 && args.length() <= 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SubString", 1));
  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args.length() == 3 && args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SubString", 1, args[0].tag.string().data(), "LIST"));
  CHECKCONDVA(args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SubString", 2, args[1].tag.string().data(), "INT"));
  int nth = args[1].val.i;
  size_t l = string::npos;
  if (args.length() == 3){
  CHECKCONDVA(args[2].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SubString", 3, args[2].tag.string().data(), "INT"));
	l = args[2].val.i;
  }

  AMString* _str = (AMString*)args[0].val.p;
  CHECKDEFINECOND(nth!=0 && nth<=(int)_str->size() && -nth<= (int)_str->size() , "Index out of range");
  if (nth > 0) nth -= 1;
  else nth = _str->size()+nth;
  string res = _str->substr(nth,l);
  return AMObj(AMObjType::STRING,new AMString(res.c_str()));
}

static AMObj K_Sin(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Sin", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Sin", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  d.val.r = sin(d0);

  return d;

}

static AMObj K_Cos(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Cos", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Cos", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  d.val.r = cos(d0);

  return d;

}



static AMObj K_Tan(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Tan", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Tan", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0!=M_PI/2, "The argument of Tan should different from Pi/2 + n*Pi for any n");

  d.val.r = tan(d0);

  return d;

}

static AMObj K_Asin(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Asin", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Asin", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0<=1 && d0 >=-1, "The argument of ASin should be in the real interval [-1,1]");

  d.val.r = asin(d0);

  return d;

}

static AMObj K_Acos(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Acos", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Acos", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  CHECKDEFINECOND(d0<=1 && d0 >=-1, "The argument of ACos should be in the real interval [-1,1]");

  d.val.r = acos(d0);

  return d;

}

static AMObj K_Atan(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Atan", 1));

  AMObjType argtype = args[0].tag;

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Atan", argtype.string().data(),"INT or REAL"));

  AMObj d(AMObjType::REAL);

  register double d0;
  if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
  else d0 = (double) args[0].val.i;

  d.val.r = atan(d0);

  return d;

}



// ----------
// Predicates
// ----------

static AMObj K_EQ(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  // if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype != AMObjType::VOID, genAMLError(ERRORMSG(K_F_ARG_DIFFTYPES_ERR_sss),"==", args[0].tag.string().data(), args[1].tag.string().data()));

  AMObj d(AMObjType::BOOL);

  if (args[0] == args[1]) d.val.b = TRUE;
  else d.val.b = FALSE;

  return d;

}

static AMObj K_DIFF(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  // if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype != AMObjType::VOID, genAMLError(ERRORMSG(K_F_ARG_DIFFTYPES_ERR_sss),"!=",args[0].tag.string().data(), args[1].tag.string().data()));

  AMObj d(AMObjType::BOOL);

  if (args[0] != args[1]) d.val.b = TRUE;
  else d.val.b = FALSE;

  return d;

}


static AMObj K_LT(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL || argtype == AMObjType::CHAR || argtype == AMObjType::DATE,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"<", argtype.string().data(), "INT, REAL or DATE"));

  AMObj d(AMObjType::BOOL);

  if (argtype == AMObjType::INTEGER) {
    if (args[0].val.i < args[1].val.i) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  if (argtype == AMObjType::CHAR) {
    if (args[0].val.c < args[1].val.c) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else if (argtype == AMObjType::DATE) {
    if (args[0].val.d < args[1].val.d) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    if (d0 < d1) d.val.i = TRUE;
    else d.val.i = FALSE;

  }

  return d;

}

static AMObj K_LTEQ(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL || argtype == AMObjType::CHAR || argtype == AMObjType::DATE,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"<=", argtype.string().data(), "INT or REAL or DATE"));

  AMObj d(AMObjType::BOOL);

  if (argtype == AMObjType::INTEGER) {
    if (args[0].val.i <= args[1].val.i) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  if (argtype == AMObjType::CHAR) {
    if (args[0].val.c <= args[1].val.c) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else if (argtype == AMObjType::DATE) {
    if (args[0].val.d <= args[1].val.d) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    if (d0 <= d1) d.val.i = TRUE;
    else d.val.i = FALSE;

  }

  return d;

}


static AMObj K_GT(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL || argtype == AMObjType::CHAR || argtype == AMObjType::DATE,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),">", argtype.string().data(), "INT or REAL or DATE"));

  AMObj d(AMObjType::BOOL);

  if (argtype == AMObjType::INTEGER) {
    if (args[0].val.i > args[1].val.i) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  if (argtype == AMObjType::CHAR) {
    if (args[0].val.c > args[1].val.c) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else if (argtype == AMObjType::DATE) {
    if (args[0].val.d > args[1].val.d) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    if (d0 > d1) d.val.i = TRUE;
    else d.val.i = FALSE;

  }

  return d;

}

static AMObj K_GTEQ(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER || argtype == AMObjType::REAL || argtype == AMObjType::CHAR || argtype == AMObjType::DATE,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss), "<=", argtype.string().data(), "INT or REAL or DATE"));

  AMObj d(AMObjType::BOOL);

  if (argtype == AMObjType::INTEGER) {
    if (args[0].val.i >= args[1].val.i) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  if (argtype == AMObjType::CHAR) {
    if (args[0].val.c >= args[1].val.c) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else if (argtype == AMObjType::DATE) {
    if (args[0].val.d >= args[1].val.d) d.val.i = TRUE;
    else d.val.i = FALSE;
  }
  else {

    register double d0;
    if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
    else d0 = (double) args[0].val.i;

    register double d1;
    if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
    else d1 = (double) args[1].val.i;

    if (d0 >= d1) d.val.i = TRUE;
    else d.val.i = FALSE;

  }

  return d;

}


static AMObj K_AND(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::BOOL || argtype == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"And", argtype.string().data(), "BOOL"));

  AMObj d(AMObjType::BOOL);

  if (args[0].val.i && args[1].val.i) d.val.b = TRUE;
  else d.val.b = FALSE;

  return d;

}

static AMObj K_OR(const AMObjVector& args) {

  AMObjType argtype = (args[0].tag & args[1].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::BOOL || argtype == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"Or", argtype.string().data(),"BOOL"));

  AMObj d(AMObjType::BOOL);

  if (args[0].val.i || args[1].val.i) d.val.b = TRUE;
  else d.val.b = FALSE;

  return d;

}

/*

static AMObj K_IN(const AMObjVector& args) {

  CHECKCONDVA(args[0].tag == AMObjType::INTEGER ||
              args[0].tag == AMObjType::REAL ||
//            args[0].tag == AMObjType::STRING ||
              args[0].tag == AMObjType::DATE,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss),"In", args[0].tag.string().data(), "INT, REAL or DATE"))

  AMObj d(AMObjType::BOOL);

  switch (args[0].tag()) {

  case AMObjType::INTEGER:
    CHECKCONDVA(args[1].tag == AMObjType::INTEGER,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 2, args[1].tag.string().data(), "INT"));
    CHECKCONDVA(args[2].tag == AMObjType::INTEGER,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 3, args[2].tag.string().data(), "INT"));
    if (args[0].val.i >= args[1].val.i && args[0].val.i <= args[2].val.i) d.val.b = TRUE;
    else d.val.b = FALSE;
    break;
  case AMObjType::REAL:
    {
    CHECKCONDVA((args[1].tag & AMObjType::INTEGER) == AMObjType::REAL,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 2, args[1].tag.string().data(), "REAL"));
    CHECKCONDVA((args[2].tag & AMObjType::INTEGER) == AMObjType::REAL,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 3, args[2].tag.string().data(), "REAL"));
      register double d0;
      if (args[0].tag() == AMObjType::REAL) d0 = args[0].val.r;
      else d0 = (double) args[0].val.i;

      register double d1;
      if (args[1].tag() == AMObjType::REAL) d1 = args[1].val.r;
      else d1 = (double) args[1].val.i;

      register double d2;
      if (args[2].tag() == AMObjType::REAL) d2 = args[2].val.r;
      else d2 = (double) args[2].val.i;

      if (d0 >= d1 && d0 <= d2) d.val.b = TRUE;
      else d.val.b = FALSE;

    }
    break;
  case AMObjType::DATE:
    CHECKCONDVA(args[1].tag == AMObjType::DATE,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 2, args[1].tag.string().data(), "DATE"));
    CHECKCONDVA(args[2].tag == AMObjType::DATE,genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"In", 3, args[2].tag.string().data(), "DATE"));
    if (args[0].val.d >= args[1].val.d && args[0].val.d <= args[2].val.d) d.val.b = TRUE;
    else d.val.b = FALSE;
    break;

  case AMObjType::STRING:
    {
      RWCString s(args[0].val.s);
      RWCString s1(args[1].val.s);
      RWCString s2(args[2].val.s);
      if (s1 <= s && s <= s2) d.val.b = TRUE;
      else d.val.b = FALSE;
    }
    break;

  default:
    assert(FALSE);
    break;

  }

  return d;
}

*/

static AMObj K_NOT(const AMObjVector& args) {

  AMObjType argtype = args[0].tag();

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::BOOL || argtype == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss), "Not", argtype.string().data(), "BOOL"));

  AMObj d(AMObjType::BOOL);

  if (args[0].val.i) d.val.b = FALSE;
  else d.val.b = TRUE;

  return d;

}

static AMObj K_ToTimeUnit(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToTimeUnit", 1));

  AMObjType argtype = args[0].tag();

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(argtype == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss),"ToTimeUnit", 1, args[0].tag.string().data(), "INT"));

  AMObj unit;
  amobjTable()->findValue(":DateUnit", unit);

  AMObj d(AMObjType::INTEGER);

  d.val.i = args[0].val.i / unit.val.i;

  return d;

}

static AMObj K_Date(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Date", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() == AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss), "Date", args[0].tag.string().data(), "STRING"));

  FType datetype = (FType)-1;

  AMObj format;
  amobjTable()->findValue(":DateFormat", format);

  AMObj d(AMObjType::DATE);
  RWCString formstg = *(AMString*)format.val.p;

  if (formstg == "DDMM") datetype = DDMM;
  else if (formstg == "DDMMYY") datetype = DDMMYY;
  else if (formstg == "MMYY") datetype = MMYY;
  else if (formstg == "DDMMTIME") datetype = DDMMTIME;
  else if (formstg == "DDMMYYTIME") datetype = DDMMYYTIME;

  CHECKCONDVA(datetype != (FType)-1,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Date", 1, "a value compatible with the format defined in DateFormat, which seems to be a wrong format"));


  const char* datestg = ((AMString*)args[0].val.p)->data();

  Date date = encodeDate(datestg, datetype);

  CHECKCONDVA(date != LUNDEF,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Date", 1, "a valid date. Example of a valid date with DateFormat=DDMMYYTIME: \"09/10/97 12:33\""));

  d.val.d = date;

  return d;

}

static VPTOOLS(Timer) TIMER;

static AMObj K_TimerStart(const AMObjVector& args) {
  TIMER.start();
  return AMObj(AMObjType::VOID);
}

static AMObj K_TimerElapsed(const AMObjVector& args) {  
  return AMObj(AMObjType::REAL,TIMER.elapsedTime());
}

static AMObj K_TimerStop(const AMObjVector& args) {  
  return AMObj(AMObjType::REAL,TIMER.stop());
}


static AMObj K_Select(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Select", 2));

  // if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA((args[1].tag() & AMObjType::BOOL) != AMObjType::UNDEF,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Select", 2, args[1].tag.string().data(), "BOOL"));

  if (args[1].val.b) return args[0];
  else return AMObj(AMObjType::VOID);

}

static AMObj K_Interval(const AMObjVector& args)
{

  int argnb = args.length();

  CHECKCONDVA(argnb == 2 || argnb == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "Interval", "2 or 3"));

  AMObjType argtype = (args[0].tag & args[1].tag);
  if (argnb == 3) argtype = (argtype & args[2].tag);

  if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  AMObjType interval_type = AMObjType::INTEGER;

  // determine first whether it is an int or a real interval
  for (register int i=0; i<argnb; i++) {
    if (args[i].tag() == AMObjType::REAL) {
      interval_type = AMObjType::REAL;
    }
    else CHECKCONDVA(args[i].tag() == AMObjType::INTEGER,
                     genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sss), "Interval", args[i].tag.string().data(), "INT or REAL"));

  }

  Array* array = new SLArray;

  switch (interval_type()) {

  case AMObjType::INTEGER: // all three nb are ints
    {
      int arg[3];
      for (int i=0; i<3; i++) {
        if (i<2 || i==argnb-1) arg[i] = args[i].val.i;
        else arg[2] = 1;
      }
      if (arg[0] > arg[1] && arg[2] == 1)  arg[2] = -1;

      int flag = (arg[0] <= arg[1] && arg[2] > 0) ? 1 : ((arg[0] >= arg[1] && arg[2] < 0) ? 2 : 0);

      CHECKDEFINECOND(flag, "Bad interval definition");

      if (flag == 1) {
        for (int i=arg[0];i<=arg[1];i+=arg[2]) {
          *array += AMObj(AMObjType::INTEGER, i);
        }
      }
      else {
        assert(flag == 2);
        for (int i=arg[0];i>=arg[1];i+=arg[2]) {
          *array += AMObj(AMObjType::INTEGER, i);
        }
      }

    }
    break;
  case AMObjType::REAL:
    {
      double arg[3];
      for (int i=0; i<3; i++) {
        if (i<2 || i==argnb-1) {
          if (args[i].tag() == AMObjType::REAL) arg[i] = args[i].val.r;
          else arg[i] = (double) args[i].val.i;
        }
        else arg[2] = 1.0;
      }

      if (arg[0] > arg[1] && arg[2] == 1)  arg[2] = -1.0;

      int flag = (arg[0] <= arg[1] && arg[2] > 0) ? 1 : ((arg[0] >= arg[1] && arg[2] < 0) ? 2 : 0);

      CHECKDEFINECOND(flag, "Bad interval definition");

      if (flag == 1) {
        for (register double r = arg[0];r<=arg[1];r+=arg[2]) {
          *array += AMObj(AMObjType::REAL, r);
        }
      }
      else {
        assert(flag == 2);
        for (register double r = arg[0];r>=arg[1];r+=arg[2]) {
          *array += AMObj(AMObjType::REAL, r);
        }
      }
    }

    break;
  default:
    assert(FALSE);

  }

  return AMObj(AMObjType::ARRAY, array);

}

static AMObj K_Rand(const AMObjVector& args) {

  int argslen = args.length();
  CHECKCONDVA(argslen == 0 || argslen == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "Rand", "0 or 2"));

  if (argslen == 0) { // Function return a real uniformly distributed over 0 and 1

    return AMObj(AMObjType::REAL, randomDouble());
  }
  else if (argslen == 2) { // Function returns an int uniformly distributed in [arg[0],arg[1]]

    AMObjType argtype = (args[0].tag & args[1].tag);

    if (argtype == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(args[0].tag() == AMObjType::INTEGER && args[1].tag() == AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Rand", args[0].tag.string().data(), "INT"));

    int i = args[0].val.i;
    int j = args[1].val.i;

    CHECKCONDVA(i <= j,
                genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_ss), "Rand", "arg1 <= arg2"));

    return AMObj(AMObjType::INTEGER, (int)randomNbInRange(i,j));

  }
  else assert(FALSE);

  return  AMObj(AMObjType::VOID);
}


static AMObj K_EchoOn(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NO_ARG_ERR_s), "EchoOn"));

  amlEchoOn();

  return AMObj(AMObjType::VOID);

}


static AMObj K_EchoOff(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NO_ARG_ERR_s), "EchoOff"));

  amlEchoOff();

  return AMObj(AMObjType::VOID);

}

static AMObj K_Delete(const AMObjVector& args) {

  CHECKCONDVA(args.length() != 0,
              genAMLError(ERRORMSG(K_ANY_NB_ARG_ERR_ss), "Delete", "0"));

  for (size_t i=0; i<args.length(); i++ ) {

    if (args[i].tag() == AMObjType::UNDEF) continue;

    CHECKCONDVA(args[i].tag() == AMObjType::STRING,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Delete", args[i].tag.string().data(), "STRING"));

    AMLOUTPUT << endl;

    RWCString name(*(AMString*)(args[i].val.p));

    CHECKCONDVA( (name(0) != ':' ),
                genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "Delete", i+1, "a system object"));

    AMObj obj;

    if (amobjTable()->findValue(name, obj)) {

      if (obj.isaAMModel())
        {
        CHECKCONDVA(obj.isLocked() <= 1,
                  genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "Delete", i+1, "an object in use elsewhere"));
        }


      amobjTable()->remove(name);
      AMLOUTPUT << name << " deleted.";

    }
    else AMLOUTPUT << name << " not deleted : object not found.";

  }

  return AMObj(AMObjType::VOID);

}

const int MAXFUNNAMELENGTH = 15;

static AMObj K_Print(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len >= 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Print"));

  if (args[0].isaAMModel()) return args[0].val.p->print(args);

  return AMObj(AMObjType::VOID);

}

static AMObj K_Save(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len >= 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Save"));

  if (args[0].isaAMModel()) return args[0].val.p->save(args);

  return AMObj(AMObjType::VOID);

}

static void set_current_plotobj(AMObj obj) {

  amobjTable()->insert(":CurrentPlottedObj", obj);

}

static AMObj get_current_plotobj() {

  AMObj var;

  amobjTable()->findValue(":CurrentPlottedObj", var);

  return var;

}

static void set_current_window(AMObj w) {

  amobjTable()->insert(":CurrentWindow", w);

}

static AMObj get_current_window() {

  AMObj var;

  amobjTable()->findValue(":CurrentWindow", var);

  return var;

}



static AMObj K_Plot(const AMObjVector& args) {

  unsigned int argth = 0;
  unsigned int len = args.length();

  AMObj thewin = get_current_window();
  AMObj theobj = get_current_plotobj();

  if (len == 0) {

    if (theobj.tag != AMObjType::UNDEF && theobj.val.p) return theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    else CHECKCONDVA(FALSE,
                     genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", 1, theobj.tag.string().data(), "a non elementary type"));


  }
  else {

    while (argth < args.length()) { // treatment of options

      if (args[argth].tag() == AMObjType::OPTION) {

        if (*(AMString*)(args[argth].val.p) == "Window") {

          CHECKCONDVA(args[argth+1].tag() == AMObjType::WINDOW,
                      genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "a WINDOW"));


          set_current_window(args[argth+1]);
          thewin = args[argth+1];
        }

        argth ++;

      }

      argth ++;

    }

    if (args[0].isaAMModel() && args[0].tag() != AMObjType::STRING
                             && args[0].tag() != AMObjType::OPTION) {
      theobj = args[0];
      set_current_plotobj(theobj);
      return theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    }
    else if (theobj.tag() != AMObjType::UNDEF) {
      return theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    }
    else CHECKCONDVA(FALSE,
                     genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Plot"));
  }


}


static AMObj K_Extract(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len >= 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Extract"));

  if (args[0].isaAMModel()) return args[0].val.p->extract(args);
  else CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Extract"));


}



static AMObj K_NewPlot(const AMObjVector& args) {

  int len = args.length();

  AMObj thewin = AMObj(AMObjType::WINDOW, new GP_window);
  set_current_window(thewin);

  AMObj theobj = get_current_plotobj();

  if (len == 0) {

    if (theobj.tag != AMObjType::UNDEF && theobj.val.p) return theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    else CHECKCONDVA(FALSE,
                     genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "NewPlot", 1, theobj.tag.string().data(), "a non elementary type"));


  }
  else {

    if (args[0].isaAMModel()  && args[0].tag() != AMObjType::STRING
                              && args[0].tag() != AMObjType::OPTION) {
      theobj = args[0];
      set_current_plotobj(theobj);
      theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    }
    else if (theobj.tag() != AMObjType::UNDEF) {
      theobj.val.p->plot(*(GP_window*)thewin.val.p, args);
    }
    else CHECKCONDVA(FALSE,
                     genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "NewPlot"));
  }


  return thewin;

}

static AMObj K_ExpSequence(const AMObjVector& args) {

  assert(args.length() == 2); // This is checked syntactically

  return AMObj(args[1]);

}

static AMObj K_Display(const AMObjVector& args) {

  unsigned int argth = 1;
  unsigned int len = args.length();

  unsigned int maxbytenb = 0; // this value means to display all the object and can be overwritten by an option

  CHECKCONDVA(len >= 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Display"));

  if (args[0].isaAMModel()) return args[0].val.p->display(AMLOUTPUT, args);

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Display", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "ByteSize") {

      CHECKCONDVA(args[argth+1].tag() == AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Display", (argth+1)/2+1, "an INT"));
      CHECKCONDVA(args[argth+1].val.i >= 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Display", (argth+1)/2+1, ">= 0"));

      maxbytenb = args[argth+1].val.i;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Display", (argth+1)/2+1));

    }

    argth += 2;

  }

  args[0].printValue(AMLOUTPUT, maxbytenb);

  return AMObj(AMObjType::VOID);

}

static AMObj K_DisplayName(const AMObjVector& args) {

  assert(args.length() == 1); // This is checked syntactically

  CHECKCONDVA(args[0].tag() == AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "?", args[0].tag.string().data(), "STRING"));

  if (amobjTable()->contains(*(AMString*)(args[0].val.p))) {

    const AMObjTable* amo_table = (AMObjTable*)amobjTable();
    RWCString name = *(AMString*)(args[0].val.p);

    AMLOUTPUT << ((RWTValHashDictionary<RWCString, AMObj>*)amo_table)->operator[](name) << endl;


    /* old version
    AMLOUTPUT << endl << setiosflags(ios::left) << setw(MAXFUNNAMELENGTH)
    << *(AMString*)(args[0].val.p) << (*(AMObjTable*)amobjTable())[*(AMString*)(args[0].val.p)] << endl;
    AMLOUTPUT << resetiosflags(ios::adjustfield);
    */


  }
  else AMLOUTPUT << "This name has not been defined" << endl;

  return AMObj(AMObjType::VOID);

}

static AMObj K_DisplayAllUserNames(const AMObjVector& args) {

  assert(args.length() == 0); // This is checked syntactically

  // The Table is not sorted => create one sorted

  RWTValSortedVector<RWCString> sorted_table;
  AMObjTable* amo_table = (AMObjTable*)amobjTable();

  AMObjTableIter next(*amo_table);

  RWCString name;

  while (next()) {

    name = next.key();
    if (name(0) != SYSTEMCHAR[0]) sorted_table.insert(next.key());

  }

  AMLOUTPUT << endl;

  int table_size = sorted_table.entries();

  if (table_size == 0) AMLOUTPUT << "No user object defined." << endl;

  for(register int i=0; i<table_size; i++) {

    name = sorted_table[i];
    AMLOUTPUT << setiosflags(ios::left) << setw(MAXFUNNAMELENGTH) << name.data() << (*amo_table)[name] << endl;

  }

  return AMObj(AMObjType::VOID);

}

static AMObj K_DisplayAllNames(const AMObjVector& args) {

  assert(args.length() == 0); // This is checked syntactically

  // The Table is not sorted => create one sorted

  RWTValSortedVector<RWCString> sorted_table;
  AMObjTable* amo_table = (AMObjTable*)amobjTable();

  AMObjTableIter next(*amo_table);

  while (next()) {

    sorted_table.insert(next.key());

  }

  int table_size = sorted_table.entries();

  RWCString name;

  AMLOUTPUT << endl;

  for(register int i=0; i<table_size; i++) {

    name = sorted_table[i];
    AMLOUTPUT << setiosflags(ios::left) << setw(MAXFUNNAMELENGTH) << name.data() << (*amo_table)[name] << endl;

  }

  return AMObj(AMObjType::VOID);

}

static AMObj K_Echo(const AMObjVector& args) {

  unsigned int argth = 0;
  unsigned int len = args.length();

  unsigned int maxbytenb = 0; // this value means to display all the object and can be overwritten by an option

#ifndef STL_EXTENSION
  const int MAXBUFSIZE = 10000; // nb of chars for the display of 1 object
  char tmp[10000];
#endif

  AMString* result = new AMString("");

  CHECKCONDVA(len >= 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Echo"));


  while (argth < args.length()) { // treatment of options

    if (args[argth].tag() == AMObjType::OPTION) {

      assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "ByteSize") {

        CHECKCONDVA(args[argth+1].tag() == AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Echo", (argth+1)/2+1, "an INT"));
        CHECKCONDVA(args[argth+1].val.i >= 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Echo", (argth+1)/2+1, ">= 0"));

        maxbytenb = args[argth+1].val.i;

      }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Echo", (argth+1)/2+1));

      }

      argth += 2;

    }
    else {

#ifndef STL_EXTENSION
      ostrstream strstr(tmp, MAXBUFSIZE-1);

      args[argth].printValue(strstr, maxbytenb);

      strstr << ends;

      if (strlen(tmp) >= MAXBUFSIZE-1) AMLOUTPUT << "Echo output was truncated. Please use option ByteSize to allocate more than " << MAXBUFSIZE << " chars  to each echoed object" << endl;

      *result += tmp;

      argth ++;
#else
      ostringstream strstr;

      args[argth].printValue(strstr, maxbytenb);

      strstr << ends;

      *result += strstr.str();

      argth ++;

#endif
    }

  }

  return AMObj(AMObjType::STRING, (AMModel*)result);

}

static AMObj K_Identity(const AMObjVector& args) {

  CHECKCOND(args.length() == 1, K_SINGLE_ARG_ERR_s);

  return args[0];

}


//-----------------------
//   Type Constructors
//-----------------------

static AMObj K_Set(const AMObjVector& args) {

  int len = args.length();

  Set* set = new HashSet;

  for (register int i=0; i <len; i++) {

    if (i>0) {
      if (!(args[0] && args[i])) {
        delete set;
        genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "Set", i+1, args[i].tag.string().data());
        return AMObj(AMObjType::ERROR);
      }
    }

    *set += args[i];

  }

  return AMObj(AMObjType::SET, set);

}


static AMObj K_ArrayBracket(const AMObjVector& args) {

  int len = args.length();

  Array* array = new SLArray;

  for (register int i=0; i <len; i++) {

    if (i>0) {
      if (!(args[0] && args[i])) {
        delete array;
        genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "Array", i+1, args[i].tag.string().data());
        return AMObj(AMObjType::ERROR);
      }
    }

    *array += args[i];

  }

  return AMObj(AMObjType::ARRAY, array);

}

static AMObj K_Array(const AMObjVector& args) {

  int len = args.length();

  if (len <= 2) {

    int dim;
    int* dimarray;

    CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Array", 1, args[0].tag.string().data(), "STRING"));

    if (len == 2) {

      CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Array", 2, args[1].tag.string().data(), "ARRAY"));

      CHECKCONDVA( ((Array*) args[1].val.p)->surfaceType() == AMObjType::INTEGER ||
                   ((Array*) args[1].val.p)->surfaceType() == AMObjType::ANY,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Array", 2, args[1].tag.string().data(), "ARRAY(INT)"));

      Array* thearray = (Array*)(args[1].val.p);

      dim = thearray->entries();
      dimarray = new int[dim];

      // initialisation du tableau dimarray a partir du 3ieme argument:

      ArrayIter* pnext = thearray->iterator();
      ArrayIter& next = *pnext;

      int i =0;
      while(next()) {

        dimarray[i++] = next.key().val.i;

      }

      delete pnext;

      // le second argument correspond au niveau (level) d'imbrication du tableau
      // que l'on veut construire: il est egal au nombre de sous-dimensions que
      // l'on considere + 1

      Array* array = new SLArray( (*((AMString*)args[0].val.p)).data(), dim+1, dimarray);

      if (array->isValid())  return AMObj(AMObjType::ARRAY, array);
      else {

        delete array;
        return AMObj(AMObjType::ERROR);

      }

    }
    else { // len == 1

      Array* array = new SLArray( (*((AMString*)args[0].val.p)).data());

      if (array->isValid())  return AMObj(AMObjType::ARRAY, array);
      else {

        delete array;
        return AMObj(AMObjType::ERROR);

      }

    }

  }
  else { // Construction similar to a construction with bracket

    Array* array = new SLArray;

    for (register int i=0; i <len; i++) {

      if (i>0) {
        if (!(args[0] && args[i])) {
          delete array;
          genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "Array", i+1, args[i].tag.string().data());
          return AMObj(AMObjType::ERROR);
        }
      }

      *array += args[i];

    }

    return AMObj(AMObjType::ARRAY, array);

  }

}

static AMObj K_At(const AMObjVector& args) {

  int len = args.length();

  assert(len == 2); // checked syntactically

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST || args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "@", 1, args[0].tag.string().data(), "LIST"));
  CHECKCONDVA(args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "@", 2, args[1].tag.string().data(), "INT"));

  int nth = args[1].val.i;

  if (args[0].tag() ==AMObjType::STRING) {
	AMString* _str = (AMString*)args[0].val.p;
    CHECKDEFINECOND(nth!=0 && nth<=(int)_str->size() && -nth<= (int)_str->size() , "Index out of range");
    if (nth > 0) {
	  return AMObj(AMObjType::CHAR,_str->at(nth-1));
	}
    else return AMObj(AMObjType::CHAR,_str->at(_str->size()+nth));

  }
  else if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;

    CHECKDEFINECOND(nth!=0 && nth<=array->entries() && -nth<=array->entries() , "Index out of range");

    if (nth > 0) return array->at(nth-1);
    else return array->at(array->entries()+nth);

  }
  else {

    List* list = (List*) args[0].val.p;

    CHECKDEFINECOND(nth!=0 && nth<=list->entries() && -nth<=list->entries() , "Index out of range");

    if (nth > 0) return list->at(nth-1);
    else return list->at(list->entries()+nth);

  }

}

static AMObj K_Head(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Head"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() == AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Head", args[0].tag.string().data(), "ARRAY"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;
    return array->head();

  }
  else {

    List* list = (List*) args[0].val.p;
    return list->head();

  }

}

static AMObj K_Tail(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Tail", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() == AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Tail", args[0].tag.string().data(), "ARRAY"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;
    return array->tail();

  }
  else {

    List* list = (List*) args[0].val.p;
    return list->tail();

  }

}

static AMObj K_Pos(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Pos", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  //if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST || args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Pos", args[0].tag.string().data(), "ARRAY or STRING"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;
    int res = array->index(args[1]);
    if (res >= 0) return AMObj(AMObjType::INTEGER, res + 1);
    else return AMObj(AMObjType::UNDEF);

  }
  else if (args[0].tag() ==AMObjType::STRING) {
	CHECKCONDVA(args[1].tag() ==AMObjType::CHAR || args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Pos", args[0].tag.string().data(), "CHAR or STRING"));

    AMString* m_string = (AMString*) args[0].val.p;
	string substring;
	if(args[1].tag() ==AMObjType::CHAR) substring = args[1].val.c;
	else substring = ((AMString*) args[1].val.p)->data();
    size_t res = m_string->find(substring);
    if (res != string::npos) return AMObj(AMObjType::INTEGER, (int)res + 1);
    else return AMObj(AMObjType::UNDEF);

  }
  else {

    List* list = (List*) args[0].val.p;
    int res = list->index(args[1]);
    if (res >= 0) return AMObj(AMObjType::INTEGER, res + 1);
    else return AMObj(AMObjType::UNDEF);

  }

}

static AMObj K_AllPos(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "AllPos", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  //if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "AllPos", args[0].tag.string().data(), "ARRAY"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* result = new SLArray;

    Array* array = (Array*) args[0].val.p;
    len = array->entries();

    for(register int i = 0; i<len; i++) {

      if (array->at(i) == args[1]) *result += AMObj(AMObjType::INTEGER, i+1);

    }

    return AMObj(AMObjType::ARRAY, result);

  }
  else {

    Array* result = new SLArray;

    List* array = (List*) args[0].val.p;
    len = array->entries();

    for(register int i = 0; i<len; i++) {

      if (array->at(i) == args[1]) *result += AMObj(AMObjType::INTEGER,i+1);

    }

    return AMObj(AMObjType::ARRAY, result);


  }

}

static AMObj K_Occurences(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Occurences", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Occurences", args[0].tag.string().data(), "ARRAY or LIST"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    int res = -1;
    cerr << "Not Yet Implemented" << endl;

    return AMObj(AMObjType::INTEGER, res);

  }
  else {

    List* list = (List*) args[0].val.p;
    // int res = list->occurencesOf(args[1]);

    int res = -1;
    cerr << "Not Yet Implemented" << endl;

    return AMObj(AMObjType::INTEGER, res);

  }

}


static AMObj K_List(const AMObjVector& args) {

  int len = args.length();

  List* list = new SLList;

  for (register int i=0; i <len; i++) {

    *list += args[i];

  }

  return AMObj(AMObjType::LIST, list);

}


static AMObj K_InsertAt(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "InsertAt", 3));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "InsertAt", 1, args[0].tag.string().data(), "LIST or ARRAY"));
  CHECKCONDVA(args[2].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "InsertAt", 3, args[2].tag.string().data(), "INT"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[2].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  int nth = args[2].val.i;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;

    AMObjType stype = array->surfaceType();
    int len = array->entries();

    CHECKCONDVA(args[1].tag == stype,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "InsertAt", 2, args[1].tag.string().data(), stype.string().data()));
    CHECKDEFINECOND(nth!=0 && nth<=array->entries()+1 && -nth<=array->entries()+1 , "Index out of range");

    if (nth > 0)
    if (nth <= array->entries()) array->insert(nth-1, args[1]);
    else (*array)+= args[1];
    else
    if (-nth > 1) array->insert(array->entries()+nth+1, args[1]);
    else (*array)+= args[1];
  }
  else {

    List* list = (List*) args[0].val.p;

    int len = list->entries();

    CHECKDEFINECOND(nth!=0 && nth<=list->entries()+1 && -nth<=list->entries()+1 , "Index out of range");

    if (nth > 0)
    if (nth <= list->entries()) list->insert(nth-1, args[1]);
    else (*list)+= args[1];
    else
    if (-nth > 1) list->insert(list->entries()+nth+1, args[1]);
    else (*list)+= args[1];

  }

  return args[0];

}


static AMObj K_RemoveAt(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "RemoveAt", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "RemoveAt", 1, args[0].tag.string().data(), "LIST or ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "RemoveAt", 2, args[1].tag.string().data(), "INT"));

  int nth = args[1].val.i;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;

    AMObjType stype = array->surfaceType();
    int len = array->entries();

    CHECKDEFINECOND(nth!=0 && nth<=array->entries() && -nth<=array->entries() , "Index out of range");

    if (nth > 0) array->remove(nth-1, nth-1);
    else array->remove(array->entries()+nth, array->entries()+nth);

  }
  else {

    List* list = (List*) args[0].val.p;

    int len = list->entries();

    CHECKDEFINECOND(nth!=0 && nth<=list->entries() && -nth<=list->entries() , "Index out of range");

    if (nth > 0) list->remove(nth-1, nth-1);
    else list->remove(list->entries()+nth, list->entries()+nth);

  }

  return args[0];

}


static AMObj K_Invert(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Invert", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Invert", 1, args[0].tag.string().data(), "LIST or ARRAY"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;

    Array* iarray = new SLArray;

    int len = array->entries();

    for (register int i = 0; i < len; i++) {

      *iarray += array->at(len-i-1);

    }

    return AMObj(AMObjType::ARRAY, iarray);

  }
  else {

    List* list = (List*) args[0].val.p;

    List* ilist = new SLList;

    int len = list->entries();

    for (register int i = 0; i < len; i++) {

      *ilist += list->at(len-i-1);

    }

    return AMObj(AMObjType::LIST, ilist);

  }

}


static AMObj K_Sort(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Sort", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Sort", 1, args[0].tag.string().data(), "ARRAYor SET"));

  Array* iarray = new SLArray;
  RWTValSortedVector<AMObj> vec;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*) args[0].val.p;

    int l = array->entries();

    for (register int i = 0; i < l; i++) {

      vec.insert(array->at(i));

    }

    for (int j = 0; j < l; j++) {

      *iarray += vec[j];
    }

  }
  else  {

    Set* set = (Set*) args[0].val.p;

    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    while(next()) {

      vec.insert(next.key());

    }

    int l = set->entries();

    for (register int i = 0; i < l; i++) {

      *iarray += vec[i];
    }


  }

  return AMObj(AMObjType::ARRAY, iarray);

}

static AMObj K_ToSet(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToSet", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY ||
              args[0].tag() ==AMObjType::LIST ||
              args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ToSet", args[0].tag.string().data(), "ARRAY or LIST or SET"));

  Set* set = 0;

  switch(args[0].tag()) {

  case AMObjType::SET:
    set = new HashSet(*(HashSet*)args[0].val.p);
    break;
  case AMObjType::ARRAY:
    {
      set = new HashSet;
      Array* array = (Array*)args[0].val.p;
      ArrayIter* pnext = array->iterator();
      ArrayIter& next = *pnext;

      while(next()) {

        *set += next.key();

      }

      delete pnext;
    }
    break;
  case AMObjType::LIST:
    {
      set = new HashSet;
      List* list = (List*)args[0].val.p;
      ListIter* pnext = list->iterator();
      ListIter& next = *pnext;

      int i = 0;
      AMObj first;

      while(next()) {

        if (i>0) {
          if (!(first && next.key())) {
            delete set;
            genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "ToSet", i+1, next.key().tag.string().data());
            return AMObj(AMObjType::ERROR);
          }
        }
        else {
          first = next.key();
        }

        *set += next.key();
        i++;

      }

      delete pnext;
    }
    break;
  default:
    assert(FALSE);
    break;
  }

  assert(set);

  return AMObj(AMObjType::SET, set);

}


static AMObj K_ToArray(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToArray", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY ||
              args[0].tag() ==AMObjType::LIST ||
              args[0].tag() ==AMObjType::SET ||
              args[0].tag() ==AMObjType::SEQUENCES ||
              args[0].tag() ==AMObjType::MARKOVIAN_SEQUENCES ||
              args[0].tag() ==AMObjType::VARIABLE_ORDER_MARKOV_DATA ||
              args[0].tag() ==AMObjType::SEMI_MARKOV_DATA ||
              args[0].tag() ==AMObjType::NONHOMOGENEOUS_MARKOV_DATA,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ToArray", args[0].tag.string().data(), "ARRAY or LIST or SET or SEQUENCES"));

  Array* array = 0;

  switch(args[0].tag()) {

  case AMObjType::ARRAY:
    array = new SLArray(*(SLArray*)args[0].val.p);
    break;
  case AMObjType::SET:
    {
      array = new SLArray;
      Set* set = (Set*)args[0].val.p;
      SetIter* pnext = set->iterator();
      SetIter& next = *pnext;

      while(next()) {

        *array += next.key();

      }

      delete pnext;
    }
    break;
  case AMObjType::LIST:
    {
      array = new SLArray;
      List* list = (List*)args[0].val.p;
      ListIter* pnext = list->iterator();
      ListIter& next = *pnext;

      int i = 0;
      AMObj first;

      while(next()) {

        if (i>0) {
          if (!(first && next.key())) {
            delete array;
            genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "ToArray", next.key().tag.string().data(), i+1);
            return AMObj(AMObjType::ERROR);
          }
        }
        else {
          first = next.key();
        }

        *array += next.key();
        i++;

      }

      delete pnext;
    }
    break;
  case AMObjType::SEQUENCES:
  case AMObjType::MARKOVIAN_SEQUENCES:
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA:
  case AMObjType::SEMI_MARKOV_DATA:
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA:
    {

      Sequences* seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;

      array = new SLArray;

      for(int i=0;i<seq->get_nb_sequence();i++) {

        Array* seq_array = new SLArray;

        for(int j=0;j<seq->get_length(i);j++) {

          Array* vect_array = new SLArray;

          for(int k=0;k<seq->get_nb_variable();k++) {

            *vect_array += AMObj(AMObjType::INTEGER,seq->get_int_sequence(i,k,j));

          }

          *seq_array += AMObj(AMObjType::ARRAY,vect_array);

        }

        *array += AMObj(AMObjType::ARRAY,seq_array);

      }

  }
    break;
  default:
    assert(FALSE);
    break;
  }

  assert(array);

  return AMObj(AMObjType::ARRAY, array);

}



static AMObj K_ToList(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ToList", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY ||
              args[0].tag() ==AMObjType::LIST ||
              args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ToList", args[0].tag.string().data(), "ARRAY or LIST or SET"));

  List* list = 0;

  switch(args[0].tag()) {

  case AMObjType::LIST:
    list = new SLList(*(SLList*)args[0].val.p);
    break;
  case AMObjType::SET:
    {
      list = new SLList;
      Set* set = (Set*)args[0].val.p;
      SetIter* pnext = set->iterator();
      SetIter& next = *pnext;

      while(next()) {

        *list += next.key();

      }

      delete pnext;
    }
    break;
  case AMObjType::ARRAY:
    {
      list = new SLList;
      Array* array = (Array*)args[0].val.p;
      ArrayIter* pnext = array->iterator();
      ArrayIter& next = *pnext;

      int i = 0;
      AMObj first;

      while(next()) {

        if (i>0) {
          if (!(first && next.key())) {
            delete list;
            genAMLError(ERRORMSG(K_C_ELEM_TYPE_ERR_sds), "ToList", i+1, next.key().tag.string().data());
            return AMObj(AMObjType::ERROR);
          }
        }
        else {
          first = next.key();
        }

        *list += next.key();
        i++;

      }

      delete pnext;
    }
    break;
  default:
    assert(FALSE);
    break;
  }

  assert(list);

  return AMObj(AMObjType::LIST, list);

}

// ------------------------
// Operators on Set types
// ------------------------

static AMObj K_Size(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Size"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY ||
              args[0].tag() ==AMObjType::SET ||
              args[0].tag() ==AMObjType::STRING ||
              args[0].tag() ==AMObjType::LIST,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Size", args[0].tag.string().data(), "ARRAY"));

  AMObj d(AMObjType::INTEGER);
  if (args[0].tag() ==AMObjType::ARRAY) d.val.i = ((Array*)args[0].val.p)->entries();
  else if (args[0].tag() == AMObjType::SET) d.val.i = ((Set*)args[0].val.p)->entries();
  else if (args[0].tag() == AMObjType::LIST) d.val.i = ((List*)args[0].val.p)->entries();
  else if (args[0].tag() == AMObjType::STRING) d.val.i = ((AMString*)args[0].val.p)->size();
  else assert(FALSE);

  return d;

}

static AMObj K_Sum(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Sum"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Sum", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL ||  stype ==AMObjType::CHAR,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Sum", stype.string().data(), "INT, REAL or CHAR"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      d.tag = AMObjType::INTEGER;

      while (next()) {

        d.val.i += next.key().val.i;

      }
    }
    else if (stype == AMObjType::CHAR) {

	  RWCString res;

      while (next()) {

        res += next.key().val.c;

      }
	  d = AMObj(AMObjType::STRING,new AMString(res.data()));

    }
    else{

      d.tag = AMObjType::REAL;

      while (next()) {

        d.val.r += next.key().val.r;

      }
    }

    delete pnext;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Sum", stype.string().data(), "INT or REAL"));


    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      d.tag = AMObjType::INTEGER;

      while (next()) {

        d.val.i += next.key().val.i;

      }
    }
    else {

      d.tag = AMObjType::REAL;

      while (next()) {

        d.val.r += next.key().val.r;

      }
    }

    delete pnext;

   }
  else assert(FALSE);

  return d;

}

static AMObj K_Prod(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Prod"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Prod", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Prod", stype.string().data(), "INT or REAL"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      d.tag = AMObjType::INTEGER;
      d.val.i = 1;

      while (next()) {

        if (next.key().tag == AMObjType::UNDEF) continue;

        d.val.i *= next.key().val.i;

        if (d.val.i == 0) break;

      }

    }
    else {

      d.tag = AMObjType::REAL;
      d.val.r = 1.0;

      while (next()) {

        if (next.key().tag == AMObjType::UNDEF) continue;

        d.val.r *= next.key().val.r;

        if (d.val.r == 0.0) break;

      }
    }

    delete pnext;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Prod", stype.string().data(), "INT or REAL"));


    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      d.tag = AMObjType::INTEGER;
      d.val.i = 1;

      while (next()) {

        if (next.key().tag == AMObjType::UNDEF) continue;

        d.val.i *= next.key().val.i;

        if (d.val.i == 0) break;

      }
    }
    else {

      d.tag = AMObjType::REAL;
      d.val.r = 1.0;

      while (next()) {

        if (next.key().tag == AMObjType::UNDEF) continue;

        d.val.r *= next.key().val.r;

        if (d.val.r == 0.0) break;

      }

    }

    delete pnext;

   }
  else assert(FALSE);

  return d;

}


static AMObj K_Max(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Max"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Max", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Max", stype.string().data(), "ARRAY(INT) or ARRAY(REAL)"));

    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      if (next()) {
        d.tag = AMObjType::INTEGER;
        d.val.i = next.key().val.i;
        while (next()) {
          if (d.val.i < next.key().val.i) d.val.i = next.key().val.i;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }
    else {

     if (next()) {
        d.tag = AMObjType::REAL;
        d.val.r = next.key().val.r;
        while (next()) {
          if (d.val.r < next.key().val.r) d.val.r = next.key().val.r;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }

    delete pnext;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Max", stype.string().data(), "SET(INT) or SET(REAL)"));

    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      if (next()) {
        d.tag = AMObjType::INTEGER;
        d.val.i = next.key().val.i;
        while (next()) {
          if (d.val.i < next.key().val.i) d.val.i = next.key().val.i;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }
    else {

     if (next()) {
        d.tag = AMObjType::REAL;
        d.val.r = next.key().val.r;
        while (next()) {
          if (d.val.r < next.key().val.r) d.val.r = next.key().val.r;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }

    delete pnext;

   }
  else assert(FALSE);

  return d;

}


static AMObj K_Min(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Min"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Min", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Min", stype.string().data(), "ARRAY(INT) or ARRAY(REAL)"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      if (next()) {
        d.tag = AMObjType::INTEGER;
        d.val.i = next.key().val.i;
        while (next()) {
          if (d.val.i > next.key().val.i) d.val.i = next.key().val.i;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }
    else {

     if (next()) {
        d.tag = AMObjType::REAL;
        d.val.r = next.key().val.r;
        while (next()) {
          if (d.val.r > next.key().val.r) d.val.r = next.key().val.r;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }

    delete pnext;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Min", stype.string().data(), "SET(INT) or SET(REAL)"));

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    if (stype == AMObjType::INTEGER) {

      if (next()) {
        d.tag = AMObjType::INTEGER;
        d.val.i = next.key().val.i;
        while (next()) {
          if (d.val.i > next.key().val.i) d.val.i = next.key().val.i;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }
    else {

     if (next()) {
        d.tag = AMObjType::REAL;
        d.val.r = next.key().val.r;
        while (next()) {
          if (d.val.r > next.key().val.r) d.val.r = next.key().val.r;
        }
      }
      else d.tag = AMObjType::UNDEF;

    }

    delete pnext;

   }
  else assert(FALSE);

  return d;

}


static AMObj K_Series(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Series"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Series", args[0].tag.string().data(), "ARRAY"));

  Array* series = new SLArray;
  AMObj sum;

  Array* array = (Array*)args[0].val.p;
  AMObjType stype = array->surfaceType();

  CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Series", stype.string().data(), "INT or REAL"));


  ArrayIter* pnext = array->iterator();
  ArrayIter& next = *pnext;

  if (stype == AMObjType::INTEGER) {

    sum.tag = AMObjType::INTEGER;

    while (next()) {

      sum.val.i += next.key().val.i;

      (*series) += sum;

    }
  }
  else {

    sum.tag = AMObjType::REAL;

    while (next()) {

      sum.val.r += next.key().val.r;

      (*series) += sum;

    }
  }

  delete pnext;



  return AMObj(AMObjType::ARRAY, series);

}

static AMObj K_ProdSeries(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "ProdSeries"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ProdSeries", args[0].tag.string().data(), "ARRAY"));

  Array* series = new SLArray;
  AMObj sum(AMObjType::INTEGER,1);

  Array* array = (Array*)args[0].val.p;
  AMObjType stype = array->surfaceType();

  CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ProdSeries", stype.string().data(), "INT or REAL"));


  ArrayIter* pnext = array->iterator();
  ArrayIter& next = *pnext;

  if (stype == AMObjType::INTEGER) {

    sum.tag = AMObjType::INTEGER;

    while (next()) {

      if (next.key().tag != AMObjType::UNDEF) {

        sum.val.i *= next.key().val.i;

      }

      (*series) += sum;

    }
  }
  else {

    sum.tag = AMObjType::REAL;

    while (next()) {

      if (next.key().tag == AMObjType::UNDEF) {

        sum.val.r *= next.key().val.r;

      }

      (*series) += sum;

    }
  }

  delete pnext;



  return AMObj(AMObjType::ARRAY, series);

}


static AMObj K_Mean(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Mean"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Sum", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Mean", stype.string().data(), "INT or REAL"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    double sum = 0;
    int nbel = array->entries();

    d.tag = AMObjType::REAL;
    d.val.r = 0;

    if (stype == AMObjType::INTEGER) {

      while (next()) {

        sum += (double) next.key().val.i;

      }

    }
    else {

      d.tag = AMObjType::REAL;

      while (next()) {

        sum += next.key().val.r;

      }

    }

    delete pnext;

    d.val.r = sum / nbel;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Sum", stype.string().data(), "INT or REAL"));


    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    d.tag = AMObjType::REAL;

    double sum = 0;
    int nbel = set->entries();

    if (stype == AMObjType::INTEGER) {

      while (next()) {

        sum += (double) next.key().val.i;

      }
    }
    else {

      while (next()) {

        sum += next.key().val.r;

      }
    }

    delete pnext;

    d.val.r = sum / nbel;

  }
  else assert(FALSE);

  return d;

}

static AMObj K_Var(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Var"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Var", args[0].tag.string().data(), "ARRAY or SET"));

  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    AMObjType stype = array->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Var", stype.string().data(), "INT or REAL"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    double sum = 0;
    double sum2 = 0;
    int nbel = array->entries();

    d.tag = AMObjType::REAL;
    d.val.r = 0;

    if (nbel == 1) return d;

    if (stype == AMObjType::INTEGER) {

      while (next()) {

        sum += (double) next.key().val.i;
        sum2 += (double) (next.key().val.i * next.key().val.i);

      }

    }
    else {

      while (next()) {

        sum += next.key().val.r;
        sum2 += (next.key().val.r * next.key().val.r);

      }

    }

    delete pnext;

    // double mean = sum/nbel;
    // d.val.r = sum2/nbel- mean*mean;
    d.val.r = (sum2-sum*sum/nbel)/nbel;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    AMObjType stype = set->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(stype ==AMObjType::INTEGER ||  stype ==AMObjType::REAL,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Var", stype.string().data(), "INT or REAL"));


    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;

    d.tag = AMObjType::REAL;

    double sum = 0;
    double sum2 = 0;
    int nbel = set->entries();

    if (stype == AMObjType::INTEGER) {

      while (next()) {

        sum += (double) next.key().val.i;
        sum2 += (double) (next.key().val.i * next.key().val.i);

      }
    }
    else {

      while (next()) {

        sum += next.key().val.r;
        sum2 += (next.key().val.r * next.key().val.r);

      }
    }

    delete pnext;

    // double mean = sum/nbel;
    // d.val.r = sum2/nbel-mean*mean;
    d.val.r = (sum2-sum*sum/nbel)/nbel;

  }
  else assert(FALSE);

  return d;

}

static AMObj K_Cov(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Cov",2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY || args[0].tag() ==AMObjType::SET,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Var", args[0].tag.string().data(), "ARRAY or SET"));

  CHECKCONDVA((args[0].tag() ==AMObjType::ARRAY ? args[1].tag() ==AMObjType::ARRAY : args[1].tag() ==AMObjType::SET),
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Cov", args[0].tag.string().data(), "ARRAY or SET"));
  AMObj d;

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array = (Array*)args[0].val.p;
    Array* array2 = (Array*)args[1].val.p;

    AMObjType stype = array->surfaceType();
    AMObjType stype2 = array2->surfaceType();

    if (!array->entries()) return AMObj(AMObjType::UNDEF);
    if (array->entries()!=array2->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA((stype ==AMObjType::INTEGER && stype2 ==AMObjType::INTEGER) ||
                (stype ==AMObjType::REAL && stype2 ==AMObjType::REAL),
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Cov", stype.string().data(), "INT or REAL"));


    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;
    ArrayIter* pnext2 = array2->iterator();
    ArrayIter& next2 = *pnext2;

    double sum = 0;
    double sum2 = 0;
    double sum3 = 0;
    int nbel = array->entries();

    d.tag = AMObjType::REAL;
    d.val.r = 0;

    if (nbel == 1) return d;

    if (stype == AMObjType::INTEGER) {

      while (next() && next2()) {
        sum += (double) next.key().val.i;
        sum2 += (double) next2.key().val.i;
        sum3 += (double) (next.key().val.i * next2.key().val.i);

      }

    }
    else {

      while (next() && next2()) {

        sum += next.key().val.r;
        sum2 += next2.key().val.r;
        sum3 += (next.key().val.r * next2.key().val.r);

      }

    }

    delete pnext;
    delete pnext2;

    //double mean = sum/nbel;
    //double mean2 = sum2/nbel;
    //d.val.r = sum3/nbel- mean*mean2;
    d.val.r = (sum3-sum*sum2/nbel)/nbel;

  }
  else if (args[0].tag() == AMObjType::SET) {

    Set* set = (Set*)args[0].val.p;
    Set* set2 = (Set*)args[1].val.p;
    AMObjType stype = set->surfaceType();
    AMObjType stype2 = set2->surfaceType();

    if (!set->entries()) return AMObj(AMObjType::UNDEF);
    if (set->entries()!=set2->entries()) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA((stype ==AMObjType::INTEGER && stype2 ==AMObjType::INTEGER) ||
                (stype ==AMObjType::REAL && stype2 ==AMObjType::REAL),
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Cov", stype.string().data(), "INT or REAL"));


    SetIter* pnext = set->iterator();
    SetIter& next = *pnext;
    SetIter* pnext2 = set2->iterator();
    SetIter& next2 = *pnext2;

    d.tag = AMObjType::REAL;

    double sum = 0;
    double sum2 = 0;
    double sum3 = 0;
    int nbel = set->entries();

    if (stype == AMObjType::INTEGER) {

      while (next() && next2()) {

        sum += (double) next.key().val.i;
        sum2 += (double) next2.key().val.i;
        sum3 += (double) (next.key().val.i * next2.key().val.i);

      }
    }
    else {

      while (next() && next2()) {

        sum += next.key().val.r;
        sum2 += next2.key().val.r;
        sum3 += (next.key().val.r * next2.key().val.r);

      }
    }

    delete pnext;
    delete pnext2;

    // double mean = sum/nbel;
    // double mean2 = sum2/nbel;
    // d.val.r = sum3/nbel-mean*mean2;
    d.val.r = (sum3-sum*sum2/nbel)/nbel;

  }
  else assert(FALSE);

  return d;

}

static AMObj K_SubArray(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "SubArray", "2 ou 3"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "SubArray", args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "SubArray", 2, args[1].tag.string().data(), "INT"));

  CHECKCONDVA(args[1].val.i != 0,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_ss), "SubArray", "arg2 != 0"));

  Array* suba = 0;

  if ( args.length() == 3) {

    if (args[2].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(args[1].val.i > 0,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_ss), "SubArray", "arg2 > 0"));

    CHECKCONDVA(args[2].tag() ==AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "SubArray", 3, args[2].tag.string().data(), "INT"));


    CHECKCONDVA(args[1].val.i <= args[2].val.i,
                genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_ss), "SubArray", "arg2 <= arg3"));

    Array* array = (Array*)args[0].val.p;
    suba = new SLArray;

    int inf = max(1,args[1].val.i);
    int sup = min(array->entries(),args[2].val.i);


    for(register int i=inf-1; i<= sup-1; i++) {

      (*suba) += array->at(i);

    }
  }
  else  { // ( args.length() == 2)

    Array* array = (Array*)args[0].val.p;
    suba = new SLArray;

    int k = args[1].val.i;
    int inf, sup;

    if (k>0) { // on prend les elements x1, x2, xk du tableau

      inf = 1;
      sup = min(array->entries(),k);

    }
    else { // k < 0 : on prend les elements xn-k+1, xn-k+2, xn-k+k du tableau

      k = min(array->entries(),-k);

      inf = array->entries()-k+1;
      sup = array->entries();

    }

    for(register int i=inf-1; i<= sup-1; i++) {

      (*suba) += array->at(i);

    }
  }

  assert(suba);

  return AMObj(AMObjType::ARRAY, suba);

}

static AMObj K_Flatten(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Flatten", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::SET || args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Flatten", 1, args[0].tag.string().data(), "SET or ARRAY"));

  if (args[0].tag() ==AMObjType::ARRAY) {

    Array* array1 = ((Array*)args[0].val.p);

    if (array1->surfaceType() == AMObjType::ARRAY) {

      Array* flattened = new SLArray;

      ArrayIter* pnext = array1->iterator();
      ArrayIter& next = *pnext;

      while(next()) {

        // assert(next.key().tag == AMObjType::ARRAY);

        if (next.key().tag != AMObjType::UNDEF)
          *flattened += ((Array*)(next.key().val.p));

      }

      delete pnext;

      return AMObj(AMObjType::ARRAY, flattened);

    }
    else if (array1->surfaceType() == AMObjType::SET) {

      Array* flattened = new SLArray;

      ArrayIter* pnext = array1->iterator();
      ArrayIter& next = *pnext;

      while(next()) {

        AMObjVector tmparg(1);
        tmparg[0] = next.key();
        AMObj ret  =  K_ToArray(tmparg);

        if (next.key().tag != AMObjType::UNDEF)
          *flattened += ((Array*)(ret.val.p));

      }

      delete pnext;

      return AMObj(AMObjType::ARRAY, flattened);

    }
    else return args[0];

  }
  else {

    if (args[0].tag() ==AMObjType::SET) {

      Set* set1 = ((Set*)args[0].val.p);

      if (set1->surfaceType() == AMObjType::SET) {

        Set* flattened = new HashSet;

        SetIter* pnext = set1->iterator();
        SetIter& next = *pnext;

        while(next()) {

          // assert(next.key().tag == AMObjType::SET);

          if (next.key().tag != AMObjType::UNDEF)
            *flattened += ((Set*)next.key().val.p);

        }

        delete pnext;

        return AMObj(AMObjType::SET, flattened);

      }
      else if (set1->surfaceType() == AMObjType::ARRAY) {

        Set* flattened = new HashSet;

        SetIter* pnext = set1->iterator();
        SetIter& next = *pnext;

        while(next()) {

          AMObjVector tmparg(1);
          tmparg[0] = next.key();
          AMObj ret  =  K_ToSet(tmparg);

          if (next.key().tag != AMObjType::UNDEF)
            *flattened += ((Set*)(ret.val.p));

        }

        delete pnext;

        return AMObj(AMObjType::SET, flattened);

      }
      else return args[0];

    }
  }
  return args[0];
}


static AMObj K_Filter(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Filter", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Filter", args[0].tag.string().data(), 1, "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Filter", args[1].tag.string().data(), 2, "ARRAY"));

  Array* array1 = ((Array*)args[0].val.p);
  Array* mask = ((Array*)args[1].val.p);

  CHECKCONDVA(array1->surfaceType() == AMObjType::INTEGER || array1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Filter", args[0].tag.string().data(), 1, "ARRAY(INT) or ARRAY(REAL)"));

  CHECKCONDVA(mask->surfaceType() == AMObjType::INTEGER || mask->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Filter", args[1].tag.string().data(), 2, "ARRAY(INT) or ARRAY(REAL)"));

  // Constructing a mask array of reals
  int mask_size = mask->entries();

  CHECKCONDVA(((mask_size+1)/2)*2 !=  mask_size,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Filter", 2, "an array with an odd number of elements"));

  double* m = new double[mask_size];

  for(register int i = 0; i < mask_size; i++) {

    if (mask->surfaceType() == AMObjType::INTEGER) m[i] = (double) mask->at(i).val.i;
    else m[i] = mask->at(i).val.r;

  }

  Array* filtered = new SLArray;

  ArrayIter* pnext = array1->iterator();
  ArrayIter& next = *pnext;

  register double val;

  int k = 0; // loop on elements of array1

  int size = array1->entries();

  int mc = mask_size/2; // mask center
  double masksum;

  while(next()) {

    val = 0;
    masksum = 0;


    int kmin = max(0, k-mc);
    int kmax = min(k+mc, size-1);

    for(int i=kmin;i<=kmax;i++) {
      if (array1->surfaceType() == AMObjType::INTEGER) val += array1->at(i).val.i*m[i-k+mc];
      else val += array1->at(i).val.r*m[i-k+mc];
      masksum += m[i-k+mc];
    }

    if (masksum != 0.0) val /= masksum;

    (*filtered) += AMObj(AMObjType::REAL,val);

    k++;

  }

  delete pnext;

  delete [] m;

  return AMObj(AMObjType::ARRAY, filtered);

}


static AMObj K_EDist(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "VDist", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VDist", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VDist", 2, args[1].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  Array* vec2 = (Array*) args[1].val.p;

  register double dist = -1;

  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "EDist", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));
  CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "EDist", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();
  CHECKCONDVA(dim == vec2->entries(),
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "EDist", 2,"an array of identical dimension"));

  double v1;
  double v2;

  dist = 0;
  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;
    v2 = vec2->at(i).val.r;

    dist += (v1-v2)*(v1-v2);
  }

  dist = sqrt(dist);

  return AMObj(AMObjType::REAL, dist);

}


static AMObj K_SProd(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SProd", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SProd", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SProd", 2, args[1].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  Array* vec2 = (Array*) args[1].val.p;

  register double sprod = -1;

  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SProd", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));
  CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "SProd", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();
  CHECKCONDVA(dim == vec2->entries(),
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "SProd", 2,"an array of identical dimension"));

  register double v1;
  register double v2;

  sprod = 0;
  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;
    v2 = vec2->at(i).val.r;

    sprod += v1*v2;
  }

  return AMObj(AMObjType::REAL, sprod);

}

static AMObj K_VPlus(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Plus", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Plus", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Plus", 2, args[1].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  Array* vec2 = (Array*) args[1].val.p;


  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Plus", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));
  CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Plus", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();
  CHECKCONDVA(dim == vec2->entries(),
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Plus", 2,"an array of identical dimension"));

  Array* vsum = new SLArray;

  register double v1;
  register double v2;

  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;
    v2 = vec2->at(i).val.r;

    (*vsum) += AMObj(AMObjType::REAL,v1+v2);
  }

  return AMObj(AMObjType::ARRAY, vsum);

}

static AMObj K_VMinus(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1 || len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "Minus", "1 or 2"));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Minus", 1, args[0].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  int dim = vec1->entries();

  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Minus", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));


  if (len == 1) {

    Array* vminus = new SLArray;

    register double v1;

    for (register int i = 0; i < dim; i++) {
      v1 = vec1->at(i).val.r;

      (*vminus) += AMObj(AMObjType::REAL,-v1);
    }

    return AMObj(AMObjType::ARRAY, vminus);

  }
  else {

    CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Minus", 2, args[1].tag.string().data(), "ARRAY"));

    Array* vec2 = (Array*) args[1].val.p;

    CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
                genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Plus", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

    CHECKCONDVA(dim == vec2->entries(),
                genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Plus", 2,"an array of identical dimension"));

    Array* vminus = new SLArray;

    register double v1;
    register double v2;

    for (register int i = 0; i < dim; i++) {
      v1 = vec1->at(i).val.r;
      v2 = vec2->at(i).val.r;

      (*vminus) += AMObj(AMObjType::REAL,v1-v2);

    }

    return AMObj(AMObjType::ARRAY, vminus);

  }

}


static AMObj K_VTimes(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Times", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Times", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Times", 2, args[1].tag.string().data(), "REAL"));

  Array* vec1 = (Array*) args[0].val.p;
  double lambda = args[1].val.r;


  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Times", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();

  Array* vsum = new SLArray;

  register double v1;

  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;

    (*vsum) += AMObj(AMObjType::REAL,v1*lambda);
  }

  return AMObj(AMObjType::ARRAY, vsum);

}


static AMObj K_Norm(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Norm", 1));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Norm", 1, args[0].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;

  register double norm = -1;

  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Norm", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();

  register double v1;

  norm = 0;
  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;

    norm += v1*v1;
  }

  norm = sqrt(norm);

  return AMObj(AMObjType::REAL, norm);

}


static AMObj K_Angle(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "VAngle", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Angle", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Angle", 2, args[1].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  Array* vec2 = (Array*) args[1].val.p;

  register double sprod = -1;

  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Angle", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));
  CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Angle", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();
  CHECKCONDVA(dim == vec2->entries(),
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Angle", 2,"an array of identical dimension"));

  register double v1;
  register double v2;

  register double n1 = 0;
  register double n2 = 0;

  sprod = 0;
  for (register int i = 0; i < dim; i++) {
    v1 = vec1->at(i).val.r;
    v2 = vec2->at(i).val.r;

    sprod += v1*v2;

    n1 += v1*v1;
    n2 += v2*v2;

  }

  if (n1 != 0 && n2 != 0) {

    n1 = sqrt(n1);
    n2 = sqrt(n2);

    sprod = sprod/(n1*n2); // cosa

    sprod = acos(sprod);

  }
  else return AMObj(AMObjType::UNDEF);

  return AMObj(AMObjType::REAL, sprod);

}



static AMObj K_VProd(const AMObjVector& args) {

  int len = args.length();

  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "VProd", 2));

  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VProd", 1, args[0].tag.string().data(), "ARRAY"));
  CHECKCONDVA(args[1].tag() ==AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VProd", 2, args[1].tag.string().data(), "ARRAY"));

  Array* vec1 = (Array*) args[0].val.p;
  Array* vec2 = (Array*) args[1].val.p;


  CHECKCONDVA(vec1->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VProd", 1, vec1->surfaceType().string().data(), "ARRAY(REAL)"));
  CHECKCONDVA(vec2->surfaceType() == AMObjType::REAL,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "VProd", 1, vec2->surfaceType().string().data(), "ARRAY(REAL)"));

  int dim = vec1->entries();
  CHECKCONDVA(dim == 3,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "VProd", 1,"an array of dimension 3"));
  CHECKCONDVA(dim == vec2->entries(),
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "VProd", 2,"an array of identical dimension"));

  register double v1;
  register double v2;
  register double v3;

  double a1 = vec1->at(0).val.r;
  double a2 = vec1->at(1).val.r;
  double a3 = vec1->at(2).val.r;

  double b1 = vec2->at(0).val.r;
  double b2 = vec2->at(1).val.r;
  double b3 = vec2->at(2).val.r;


  Array* vprod = new SLArray;

  v1 = a2*b3-a3*b2;
  v2 = - (a1*b3-a3*b1);
  v3 = a1*b2-a2*b3;

  (*vprod) += AMObj(AMObjType::REAL,v1);
  (*vprod) += AMObj(AMObjType::REAL,v2);
  (*vprod) += AMObj(AMObjType::REAL,v3);


  return AMObj(AMObjType::ARRAY, vprod);

}


static AMObj K_Assignment(const AMObjVector& args) {

  assert(args.length() == 2);
  assert(args[0].tag == AMObjType::STRING);

  if (args[1].tag == AMObjType::ERROR) return AMObj(AMObjType::ERROR);

  RWCString str(*(AMString*)(args[0].val.p));

  AMObj* variable = amobjTable()->insert(str, args[1]); // cast of an FAMObj in an AMObj

  return AMObj(*variable);

}

static AMObj K_IfThenElse(const AMObjVector& args) {

  assert(args.length() == 3);
  // assert(args[0].tag == AMObjType::BOOL);

  //  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag ==AMObjType::INTEGER ||  args[0].tag ==AMObjType::REAL ||  args[0].tag ==AMObjType::BOOL,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "IfThenElse", args[0].tag.string().data(), "INT, REAL or BOOL"));

  int test;

  switch(args[0].tag()) {

  case AMObjType::INTEGER:
  case AMObjType::BOOL:
    test = args[0].val.i;
    break;

  case AMObjType::REAL:
    test = (args[0].val.r != 0.0);
    break;

  }

  if (test) return args[1];
  else return args[2];

}

static AMObj K_Switch(const AMObjVector& args) {

  int len = args.length();

  assert(len >=2 && len%2 == 0);
  // assert(args[0].tag == AMObjType::BOOL);

  //  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  for (register int i = 0; i<(len-2)/2; i++) {

    if (args[0] == args[1+i*2]) return args[(i+1)*2];

  }

  return args[len-1]; // Default value

}

static AMObj K_Include(const AMObjVector& args) {
  CHECKCONDVA(args.length() >= 1 && (args.length() %2 != 0),
             genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Include", 1));

  CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_OP_ARG_TYPE_ERR_sdss), "Include", 1, args[0].tag.string().data(), "STRING"));

  return AMObj(AMObjType::BOOL,pushInclude(args));
}


// ----------------------------------
// Initialization of system functions
// ----------------------------------

void installFNode(const char* name, PFUN fun, int argnb, AMObjType* type, AMObjType rettype) {

  assert(name);
  RWCString item_name(name);

  /// For win32, we can't do new AMObj[0] and destroy it after.
  AMObj* args = NULL;
  if(argnb > 0)
  args = new AMObj[argnb];
  // else args = new AMObj[1];

  for (register int i=0; i<argnb; i++) {
    args[i].tag = type[i];
    args[i].val.i = 0;
  }

  item_name.prepend(SYSTEMCHAR);

  AMObj evft(AMObjType::FNODE,new FNode(item_name, fun, argnb, args, rettype));

  amobjTable()->insert(item_name, evft);

}

void installKERNELModule() {

  AMObjType type[10]; // max number of arguments
  AMObj var;
  RWCString varname;

  var = AMObj(AMObjType::UNDEF);
  varname = ":Undef";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::WINDOW, new GP_window);
  varname = ":DefaultWindow";
  amobjTable()->insert(varname, var);

  varname = ":CurrentWindow";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::UNDEF);
  varname = ":CurrentPlottedObj";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::BOOL,1);
  varname = ":True";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::BOOL,0);
  varname = ":False";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::REAL,M_PI);
  varname = ":Pi";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,0);
  varname = ":Black";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,1);
  varname = ":White";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,2);
  varname = ":Green";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,3);
  varname = ":Red";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,4);
  varname = ":Blue";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,5);
  varname = ":Yellow";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,6);
  varname = ":Violet";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,7);
  varname = ":LightBlue";
  amobjTable()->insert(varname, var);

  // Arithmetic Operators

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("+", K_PLUS, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("-", K_MINUS, 2, type, AMObjType::ANY);

  type[0] = AMObjType::INTEGER;
  installFNode("Unary-", K_UNARYMINUS, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::INTEGER;
  type[1] = AMObjType::INTEGER;
  installFNode("*", K_TIMES, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::INTEGER;
  type[1] = AMObjType::INTEGER;
  installFNode("/", K_DIVIDED, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::INTEGER;
  type[1] = AMObjType::INTEGER;
  installFNode("Mod", K_MOD, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("^", K_POWER, 2, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Exp", K_Exp, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Sqrt", K_Sqrt, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Log", K_Log, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Log10", K_Log10, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Cos", K_Cos, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Sin", K_Sin, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Tan", K_Tan, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Acos", K_Acos, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Asin", K_Asin, 1, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("Atan", K_Atan, 1, type, AMObjType::REAL);

  // Boolean Operators

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("==", K_EQ, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("!=", K_DIFF, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("<=", K_LTEQ, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("<", K_LT, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode(">=", K_GTEQ, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode(">", K_GT, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("And", K_AND, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Or", K_OR, 2, type, AMObjType::BOOL);

/*
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("In", K_IN, 2, type, AMObjType::BOOL);
*/
  type[0] = AMObjType::ANY;
  installFNode("Not", K_NOT, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::BOOL;
  installFNode("Select", K_Select, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Interval", K_Interval, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::ANY;
  installFNode("Abs", K_Abs, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Floor", K_Floor, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Ceil", K_Ceil, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Rint", K_Rint, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Truncate", K_Truncate, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("ToInt", K_ToInt, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("ToReal", K_ToReal, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("ToString", K_ToString, 1, type, AMObjType::ANY);
  type[0] = AMObjType::STRING;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("SubString", K_SubString, 3, type, AMObjType::STRING);
  type[1] = AMObjType::ANY;
  type[2] = AMObjType::ANY;

  // Dates

  var = AMObj(AMObjType::INTEGER,1);
  varname = ":Second";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,60);
  varname = ":Minute";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER,3600);
  varname = ":Hour";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER, 24*3600);
  varname = ":Day";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::INTEGER, 24*3600);
  varname = ":DateUnit";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::STRING, new AMString("DDMMYY"));
  varname = ":DateFormat";
  amobjTable()->insert(varname, var);

  type[0] = AMObjType::ANY;
  installFNode("Date", K_Date, 1, type, AMObjType::ANY);

  type[0] = AMObjType::INTEGER;
  installFNode("ToTimeUnit", K_ToTimeUnit, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::ANY;
  installFNode("TimerStart", K_TimerStart, 1, type, AMObjType::ANY);
  installFNode("TimerElapsed", K_TimerElapsed, 1, type, AMObjType::REAL);
  installFNode("TimerStop", K_TimerStop, 1, type, AMObjType::REAL);

  // Set type constructor

  installFNode("Set", K_Set, 0, type, AMObjType::SET);
  installFNode("List", K_List, 0, type, AMObjType::LIST);
  installFNode("[]", K_ArrayBracket, 0, type, AMObjType::ARRAY);
  installFNode("Array", K_Array, 0, type, AMObjType::ARRAY);

  type[0] = AMObjType::INTEGER;
  installFNode("Sort", K_Sort, 1, type, AMObjType::ARRAY);

  // casts
  installFNode("ToSet", K_ToSet, 0, type, AMObjType::SET);
  installFNode("ToList", K_ToList, 0, type, AMObjType::LIST);
  installFNode("ToArray", K_ToArray, 0, type, AMObjType::LIST);

  // Operation on arrays and lists

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("@", K_At, 2, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode(";", K_ExpSequence, 2, type, AMObjType::ANY);
  installFNode("ExpSequence", K_ExpSequence, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  type[2] = AMObjType::INTEGER;
  installFNode("InsertAt", K_InsertAt, 3, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("Append", K_PLUS, 2, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("Remove", K_MINUS, 2, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("RemoveAt", K_RemoveAt, 2, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Invert", K_Invert, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Head", K_Head, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Tail", K_Tail, 1, type, AMObjType::ARRAY);
  type[0] = AMObjType::ANY;
  installFNode("Pos", K_Pos, 1, type, AMObjType::INTEGER);
  type[0] = AMObjType::ANY;
  installFNode("AllPos", K_AllPos, 1, type, AMObjType::ARRAY);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("SubArray", K_SubArray, 3, type, AMObjType::ARRAY);

  // Operators on Set types

  type[0] = AMObjType::ANY;
  installFNode("Size", K_Size, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::ANY;
  installFNode("Sum", K_Sum, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Prod", K_Prod, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Max", K_Max, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Min", K_Min, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;

  // new
  installFNode("Mean", K_Mean, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Var", K_Var, 1, type, AMObjType::ANY);
  installFNode("Cov", K_Cov, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  installFNode("Series", K_Series, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("ProdSeries", K_ProdSeries, 1, type, AMObjType::ANY);
  type[0] = AMObjType::ANY;
  installFNode("Flatten", K_Flatten, 1, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("|", K_Union, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Union", K_Union, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("&", K_Inter, 2, type, AMObjType::SET);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Inter", K_Inter, 2, type, AMObjType::SET);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("SetMinus", K_SetMinus, 2, type, AMObjType::SET);

  // General functions

  type[0] = AMObjType::ANY;
  installFNode("Display", K_Display, 1, type, AMObjType::VOID);


  type[0] = AMObjType::ANY;
  installFNode("Plot", K_Plot, 1, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("NewPlot", K_NewPlot, 1, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("Echo", K_Echo, 1, type, AMObjType::VOID);
  type[0] = AMObjType::ANY;
  installFNode("Print", K_Print, 1, type, AMObjType::VOID);
  type[0] = AMObjType::ANY;
  installFNode("Save", K_Save, 1, type, AMObjType::VOID);
  type[0] = AMObjType::STRING;
  installFNode("Include", K_Include, 1, type, AMObjType::BOOL);

  installFNode("Extract", K_Extract, 1, type, AMObjType::VOID);
  type[0] = AMObjType::ANY;

  type[0] = AMObjType::ANY;
  installFNode("?name", K_DisplayName, 1, type, AMObjType::VOID);

  installFNode("?user", K_DisplayAllUserNames, 0, type, AMObjType::VOID);
  installFNode("?all", K_DisplayAllNames, 0, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("Identity", K_Identity, 1, type, AMObjType::ANY);


  type[0] = AMObjType::INTEGER;
  type[1] = AMObjType::INTEGER;
  installFNode("Rand", K_Rand, 2, type, AMObjType::ANY);


  installFNode("EchoOn", K_EchoOn, 0, type, AMObjType::VOID);

  installFNode("EchoOff", K_EchoOff, 0, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("Delete", K_Delete, 1, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("=", K_Assignment, 2, type, AMObjType::ANY);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Filter", K_Filter, 2, type, AMObjType::ANY);

  // Operations on vectors

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("EDist", K_EDist, 2, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Norm", K_Norm, 2, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Angle", K_Angle, 2, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("VProd", K_VProd, 2, type, AMObjType::REAL);

  type[0] = AMObjType::ANY;
  installFNode("SProd", K_SProd, 2, type, AMObjType::REAL);

  // new
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Plus", K_VPlus, 2, type, AMObjType::ARRAY);
  installFNode("Times", K_VTimes, 2, type, AMObjType::ARRAY);
  installFNode("Minus", K_VMinus, 1, type, AMObjType::ARRAY);


  // Control operators

  type[0] = AMObjType::BOOL;
  type[1] = AMObjType::ANY;
  type[2] = AMObjType::ANY;
  installFNode("IfThenElse", K_IfThenElse, 3, type, AMObjType::ANY);


  type[0] = AMObjType::ANY;
  installFNode("Switch", K_Switch, 0, type, AMObjType::ANY);

  // Iterators

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Foreach", 0, 2, type, AMObjType::ANY);

}
