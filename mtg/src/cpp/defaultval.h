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
 *       $Id: defaultval.h 3258 2007-06-06 13:18:26Z dufourko $
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





#ifndef _DEFAULT_VAL_SAMIR_DEF_
#define _DEFAULT_VAL_SAMIR_DEF_

#include "definitions.h"
#include "symbol.h"

#define  DEFAULT_SYMBOL_PATH ""
#define  DEFAULT_DIAMETERS_UNIT 1
#define  DEFAULT_LENGTH_UNIT 1
#define  DEFAULT_MIN_LENGTH 10
#define  DEFAULT_MIN_TOPDIA 1
#define  DEFAULT_MIN_BOTDIA 1
#define  DEFAULT_EDGE NONE
#define  DEFAULT_ALPHA 30
#define  DEFAULT_TETA 0
#define  DEFAULT_PHI 0
#define  DEFAULT_PSI 0
#define  DEFAULT_CATEGORY -1
#define  AXE_DEFAULT_CATEGORY -1  /* default category for the trunk */
#define  DEFAULT_AZIMUT 180
#define  MAX_TRESHOLD_GREEN 0
#define  MIN_TRESHOLD_GREEN 1
#define  MEDIUM_TRESHOLD_GREEN 0.05
#define  MAX_TRESHOLD_BLUE 1
#define  MIN_TRESHOLD_BLUE 0
#define  MEDIUM_TRESHOLD_BLUE 0.01
#define  MAX_TRESHOLD_RED 1
#define  MIN_TRESHOLD_RED 0
#define  MEDIUM_TRESHOLD_RED 0.07
#define  DELTA_INDEX 10
#define  ELEMENT_LENGTH 10
#define  DEFAULT_DISTANCE 100
#define  DEFAULT_AZIMUTUNIT 180/M_PI
#define  DEFAULT_ALPHAUNIT 180/M_PI
#define  DEFAULT_TETAUNIT 180/M_PI
#define  DEFAULT_PHIUNIT 180/M_PI
#define  DEFAULT_PSIUNIT 180/M_PI
#define  DEFAULT_NBPLINE 10

#define  DEFAULT_LEAF_SYMBOL 'L'
#define  DEFAULT_FLOWER_SYMBOL 'f'
#define  DEFAULT_FRUIT_SYMBOL 'F'

#define  DEFAULT_VERTICILLE 2

#define  DEFAULT_LEAF_LENGTH 1
#define  DEFAULT_LEAF_TOPDIA 1
#define  DEFAULT_LEAF_BOTTOMDIA 1
#define  DEFAULT_LEAF_ALPHA 30
#define  DEFAULT_LEAF_BETA 0

#define  DEFAULT_FRUIT_LENGTH 1
#define  DEFAULT_FRUIT_TOPDIA 1
#define  DEFAULT_FRUIT_BOTTOMDIA 1
#define  DEFAULT_FRUIT_ALPHA 30
#define  DEFAULT_FRUIT_BETA 0

#define  DEFAULT_FLOWER_LENGTH 1
#define  DEFAULT_FLOWER_TOPDIA 1
#define  DEFAULT_FLOWER_BOTTOMDIA 1
#define  DEFAULT_FLOWER_ALPHA 30
#define  DEFAULT_FLOWER_BETA 0


#endif
