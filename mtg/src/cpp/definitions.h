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
 *       $Id: definitions.h 3263 2007-06-06 14:07:06Z dufourko $
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





#ifndef SAMIR_DEFINTIONS_DEF
#define SAMIR_DEFINTIONS_DEF

#include <math.h>
#include <limits.h>
#ifdef SYSTEM_IS__IRIX
#include <values.h>
#else
#include <float.h>
#define MINFLOAT FLT_MIN
#ifndef MAXFLOAT 
#define MAXFLOAT FLT_MAX
#endif
#endif

#include "mtg.h"

// Definitions of basics types

// Si l'on change le type ValType il faut modifier en consequence
// les fonctions definies a la fin du fichier. 


#define FLOAT_TYPE

typedef float ValType;
typedef long SymbType;
typedef int IntType;
typedef long LongType;
typedef int BranchIndex;

enum CoordsType { TRIANGULAR, CARTESIAN };
enum Options { SYMPODIAL, NORMAL };

const ValType VAL_ERROR= INT_MIN; // AML2: previously: -9999999999;
const IntType INT_ERROR=-1;

const char PROTECT_FILE_NAME[]="amapmod";
const char DEFAULT_DRESSING_FILE_NAME[]=".drf";

#ifndef MAX
#define MAX( x,y ) ((x)>(y) ? (x):(y))
#endif

#ifndef MIN
#define MIN( x,y ) ((x)<(y) ? (x):(y))
#endif


const ValType MAX_VALTYPE=MAXFLOAT;
const ValType MIN_VALTYPE=MINFLOAT;


// const ValType MAX_VALTYPE=MAXDOUBLE;
// const ValType MIN_VALTYPE=MINDOUBLE;

// Noms des modes de representation.

const char SYM_MODE[]="Sympodial"; // For sympodial trees.
const char STAND_MODE[]="Standard"; // use standards methods. No matter the kind of information available.
const char SYMPSTAND_MODE[]="SympStandard"; //Sympodial and standard tree
const char NONE_MODE[]=""; // a void string as a mode.



// Define sin and cos functions with float ValType

extern float MySqrt(float);
extern float MySin(float);
extern float MyCos(float);
extern float MyAcos(float);
extern float MyAsin(float);
extern ValType MyAbs(float);


#endif
