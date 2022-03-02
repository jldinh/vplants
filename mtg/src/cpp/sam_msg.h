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
 *       $Id: sam_msg.h 3258 2007-06-06 13:18:26Z dufourko $
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





#ifndef _SAM_MSG_DEF_
#define _SAM_MSG_DEF_


#include "tool/rw_cstring.h"
//#include <rw/cstring.h>

// Ce fichier contient les differents messages affiches dans l'application.
// Les messages relatifs au dressing files sont definis dans
// le fichier dressingfile.C


#define NB_SAM_MSG 24

const RWCString APPL_MSG[NB_SAM_MSG] = {

RWCString("ERROR : Cannot execute Glance."),
RWCString("ERROR : Cannot fork Glance. See number of process."),
RWCString("ERROR : Cannot plot a nonvalid PlantFrame object."),
RWCString("ERROR : No reference system."),
RWCString("WARNING : No way to find or compute the origin. It should be specified at a lower level."),

RWCString("WARNING : If a branch is not supported by a segment with top and bottom coordinates\n You must give its origin. Otherwise, an approximation of the origin will be taken."),
RWCString("Standard PlantFrame"),
RWCString("ERROR : Cannot create a standard PlantFrame : Bad geometry informations."),
RWCString( "Plant with triangular reference system coordinates. "),
RWCString( "ERROR : Cannot create a PlantFrame with triangular reference system coordinates. Bad geometry informations."),

RWCString("Plant with cartesian reference system coordinates. "),
RWCString( "ERROR : Cannot create a PlantFrame with cartesian reference system coordinates. Bad geometry informations."),
RWCString("ERROR : PlantFrame arguments not valid."),
RWCString("Default dressing data used."),
RWCString ("Dressing data read from file  `"),

RWCString (" ERROR : Default dressing data. Cannot read file `"),
RWCString ("WARNING : Unknown Mode. Try : "),
RWCString ("Sympodial    : Treat the MTG as a sympodial plant."),
RWCString ("Standard     : Use standard MTG's treatment methods whatever the kind of available informations (e.g. do not consider geometric coordinates)."),
RWCString ("SympStandard : Combine the two modes."),
RWCString ("WARNING : The same index is used twice in the same axis."),
RWCString ("WARNING : The index have to be in an increasing order."),
RWCString ("ERROR : No coordinates computed for the vertex  "),
RWCString ("ERROR : Cannot create linetree file.")
};

#define GLANCE_MSG 0
#define GLANCE_MSG2 1
#define PLOT_MSG 2
#define REFERENCE_MSG 3
#define ORIGIN_MSG1 4
#define ORIGIN_MSG2 5
#define STANDARD_PF_MSG 6
#define STANDARD_PFERR_MSG 7
#define TRIANGULAR_MSG 8
#define TRIANGULAR_ERR_MSG 9
#define CARTESIAN_MSG 10
#define CARTESIAN_ERR_MSG 11
#define PF_CONSTRUCTOR_ERR_MSG 12
#define DEFAULT_DRD_MSG 13
#define DRD_FILE_MSG 14
#define DRD_ERR_MSG 15
#define MODE_ERR_MSG 16
#define MODE_SYMP_MSG 17
#define MODE_STAND_MSG 18
#define ALL_MODES_MSG 19
#define INDEX_WARNING 20
#define INDEX_WARNING2 21
#define COORD_ERR 22
#define LINE_ERR 23

#endif

