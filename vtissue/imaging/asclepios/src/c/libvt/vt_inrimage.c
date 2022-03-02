/*************************************************************************
 * vt_inrimage.c -
 *
 * $Id: vt_inrimage.c,v 1.10 2006/04/14 08:39:32 greg Exp $
 *
 * Copyright©INRIA 1999
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: 
 * 
 *
 * ADDITIONS, CHANGES
 *
 */



#include <vt_inrimage.h>

#define PACK_MAGIC     "\037\036" /* Magic header for packed files */
#define GZIP_MAGIC     "\037\213" /* Magic header for gzip files, 1F 8B */
#define OLD_GZIP_MAGIC "\037\236" /* Magic header for gzip 0.5 = freeze 1.x */
#define LZH_MAGIC      "\037\240" /* Magic header for SCO LZH Compress files*/
#define PKZIP_MAGIC    "\120\113\003\004" /* Magic header for pkzip files */
#define LZW_MAGIC      "\037\235"   /* Magic header for lzw files, 1F 9D */

static int _COMPRESS_FLAG_ = 0;

typedef enum {
  INRTYPE_UNKNOWN=0,
  INRTYPE_FLOAT=1,
  INRTYPE_UNSIGNEDFIXED=2,
  INRTYPE_SIGNEDFIXED=3
} InrimageType;

/*------- Definition des fonctions statiques ----------*/
#ifndef NO_PROTO
static int _VT_ReadInrimHeader( FILE *fd, vt_image *image, int *nh, int offset );
static void VT_PR_HImage( vt_image *image, int nh );
#else
static int _VT_ReadInrimHeader();
static void VT_PR_HImage();
#endif

/* Lecture d'une image avec creation de la structure associee.

   Cette fonction essaye de lire le fichier de nom name 
   (si c'est "<", c'est le standard input). Si l'en-tete
   est correctement lu, une structure image est allouee
   et on lit l'image que l'on range dans le buffer de 
   la structure. En cas d'erreur, la structure est desallouee.
   Ne reconnait qu'INRIMAGE-4.

RETURN
  Retourne (vt_image*)NULL en cas d'erreur.
*/
#if defined(_ANSI_)
vt_image* _VT_Inrimage( char *name /* file name containing the inrimage image */ )
#else
vt_image* _VT_Inrimage( name )
char *name; /* file name containing the inrimage image */ 
#endif
{
  char *proc = "_VT_Inrimage";
  vt_image *image;


  image = (vt_image*)VT_Malloc( (unsigned)sizeof(vt_image) );
  if (image == (vt_image*)NULL) {
    VT_Error("allocation of image structure failed", proc );
    return( (vt_image*)NULL );
  }
  VT_Image( image );


  if ( VT_ReadInrimage( image, name ) != 1 ) {
    VT_Error("Unable to read file", proc );
    VT_Free( (void**)&image );
    return( (vt_image*)NULL );
  }
  
  return( image );
}







/* Lecture d'une image.

   Cette fonction essaye de lire le fichier de nom name 
   (si c'est "<", c'est le standard input). Si l'en-tete
   est correctement lu, une structure image est allouee
   et on lit l'image que l'on range dans le buffer de 
   la structure. En cas d'erreur, la structure est desallouee.
   Ne reconnait qu'INRIMAGE-4.

RETURN
  Retourne (vt_image*)NULL en cas d'erreur.
*/

#ifndef LIBINRIMAGE 

#if defined(_ANSI_)
int VT_ReadInrimage( vt_image *image, /* structure deja allouee */
		     char *name /* file name containing the inrimage image */ )
#else
int VT_ReadInrimage( image, name )
vt_image *image;
char *name; /* file name containing the inrimage image */ 
#endif
{
  char *proc ="___VT_ReadInrimage";
  int nh, size, rsize;
  int ifd;
  FILE *fd, *fopen(), *popen();
  typeBoolean thisFileIsCompressed = False;
  
  /*--- opening the file
    1st case: standard input, the file is supposed not to be compressed
    2nd case: file on the disk, ok let see if it is compressed
    ---*/
  if( (name[0] == '<') && (name[1] == '\0') ) {
    ifd = VT_ROpen( name );
    if ( ifd == -1 ) {
      VT_Error("Unable to open file for reading", proc );
      return( 0 );
    }
    
    /*--- reading the header ---*/
    nh = 0;
    if ( VT_ReadInrimHeader( ifd, image, &nh ) == 0 ) {
      VT_Error("Unable to read image header", proc );
      VT_Close( ifd );
      return( 0 );
    }

    /*--- allocating the image ---*/
    if ( VT_AllocImage( image ) == 0 ) {
      VT_Error("Unable to allocate image", proc );
      VT_Close( ifd );
      return( 0 );
    }

    /*--- reading the image ---*/
    size = VT_SizeImage( image );
    rsize = VT_Read( ifd, (char*)(image->buf), size );
    if ( rsize < size) {
      char text[80];
      size += nh * 256;
      rsize += nh * 256;
      sprintf(text,"file size is %d bytes instead of %d", rsize, size);
      VT_Error(text, proc );
      VT_FreeImage( image );
      VT_Close( ifd );
      return( 0 );
    }

    /*--- closing the file ---*/
    VT_Close( ifd );
    



  } else {




    
    fd  = fopen( name, "r" );
    if ( fd == (FILE*)NULL ) {
      VT_Error("Unable to open file for reading", proc );
      return( 0 );
    }

    /*--- reading a magic number ---*/
    {
      char magic_string[5];
      rsize = fread( magic_string, 1, 4 ,fd );
      if ( rsize < 4 ) {
	VT_Error("Unable to read magic string", proc );
	return( 0 );
      }
      
      if ( (memcmp(magic_string , GZIP_MAGIC, 2) == 0) ||
	   (memcmp(magic_string , OLD_GZIP_MAGIC, 2) == 0) ||
	   (memcmp(magic_string , PKZIP_MAGIC, 4) == 0) ||
	   (memcmp(magic_string , PACK_MAGIC, 2) == 0) ||
	   (memcmp(magic_string , LZW_MAGIC, 2) == 0) ||
	   (memcmp(magic_string , LZH_MAGIC, 2) == 0) ) {
	char cmd[256];
	_COMPRESS_FLAG_ = 1;
	thisFileIsCompressed = True;
	if ( fclose( fd ) != 0 ) {
	  VT_Error("Unable to close the first stream", proc );
	  return( 0 );
	}
	(void)sprintf(cmd, "gzip -dc %s 2> /dev/null", name );
	fd = popen( cmd, "r" );
      }
    }
    
    /* we've got a file descriptor to read the input 
       this should be an inrimage file */
    
    /*--- reading the header ---*/
    nh = 0;
    if ( thisFileIsCompressed != True ) {
      if ( _VT_ReadInrimHeader( fd, image, &nh, 4 ) == 0 ) {
	VT_Error("Unable to read image header", proc );
	fclose( fd );
	return( 0 );
      }
    } else {
      if ( _VT_ReadInrimHeader( fd, image, &nh, 0 ) == 0 ) {
	VT_Error("Unable to read image header", proc );
	pclose( fd );
	return( 0 );
      }
    }

    /*--- allocating the image ---*/
    if ( VT_AllocImage( image ) == 0 ) {
      VT_Error("Unable to allocate image", proc );
      if ( thisFileIsCompressed == True ) pclose( fd );
      else fclose( fd );
      return( 0 );
    }

    /*--- reading the image ---*/
    size = VT_SizeImage( image );
    rsize = fread( (void *)(image->buf), 1, size, fd );
    if ( rsize < size) {
      char text[80];
      size += nh * 256;
      rsize += nh * 256;
      sprintf(text,"file size is %d bytes instead of %d", rsize, size);
      VT_Error(text, proc );
      VT_FreeImage( image );
      if ( thisFileIsCompressed == True ) pclose( fd );
      else fclose( fd );
      return( 0 );
    }

    /*--- closing the file ---*/
    if ( thisFileIsCompressed == True ) pclose( fd );
    else  fclose( fd );
  }
	
  
  if (VT_CopyName( image->name, name ) != 1 ) {
    VT_Error("Unable to write image name into image structure", proc );
  }


  /*--- transformation of the image --*/
  if ( _CPUtoCPU( image ) == 0 ) {
    VT_Error("can not convert image type to local type", proc );
    VT_FreeImage( image );
    
    return( 0 );
  }


  return( 1 );
  
}


#else

#include <imageio/ImageIO.h> 

static int _flag_init_readers = 0;

#include <analyze.h>
#include <bmp.h>
#include <gif.h>
#include <gis.h>
/* #include <interfile.h> */
#include <pnm.h>

void _init_readers()
{
  initSupportedFileFormat();
  addImageFormat( createAnalyzeFormat() );
  addImageFormat( createBMPFormat() );
  addImageFormat( createGifFormat() );
  addImageFormat( createGisFormat() );
  /*   addImageFormat( createInterfileFormat() ); */
  addImageFormat(createPgmFormat());
  addImageFormat(createPgmAscIIFormat());
  addImageFormat( createPpmFormat() );
}


int VT_ReadInrimage( vt_image *image, char *name )
{
  char *proc = "VT_ReadInrimage";
  _image *inr;
  ImageType type = TYPE_UNKNOWN;

  if ( _VT_DEBUG_ ) {
    fprintf( stderr, "%s: uses LIBINRIMAGE routines\n", proc );
  }

  if ( _flag_init_readers == 0 ) {
    _init_readers();
    _flag_init_readers = 1;
  }

  VT_FreeImage( image );
  /* lecture
   */
  inr = _readImage( name );
  if( !inr ) {
    if ( _VT_VERBOSE_ )
      fprintf( stderr, "%s: unable to read '%s'\n ", proc, name );
    return 0;
  }
  if ( 0 ) {
  if ( inr->vectMode != VM_SCALAR || inr->vdim != 1 ) {
    if ( _VT_VERBOSE_ )
      fprintf( stderr, "%s: can not deal with vectorial image '%s'\n ", proc, name );
    _freeImage(inr);
    return 0;
  }
  }

  /* conversion
   */
  switch ( inr->wordKind ) {
  case WK_FIXED :
    switch( inr->sign ) {
    case SGN_UNSIGNED :
      if ( inr->wdim  == sizeof( unsigned char ) ) {
	type = UCHAR;
      }
      else if ( inr->wdim  == sizeof( unsigned short int ) ) {
	type = USHORT;
      }
      else if ( inr->wdim  == sizeof( unsigned int ) ) {
	type = UINT;
      }
      else {
	if ( _VT_VERBOSE_ )
	  fprintf( stderr, "%s: unknown WK_FIXED UNSIGNED word dim (%d) for image '%s'\n ", proc, inr->wdim, name );
	_freeImage(inr);
	return 0;
      }
      break;
    case SGN_SIGNED :
      if ( inr->wdim  == sizeof( char ) ) {
	type = SCHAR;
      }
      else if ( inr->wdim  == sizeof( short int ) ) {
	type = SSHORT;
      }
      else if ( inr->wdim  == sizeof( int ) ) {
	type = INT;
      }
      else {
	if ( _VT_VERBOSE_ )
	  fprintf( stderr, "%s: unknown WK_FIXED SIGNED word dim (%d) for image '%s'\n ", proc, inr->wdim, name );
	_freeImage(inr);
	return 0;
      }
      break;
    default :
      if ( _VT_VERBOSE_ )
	fprintf( stderr, "%s: unknown wordSign for image '%s'\n ", proc, name );
      _freeImage(inr);
      return 0;    
    }
    break;
  case WK_FLOAT :
    if ( inr->wdim  == sizeof( float ) ) {
      type = FLOAT;
    }
    else if ( inr->wdim  == sizeof( double ) ) {
      type = DOUBLE;
    }
    else {
      if ( _VT_VERBOSE_ )
	fprintf( stderr, "%s: unknown WK_FLOAT word dim for image '%s'\n ", proc, name );
      _freeImage(inr);
      return 0;
    }
    break;
  default :
    if ( _VT_VERBOSE_ )
      fprintf( stderr, "%s: unknown wordKind for image '%s'\n ", proc, name );
    _freeImage(inr);
    return 0;
  }
  
  /* copie des attributs
   */
  image->type = type;

  image->dim.x = inr->xdim; 
  image->dim.y = inr->ydim; 
  image->dim.z = inr->zdim; 
  image->dim.v = inr->vdim; 

  image->siz.x = inr->vx;
  image->siz.y = inr->vy;
  image->siz.z = inr->vz;

  image->off.x = inr->tx;
  image->off.y = inr->ty;
  image->off.z = inr->tz;

  image->rot.x = inr->rx;
  image->rot.y = inr->ry;
  image->rot.z = inr->rz;

  image->ctr.x = inr->cx;
  image->ctr.y = inr->cy;
  image->ctr.z = inr->cz;

  image->nuser = inr->nuser;
  image->user = inr->user;
  
  image->buf = inr->data;

  strcpy( image->name, name );

  {
    unsigned int vol_ptr;
    int i,j;

    switch ( image->type ) {
    case SCHAR :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( s8* );
      vol_ptr += image->dim.z                * sizeof( s8** );
      break;
    case UCHAR :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( u8* );
      vol_ptr += image->dim.z                * sizeof( u8** );
      break;
    case SSHORT :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( s16* );
      vol_ptr += image->dim.z                * sizeof( s16** );
      break;
    case USHORT :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( u16* );
      vol_ptr += image->dim.z                * sizeof( u16** );
      break;
    case FLOAT :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( r32* );
      vol_ptr += image->dim.z                * sizeof( r32** );
      break;
    case DOUBLE :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( r64* );
      vol_ptr += image->dim.z                * sizeof( r64** );
      break;
    case INT :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( i32* );
      vol_ptr += image->dim.z                * sizeof( i32** );
      break;
    case UINT :
      vol_ptr  = image->dim.z * image->dim.y * sizeof( u32* );
      vol_ptr += image->dim.z                * sizeof( u32** );
      break;
    default :
      if ( _VT_VERBOSE_ )
	fprintf( stderr, "%s: unknown image type", proc );
      _freeImage(inr);
      return 0;
    }

    image->array = (void***) malloc( (unsigned int)(vol_ptr) );
    if ( image->array == NULL ) {
      if ( _VT_VERBOSE_ )
	fprintf( stderr, "%s: private buffer allocation failed", proc );
      _freeImage(inr);
      return 0;
    }

    switch ( image->type ) {
    case SCHAR :
      {
	s8 ***z;
	s8 **zy;
	s8 *zyx;
	
	z = (s8 ***)(image->array);
	zy = (s8 **)(z + image->dim.z);
	zyx = (s8 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case UCHAR :
      {
	u8 ***z;
	u8 **zy;
	u8 *zyx;
	
	z = (u8 ***)(image->array);
	zy = (u8 **)(z + image->dim.z);
	zyx = (u8 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case SSHORT :
      {
	s16 ***z;
	s16 **zy;
	s16 *zyx;
	
	z = (s16 ***)(image->array);
	zy = (s16 **)(z + image->dim.z);
	zyx = (s16 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case USHORT :
      {
	u16 ***z;
	u16 **zy;
	u16 *zyx;
	
	z = (u16 ***)(image->array);
	zy = (u16 **)(z + image->dim.z);
	zyx = (u16 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case FLOAT :
      {
	r32 ***z;
	r32 **zy;
	r32 *zyx;
	
	z = (r32 ***)(image->array);
	zy = (r32 **)(z + image->dim.z);
	zyx = (r32 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case DOUBLE :
      {
	r64 ***z;
	r64 **zy;
	r64 *zyx;
	
	z = (r64 ***)(image->array);
	zy = (r64 **)(z + image->dim.z);
	zyx = (r64 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case INT :
      {
	i32 ***z;
	i32 **zy;
	i32 *zyx;
	
	z = (i32 ***)(image->array);
	zy = (i32 **)(z + image->dim.z);
	zyx = (i32 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    case UINT :
      {
	u32 ***z;
	u32 **zy;
	u32 *zyx;
	
	z = (u32 ***)(image->array);
	zy = (u32 **)(z + image->dim.z);
	zyx = (u32 *)(image->buf);
	
	/*--- calcul pour le premier indice Z ---*/
	for ( i = 0; i < image->dim.z; i ++ ) {
	  *z = zy;
	  z ++;
	  /*--- calcul pour le deuxieme indice Y ---*/
	  for ( j = 0; j < image->dim.y; j ++ ) {
	    *zy = zyx;
	    zy ++;
	    zyx += image->dim.x * image->dim.v;
	  }
	}}
      break;
    default :
      if ( _VT_VERBOSE_ )
	fprintf( stderr, "%s: unknown image type", proc );
      _freeImage(inr);
      return 0;
    }
   

  }
  
  ImageIO_free( inr );

  return 1;
}


#endif











/* Fonction d'ecriture d'une image inrimage.

RETURN 
   Retourne 0 en cas de probleme.
*/

#ifndef LIBINRIMAGE 

#if defined(_ANSI_)
int VT_WriteInrimage( vt_image *image /* image to be written */ )
#else
int VT_WriteInrimage( image )
vt_image *image; /* image to be written */
#endif
{
    char header[257];
    int ifd ,nb, size;
    FILE *fd, *popen();
    int l;
    
    if ( VT_Test1VImage( image, "VT_WriteInrimage" ) == 0 ) 
	return( 0 );


    VT_FillInrimHeader( header, image );
    
    l = VT_Strlen( image->name ); 
    if ( (l < 3) || (strncmp( &(image->name[l-3]), ".gz", 3 ) != 0) ) {
      /* Normal case */
      /*--- opening the file ---*/
      ifd = VT_WOpen( image->name );
      if ( ifd == -1 ) {
	VT_Error("Unable to open file for writing","VT_WriteInrimage");
	return( 0 );
      }
      /*--- writing the header ---*/
      nb = VT_Write( ifd, header, 256 );
      if ( nb == -1 ) {
	VT_Error("error when writing the header","VT_WriteInrimage");
	VT_Close( ifd );
	return( 0 );
      }
      if ( nb < 256 ) {
	VT_Error("not enough space left for writing","VT_WriteInrimage");
	VT_Close( ifd );
	return( 0 );
      }
      /*--- writing the image ---*/
      size = VT_SizeImage( image );
      nb = VT_Write( ifd, (char*)(image->buf), size );
      if ( nb == -1 ) {
	VT_Error("error when writing","VT_WriteInrimage");
	VT_Close( ifd );
	return( 0 );
      }
      if ( nb < size ) {
	VT_Error("not enough space left for writing","VT_WriteInrimage");
	VT_Close( ifd );
	return( 0 );
      }
      /*--- closing the file ---*/
      VT_Close( ifd );
    } else {
      /* write compressed file */
      char cmd[256];
      (void)sprintf(cmd, "gzip -c > %s", image->name);
      fd = popen(cmd, "w");
      if ( fd == (FILE*)NULL ) {
	VT_Error("Unable to open file for writing","VT_WriteInrimage");
	return( 0 );
      }
      /*--- writing the header ---*/
      if ( fwrite( header, 1, 256, fd ) != 256 ) {
	VT_Error("error when copying the header","VT_WriteInrimage");
	pclose( fd );
	return( 0 );
      }
      /*--- writing the image ---*/
      size = VT_SizeImage( image );
      if ( (int)fwrite( (void *)(image->buf), 1, size, fd ) != size ) {
	VT_Error("error when copying the data","VT_WriteInrimage");
	pclose( fd );
	return( 0 );
      }
      /*--- closing the file ---*/
      fflush( fd );
      pclose( fd );
    }
    return( 1 );
}


#else

#include <imageio/ImageIO.h> 


int VT_WriteInrimage( vt_image *image )
{
  char *proc = "VT_WriteImage";
  _image *inr = NULL;
  
  if ( _VT_DEBUG_ ) {
    fprintf( stderr, "%s: uses LIBINRIMAGE routines\n", proc );
  }

  if ( _flag_init_readers == 0 ) {
    _init_readers();
    _flag_init_readers = 1;
  }

  inr = _initImage();

  
  switch ( image->type ) {
  case SCHAR :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_SIGNED;
    inr->wdim     = sizeof( char );
    break;
  case UCHAR :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_UNSIGNED;
    inr->wdim     = sizeof( char );
    break;
  case SSHORT :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_SIGNED;
    inr->wdim     = sizeof( short int );
    break;
  case USHORT :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_UNSIGNED;
    inr->wdim     = sizeof( short int );
    break;
  case FLOAT :
    inr->wordKind = WK_FLOAT;
    inr->sign     = SGN_UNKNOWN;
    inr->wdim     = sizeof( float );
    break;
  case DOUBLE :
    inr->wordKind = WK_FLOAT;
    inr->sign     = SGN_UNKNOWN;
    inr->wdim     = sizeof( double );
    break;
  case INT :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_SIGNED;
    inr->wdim     = sizeof( int );
    break;
  case UINT :
    inr->wordKind = WK_FIXED;
    inr->sign     = SGN_UNSIGNED;
    inr->wdim     = sizeof( int );
    break;
  default :
    free(inr);
    return 0;
  }

  inr->xdim = image->dim.x;
  inr->ydim = image->dim.y;
  inr->zdim = image->dim.z;
  inr->vdim = image->dim.v;

  inr->vx = image->siz.x;
  inr->vy = image->siz.y;
  inr->vz = image->siz.z;

  inr->tx = image->off.x;
  inr->ty = image->off.y;
  inr->tz = image->off.z;

  inr->rx = image->rot.x;
  inr->ry = image->rot.y;
  inr->rz = image->rot.z;

  inr->cx = image->ctr.x;
  inr->cy = image->ctr.y;
  inr->cz = image->ctr.z;

  inr->nuser = image->nuser;
  inr->user  = image->user;

  inr->data = image->buf;

  if ( _writeImage( inr, image->name ) == -1 ) {
    if ( _VT_VERBOSE_ )
      fprintf( stderr, "%s: unable to write image '%s'", proc, image->name );
    free( inr );
    return 0;
  }
    
  free( inr );
  return 1;
}

#endif




/* entete par od -s -Ad
#INRIMAGE-4#{\nXDIM=256\nYDIM=256\nZDIM=45\nVDIM=1\nTYPE=unsigned fixed\nPIXSIZE=8 
bits\nSCALE=2**0\nCPU=decm\nVX=0.898438\nVY=0.898438\nVZ=3.000000\n\n\n\n\n\n\n\n\n\n\n\n\n
\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\
n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
\n\n\n\n\n\n\n\n\n\n\n##}\n

#INRIMAGE-4#{
XDIM=256
YDIM=256
ZDIM=45
VDIM=1
TYPE=unsigned fixed
PIXSIZE=8 bits
SCALE=2**0
CPU=decm
VX=0.898438
VY=0.898438
VZ=3.000000


*/


static int _VT_DecodeInrimHeader( char *header, vt_image *image, int offset )
{
  char *proc = "_VT_DecodeInrimHeader";
  InrimageType type=INRTYPE_UNKNOWN;
  int nbBits;
  char *str=header;

  /*
    find the magic string 
  */
  switch ( offset ) {
  case 0 :
    if ( VT_Strncmp(str, "#INRIMAGE-4#{", 13) != 0 ) {
      VT_Error("Unable to read image header (2a)",proc);
      return( 0 );
    }
    str+=13;
    break;
  case 4 :
    if ( VT_Strncmp(str, "IMAGE-4#{", 9) != 0 ) {
      VT_Error("Unable to read image header (2b)",proc);
      return( 0 );
    }
    str += 9;
    break;
  default :
    VT_Error("Unable to deal with such offset",proc);
    return( 0 );
  }

  

  do {
    
    
    /* on avance jusqu'a \n */
    for ( ; (*str != '\n') && (*str != '\0') ; str++ )
      ;
    
    if ( *str != '\0' ) {
      str ++;

      switch( *str ) {
	/*
	  les dimensions
	*/
      case 'X' :
	if(!strncmp(str, "XDIM=", 5))
	  if(sscanf(str+5, "%i", &(image->dim.x)) != 1) {
	    VT_Error("Unable to read X dimension in image header",proc);
	    return( 0 );
	  }
	break;
      case 'Y' :
	if(!strncmp(str, "YDIM=", 5))
	  if(sscanf(str+5, "%i", &(image->dim.y)) != 1) {
	    VT_Error("Unable to read Y dimension in image header",proc);
	    return( 0 );
	  }
	break;
      case 'Z' :
	if(!strncmp(str, "ZDIM=", 5))
	  if(sscanf(str+5, "%i", &(image->dim.z)) != 1) {
	    VT_Error("Unable to read Z dimension in image header",proc);
	    return( 0 );
	  }
	break;
      case 'V' :
	if(!strncmp(str, "VDIM=", 5)) {
	  if(sscanf(str+5, "%i", &(image->dim.v)) != 1) {
	    VT_Error("Unable to read V dimension in image header",proc);
	    return( 0 );
	  }
	  if ( image->dim.v != 1 )
	    VT_Warning("Vectorial image",proc);
	}
	if(!strncmp(str, "VX=", 3))
	  if(sscanf(str+3, "%f", &(image->siz.x)) != 1) {
	    VT_Error("Unable to read X voxel size in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "VY=", 3))
	  if(sscanf(str+3, "%f", &(image->siz.y)) != 1) {
	    VT_Error("Unable to read Y voxel size in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "VZ=", 3))
	  if(sscanf(str+3, "%f", &(image->siz.z)) != 1) {
	    VT_Error("Unable to read Z voxel size in image header",proc);
	    return( 0 );
	  }
	break;

	/* codage du point */
      case 'T' :
	if(!strncmp(str, "TYPE=", 5)) {
	  if(!strncmp(str+5, "float", 5)) 
	    type=INRTYPE_FLOAT;
	  else {
	    if(!strncmp(str+5, "signed fixed", 12)) {
	      type=INRTYPE_SIGNEDFIXED;
	    }
	    else {
	      if(!strncmp(str+5, "unsigned fixed", 14)) {
		type=INRTYPE_UNSIGNEDFIXED;
	      } 
	      else {
		VT_Error("Unable to read type in image header",proc);
		return( 0 );
	      }
	    }
	  }
	}
	if(!strncmp(str, "TX=", 3))
	  if(sscanf(str+3, "%f", &(image->off.x)) != 1) {
	    VT_Error("Unable to read X offset in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "TY=", 3))
	  if(sscanf(str+3, "%f", &(image->off.y)) != 1) {
	    VT_Error("Unable to read Y offset in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "TZ=", 3))
	  if(sscanf(str+3, "%f", &(image->off.z)) != 1) {
	    VT_Error("Unable to read Z offset in image header",proc);
	    return( 0 );
	  }
	
	break;
	
      case 'O' :
	if(!strncmp(str, "OX=", 3))
	  if(sscanf(str+3, "%d", &(image->ctr.x)) != 1) {
	    VT_Error("Unable to read X center in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "OY=", 3))
	  if(sscanf(str+3, "%d", &(image->ctr.y)) != 1) {
	    VT_Error("Unable to read Y center in image header",proc);
	    return( 0 );
	  }
	if(!strncmp(str, "OZ=", 3))
	  if(sscanf(str+3, "%d", &(image->ctr.z)) != 1) {
	    VT_Error("Unable to read Z center in image header",proc);
	    return( 0 );
	  }
	
	break;
	
      case 'P' :
	if(!strncmp(str, "PIXSIZE=", 8)) {
	  if(sscanf(str+8, "%d bits", &nbBits) != 1) {
	    VT_Error("Unable to read point size in image header",proc);
	    return( 0 );
	  }
	  if ( nbBits != 8 && nbBits != 16 && nbBits != 32 && nbBits != 64 ) {
	    VT_Error("PIXSIZE not handled yet",proc);
	    return( 0 );
	  }
	}
	break;
	
      case 'C' :
	if(!strncmp(str, "CPU=", 4)) {
	  if(!strncmp(str+4, "decm", 4)) image->cpu = LITTLEENDIAN;
	  else if(!strncmp(str+4, "alpha", 5)) image->cpu = LITTLEENDIAN;
	  else if(!strncmp(str+4, "pc", 2)) image->cpu = LITTLEENDIAN;
	  else if(!strncmp(str+4, "linux", 5)) image->cpu = LITTLEENDIAN;
	  else if(!strncmp(str+4, "sun", 3)) image->cpu = BIGENDIAN;
	  else if(!strncmp(str+4, "sgi", 3)) image->cpu = BIGENDIAN;
	  else {
	    VT_Error("image cpu set to default",proc);
	    image->type = MY_CPU;
	  }
	}
      } /* end switch */
    } /* end if */ 
  } while ( *str != '\0'); /* end do */
  

  switch ( type ) {
  case INRTYPE_UNKNOWN :
  default :
    VT_Error("Unable to determine image type from image header",proc);
    return( 0 );
  case INRTYPE_FLOAT :
    switch( nbBits ) {
    case 32 : image->type = FLOAT; break;
    case 64 : image->type = DOUBLE; break;
    default :
      VT_Error("Unable to determine float type from image header",proc);
      return( 0 );
    }
    break;
  case INRTYPE_UNSIGNEDFIXED :
    switch( nbBits ) {
    case  8 : image->type = UCHAR; break;
    case 16 : image->type = USHORT; break;
    case 32 : image->type = UINT; break;
    case 64 : image->type = ULINT; break;
    default :
      VT_Error("Unable to determine unsigned type from image header",proc);
      return( 0 );
    }
    break;
  case INRTYPE_SIGNEDFIXED :
    switch( nbBits ) {
    case  8 : image->type = SCHAR; break;
    case 16 : image->type = SSHORT; break;
    case 32 : image->type = INT; break;
    default :
      VT_Error("Unable to determine signed type from image header",proc);
      return( 0 );
    }
    break;
  }

  return(1);
}



#if defined(_ANSI_)
static int _VT_ReadInrimHeader( FILE *fd, vt_image *image, int *nh, int offset )
#else
static int _VT_ReadInrimHeader( fd, image, nh, offset )
FILE *fd;
vt_image *image;
int *nh;
int offset;
#endif
{
    char *proc = "_VT_ReadInrimHeader";
    char header[257];
    int first_length = 256-offset; /* 256 - 4 */
    int tmp;
    
    /*--- read one header ---*/
    if ( (int)fread( header, 1, first_length, fd ) < first_length ) {
	VT_Error("Unable to read image header (1)",proc);
	return( 0 );
    }
    header[256] = '\0';
    *nh = 1;

    if ( _VT_DecodeInrimHeader( header, image, offset ) != 1 ) {
      VT_Error("Unable to understand image header","VT_ReadInrimHeader");
	return( 0 );
    }


    /*--- fin de l'header ? ---*/
    if ( VT_Strncmp( &(header[252-offset]), "##}", 3 ) == 0 ) {
	VT_PR_HImage( image, *nh );
	return( 1 );
    }
    /*--- si la taille de l'header est superieure a 256 ---*/
    tmp = 0;
    while ( tmp == 0 ) {
	(*nh) ++;
	if ( fread( header, 1, 256, fd ) < 256 ) {
	    VT_Error("Unable to read image header (10)",proc);
	    return( 0 );
	}
	if ( VT_Strncmp( &(header[252]), "##}", 3 ) == 0 ) tmp = 1;
    }
    if ( _VT_DEBUG_ == 1 ) VT_PR_HImage( image, *nh );
    return( 1 );
}

#if defined(_ANSI_)
int VT_ReadInrimHeader( int fd, vt_image *image, int *nh )
#else
int VT_ReadInrimHeader( fd, image, nh )
int fd;
vt_image *image;
int *nh;
#endif
{
    char header[257];
    int tmp;

    /*--- read one header ---*/
    if ( VT_Read( fd, header, (int)256 ) < 256 ) {
	VT_Error("Unable to read image header (1)","VT_ReadInrimHeader");
	return( 0 );
    }
    header[256] = '\0';
    *nh = 1;

    if ( _VT_DecodeInrimHeader( header, image, 0 ) != 1 ) {
      VT_Error("Unable to understand image header","VT_ReadInrimHeader");
	return( 0 );
    }


    /*--- fin de l'header ? ---*/
    if ( VT_Strncmp( &(header[252]), "##}", 3 ) == 0 ) {
	VT_PR_HImage( image, *nh );
	return( 1 );
    }
    /*--- si la taille de l'header est superieure a 256 ---*/
    tmp = 0;
    while ( tmp == 0 ) {
	(*nh) ++;
	if ( VT_Read( fd, header, (int)256 ) < 256 ) {
	    VT_Error("Unable to read image header (10)","VT_ReadInrimHeader");
	    return( 0 );
	}
	if ( VT_Strncmp( &(header[252]), "##}", 3 ) == 0 ) tmp = 1;
    }
    if ( _VT_DEBUG_ == 1 ) VT_PR_HImage( image, *nh );
    return( 1 );
}

#if defined(_ANSI_)
void VT_FillInrimHeader( char *header, vt_image *image )
#else
void VT_FillInrimHeader( header, image )
char *header;
vt_image *image;
#endif
{
  register int i, l;
  for (i=0; i<256; i++) header[i] = '\0';
  l = 0;
  sprintf( &(header[l]), "#INRIMAGE-4#{\n" );
  l += VT_Strlen( &(header[l]) );
  sprintf( &(header[l]), "XDIM=%d\nYDIM=%d\nZDIM=%d\nVDIM=%d\n", 
	   image->dim.x, image->dim.y, image->dim.z, image->dim.v );
  l += VT_Strlen( &(header[l]) );
  sprintf( &(header[l]), "TYPE=" );
  l += VT_Strlen( &(header[l]) );
  switch ( image->type ) {
  case UCHAR :
  case USHORT :
  case ULINT :
  case UINT :
    sprintf( &(header[l]), "unsigned fixed\n" );
    break;
  case SCHAR :
  case SSHORT :
  case INT :
    sprintf( &(header[l]), "signed fixed\n" );
    break;
  case FLOAT :
  case DOUBLE :
    sprintf( &(header[l]), "float\n" );
    break;
  case TYPE_UNKNOWN :
    sprintf( &(header[l]), "unknown\n" );
  }
  l += VT_Strlen( &(header[l]) );
  switch ( image->type ) {
  case SCHAR :
  case UCHAR :
    sprintf( &(header[l]), "PIXSIZE=8 bits\n" );
    break;
  case USHORT :
  case SSHORT :
    sprintf( &(header[l]), "PIXSIZE=16 bits\n" );
    break;
  case UINT :
  case INT :
  case FLOAT :
    sprintf( &(header[l]), "PIXSIZE=32 bits\n" );
    break;
  case DOUBLE :
  case ULINT :
    sprintf( &(header[l]), "PIXSIZE=64 bits\n" );
    break;
  case TYPE_UNKNOWN :
    sprintf( &(header[l]), "PIXSIZE=unknown\n" );
  }
  l += VT_Strlen( &(header[l]) );
  switch ( image->type ) {
  case UCHAR :
  case SCHAR :
  case USHORT :
  case SSHORT :
  case UINT :
  case INT :
    sprintf( &(header[l]), "SCALE=2**0\n" );
    break;
  default :
    break;
  }
  l += VT_Strlen( &(header[l]) );
  switch ( MY_CPU ) {
  case LITTLEENDIAN :
    sprintf( &(header[l]), "CPU=decm\n" );
    break;
  case BIGENDIAN :
  default :
    sprintf( &(header[l]), "CPU=sun\n" );
  }
  l += VT_Strlen( &(header[l]) );
  sprintf( &(header[l]), "VX=%f\nVY=%f\nVZ=%f\n",
	   image->siz.x, image->siz.y, image->siz.z );
  l += VT_Strlen( &(header[l]) );

  if ( image->off.x > 0 || image->off.y > 0 || image->off.z > 0 ) {
    sprintf( &(header[l]), "TX=%f\nTY=%f\nTZ=%f\n",
	     image->off.x, image->off.y, image->off.z );
    l += VT_Strlen( &(header[l]) );
  }

  if ( image->ctr.x > 0 || image->ctr.y > 0 || image->ctr.z > 0 ) {
    sprintf( &(header[l]), "OX=%d\nOY=%d\nOZ=%d\n",
	     image->ctr.x, image->ctr.y, image->ctr.z );
    l += VT_Strlen( &(header[l]) );
  }

  for ( i=l; i<252; i++ ) header[i] = '\n';
  sprintf( &(header[252]), "##}" );
  header[255] = '\n';
}

/* Fonction d'ecriture des parametres d'une image.

   L'ecriture se fait sur la sortie standard
   d'erreur (stderr).
*/
#if defined(_ANSI_)
static void VT_PR_HImage( vt_image *image /* image whose header is to be printed */,
		  int nh /* number of blocks of 256 bytes in the header */ )
#else
static void VT_PR_HImage( image, nh )
vt_image *image; /* image whose header is to be printed */
int nh; /* number of blocks of 256 bytes in the header */
#endif
{
    if ( (_VT_DEBUG_ == 0) ) return;
    (void)fprintf(stderr,"%-20s",image->name);
    (void)fprintf(stderr," hdr=%-2d",nh);
    (void)fprintf(stderr," x=%-5d",image->dim.x);
    (void)fprintf(stderr," y=%-5d",image->dim.y);
    (void)fprintf(stderr," z=%-5d",image->dim.z);
    switch ( image->cpu ) {
    case LITTLEENDIAN :
	(void)fprintf(stderr," cpu=decm    ");
	break;
    case BIGENDIAN :
	(void)fprintf(stderr," cpu=sun     ");
	break;
    case CPU_UNKNOWN :
    default :	
	(void)fprintf(stderr," cpu=inconnu");
    }
    (void)fprintf(stderr," type=");
    switch ( image->type ) {
    case SCHAR :
	(void)fprintf(stderr,"signed char");
	break;
    case UCHAR :
	(void)fprintf(stderr,"unsigned char");
	break;
    case SSHORT :
	(void)fprintf(stderr,"signed short int");
	break;
    case USHORT :
	(void)fprintf(stderr,"unsigned short int");
	break;
    case FLOAT :
	(void)fprintf(stderr,"float");
	break;
    case DOUBLE :
	(void)fprintf(stderr,"double");
	break;
    case INT :
	(void)fprintf(stderr,"signed int");
	break;
    case UINT :
	(void)fprintf(stderr,"unsigned int");
	break;
    case ULINT :
	(void)fprintf(stderr,"unsigned long int");
	break;
    case TYPE_UNKNOWN :
    default :
	(void)fprintf(stderr,"inconnu");
    }
    (void)fprintf(stderr," vs = %f %f %f",
		  image->siz.x, image->siz.y, image->siz.z );
    (void)fprintf(stderr," offs = %f %f %f",
		  image->off.x, image->off.y, image->off.z );
    (void)fprintf(stderr,"\n");
}
