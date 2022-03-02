#ifndef CPL
#define CPL
#endif
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
 *       $Id: defs.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef DEF_HEADER
#define DEF_HEADER

#include <iostream>
#ifndef SYSTEM_IS__IRIX
#include <limits.h>
#include <float.h>
#define MAXINT INT_MAX
#else
#include  <values.h>
#endif

#ifndef CPL

#include "bitvec.h"

#else

#ifndef AmlBoolean
#define AmlBoolean int
#endif

#endif

const int MAXSTRINGSIZE = 15;

typedef char CString[MAXSTRINGSIZE]; // String definie comme en C.

// Definition de synonymes:

typedef int IDENTIFIER;  // identificateur entier d'un element de tableau
                         // Normalement on devrait avoir: typedef size_t IDENTIFIER;
                         // Optim: On pourrait mettre 'short' pour gagner un peu et unsigned
typedef IDENTIFIER VId;
typedef IDENTIFIER EId;
typedef IDENTIFIER FId;
typedef IDENTIFIER FSetId;
typedef int VClass;

typedef enum {FORM_A, FORM_B} MTGCode ;

typedef enum {
  ALPHA, INTEGER, REAL,
  DDMM, DDMMYY, MMYY, DDMMTIME, DDMMYYTIME,
  GEOMETRY,
  APPEARANCE,
  GENERIC
} FType;

typedef enum {FREE_D = 0, LESSLINEAR, PLUSLINEAR, LINEAR, LESSPURELINEAR, PLUSPURELINEAR, PURELINEAR, CONNECTED, NOTCONNECTED, NONE_D} DecompType;
typedef enum {FREE_I = 0, CONSECUTIVE} IndexType;
typedef enum {EXPLICIT, IMPLICIT} VDefType;


#ifndef CPL
typedef BitVec EType;

const EType PLUS(0);
const EType LESS(1);
const EType SLASH(2);
const EType PLUSPLUS(3);
const EType LESSLESS(4);
const EType LESSDOTLESS(5);
const EType PLUSDOTPLUS(6);
const EType NONE;
const EType ANY(~NONE);
const EType ANYTOPO(PLUS | LESS | PLUSPLUS | LESSLESS);
const EType ANYLESS(LESS | LESSLESS);
const EType ANYPLUS(PLUS | PLUSPLUS);
#endif

const int MAXCLASSNB = 50;
const int MAXFEATURENB = 50;

typedef int FIndex; // index d'une feature dans un ensemble de features

typedef unsigned long Date;
typedef unsigned long IVal;
typedef float RVal;
typedef CString SVal;
typedef void* PVal;

typedef union _Feature {

  IVal i;
  RVal r;
  SVal s; // une union ne peut pas contenir un type ayant un constructeur
  PVal p;

  int unionLength() const {return sizeof(_Feature);}

  /*
  Feature& operator=(const Feature& rec) {
    if (this != &rec) {
      bcopy((void*)&(rec.i), (void*)&i, unionLength());
    }
    return *this;
  }
  */

  AmlBoolean operator==(const _Feature& f) const {return i == f.i;}

} Feature;

const int ROOT          = 0;
const int UNDEF         = -1;
const int CHECKERROR    = -2;

// use of cast such as
// long val1;
// unsigned long val2 = (unsigned long) LUNDEF;
// val1 = ...;
// if (val1 == val2) may be implementation dependent: be careful !!!!
// idem for UNDEF

const long LUNDEF       = (long)-1;

const int FILEMAXERROR  = 10;
const int MAXLINELENGTH = 10000; // max length of a line of the parsed file


#ifndef FALSE
const int FALSE = 0;
const int TRUE = !FALSE;
#endif

#endif
