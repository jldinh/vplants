/*************************************************************************
 * iobmp.h - I procedures for BMP raw images
 *
 * $Id: bmp.h,v 1.3 2004/03/03 12:57:25 xpennec Exp $
 *
 * Copyright INRIA
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: 
 * Wed Oct  6 17:03:48 MET DST 1999
 *
 * ADDITIONS, CHANGES
 *
 *
 */

#ifndef _bmp_h_
#define _bmp_h_

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#ifdef __APPLE__
#include <malloc/malloc.h>
#else
#include <malloc.h>
#endif
#include <stdio.h>
#include <fcntl.h> /* open, close */
#include <sys/stat.h> /* open, close */
#include <sys/types.h> /* open, close */
#include <string.h>
#include <imageio/ImageIO.h>
extern int readBmpImage(const char *name, _image *im);
extern void *_readBmpImage( const char *name, int *dimx, int *dimy, int *dimz );
int testBmpHeader(char *magic,const char *name);
/** creates an return the file format structure associated with the BMP file format */
PTRIMAGE_FORMAT createBMPFormat();

extern void IoBmp_verbose ( );
extern void IoBmp_noverbose ( );

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* _bmp_h_ */
