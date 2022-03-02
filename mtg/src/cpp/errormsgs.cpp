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
 *       $Id: errormsgs.cpp 3258 2007-06-06 13:18:26Z dufourko $
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





const char* err_messages[] = {

  // ClassDefinition

  "Syntax should be: \"CODE : tab [FORM-A | FORM-B]\"",				// CODEFORMSTX_0
  "Syntax should be: \"CLASSES :\"",						// CLASSDEFSTX1_0
  "Syntax should be: \"SYMBOL tab SCALE tab DECOMPOSITION tab INDEXATION tab DEFINITION\"",// CLASSDEFSTX2_0
  "Syntax should be: \"{char} tab {int} tab {decomp} tab {index} tab {def}\" \x0a\x0d\x0a\x0d\
          where {decomp} in [FREE|CONNECTED|LINEAR|+-LINEAR|<-LINEAR|NOTCONNECTED|NONE] \x0a\x0d\
                {index}  in [FREE|CONSECUTIVE] \x0a\x0d\
                {def}    in [IMPLICIT|EXPLICIT]",			        // CLASSLISTSTX_0
  "Every scale must be defined as an integer.\x0a\x0d\
   Integers should appear in increasing order, starting at 0 for the first class", // SCALEORDER_0
  "A class cannot be defined several times",					// CLASSDEFUNICITY_0
  "In FORM-B code, classes must necessarily have either <-LINEAR, NOTCONNECTED or NONE decomposition", // FORMBCOND1_0

  // ClassDescription

  "Syntax should be: \"DESCRIPTION :\"",					// CLASSDESCSTX1_0
  "Syntax should be: \"LEFT tab RIGHT tab RELTYPE tab MAX\"",			// CLASSDESCSTX2_0
  "Syntax should be: \" {char} tab {char}(,{char})* tab [+|<] tab [{int}|?] \"",	// CLASSDESCLISTSTX_0
  "This class has not been declared in the CLASSES header",			// CLASSNOTDEFINED_0
  "A 3-uple %s can only be defined once",					// CLASSDESCUNICITY_1
  "A topological edge can only be defined between classes at the same scale",	// TOPOLINKSCALE_0
  "In FORM-B code, every entity x must have at most 1 edge of type < to any other entity y", // FORMBCOND2_0

  // FeatureDefinition

  "Syntax should be: \"FEATURES :\"",						// FEATUREDEFSTX1_0
  "Syntax should be: \"NAME tab TYPE\"",					// FEATUREDEFSTX2_0
  "Syntax should be: \"[ {name} tab [INT|ALPHA|REAL|DD/MM|DD/MM/YY|MM/YY|DD/MM-TIME|DD/MM/YY-TIME] ]\"\x0a\x0d\x0a\x0d\
          where  {name} is any string of caracteres : [A-Za-z_][A-Za-z_0-9\\-]*\x0a\x0d\
   (predefined names are: Alias, Date, State, NbEl, Length, Diam.\x0a\x0d\
    If used, they should appear in this order, no matter some are missing)", // FEATUREDEFLISTSTX_0
  "A predefined feature has a predefined type:\x0a\x0d\x0a\x0d\
       Alias  has type ALPHA\x0a\x0d\
       Date   has type in {DD/MM,DD/MM/YY,MM/YY,DD/MM-TIME,DD/MM/YY-TIME}\x0a\x0d\
       State  has type ALPHA\x0a\x0d\
       NbEl   has type INT\x0a\x0d\
       Length has type INT\x0a\x0d\
       Diam   has type INT\x0a\x0d",				                // NOTYPEFORPREDFEAT_0
  "A feature name can only be defined once",					// FEATURENAMEUNICITY_0
  "predefined names are: Alias, Date, State, NbEl, Length, Diam.\x0a\x0d\
   If used, they should appear in this order, even if some are missing or others are inserted", // PREDFEATORDERING_0
  "Alias should always be the first feature defined",                           // ALIASDEFINEDFIRST_0

  // MTG description
  // 1. general syntax

  "Syntax should be: \"MTG :\"",						// MTGSTX1_0
  "Syntax should be: \"ENTITY-CODE (tab)* (tab {string})*\"",			// MTGSTX2_0
  "Syntax should be: \"(tab)* {code} (tab)* (tab {string} [tab]*)*\"\x0a\x0d\x0a\x0d\
          where {code}   is defined in the Amapmod manual,\x0a\x0d\
                {string} is any string of caracteres : [A-Za-z_0-9\\-/:\\*@&%$^!+=-|?\"'`{}<>]+", // MTGLISTSTX
  "This feature name does not exist in the attribute list declaration",	// ATTRNAME1_0
  "This feature name is not defined at the right place (cf. feature list declaration)",		//ATTRNAME2_0
  "The number of features is different from what has been declared in the header", // FEATNBDIFF_0

  // 2. Outset

  "Indentation not correct: line starting with a caret (^ or *) \
should be at the same indentation level as some previous line",                    // IDENTERR1_0
  "Indentation not correct: line starting with an alias \
should always start in column 1",                                                  // IDENTERR2_0
  "Indentation not correct: indentation level must be AT MOST one level higher compared\
 with the previous line",		                                           // IDENTERR3_0
  "This alias has not been defined previously",	                                   // ALIASDONOTEXIST_0
  "An alias should be a valid string",						   // ALIASSTRING_0
  "unbalanced parenthesis",						   	   // MISSINGALIASPARENTH_0
  "This cannot be the start of an entity code",					   // NOTACODESTART_0

  // 3.1. Code (general)

  "This class symbol is not valid (not defined in the header)",        		// CLASSERR_0
  "This index is not valid (should be a positive integer)",            		// INDEXERR_0 
  "Index missing",								// INDEXMISSING_0 
  "This is not a valid relation (valid relations are /,<,+,++,<<)",		// RELATIONNOTVALID_0
  "This entity code is not correct",						// ENTITYCODEERR_0
  "This entity should not have any features since it is IMPLICIT",		// IMPLICITERR_0

  // 3.2. Code (logic)

  "Entity already declared at line %s", 					// ALREADYDEFINED_1
  "Bad class: not a topologically expected class",           	         	// A1FAILED_0
  "Relation '%s' cannot be added: number of topologically expected daughters exceeded",	// A1_1FAILED_1
  "This vertex has a topological relation to itself",  				// A2FAILED_0
  "This entity should be at the same scale as its topological mother",		// A3FAILED_0
  "This entity should have a scale one level deeper than its complex mother",	// A4FAILED_0
  "This entity cannot be the global root of the tree",				// A5FAILED_0
  "This entity has more than one complex mother",				// A6FAILED_0
  "There is no topological edge at the complex scale reflecting this new topological edge",	// A7FAILED_0
  "The vprefix of an entity cannot have a scale 0",				// LOCERR1_0
  "The vprefix of this entity should be its complex mother",			// LOCERR2_0
  "The vprefix of this entity should be at a finer or equal scale",		// LOCERR3_0
  "An entity of class '%s' cannot be decomposed",				// NODECOMP_1
  "These entities should be connected by a topological relation \x0a\x0d\
   (topological relations are <,+,++,<<)", 					// NOTTOPOREL_0
  "An abbreviation of the form x << y or x ++ y should be made between vertices of the same class", // VTXLISTERR_0,
  "An abbreviation of the form x << y or x ++ y should be made only for increasing indexes", // VTXLIST2ERR_0,

  // 4.1. Feature (general)

  "This integer is not valid",							// INVALIDINTEGER_0
  "This string is too large. The current maximum width is %s",			// STRINGSIZETOOBIG_1
  "This value is not defined in any feature column",				// WRONGFEATCOLUMN_0
  "The feature 'Date' must always contain a defined and valid value",		// DATEMUSTBEDEFINED_0,

  // 4.2. Feature (predefined verif)

  // 4.2.1 Dates

  "This date is not valid",							// INVALIDDATE_0
  "*This time is not valid",							// INVALIDTIME_0
  "This date does not respect the format defined in the header",		// INVALIDDATEFORMAT_0
  "This entity has already been defined at the same date before",               // ALREADYDEFINEDATSAMEDATE_0
  "This entity has already been defined with a posterior date",                 // DATENOTINCREASING_0
  "The vprefix entity of this entity is not defined at this date",             // DATEINVALIDLOC_0
  "The topological mother of this entity is not defined at this date",          // DATEINVALIDTOPOFATHER_0
  "The complex entity of this entity is not defined at this date",              // DATEINVALIDCOMPLEX_0
  "The <-topological mother of this entity has a growing number of elements at this date", // DATEGRWNBELERR_0
  "The <-topological mother of this entity has a growing length at this date",		   // DATEGRWLGTHERR_0
  "*This entity cannot exist at this date since one of its topological ancestor has been pruned", // DATEPRUNEDTFATHER_0

  // 4.2.2 NbEl

  "*An entity which has a decomposition set to NONE cannot have a defined number of element",  // NBELMUSTBEDEF1_0
  "*The number of elements of this entity must be defined since it has just been pruned",      // NBELMUSTBEDEF2_0
  "*This entity cannot be growing at this date since there exist anterior <-topological daughters", // NBELCANNOTGRW1_0
  "*This entity cannot be growing at this date since it has been pruned before",			   // NBELCANNOTGRW2_0
  "*This entity has already been defined with a greater number of elements",			   // NBELGREATEREXIS_0

  // 4.2.3 Length

  "*The length of this entity must be defined since it has just been pruned", // LGTHMUSTBEDEF_0
  "*This entity has already been defined with a greater length",		     // LGTHGREATEREXIS_0

  // 4.2.4 Diam

  "*This entity has already been defined with a greater diameter", // DIAMGREATEREXIS_0

  // 4.2.5 State


  // General messages

  "The general structure of a MTG code file must be:\x0a\x0d\
\x0a\x0d\
  CODE: tab <code-form>\x0a\x0d\
\x0a\x0d\
  CLASSES:\x0a\x0d\
  SYMBOL tab SCALE tab DECOMPOSITION tab INDEXATION tab DEFINITION\x0a\x0d\
  <list of classes>\x0a\x0d\
\x0a\x0d\
  DESCRIPTION:\x0a\x0d\
  LEFT tab RIGHT tab RELTYPE tab MAX\x0a\x0d\
  <list of class descriptions>\x0a\x0d\
\x0a\x0d\
  FEATURES:\x0a\x0d\
  NAME tab TYPE\x0a\x0d\
  <list of features>\x0a\x0d\
\x0a\x0d\
  MTG:\x0a\x0d\
  ENTITY-CODE (tab {column-name})*\x0a\x0d\
  <list of entity codes>",							// FILEGENERALSTRUCTURE_0

  "End of file encountered prematurely",					// FILEENDSPREMATURELY_0
  "Unexpected string of characters ...",                                        // UNEXPECTEDSTRING_0
  "Error message Not Yet Implemented ... "					// NYIERR_0

};

 
const char* err_types[] = {
  "Class-Definition",
  "Class-Description",
  "Feature-Definition",
  "MTG-Header",
  "Entity-Outset",
  "Entity-Code",
  "Feature-Value",
  "Date",
  "NbEl",
  "Length",
  "Diam",
  "State",
  "General"
};
