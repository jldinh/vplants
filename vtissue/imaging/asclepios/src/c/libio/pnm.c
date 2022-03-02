#ifdef _MSC_VER
#pragma warning ( disable : 4068 4786 4081 )
#endif

#include <string.h>

#include "pnm.h"




/** pnm - portable anymap file format */
/** Magic header for pgm - portable graymap file format */
#define PGM_ASCII_MAGIC "P2"
#define PGM_MAGIC "P5"

/** Magic header for ppm - portable pixmap file format */
#define PPM_ASCII_MAGIC "P3"
#define PPM_MAGIC "P6"



#define _LGTH_STRING_ 1024



int testPpmHeader(char *magic,const char *name) {
  if( !strncmp(magic, PPM_MAGIC, strlen(PPM_MAGIC))) 
    return 0;
  else 
    return -1;
}
int testPpmAsciiHeader(char *magic,const char *name) {
  if  ( !strncmp(magic, PPM_ASCII_MAGIC, strlen(PPM_ASCII_MAGIC)))
    return 0;
  else 
    return -1;
}

int testPgmHeader(char *magic,const char *name) {
  if (( !strncmp(magic, PGM_MAGIC, strlen(PGM_MAGIC))))
    return 0;
  else 
    return -1;
}
int testPgmAsciiHeader(char *magic,const char *name) {
  if  ( !strncmp(magic, PGM_ASCII_MAGIC, strlen(PGM_ASCII_MAGIC)))
    return 0;
  else 
    return -1;
}

PTRIMAGE_FORMAT createPgmFormat() {
  PTRIMAGE_FORMAT f=(PTRIMAGE_FORMAT) ImageIO_alloc(sizeof(IMAGE_FORMAT));

  f->testImageFormat=&testPgmHeader;
  f->readImageHeader=&readPgmImage;
  f->writeImage=&writePgmImage;
  strcpy(f->fileExtension,".pgm,.pgm.gz");
  strcpy(f->realName,"Pgm");
  return f;
}

PTRIMAGE_FORMAT createPgmAscIIFormat() {
  PTRIMAGE_FORMAT f=(PTRIMAGE_FORMAT) ImageIO_alloc(sizeof(IMAGE_FORMAT));

  f->testImageFormat=&testPgmAsciiHeader;
  f->readImageHeader=&readPgmAsciiImage;
  f->writeImage=&writePgmImage;
  strcpy(f->fileExtension,".pgm,.pgm.gz");
  strcpy(f->realName,"Pgm-ASCII");
  return f;
}

PTRIMAGE_FORMAT createPpmFormat() {
  PTRIMAGE_FORMAT f=(PTRIMAGE_FORMAT) ImageIO_alloc(sizeof(IMAGE_FORMAT));

  f->testImageFormat=&testPpmHeader;
  f->readImageHeader=&readPpmImage;
  f->writeImage=&writePpmImage;
  strcpy(f->fileExtension,".ppm,.ppm.gz");
  strcpy(f->realName,"Ppm");
  return f;
}

PTRIMAGE_FORMAT createPpmAscIIFormat() {
  PTRIMAGE_FORMAT f=(PTRIMAGE_FORMAT) ImageIO_alloc(sizeof(IMAGE_FORMAT));

  f->testImageFormat=&testPpmAsciiHeader;
  f->readImageHeader=&readPpmAsciiImage;
  f->writeImage=&writePpmImage;
  strcpy(f->fileExtension,".ppm,.ppm.gz");
  strcpy(f->realName,"Ppm-ASCII");
  return f;
}

/* get a string from a file and discard the ending newline character
   if any */
static char *fgetns(char *str, int n, _image *im ) 
{
  char *ret;
  int l;

  ret = ImageIO_gets( im, str, n );
  
  if(!ret) return NULL;
  l = strlen(str);
  if(l > 0 && str[l-1] == '\n') str[l-1] = '\0';
  return ret;
}


/*
       The  portable pixmap format is a lowest common denominator
       color image file format.

       The definition is as follows:

       - A  "magic  number" for identifying the file type.  A ppm
         file's magic number is the two characters "P3".

       - Whitespace (blanks, TABs, CRs, LFs).

       - A width, formatted as ASCII characters in decimal.

       - Whitespace.

       - A height, again in ASCII decimal.
       - Whitespace.

       - The maximum color value (Maxval), again in  ASCII  deci-
         mal.  Must be less than 65536.

       - Newline or other single whitespace character.

       - A raster of  Width  *  Height  gray  values,  proceeding
         through the image in normal English reading order.  Each
         gray value is a number from 0  through  Maxval,  with  0
         being  black and Maxval being white.  Each gray value is
         represented in pure binary by either 1 or 2  bytes.   If
         the  Maxval  is less than 256, it is 1 byte.  Otherwise,
         it is 2 bytes.  The most significant byte is first.

       - Characters from a "#" to the  next  end-of-line,  before
         the maxval line, are comments and are ignored.

       The difference in the plain format is:

       - There is exactly one image in a file. 

       - The magic number is P3 instead of P6. 
       
       - Each sample in the raster is represented as an ASCII decimal
       number (of arbitrary size).

       - Each sample in the raster has white space before and after
       it. There must be at least one character of white space between
       any two samples, but there is no maximum. There is no
       particular separation of one pixel from another -- just the
       required separation between the blue sample of one pixel from
       the red sample of the next pixel.  - No line should be longer
       than 70 characters.

*/
int readPpmAsciiImage(const char *name,_image *im)
{
  char string[256];
  int x=0, y=0;
  int max=0;
  
  int n;
  char *tmp;
  int iv;

  fgetns( string, 255, im );
  if ( strncmp(string, PPM_ASCII_MAGIC, strlen(PPM_ASCII_MAGIC) ) ) {
    fprintf( stderr, "readAsciiPpmImage: bad magic string in \'%s\'\n", name );
    return( -1 );
  }
  
  do {
    fgetns( string, 255, im );

    if ( string[0] != '#' ) {
      if ( x == 0 && y == 0 ) {
	sscanf( string, "%d %d", &x, &y );
      }
      else if ( max == 0 ) {
	sscanf( string, "%d", &max );
      }
    }
  } while ( max == 0 );


  im->xdim = x;
  im->ydim = y;
  im->zdim = 1;
  im->vdim = 3;

  im->wordKind = WK_FIXED;
  im->sign = SGN_UNSIGNED;

  if ( max < 256 ) im->wdim = 1;
  else if ( max < 65536 ) {
    im->wdim = 2;
    fprintf( stderr, "readPpmImage: Warning, data of \'%s\' may have to be swapped\n", name );
  }
  else {
    fprintf( stderr, "readPpmImage: max value too large (%d) in \'%s\'\n", max, name );
    return( -1 );
  }
  im->data = ImageIO_alloc( x*y*3 );		     
  
  n=0;

  while( fgetns( string, 255, im ) != 0 && n < x*y*3 ) {
    tmp = string;
    while ( *tmp != '\n' && *tmp != '\0' && *tmp != EOF && n < x*y*3 ) {
      /* skip trailing whitespace
       */
      while ( *tmp == ' ' || *tmp == '\t' )
	tmp++;
      if ( *tmp == '\0' || *tmp == '\n' || *tmp == EOF )
	continue;
      
      /* read a number
       */
      switch ( im->wordKind ) {
      case WK_FIXED :
	if ( sscanf( tmp, "%d", &iv ) != 1 ) {
	  fprintf( stderr, "readAsciiPpmImage: error in reading ascii data\n" );
	  ImageIO_free( im->data ); im->data = NULL;
	  return 0;
	}
	break;
      default :
	ImageIO_free( im->data ); im->data = NULL;
	return 0;
      }
	  
      if ( im->wdim == 1 ) {
	unsigned char *buf = (unsigned char *)im->data;
	buf += n;
	if ( iv < 0 )        *buf = (unsigned char)0;
	else if ( iv > 255 ) *buf = (unsigned char)255;
	else                 *buf = (unsigned char)iv;
	n ++;
      }
      else if ( im->wdim == 2 ) {
	unsigned short int *buf = (unsigned short int *)im->data;
	buf += n;
	if ( iv < 0 )          *buf = (unsigned short int)0;
	else if ( iv > 65535 ) *buf = (unsigned short int)65535;
	else                   *buf = (unsigned short int)iv;
	n ++;
      }
      else {
	fprintf( stderr, "readAsciiPpmImage: word im not handled\n" );
	ImageIO_free( im->data ); im->data = NULL;
	return 0;
      }
      
      /* skip a number 
       */
      while ( (*tmp >= '0' && *tmp <= '9') || *tmp == '.' || *tmp == '-' )
	tmp++;
    }
  }

  
  return 1;
}

/*
       The  portable pixmap format is a lowest common denominator
       color image file format.

       The definition is as follows:

       - A  "magic  number" for identifying the file type.  A ppm
         file's magic number is the two characters "P6".

       - Whitespace (blanks, TABs, CRs, LFs).

       - A width, formatted as ASCII characters in decimal.

       - Whitespace.

       - A height, again in ASCII decimal.
       - Whitespace.

       - The maximum color value (Maxval), again in  ASCII  deci-
         mal.  Must be less than 65536.

       - Newline or other single whitespace character.

       - A  raster  of  Width * Height pixels, proceeding through
         the image in normal English reading order.   Each  pixel
         is  a  triplet  of red, green, and blue samples, in that
         order.  Each sample is represented  in  pure  binary  by
         either 1 or 2 bytes.  If the Maxval is less than 256, it
         is 1 byte.  Otherwise, it is 2 bytes.  The most signifi-
         cant byte is first.

       - In the raster, the sample values are proportional to the
         intensity of the CIE Rec. 709 red, green,  and  blue  in
         the pixel.  A value of Maxval for all three samples rep-
         resents CIE D65 white and the most intense color in  the
         color  universe  of  which  the image is part (the color
         universe is all the colors in all images to  which  this
         image might be compared).

       - Characters  from  a  "#" to the next end-of-line, before
         the maxval line, are comments and are ignored.

*/
int readPpmImage(const char *name,_image *im)
{
  char string[256];
  int x=0, y=0;
  int max=0;
  
  fgetns( string, 255, im );
  if ( strncmp(string, PPM_MAGIC, strlen(PPM_MAGIC) ) ) {
    fprintf( stderr, "readPpmImage: bad magic string in \'%s\'\n", name );
    return( -1 );
  }
  
  do {
    fgetns( string, 255, im );

    if ( string[0] != '#' ) {
      if ( x == 0 && y == 0 ) {
	sscanf( string, "%d %d", &x, &y );
      }
      else if ( max == 0 ) {
	sscanf( string, "%d", &max );
      }
    }
  } while ( max == 0 );


  im->xdim = x;
  im->ydim = y;
  im->zdim = 1;
  im->vdim = 3;

  im->wordKind = WK_FIXED;
  im->sign = SGN_UNSIGNED;

  if ( max < 256 ) im->wdim = 1;
  else if ( max < 65536 ) {
    im->wdim = 2;
    fprintf( stderr, "readPpmImage: Warning, data of \'%s\' may have to be swapped\n", name );
  }
  else {
    fprintf( stderr, "readPpmImage: max value too large (%d) in \'%s\'\n", max, name );
    return( -1 );
  }
  im->data = ImageIO_alloc( x*y*3*im->wdim );		     
  
  ImageIO_read( im, im->data,  x*y*3*im->wdim );
  
  return 1;
}


int writePpmImage( char *name,_image *im )
{
  char string[256];
  int max;
  unsigned int i;

  if ( im->xdim <= 0 || im->ydim <= 0 || im->zdim != 1 || im->vdim != 3 ) {
    fprintf( stderr, "writePpmImage: bad dimensions, unable to write '%s'\n", name );
    return -1;
  }
  if ( im->wordKind != WK_FIXED || im->sign != SGN_UNSIGNED 
       || ( im->wdim != 1 && im->wdim != 2 ) ) {
    fprintf( stderr, "writePpmImage: bad type, unable to write '%s'\n", name );
    return -1;  
  }
  
  _openWriteImage( im, name );
  
  if(!im->fd) {
    fprintf(stderr, "writeInrimage: error: unable to open file \'%s\'\n", name );
    return ImageIO_OPENING;
  }
  
  sprintf( string, "%s\n", PPM_MAGIC );
  ImageIO_write( im, string, strlen( string ) );
  sprintf( string, "# CREATOR: pnm.c $Revision: 1.4 $ $Date: 2004/03/03 12:57:25 $\n" );
  ImageIO_write( im, string, strlen( string ) );
  sprintf( string, "%d %d\n", im->xdim, im->ydim );
  ImageIO_write( im, string, strlen( string ) );
  max = 0;
  switch ( im->wdim ) {
  case 1 :
    {
      unsigned char *buf = (unsigned char *)im->data;
      for ( i=0; i<im->xdim*im->ydim*3; i++, buf++ )
	if ( max < *buf ) max = *buf;
    }
    break;
  case 2 :
    {
      unsigned short *buf = (unsigned short *)im->data;
      for ( i=0; i<im->xdim*im->ydim*3; i++, buf++ )
	if ( max < *buf ) max = *buf;
    }
    break;
  }

  if ( max == 0 ) max = 1;
  sprintf( string, "%d\n", max );
  ImageIO_write( im, string, strlen( string ) );
  if ( im->wdim == 1 || ( im->wdim == 2 && max > 255 ) ) {
    ImageIO_write( im, im->data, im->xdim*im->ydim*3*im->wdim );
  }
  else {
    /* 2 octets, but max <= 255
       has to be converted on one octet
    */
    unsigned short *buf = (unsigned short *)im->data;
    unsigned char *tmp = (unsigned char *)ImageIO_alloc( im->xdim*im->ydim*3 );
    if ( tmp == NULL ) {
      fprintf( stderr, "writePpmImage: unable to allocate auxiliary buffer\n" );
      return -1; 
    }
    for ( i=0; i<im->xdim*im->ydim*3; i++, buf++ )
      tmp[i] = (unsigned char)*buf;
    ImageIO_write( im, tmp, im->xdim*im->ydim*3 );
    ImageIO_free( tmp );
  }
  ImageIO_close( im );
  im->openMode = OM_CLOSE;
  return 1;
}



/*
       The portable graymap format is a lowest common denominator
       grayscale file format.  The definition is as follows:

       - A "magic number" for identifying the file type.   A  pgm
         file's magic number is the two characters "P2".

       - Whitespace (blanks, TABs, CRs, LFs).

       - A width, formatted as ASCII characters in decimal.

       - Whitespace.
       - A height, again in ASCII decimal.

       - Whitespace.

       - The maximum gray value (Maxval), again in ASCII decimal.
         Must be less than 65536.

       - Newline or other single whitespace character.

       - A raster of  Width  *  Height  gray  values,  proceeding
         through the image in normal English reading order.  Each
         gray value is a number from 0  through  Maxval,  with  0
         being  black and Maxval being white.  Each gray value is
         represented in pure binary by either 1 or 2  bytes.   If
         the  Maxval  is less than 256, it is 1 byte.  Otherwise,
         it is 2 bytes.  The most significant byte is first.

       - Characters from a "#" to the  next  end-of-line,  before
         the maxval line, are comments and are ignored.
*/
int readPgmAsciiImage(const char *name,_image *im)
{
  char string[256];
  int x=0, y=0;
  int max=0;

  int n;
  char *tmp;
  int iv;

  fgetns( string, 255, im );
  if ( strncmp(string, PGM_ASCII_MAGIC, strlen(PGM_ASCII_MAGIC) ) ) {
    fprintf( stderr, "readAsciiPgmImage: bad magic string in \'%s\'\n", name );
    return( -1 );
  }
  
  do {
    fgetns( string, 255, im );

    if ( string[0] != '#' ) {
      if ( x == 0 && y == 0 ) {
	sscanf( string, "%d %d", &x, &y );
      }
      else if ( max == 0 ) {
	sscanf( string, "%d", &max );
      }
    }
  } while ( max == 0 );

  im->xdim = x;
  im->ydim = y;
  im->zdim = 1;
  im->vdim = 1;

  im->wordKind = WK_FIXED;
  im->sign = SGN_UNSIGNED;

  if ( max < 256 ) im->wdim = 1;
  else if ( max < 65536 ) {
    im->wdim = 2;
  }
  else {
    fprintf( stderr, "readAsciiPgmImage: max value too large (%d) in \'%s\'\n", max, name );
    return( -1 );
  }
  im->data = ImageIO_alloc( x*y );		     
  
  n=0;

  while( fgetns( string, 255, im ) != 0 && n < x*y ) {
    tmp = string;
    while ( *tmp != '\n' && *tmp != '\0' && *tmp != EOF && n < x*y ) {
      /* skip trailing whitespace
       */
      while ( *tmp == ' ' || *tmp == '\t' )
	tmp++;
      if ( *tmp == '\0' || *tmp == '\n' || *tmp == EOF )
	continue;
      
      /* read a number
       */
      switch ( im->wordKind ) {
      case WK_FIXED :
	if ( sscanf( tmp, "%d", &iv ) != 1 ) {
	  fprintf( stderr, "readAsciiPgmImage: error in reading ascii data\n" );
	  ImageIO_free( im->data ); im->data = NULL;
	  return 0;
	}
	break;
      default :
	ImageIO_free( im->data ); im->data = NULL;
	return 0;
      }
	  
      if ( im->wdim == 1 ) {
	unsigned char *buf = (unsigned char *)im->data;
	buf += n;
	if ( iv < 0 )        *buf = (unsigned char)0;
	else if ( iv > 255 ) *buf = (unsigned char)255;
	else                 *buf = (unsigned char)iv;
	n ++;
      }
      else if ( im->wdim == 2 ) {
	unsigned short int *buf = (unsigned short int *)im->data;
	buf += n;
	if ( iv < 0 )          *buf = (unsigned short int)0;
	else if ( iv > 65535 ) *buf = (unsigned short int)65535;
	else                   *buf = (unsigned short int)iv;
	n ++;
      }
      else {
	fprintf( stderr, "readAsciiPgmImage: word im not handled\n" );
	ImageIO_free( im->data ); im->data = NULL;
	return 0;
      }
      
      /* skip a number 
       */
      while ( (*tmp >= '0' && *tmp <= '9') || *tmp == '.' || *tmp == '-' )
	tmp++;
    }
  }

  
  return 1;
}




/*
       The portable graymap format is a lowest common denominator
       grayscale file format.  The definition is as follows:

       - A "magic number" for identifying the file type.   A  pgm
         file's magic number is the two characters "P5".

       - Whitespace (blanks, TABs, CRs, LFs).

       - A width, formatted as ASCII characters in decimal.

       - Whitespace.
       - A height, again in ASCII decimal.

       - Whitespace.

       - The maximum gray value (Maxval), again in ASCII decimal.
         Must be less than 65536.

       - Newline or other single whitespace character.

       - A raster of  Width  *  Height  gray  values,  proceeding
         through the image in normal English reading order.  Each
         gray value is a number from 0  through  Maxval,  with  0
         being  black and Maxval being white.  Each gray value is
         represented in pure binary by either 1 or 2  bytes.   If
         the  Maxval  is less than 256, it is 1 byte.  Otherwise,
         it is 2 bytes.  The most significant byte is first.

       - Characters from a "#" to the  next  end-of-line,  before
         the maxval line, are comments and are ignored.
*/
int readPgmImage(const char *name,_image *im)
{
  
  char string[256];
  int x=0, y=0;
  int max=0;
  
  fgetns( string, 255, im );
  if ( strncmp(string, PGM_MAGIC, strlen(PGM_MAGIC) ) ) {
    fprintf( stderr, "readPgmImage: bad magic string in \'%s\'\n", name );
    return( -1 );
  }
  
  do {
    fgetns( string, 255, im );

    if ( string[0] != '#' ) {
      if ( x == 0 && y == 0 ) {
	sscanf( string, "%d %d", &x, &y );
      }
      else if ( max == 0 ) {
	sscanf( string, "%d", &max );
      }
    }
  } while ( max == 0 );


  im->xdim = x;
  im->ydim = y;
  im->zdim = 1;
  im->vdim = 1;

  im->wordKind = WK_FIXED;
  im->sign = SGN_UNSIGNED;

  if ( max < 256 ) im->wdim = 1;
  else if ( max < 65536 ) {
    im->wdim = 2;
    fprintf( stderr, "readPgmImage: Warning, data of \'%s\' may have to be swapped\n", name );
  }
  else {
    fprintf( stderr, "readPgmImage: max value too large (%d) in \'%s\'\n", max, name );
    return( -1 );
  }
  im->data = ImageIO_alloc( x*y );		     
  
  ImageIO_read( im, im->data,  x*y );
  
  return 1;
}


int writePgmImage(char *name,_image *im  )
{
  char string[256];
  int max;
  unsigned int i;

  if ( im->xdim <= 0 || im->ydim <= 0 || im->zdim != 1 || im->vdim != 1 ) {
    fprintf( stderr, "writePgmImage: bad dimensions, unable to write '%s'\n", name );
    return -1;
  }
  if ( im->wordKind != WK_FIXED || im->sign != SGN_UNSIGNED 
       || ( im->wdim != 1 && im->wdim != 2 ) ) {
    fprintf( stderr, "writePgmImage: bad type, unable to write '%s'\n", name );
    return -1;  
  }

  if ( 0 )
    im->dataMode = DM_ASCII;
  
  _openWriteImage( im, name );
  
  if(!im->fd) {
    fprintf(stderr, "writePgmImage: error: unable to open file \'%s\'\n", name );
    return ImageIO_OPENING;
  }
  
  if ( im->dataMode == DM_ASCII ) 
    sprintf( string, "%s\n", PGM_ASCII_MAGIC );
  else 
    sprintf( string, "%s\n", PGM_MAGIC );
  
  ImageIO_write( im, string, strlen( string ) );
  sprintf( string, "# CREATOR: pnm.c $Revision: 1.4 $ $Date: 2004/03/03 12:57:25 $\n" );
  ImageIO_write( im, string, strlen( string ) );
  sprintf( string, "%d %d\n", im->xdim, im->ydim );
  ImageIO_write( im, string, strlen( string ) );
  max = 0;
  switch ( im->wdim ) {
  case 1 :
    {
      unsigned char *buf = (unsigned char *)im->data;
      for ( i=0; i<im->xdim*im->ydim; i++, buf++ )
	if ( max < *buf ) max = *buf;
    }
    break;
  case 2 :
    {
      unsigned short *buf = (unsigned short *)im->data;
      for ( i=0; i<im->xdim*im->ydim; i++, buf++ )
	if ( max < *buf ) max = *buf;
    }
    break;
  }
  /* max == 0 causes problems for xv */
  if ( max == 0 ) max = 1;
  sprintf( string, "%d\n", max );
  ImageIO_write( im, string, strlen( string ) );

  if ( im->dataMode == DM_ASCII ) {
    int i, j, n, size;
    char *str = (char*)ImageIO_alloc( _LGTH_STRING_+1 );
    size = im->xdim * im->ydim * im->zdim * im->vdim;
    n = ( im->xdim < 16 ) ? im->xdim : 16;
    i = 0;
    switch( im->wdim ) {
    default :
      /* can not occur */
      fprintf( stderr, "writePgmImage: bad type, unable to write '%s'\n", name );
      ImageIO_close( im );
      im->openMode = OM_CLOSE;
      return -1;
    case 1 :
      {
	unsigned char *theBuf = ( unsigned char * )im->data;
	do {
	  memset( str, 0, _LGTH_STRING_ );
	  for ( j=0; j<n && i<size; j++, i++ ) {
	    sprintf( str+strlen(str), "%d", theBuf[i] );
	    if ( j<n && i<size ) sprintf( str+strlen(str), " " );
	  }
	  sprintf( str+strlen(str), "\n" );
	  if ( ImageIO_write( im, str, strlen( str ) ) <= 0 ) {
	    fprintf(stderr, "writePgmImage: error when writing data in \'%s\'\n", name );
	    return( -3 );
	  }
	} while ( i < size );
      }
      break;
    case 2 :
      {
	unsigned short int *theBuf = ( unsigned short int * )im->data;
	do {
	  memset( str, 0, _LGTH_STRING_ );
	  for ( j=0; j<n && i<size; j++, i++ ) {
	    sprintf( str+strlen(str), "%d", theBuf[i] );
	    if ( j<n && i<size ) sprintf( str+strlen(str), " " );
	  }
	  sprintf( str+strlen(str), "\n" );
	  if ( ImageIO_write( im, str, strlen( str ) ) <= 0 ) {
	    fprintf(stderr, "writePgmImage: error when writing data in \'%s\'\n", name );
	    return( -3 );
	  }
	} while ( i < size );
      }
      break;
    }
  }
  else {
    if ( im->wdim == 1 || ( im->wdim == 2 && max > 255 ) ) {
      ImageIO_write( im, im->data, im->xdim*im->ydim*im->wdim );
    }
    else {
      /* 2 octets, but max <= 255
	 has to be converted on one octet
      */
      unsigned short *buf = (unsigned short *)im->data;
      unsigned char *tmp = (unsigned char *)ImageIO_alloc( im->xdim*im->ydim );
      if ( tmp == NULL ) {
	fprintf( stderr, "writePgmImage: unable to allocate auxiliary buffer\n" );
	return -1; 
      }
      for ( i=0; i<im->xdim*im->ydim; i++, buf++ )
	tmp[i] = (unsigned char)*buf;
      ImageIO_write( im, tmp, im->xdim*im->ydim );
      ImageIO_free( tmp );
    }
  }

  ImageIO_close( im );
  im->openMode = OM_CLOSE;
  return 1;
}



