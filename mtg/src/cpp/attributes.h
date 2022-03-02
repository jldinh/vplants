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
 *       $Id: attributes.h 3258 2007-06-06 13:18:26Z dufourko $
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





#ifndef _ATTRIBUTES_SAMIR_DEF_
#define _ATTRIBUTES_SAMIR_DEF_

// Definition des noms des attributs utilises dans le code.


// Attributs contenant les coordonnees dans un systeme de reference triangulaire.

const char TR_X[]="L1";
const char TR_Y[]="L2";
const char TR_Z[]="L3";

// Distances entre les sommets

const char TR_DAB[]="DAB"; // Distance entre les sommets A et B.
const char TR_DAC[]="DAC"; // Distance entre les sommets A et C.
const char TR_DBC[]="DBC"; // Distance entre les sommets B et C.

// Attributs contenant les coordonnees dans un systeme de reference cartesien.

const char CA_X[]="XX";
const char CA_Y[]="YY";
const char CA_Z[]="ZZ";

// Attributs contenant des mesures.

const char ATT_LENGTH[]="Length";
const char ATT_AZIMUT[]="Azimut";
const char ATT_ALPHA[]="Alpha";
const char ATT_TETA[]="AA";
const char ATT_PHI[]="BB";
const char ATT_PSI[]="CC";
const char ATT_TOPDIA[]="TopDia";
const char ATT_BOTTOMDIA[]="BotDia";
const char ATT_POSITION[]="Position";
const char ATT_CATEGORY[]="Category";


#endif
