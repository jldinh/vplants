/* -*-c++-*- 
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Plant Graphic Library
 *
 *       Copyright 1995-2003 UMR Cirad/Inria/Inra Dap - Virtual Plant Team
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr) 
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

#include "readline.h"

#ifdef USE_READLINE

#include <iostream>
#include <stdlib.h>
#include <assert.h>
/*
#define ON_ERROR failwith(our_error_message());
*/

static const char* DEFAULT_PROMPT = ">";

#if 0
#define NOHISTORY
#endif

extern "C" {
#include <stdio.h>
#include <readline/readline.h>
#include <readline/history.h>
}

// int rl_blink_matching_paren = 1;

typedef const char* mt;
mt * key_word(NULL);
/*[]={       
  "VOID" ,
  (char *)NULL      
};*/                    

static int list_index;


/*! Function that detects if a given word is a key_word from the table key_word[].
 If the key_word is in the table, the returned value is a copy of the key_word argument (text).
 It is a char* that must be freed by the callee.
 If the function is called a second time, a second occurence of the key_word is searched for.
 To reinitialise the search, argument state must be set to 0

*/

const char *keyword_generator(const char* text, int state) {

    static int len;

    const char *key;

//    cerr << "Text : " << text << ", State : " << state << " , index : " << list_index << endl;
    if (!state /*&& !list_index*/)
    {
	list_index = 0;
	len = strlen(text);
    }

    if(key_word){
      while((key = key_word[list_index])) // stops when the end of the array is reached :(char *)NULL
	{
	  list_index++;
	  
	  /** !!! Attention, faut dupliquer le mot car il sera libere plus tard !!! ***/
	  if (strncmp(key, text, len) == 0)
	    return(strdup(key));	
	}
    }

    return ((const char *)NULL);

}

const char **keyword_completion(const char* text, int start, int end) {

    const char **matches;
    // char *keyword_generator();

    matches=(const char **)NULL;

//    cerr << "Text : " << text << ", start " << start  << ", end " << end <<  endl;
    if(start == 0)
#if defined (_RL_FUNCTION_TYPEDEF)
      matches=(const char **)rl_completion_matches(text,(rl_compentry_func_t*)keyword_generator); 
#else
      matches=completion_matches(text,(CPFunction*)keyword_generator); 
#endif

    return(matches);
}



void setKeyword(const char ** keyword)
{
  key_word = keyword;
}

void gnu_init_readline()
{
  using_history();
#if defined (_RL_FUNCTION_TYPEDEF)
  rl_attempted_completion_function =  (rl_completion_func_t*) keyword_completion;
#else
  rl_attempted_completion_function =  (CPPFunction*) keyword_completion;
#endif
  /*    rl_completion_entry_function     =  keyword_completion1; */
}


int readline_input(char* buff, const char* prompt) {

  static char *ligne=(char *)NULL;
  int done=0;

  if (ligne) free(ligne);
  ligne=(char *)readline(prompt? // readline does not return the \n
			 (strlen(prompt)?(char*)prompt:DEFAULT_PROMPT): 
			 DEFAULT_PROMPT); 
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

    while ((*ptr++ = *p++)) lg++; // copy of ligne into buff 

    --ptr;
    *ptr++ = '\n';		// put "\n\0" at the end of the string
    *ptr++ = '\0';
      
    // cerr << "readline: line lg = " << lg+1 << endl;

    return(lg+1);
    
  }
  else { // if readline returns 
    buff[0] = '\n';
    buff[1] = '\0';

    // cerr << "readline: line null, lg = 1" << endl;

    return 1;
  }
}

#endif


