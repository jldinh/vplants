/*************************************************************************
 * typedefs.h - 
 *
 * $Id: typedefs.h,v 1.3 2004/06/04 16:47:31 greg Exp $
 *
 * CopyrightŠINRIA 1998
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * http://www.inria.fr/epidaure/personnel/malandain/
 * 
 * CREATION DATE: 
 * June, 9 1998
 *
 *
 *
 */

#ifndef _typedefs_h_
#define _typedefs_h_

#ifdef __cplusplus
extern "C" {
#endif




/* Differents type coding for images and buffers.
 */
typedef enum {
  TYPE_UNKNOWN /* unknown type */,
  UCHAR  /* unsigned char */,
  SCHAR  /* signed char */,
  USHORT /* unsigned short int */,
  SSHORT /* signed short int */,
  UINT   /* unsigned int */,
  INT    /* signed int */,
  ULINT  /* unsigned long int */,
  FLOAT  /* float */,
  DOUBLE  /* double */
} ImageType, bufferType;

typedef char               s8;
typedef unsigned char      u8;
typedef short int          s16;
typedef unsigned short int u16;
typedef int                i32;
typedef int                s32;
typedef unsigned int       u32;
typedef unsigned long int  u64;
typedef float              r32;
typedef double             r64;





/* Typedef Booleen
 */
typedef enum {
  False = 0,
  True = 1
} typeBoolean;


#ifdef __cplusplus
}
#endif

#endif
