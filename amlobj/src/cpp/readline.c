/*  -*-c++-*-----------------------------------------------------------------
 *  Amapmod                   CIRAD - Laboratoire de Modelisation des Plantes
 *
 *  $Source$
 *  $Id: readline.c 5941 2009-01-13 07:26:18Z pradal $
 *
 *  -------------------------------------------------------------------------
 *
 *  Note:
 *
 *  -------------------------------------------------------------------------
 *
 *  $Log$
 *  Revision 1.5  2002/10/11 13:52:32  fboudon
 *  no message
 *
 *  Revision 1.4  2002/10/08 12:42:07  fboudon
 *  no message
 *
 *  Revision 1.3  2002/09/02 13:19:07  pradal
 *  *** empty log message ***
 *
 *  Revision 1.2  2002/04/28 22:52:30  fboudon
 *  *** empty log message ***
 *
 *  Revision 1.1.1.1  2001/01/31 16:54:44  godin
 *  AMAPmod v1.6 imported into CVS
 *
 *  Revision 1.1.1.1  2001/01/08 11:10:58  amapmod
 *  version 1.6 importee sous CVS
 *
 *  Revision 1.1  1999/08/10 13:59:33  godin
 *  Initial revision
 *
 *
 *  -------------------------------------------------------------------------
 */

#if defined( __GNUC__ )
#if defined(  __MINGW32__ ) || defined(__APPLE__)
#else
#define USE_READLINE
#endif
#endif

#ifdef USE_READLINE

/*
#define ON_ERROR failwith(our_error_message());
*/

#if 0
#define NOHISTORY
#endif

#include <stdio.h>
#include <string.h>
#include <readline/readline.h>
#include <readline/history.h>

extern int rl_blink_matching_paren;

typedef char* mt;
mt keyword[]={

  "Display" ,
  "Plot" ,
  "Print" ,
  "Save" ,

  "Activate" ,
  "Active" ,

  "EchoOn" ,
  "EchoOff" ,

  "Bye" ,
  "Quit" ,
  "Exit" ,

  "Foreach" ,
  "In" ,

  "Select" ,

  "Mod" ,
  "If" ,
  "Then" ,
  "Else" ,

  "==" ,
  "!=" ,
  "Not" ,
  "And" ,
  "Or" ,
  "In" ,

  "Flatten" ,
  "Pos" ,

  "Feature" ,
  "Index" ,
  "Class" ,

  "Father" ,
  "Complex" ,
  "Sons" ,
  "Roots" ,
  "Components" ,
  "Root" ,
  "Extremities" ,
  "Ancestors" ,
  "Descendants" ,

  "Path" ,
  "First" ,
  "NthFirst" ,
  "Last" ,
  "NthLast" ,
  "Next" ,
  "Previous" ,

  "Order" ,
  "Rank" ,
  "Dist" ,
  "AlgOrder" ,
  "AlgRank" ,
  "AlgDist" ,

  "Sum" ,

  "Size" ,

  "AbsorbingVector" ,
  "Cluster" ,
  "ClusterNbEvent" ,
  "ClusterSymbol" ,
  "Compare" ,
  "Compound" ,
  "ComputeCorrelation" ,
  "ComputeSelfTransition" ,
  "Convolution" ,
  "Distribution" ,
  "ElementaryHistogram" ,
  "Estimate" ,
  "Extract" ,
  "ExtractData" ,
  "ExtractVariable" ,
  "HiddenMarkov" ,
  "HiddenSemiMarkov" ,
  "Histogram" ,
  "LengthSelect" ,
  "LengthTruncate" ,
  "Load" ,
  "Markov" ,
  "Merge" ,
  "Mixture" ,
  "NbEventSelect" ,
  "RemoveApicalInternodes" ,
  "RemoveSerie" ,
  "RemoveVariable" ,
  "Renewal" ,
  "Reverse" ,
  "Segment" ,
  "SegmentationExtract" ,
  "SemiMarkov" ,
  "Sequences" ,
  "Shift" ,
  "Simulate" ,
  "SubHistogram" ,
  "SymbolSelect" ,
  "TimeEvents" ,
  "TimeScale" ,
  "TimeSelect" ,
  "Top" ,
  "TopParameters" ,
  "Transcode" ,
  "TransformPosition" ,
  "TruncateMainAxes" ,

  "Absence" ,
  "AddVariable" ,
  "AdjacentInterval" ,
  "Algorithm" ,
  "ASCII" ,
  "Begin" ,
  "Binary" ,
  "BINOMIAL" ,
  "Blocking" ,
  "Characteristics" ,
  "Column" ,
  "COMPOUND" ,
  "Computation" ,
  "CONVOLUTION" ,
  "Counting" ,
  "Data" ,
  "Default" ,
  "Detail" ,
  "Direct" ,
  "DistInfBoundStatus" ,
  "Elementary" ,
  "End" ,
  "EqualProba" ,
  "Equilibrium" ,
  "FileName" ,
  "Fixed" ,
  "Format" ,
  "Forward" ,
  "Free" ,
  "HIDDEN_MARKOV" ,
  "HIDDEN_SEMI-MARKOV" ,
  "InfBoundStatus" ,
  "Irreductible" ,
  "Iterative" ,
  "KnownDistribution" ,
  "LeftRight" ,
  "Length" ,
  "Line" ,
  "LINEAR" ,
  "MARKOV" ,
  "MaxLag" ,
  "MaxLength" ,
  "MaxOrder" ,
  "MinInfBound" ,
  "MIXTURE" ,
  "Mode" ,
  "NbAxillary" ,
  "NbState" ,
  "NEGATIVE_BINOMIAL" ,
  "NextDate" ,
  "NextInterval" ,
  "NonBlocking" ,
  "NON-HOMOGENEOUS_MARKOV" ,
  "Observation" ,
  "ObservationTime" ,
  "Ordinary" ,
  "POISSON" ,
  "POWER" ,
  "Presence" ,
  "PreviousDate" ,
  "PreviousInterval" ,
  "Recurrence" ,
  "Segmentation" ,
  "SelfTransition" ,
  "SEMI-MARKOV" ,
  "Serie" ,
  "SpreadSheet" ,
  "SumMinInfBound" ,
  "Survival" ,
  "Title" ,
  "Type" ,
  "ViewPoint" ,
  "Viterbi" ,
  "VOID" ,

  "AMAPMOD_DIR",
  "HOME",
  "CWD",
  "Cd",
  "Copy",
  "Dir",
  "Exists",
  "FileHelp",
  "Ls",
  "Mkdir",
  "Pwd",
  "Rename",
  "Rm",

  "SetViewer",
  "StartViewer",
  "StopViewer",
  "ViewerIsRunning",
  "ViewerSelection",
  "ViewerHelp",
  "WaitViewer",

  (char *)NULL
};


/****************************************************************/
/* Concerning the completion                                    */
/****************************************************************/

char **keyword_completion(char* text, int start, int end) {

    char **matches;
    char *keyword_generator();

    matches=(char **)NULL;

    if(start == 0)
      matches=completion_matches(text,keyword_generator);

    return(matches);
}

char *keyword_generator(char* text, int state) {

    static int list_index;
    static int len;

    char *key;

    if (!state)
    {
        list_index = 0;
        len = strlen(text);
    }

    while(key = keyword[list_index])
    {
        list_index++;

        /** !!! Attention, faut dupliquer le mot car il sera libere plus tard !!! ***/
        if (strncmp(key, text, len) == 0)
            return(strdup(key));
    }

    return ((char *)NULL);

}


void gnu_init_readline()
{
	using_history();
  rl_attempted_completion_function =  keyword_completion;
// cpl 08/07/02
  rl_blink_matching_paren= 1;
  /*    rl_completion_entry_function     =  keyword_completion1; */
}

int readline_input(char* buff) {

  static char *ligne=(char *)NULL;
  char   *ptr;
  int    i,done=0;

  if (ligne) free(ligne);
  ligne=(char *)readline("AML> ");
  if (!ligne) done=1;

  if (done) return (0);
  if (*ligne) /* le premier caractere est-il nul ? */
  {

    register char* p = ligne;
    register char* ptr = buff;
    register int lg = 0;

#ifndef NOHISTORY
    add_history(ligne);
#endif


    while (*ptr++ = *p++) lg++;

    --ptr;
    *ptr++ = '\n';
    *ptr++ = '\0';

    return(lg+1);

  }
  else {
    ligne[0] = '\n';
    ligne[1] = '\0';
    return 1;
  }

}


#endif

