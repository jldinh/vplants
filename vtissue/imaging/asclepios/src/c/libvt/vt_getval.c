
#include <vt_getval.h>

/* Calcul de la valeur entiere a partir d'une valeur double.

*/

#define COMPUTE_INT_FROM_DOUBLE( I, D ) { \
        if ( (D) < 0.0 ) (I) = ((i32)( (D) - 0.5 )); \
        else             (I) = ((i32)( (D) + 0.5 )); }

/* Calcul de la valeur entiere a partir d'une valeur double.

   Si la valeur est inferieure au MIN ou superieure ou MAX,
   on lui affecte MIN ou MAX respectivement.
*/

#define COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( I, D, MIN, MAX ) { \
        if      ( (D) < (MIN) ) (I) = (MIN); \
        else if ( (D) > (MAX) ) (I) = (MAX); \
        else if ( (D) < 0.0 )   (I) = ((i32)( (D) - 0.5 )); \
        else                    (I) = ((i32)( (D) + 0.5 )); }

/*---
  Procedures de lecture de la valeur d'un point.
---*/

/* Getting an image value, knowing x, y and z.

   Given x, y, z coordinates (the v coordinate is
   assumed to be 0), compute the image value.

   The coordinates are tested. If not in the bounds,
   the return value is 0.0.
*/
   
#if defined(_ANSI_)
double VT_GetXYZvalue( vt_image *image, int x, int y, int z )
#else
double VT_GetXYZvalue( image, x, y, z )
vt_image *image;
int x;
int y;
int z;
#endif
{
    if ( (x < 0) || (x >= image->dim.x) ) return( (double)0.0 );
    if ( (y < 0) || (y >= image->dim.y) ) return( (double)0.0 );
    if ( (z < 0) || (z >= image->dim.z) ) return( (double)0.0 );
    return( _VT_GetVXYZvalue( image, (int)0, x, y, z ) );
}

/* Getting an image value, knowing v, x, y and z.

   Given v, x, y, z coordinates,
   compute the image value.

   The coordinates are tested. If not in the bounds,
   the return value is 0.0.
*/
   
#if defined(_ANSI_)
double VT_GetVXYZvalue( vt_image *image, int v, int x, int y, int z )
#else
double VT_GetVXYZvalue( image, v, x, y, z )
vt_image *image;
int v;
int x;
int y;
int z;
#endif
{
    if ( (v < 0) || (v >= image->dim.v) ) return( (double)0.0 );
    if ( (x < 0) || (x >= image->dim.x) ) return( (double)0.0 );
    if ( (y < 0) || (y >= image->dim.y) ) return( (double)0.0 );
    if ( (z < 0) || (z >= image->dim.z) ) return( (double)0.0 );
    return( _VT_GetVXYZvalue( image, v, x, y, z ) );
}

/* Getting an image value, knowing x, y and z.

   Given x, y, z coordinates (the v coordinate is
   assumed to be 0), compute the image value.

   The coordinates are NOT tested.
*/
   
#if defined(_ANSI_)
double _VT_GetXYZvalue( vt_image *image, int x, int y, int z )
#else
double _VT_GetXYZvalue( image, x, y, z )
vt_image *image;
int x;
int y;
int z;
#endif
{
    return( _VT_GetVXYZvalue( image, (int)0, x, y, z ) );
}

/* Getting an image value, knowing v, x, y and z.

   Given v, x, y, z coordinates,
   compute the image value.

   The coordinates are NOT tested.
*/
   
#if defined(_ANSI_)
double _VT_GetVXYZvalue( vt_image *image, int v, int x, int y, int z )
#else
double _VT_GetVXYZvalue( image, v, x, y, z )
vt_image *image;
int v;
int x;
int y;
int z;
#endif
{
    switch ( image->type ) {
    case SCHAR :
        {
	s8 ***buf;
	buf = (s8***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    case UCHAR :
        {
	u8 ***buf;
	buf = (u8***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    case SSHORT :
        {
	s16 ***buf;
	buf = (s16***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    case USHORT :
        {
	u16 ***buf;
	buf = (u16***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    case FLOAT :
        {
	r32 ***buf;
	buf = (r32***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    case INT :
        {
	i32 ***buf;
	buf = (i32***)(image->array);
	return( (double)(buf[z][y][x * image->dim.v + v]) );
	}
    default :
	VT_Error( "unknown image type", "_VT_GetVXYZvalue" );
	return( (double)0.0 );
    }
    return( (double)0.0 );
}

/* Getting an image value, knowing the point index.

   Given the point index i, compute the image value.

   The index is tested. If not in the bounds,
   the return value is 0.0.
*/

#if defined(_ANSI_)
double VT_GetINDvalue( vt_image *image, int i )
#else
double VT_GetINDvalue( image, i )
vt_image *image;
int i;
#endif
{
  if ( (i < 0) || (i >= (image->dim.x * image->dim.y * image->dim.z)) )
    return( (double)0.0 );
  return( _VT_GetINDvalue( image, i ) );
}

/* Getting an image value, knowing the point index.

   Given the point index i, compute the image value.

   The index is NOT tested.
*/

#if defined(_ANSI_)
double _VT_GetINDvalue( vt_image *image, int i )
#else
double _VT_GetINDvalue( image, i )
vt_image *image;
int i;
#endif
{
    switch ( image->type ) {
    case SCHAR :
        {
	s8 *buf;
	buf = (s8*)(image->buf);
	return( (double)(buf[i]) );
	}
    case UCHAR :
        {
	u8 *buf;
	buf = (u8*)(image->buf);
	return( (double)(buf[i]) );
	}
    case SSHORT :
        {
	s16 *buf;
	buf = (s16*)(image->buf);
	return( (double)(buf[i]) );
	}
    case USHORT :
        {
	u16 *buf;
	buf = (u16*)(image->buf);
	return( (double)(buf[i]) );
	}
    case FLOAT :
        {
	r32 *buf;
	buf = (r32*)(image->buf);
	return( (double)(buf[i]) );
	}
    case INT :
        {
	i32 *buf;
	buf = (i32*)(image->buf);
	return( (double)(buf[i]) );
	}
    default :
	VT_Error( "unknown image type", "_VT_GetINDvalue" );
	return( (double)0.0 );
    }
    return( (double)0.0 );
}

/*---
  Procedures d'ecriture de la valeur d'un point.
---*/

/* Setting an image value, knowing x, y and z.

   Given x, y, z coordinates (the v coordinate is
   assumed to be 0), set the image value.

   The coordinates are tested. If not in the bounds,
   the image is not modified.
*/
   
#if defined(_ANSI_)
void VT_SetXYZvalue( vt_image *image, int x, int y, int z, double val )
#else
void VT_SetXYZvalue( image, x, y, z, val )
vt_image *image;
int x;
int y;
int z;
double val;
#endif
{
    if ( (x < 0) || (x >= image->dim.x) ) return;
    if ( (y < 0) || (y >= image->dim.y) ) return;
    if ( (z < 0) || (z >= image->dim.z) ) return;
    
    _VT_SetVXYZvalue( image, (int)0, x, y, z, val );
}

/* Setting an image value, knowing v, x, y and z.

   Given v, x, y, z coordinates,
   set the image value.

   The coordinates are tested. If not in the bounds,
   the image is not modified.
*/
   
#if defined(_ANSI_)
void VT_SetVXYZvalue( vt_image *image, int v, int x, int y, int z, double val )
#else
void VT_SetVXYZvalue( image, v, x, y, z, val )
vt_image *image;
int v;
int x;
int y;
int z;
double val;
#endif
{
    if ( (v < 0) || (v >= image->dim.v) ) return;
    if ( (x < 0) || (x >= image->dim.x) ) return;
    if ( (y < 0) || (y >= image->dim.y) ) return;
    if ( (z < 0) || (z >= image->dim.z) ) return;
 
    _VT_SetVXYZvalue( image, v, x, y, z, val );
}

/* Setting an image value, knowing x, y and z.

   Given x, y, z coordinates (the v coordinate is
   assumed to be 0), set the image value.

   The coordinates are NOT tested.
*/
   
#if defined(_ANSI_)
void _VT_SetXYZvalue( vt_image *image, int x, int y, int z, double val )
#else
void _VT_SetXYZvalue( image, x, y, z, val )
vt_image *image;
int x;
int y;
int z;
double val;
#endif
{
    _VT_SetVXYZvalue( image, (int)0, x, y, z, val );
}

/* Setting an image value, knowing v, x, y and z.

   Given v, x, y, z coordinates,
   set the image value.

   The coordinates are NOT tested.
*/
   
#if defined(_ANSI_)
void _VT_SetVXYZvalue( vt_image *image, int v, int x, int y, int z, double val )
#else
void _VT_SetVXYZvalue( image, v, x, y, z, val )
vt_image *image;
int v;
int x;
int y;
int z;
double val;
#endif
{
    i32 iv;
    
    switch ( image->type ) {
    case SCHAR :
        {
	s8 ***buf;
	buf = (s8***)(image->array);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, -128, 127 )
	buf[z][y][x * image->dim.v + v] = (s8)iv;
	return;
	}
    case UCHAR :
        {
	u8 ***buf;
	buf = (u8***)(image->array);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, 0, 255 )
	buf[z][y][x * image->dim.v + v] = (u8)iv;
	return;
	}
    case SSHORT :
        {
	s16 ***buf;
	buf = (s16***)(image->array);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, -32768, 32767 )
	buf[z][y][x * image->dim.v + v] = (s16)iv;
	return;
	}
    case USHORT :
        {
	u16 ***buf;
	buf = (u16***)(image->array);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, 0, 65535 )
	buf[z][y][x * image->dim.v + v] = (u16)iv;
	return;
	}
    case FLOAT :
        {
	r32 ***buf;
	buf = (r32***)(image->array);
	buf[z][y][x * image->dim.v + v] = (r32)val;
	return;
	}
    case INT :
        {
	i32 ***buf;
	buf = (i32***)(image->array);
	COMPUTE_INT_FROM_DOUBLE( iv, val )
	buf[z][y][x * image->dim.v + v] = (i32)iv;
	return;
	}
    default :
	VT_Error( "unknown image type", "_VT_SetVXYZvalue" );
	return;
    }
    return;
}

/* Setting an image value, knowing the point index.

   Given the point index i, set the image value.

   The index is tested. If not in the bounds,
   the image is not modified.
*/

#if defined(_ANSI_)
void VT_SetINDvalue( vt_image *image, int i, double val )
#else
void VT_SetINDvalue( image, i, val )
vt_image *image;
int i;
double val;
#endif
{
    if ( (i < 0) || (i >= (image->dim.x * image->dim.y * image->dim.z)) )
      return;
    _VT_SetINDvalue( image, i, val );
}

/* Setting an image value, knowing the point index.

   Given the point index i, set the image value.

   The index is NOT tested.
*/

#if defined(_ANSI_)
void _VT_SetINDvalue( vt_image *image, int i, double val )
#else
void _VT_SetINDvalue( image, i, val )
vt_image *image;
int i;
double val;
#endif
{
    i32 iv = 0;

    switch ( image->type ) {
    case SCHAR :
        {
	s8 *buf;
	buf = (s8*)(image->buf);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, -128, 127 )
	buf[i] = (s8)iv;
	return;
	}
    case UCHAR :
        {
	u8 *buf;
	buf = (u8*)(image->buf);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, 0, 255 )
	buf[i] = (u8)iv;
	return;
	}
    case SSHORT :
        {
	s16 *buf;
	buf = (s16*)(image->buf);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, -32768, 32767 )
	buf[i] = (s16)iv;
	return;
	}
    case USHORT :
        {
	u16 *buf;
	buf = (u16*)(image->buf);
	COMPUTE_INT_FROM_DOUBLE_WITH_MIN_AND_MAX( iv, val, 0, 65535 )
	buf[i] = (u16)iv;
	return;
	}
    case FLOAT :
        {
	r32 *buf;
	buf = (r32*)(image->buf);
	buf[i] = (r32)iv;
	return;
	}
    case INT :
        {
	i32 *buf;
	buf = (i32*)(image->buf);
	COMPUTE_INT_FROM_DOUBLE( iv, val )
	buf[i] = (i32)iv;
	return;
	}
    default :
	VT_Error( "unknown image type", "_VT_SetINDvalue" );
	return;
    }
    return;
}
