/****************************************************
 * regionalmax.h - 
 *
 * $Id$
 *
 * Copyright©INRIA 2008
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * http://www.inria.fr/epidaure/personnel/malandain/
 * 
 * CREATION DATE: 
 * Thu May 22 07:51:56 CEST 2008
 *
 * ADDITIONS, CHANGES
 *
 *
 *
 *
 *
 */

#ifndef _regionalmax_h_
#define _regionalmax_h_

#ifdef __cplusplus
extern "C" {
#endif


#ifdef __APPLE__
#include <malloc/malloc.h>
#else
#include <malloc.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <typedefs.h>

extern void regionalmax_setnoverbose();
extern void regionalmax_setverbose();

extern void regionalmax_setNumberOfPointsForAllocation( int n );


/* The regional maxima are defined as the difference between the input I and 
min( I-height, I*multiplier) dilated infinitely under I.
With multiplier=1.0, we get the H-maxima
*/ 

extern int regionalmax( void *theInput, void *theOutput, bufferType theType,
			int *theDim, int height, double multiplier );



#ifdef __cplusplus

}
#endif

#endif
