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
 *       $Id: errormsgs.h 3258 2007-06-06 13:18:26Z dufourko $
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




#ifndef ERRORMSGS_HEADER
#define ERRORMSGS_HEADER

extern const char* err_messages[];
extern const char* err_types[];

typedef enum  {

  // ClassDefinition

  CODEFORMSTX_0 = 0,
  CLASSDEFSTX1_0,
  CLASSDEFSTX2_0,
  CLASSLISTSTX_0,
  SCALEORDER_0,
  CLASSDEFUNICITY_0,
  FORMBCOND1_0,

  // ClassDescription

  CLASSDESCSTX1_0,
  CLASSDESCSTX2_0,
  CLASSDESCLISTSTX_0,
  CLASSNOTDEFINED_0,
  CLASSDESCUNICITY_1,
  TOPOLINKSCALE_0,
  FORMBCOND2_0,

  // FeatureDefinition

  FEATUREDEFSTX1_0,
  FEATUREDEFSTX2_0,
  FEATUREDEFLISTSTX_0,
  NOTYPEFORPREDFEAT_0,
  FEATURENAMEUNICITY_0,
  PREDFEATORDERING_0,
  ALIASDEFINEDFIRST_0,

  // MTG description
  // 1. header syntax

  MTGSTX1_0,
  MTGSTX2_0,
  MTGLISTSTX_0,
  ATTRNAME1_0,
  ATTRNAME2_0,
  FEATNBDIFF_0,

  // 2. Outset

  IDENTERR1_0,
  IDENTERR2_0,
  IDENTERR3_0,
  ALIASDONOTEXIST_0,
  ALIASSTRING_0,
  MISSINGALIASPARENTH_0,
  NOTACODESTART_0,

  // 3.1. Entity-Code (general)

  CLASSERR_0,
  INDEXERR_0,
  INDEXMISSING_0,
  RELATIONNOTVALID_0,
  ENTITYCODEERR_0,
  IMPLICITERR_0,

  // 3.2. Code (logic)

  ALREADYDEFINED_1,
  A1FAILED_0,
  A1_1FAILED_1,
  A2FAILED_0,
  A3FAILED_0,
  A4FAILED_0,
  A5FAILED_0,
  A6FAILED_0,
  A7FAILED_0,
  LOCERR1_0,
  LOCERR2_0,
  LOCERR3_0,
  NODECOMP_1,
  NOTTOPOREL_0,
  VTXLISTERR_0,
  VTXLIST2ERR_0,

  // 4.1. Feature (general)

  INVALIDINTEGER_0,
  STRINGSIZETOOBIG_1,
  WRONGFEATCOLUMN_0,
  DATEMUSTBEDEFINED_0,

  // 4.2. Feature (predefined verif)

  // 4.2.1 Dates

  INVALIDDATE_0,
  INVALIDTIME_0,
  INVALIDDATEFORMAT_0,
  ALREADYDEFINEDATSAMEDATE_0,
  DATENOTINCREASING_0,
  DATEINVALIDLOC_0,
  DATEINVALIDTOPOFATHER_0,
  DATEINVALIDCOMPLEX_0,
  DATEGRWNBELERR_0,
  DATEGRWLGTHERR_0,
  DATEPRUNEDTFATHER_0,

  // 4.2.2 NbEl

  NBELMUSTBEDEF1_0,
  NBELMUSTBEDEF2_0,
  NBELCANNOTGRW1_0,
  NBELCANNOTGRW2_0,
  NBELGREATEREXIS_0,

  // 4.2.3 Length

  LGTHMUSTBEDEF_0,
  LGTHGREATEREXIS_0,

  // 4.2.4 Diam

  DIAMGREATEREXIS_0,

  // 4.2.5 State

  // General message messages

  FILEGENERALSTRUCTURE_0,
  FILEENDSPREMATURELY_0,
  UNEXPECTEDSTRING_0,
  NYIERR_0

}ERRORLABEL ;


typedef enum  {
  CLASSDEFINITION,
  CLASSDESCRIPTION,
  FEATUREDEFINITION,
  MTGHEADER,
  OUTSET,
  ENTITYCODE,
  FEATUREVALUE,
  DATEFEATURE,
  NBELFEATURE,
  LENGTHFEATURE,
  DIAMFEATURE,
  STATEFEATURE,
  GENERAL
} ErrorType ;


#endif
