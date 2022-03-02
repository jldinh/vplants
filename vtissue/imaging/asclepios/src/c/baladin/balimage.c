
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <balimage.h>

#include <imageio/ImageIO.h>
#include <reech4x4.h>
#include <recbuffer.h>
#include <convert.h>

static int _verbose_ = 1;





/*--------------------------------------------------
 *
 * MISC
 *
 --------------------------------------------------*/



bufferType translateType( VOXELTYPE type ) 
{
  switch ( type ) {
  default : return( TYPE_UNKNOWN );
  case VT_UNSIGNED_CHAR : return ( UCHAR );
  case VT_UNSIGNED_SHORT : return ( USHORT );
  case VT_SIGNED_SHORT : return ( SSHORT );
  case VT_SIGNED_INT : return ( INT );
  case VT_UNSIGNED_LONG : return ( ULINT );
  case VT_FLOAT : return ( FLOAT );
  case VT_DOUBLE : return ( DOUBLE );
  }
  return( TYPE_UNKNOWN );
}





/*--------------------------------------------------
 *
 * IMAGE MANAGEMENT
 *
 --------------------------------------------------*/



int BAL_InitImage( bal_image *image, char *name,
		   int dimx, int dimy, int dimz, int dimv, VOXELTYPE type )
{
  if ( image == NULL ) return( -1 );

  if ( name != NULL && name[0] != '\0' && strlen(name) > 0 ) {
    image->name = (char*)malloc( (strlen(name)+1)*sizeof( char ) );
    if ( image->name == NULL ) {
      if ( _verbose_ )
	fprintf( stderr, "BAL_InitImage: can not allocate name\n" );
      return( -1 );
    }
    strcpy( image->name, name );
  }
  else
    image->name = NULL;

  image->type = type;
  
  image->ncols = dimx;
  image->nrows = dimy;
  image->nplanes = dimz;
  image->vdim = dimv;
  
  image->vx = 1.0;
  image->vy = 1.0;
  image->vz = 1.0;


  image->array = NULL;
  image->data = NULL;
  return( 1 );
}



void BAL_FreeImage( bal_image *image )
{
  if ( image->array != NULL ) free( image->array );
  image->array = NULL;
  if ( image->data != NULL ) free( image->data );
  image->data = NULL;
  if ( image->name != NULL ) free( image->name );
  image->name = NULL;
  
  image->ncols = 0;
  image->nrows = 0;
  image->nplanes = 0;
  image->vdim = 0;

  image->vx = 0.0;
  image->vy = 0.0;
  image->vz = 0.0;
}



int BAL_AllocImageArray( bal_image *image )
{
  int size=0;
  
  if ( image == NULL || image->data == NULL ) 
    return( -1 );
  if ( image->ncols * image->nrows * image->nplanes * image->vdim < 0 )
    return( -1 );
  
  switch ( image->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "BAL_AllocImageArray: image type not handled yet\n" );
    return( -1 );
  case VT_UNSIGNED_CHAR :
    size += image->nplanes * sizeof( unsigned char **);
    size += image->nplanes * image->nrows * sizeof( unsigned char *);
    break;
  case VT_UNSIGNED_SHORT :
    size += image->nplanes * sizeof( unsigned short int **);
    size += image->nplanes * image->nrows * sizeof( unsigned short int *);
    break;
  case VT_SIGNED_SHORT :
    size += image->nplanes * sizeof( short int **);
    size += image->nplanes * image->nrows * sizeof( short int *);
    break;
  }
  
  image->array = (void***)malloc( size );
  if ( image->array == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_AllocImageArray: allocation failed\n" );
    return( -1 );
  }
  return( 1 );
}



int BAL_BuildImageArray( bal_image *image )
{  
  int k, j;

  if ( image == NULL || image->data == NULL || image->array == NULL ) 
    return( -1 );
  if ( image->ncols * image->nrows * image->nplanes * image->vdim < 0 )
    return( -1 );
  
  switch ( image->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "BAL_BuildImageArray: image type not handled yet\n" );
    return( -1 );
  case VT_UNSIGNED_CHAR :
    {
      unsigned char ***z = (unsigned char ***)image->array;
      unsigned char **zy = (unsigned char **)(z + image->nplanes);
      unsigned char *zyx = (unsigned char *)(image->data);
      for ( k=0; k<image->nplanes; k++, z++ ) {
	*z = zy;
	for ( j=0 ; j < image->nrows; j++, zy++, zyx += image->ncols*image->vdim )
	  *zy = zyx;
      }
    }
    break;
  case VT_UNSIGNED_SHORT :
    {
      unsigned short int ***z = (unsigned short int ***)image->array;
      unsigned short int **zy = (unsigned short int **)(z + image->nplanes);
      unsigned short int *zyx = (unsigned short int *)(image->data);
      for ( k=0; k<image->nplanes; k++, z++ ) {
	*z = zy;
	for ( j=0 ; j < image->nrows; j++, zy++, zyx += image->ncols*image->vdim )
	  *zy = zyx;
      }
    }
    break;
  case VT_SIGNED_SHORT :
    {
      short int ***z = (short int ***)image->array;
      short int **zy = (short int **)(z + image->nplanes);
      short int *zyx = (short int *)(image->data);
      for ( k=0; k<image->nplanes; k++, z++ ) {
	*z = zy;
	for ( j=0 ; j < image->nrows; j++, zy++, zyx += image->ncols*image->vdim )
	  *zy = zyx;
      }
    }
    break;
  }
  return( 1 );
}



int BAL_AllocImage( bal_image *image )
{
  int size=0;
  
  if ( image == NULL ) 
    return( -1 );
  if ( image->ncols * image->nrows * image->nplanes * image->vdim < 0 )
    return( -1 );
  
  image->data = image->array = NULL;

  size = BAL_ImageDataSize( image );
  if ( size <= 0 ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_AllocImage: bad image size\n" );
    return( -1 );
  }

  image->data = (void*)malloc( size );
  if ( image->data == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_AllocImage: allocation failed\n" );
    return( -1 );
  }
  memset( image->data, 0, size );
  
  if ( BAL_AllocImageArray( image ) != 1 ) {
    if ( image->data != NULL ) free( image->data );
    image->data = NULL;
    return( -1 );
  }
  if ( BAL_BuildImageArray( image ) != 1 ) {
    if ( image->data != NULL ) free( image->data );
    if ( image->array != NULL ) free( image->array );
    image->data = NULL;
    image->array = NULL;
    return( -1 );
  }

  return( 1 );
}


int BAL_InitAllocImage( bal_image *image, char *name,
			int dimx, int dimy, int dimz, int dimv, VOXELTYPE type )
{
  if ( BAL_InitImage( image, name, dimx, dimy, dimz, dimv, type ) != 1 ) 
    return( -1 );
  if ( BAL_AllocImage( image ) != 1 ) {
    BAL_FreeImage( image );
    return( -1 );
  }
  return( 1 );
}



int BAL_CopyImage( bal_image *theIm, bal_image *resIm )
{
  bufferType theType = translateType( theIm->type );
  bufferType resType = translateType( resIm->type );
 
  if ( theIm->ncols != resIm->ncols 
       || theIm->nrows != resIm->nrows 
       || theIm->nplanes != resIm->nplanes 
       || theIm->vdim != resIm->vdim ) {
    if ( _verbose_ ) 
      fprintf( stderr, "BAL_CopyImage: image have different dimensions\n" );
    return( -1 );
  }
  if ( theType == TYPE_UNKNOWN || resType == TYPE_UNKNOWN ) {
    if ( _verbose_ ) 
      fprintf( stderr, "BAL_CopyImage: unable to deal with such image types\n" );
    return( -1 );
  }

  ConvertBuffer( theIm->data, theType, resIm->data, resType, 
		 theIm->ncols * theIm->nrows * theIm->nplanes * theIm->vdim );
  return( 1 );
       
}



int BAL_ImageDataSize( bal_image *image )
{
  int size=0;
  
  if ( image == NULL ) 
    return( -1 );
  if ( image->ncols * image->nrows * image->nplanes * image->vdim < 0 )
    return( -1 );
  
  switch ( image->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "BAL_ImageDataSize: image type not handled yet\n" );
    return( -1 );
  case VT_UNSIGNED_CHAR :
    size = sizeof( unsigned char );
    break;
  case VT_UNSIGNED_SHORT :
    size = sizeof( unsigned short int );
    break;
  case VT_SIGNED_SHORT :
    size = sizeof( short int );
    break;
  }
  size *= image->ncols * image->nrows * image->nplanes * image->vdim;
  return( size );
}










/*--------------------------------------------------
 *
 * IMAGE I/O
 *
 --------------------------------------------------*/



int BAL_ReadImage( bal_image *image, char *name )
{
  _image *theIm;
  VOXELTYPE type=VT_UNSIGNED_CHAR;
  int size;
  
  theIm = _readImage( name );
  if ( theIm == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_ReadImage: unable to read '%s'\n", name );
    return( -1 );
  }
  
  switch( theIm->wordKind ) {
  default :
  case WK_FLOAT :
    if ( _verbose_ )
      fprintf( stderr, "BAL_ReadImage: such word kind not handled yet\n" );
    _freeImage( theIm );
    return( -1 );
  case WK_FIXED :
    switch( theIm->sign ) {
    default :
      if ( _verbose_ )
	fprintf( stderr, "BAL_ReadImage: such sign not handled yet\n" );
      _freeImage( theIm );
      return( -1 );
    case SGN_SIGNED :
      switch( theIm->wdim ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "BAL_ReadImage: such signed word dim not handled yet\n" );
	_freeImage( theIm );
	return( -1 );
      case 2 :
	type = VT_SIGNED_SHORT;
	break;
      }
      break;
    case SGN_UNSIGNED :
      switch( theIm->wdim ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "BAL_ReadImage: such unsigned word dim not handled yet\n" );
	_freeImage( theIm );
	return( -1 );
      case 1 :
	type = VT_UNSIGNED_CHAR;
	break;
      case 2 :
	type = VT_UNSIGNED_SHORT;
	break;
      }
      break;
    } /* switch( theIm->sign ) */
    break;
  }

  if ( BAL_InitImage( image, name, theIm->xdim, theIm->ydim, 
		      theIm->zdim, theIm->vdim, type ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_ReadImage: unable to initialize image '%s'\n", name );
    _freeImage( theIm );
    return( -1 );
  }

  image->vx = theIm->vx;
  image->vy = theIm->vy;
  image->vz = theIm->vz;

  if ( BAL_AllocImage( image ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_ReadImage: unable to allocate image '%s'\n", name );
    _freeImage( theIm );
    return( -1 );
  }

  size = BAL_ImageDataSize( image );
  if ( size <= 0 ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_ReadImage: can not copy raw data of '%s'\n", name );
    _freeImage( theIm );
    return( -1 );
  }

  (void)memcpy( image->data, theIm->data, size );
  _freeImage( theIm );
  return( 1 );
}



int BAL_WriteImage( bal_image *image, char *name )
{
  _image *theIm = _initImage();
  
  if ( theIm == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_WriteImage: unable to allocate structure for '%s'\n", name );
    return( -1 );
  }

  theIm->xdim = image->ncols;
  theIm->ydim = image->nrows;
  theIm->zdim = image->nplanes;
  theIm->vdim = image->vdim;

  theIm->vx = image->vx;
  theIm->vy = image->vy;
  theIm->vz = image->vz;

  switch( image->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "BAL_WriteImage: such type not handled yet\n" );
    _freeImage( theIm );
    return( -1 );
  case VT_UNSIGNED_CHAR :
    theIm->wdim = 1;
    theIm->wordKind = WK_FIXED;
    theIm->sign = SGN_UNSIGNED;
    break;
  case VT_UNSIGNED_SHORT :
    theIm->wdim = 2;
    theIm->wordKind = WK_FIXED;
    theIm->sign = SGN_UNSIGNED;
    break;
  case VT_SIGNED_SHORT :
    theIm->wdim = 2;
    theIm->wordKind = WK_FIXED;
    theIm->sign = SGN_SIGNED;
    break;
  }
  
  theIm->data = image->data;

  if ( _writeImage( theIm, name ) != 0 ) {
    if ( _verbose_ )
      fprintf( stderr, "BAL_WriteImage: unable to write '%s'\n", name );
    theIm->data = NULL;
    _freeImage( theIm );
    return( -1 );
  }
  
  theIm->data =NULL;
  _freeImage( theIm );
  return( 1 );
}










/*--------------------------------------------------
 *
 * IMAGE RESAMPLING
 *
 --------------------------------------------------*/



int BAL_Reech3DTriLin4x4( bal_image *theIm, bal_image *resIm,
			   double *m )
{
  char *proc = "BAL_Reech3DTriLin4x4";
  int theDim[3];
  int resDim[3];

  if ( theIm->type != resIm->type ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: images have different types\n", proc );
    return( -1 );
  }

  theDim[0] = theIm->ncols;
  theDim[1] = theIm->nrows;
  theDim[2] = theIm->nplanes;
  
  resDim[0] = resIm->ncols;
  resDim[1] = resIm->nrows;
  resDim[2] = resIm->nplanes;

  switch( theIm->type ) {
  default :
    if ( _verbose_ )
      fprintf(stderr, "%s: such type not handled yet\n", proc );
    return( -1 );
  case VT_UNSIGNED_CHAR :
    if ( theIm->nplanes == 1 && resIm->nplanes == 1 )
      Reech2DTriLin4x4_u8( theIm->data, theDim, resIm->data, resDim, m );
    else
      Reech3DTriLin4x4_u8( theIm->data, theDim, resIm->data, resDim, m );
    break;
  case VT_SIGNED_SHORT :
    if ( theIm->nplanes == 1 && resIm->nplanes == 1 )
      Reech2DTriLin4x4_s16( theIm->data, theDim, resIm->data, resDim, m );
    else
      Reech3DTriLin4x4_s16( theIm->data, theDim, resIm->data, resDim, m );
    break;
  case VT_UNSIGNED_SHORT :
    if ( theIm->nplanes == 1 && resIm->nplanes == 1 )
      Reech2DTriLin4x4_u16( theIm->data, theDim, resIm->data, resDim, m );
    else
      Reech3DTriLin4x4_u16( theIm->data, theDim, resIm->data, resDim, m );
    break;
  }
  return( 1 );
}










/*--------------------------------------------------
 *
 * IMAGE FILTERING
 *
 --------------------------------------------------*/



int BAL_SmoothImage( bal_image *theIm,
		     recursiveFilterType theFilter, double sigma )
{
  return( BAL_SmoothImageIntoImage( theIm, theIm, theFilter, sigma ) );
}


int BAL_SmoothImageIntoImage( bal_image *theIm, bal_image *resIm,
			      recursiveFilterType theFilter, double sigma )
{
  char *proc = "BAL_SmoothImageIntoImage";
  bufferType theType = TYPE_UNKNOWN;
  bufferType resType = TYPE_UNKNOWN;
  int theDim[3];
  int borders[3];
  derivativeOrder derivatives[3];
  float coeffs[3];
  
  theType = translateType( theIm->type );
  resType = translateType( theIm->type );
  if ( theType == TYPE_UNKNOWN || resType == TYPE_UNKNOWN ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to deal with such image type\n", proc );
    return( -1 );
  }
  
  if ( theIm->ncols != resIm->ncols || theIm->nrows != resIm->nrows
       || theIm->nplanes != resIm->nplanes ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: images should have the same dimensions\n", proc );
    return( -1 );
  }

  theDim[0] = theIm->ncols;
  theDim[1] = theIm->nrows;
  theDim[2] = theIm->nplanes;

  borders[0] = (int)floor( sigma );
  borders[1] = (int)floor( sigma );
  borders[2] = (int)floor( sigma );

  derivatives[0] = SMOOTHING;
  derivatives[1] = SMOOTHING;
  derivatives[2] = ( theIm->nplanes > 1 ) ? SMOOTHING : NODERIVATIVE;
  
  coeffs[0] = sigma;
  coeffs[1] = sigma;
  coeffs[2] = sigma;

  if ( RecursiveFilterOnBuffer( (void*)theIm->data, theType,
				(void*)resIm->data, resType,
				theDim, borders, derivatives,
				coeffs, theFilter ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to smooth image\n", proc );
    return( -1 );
  }

  return( 1 );
}
