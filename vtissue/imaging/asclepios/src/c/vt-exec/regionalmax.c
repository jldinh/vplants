/*************************************************************************
 * regionalmax.c - extraction des maxima regionaux
 *
 * $Id$
 *
 * DESCRIPTION: 
 *
 *
 *
 *
 *
 * AUTHOR:
 * Gregoire Malandain
 *
 * CREATION DATE:
 * Tue Jul 22 11:00:11 CEST 2008
 *
 * Copyright Gregoire Malandain, INRIA
 *
 *
 * ADDITIONS, CHANGES:
 *
 *
 */

#include <vt_common.h>
#include <vt_histo.h>
#include <regionalmax.h>

typedef struct local_par {
  vt_names names;

  double height;
  double heightMultiplier;
  
  int method;

} local_par;

/*------- Definition des fonctions statiques ----------*/
#ifndef NO_PROTO
static void VT_Parse( int argc, char *argv[], local_par *par );
static void VT_ErrorParse( char *str, int l );
static void VT_InitParam( local_par *par );
#else 
static void VT_Parse();
static void VT_ErrorParse();
static void VT_InitParam();
#endif

#ifndef NO_PROTO

static char *usage = "[image-in] [image-out]\n\
\t [-h %d] [-hm %lf]\n\
\t [-inv] [-swap] [-v] [-D] [-help]";

static char *detail = "\
\t si 'image-in' est '-', on prendra stdin\n\
\t si 'image-out' est absent, on prendra stdout\n\
\t si les deux sont absents, on prendra stdin et stdout\n\
\t -h %d  : hauteur du maximum\n\
\t -hm %lf : coefficient multiplicateur\n\
\t\t actif uniquement pour type UCHAR et USHORT\n\
\t \n\
\t la recherche du maximum se fait en dilatant MIN( distance*hm , distance-h )\n\
\t 'en-dessous' de l'image originale, puis en soutrayant.\n\
\t\n\
\t -inv : inverse 'image-in'\n\
\t -swap : swap 'image-in' (si elle est codee sur 2 octets)\n\
\t -v : mode verbose\n\
\t -D : mode debug\n";

#else

static char *usage = "";
static char *detail = "";

#endif

static char program[STRINGLENGTH];

#ifndef NO_PROTO
int main( int argc, char *argv[] )
#else
int main( argc, argv )
int argc;
char *argv[];
#endif
{
	local_par par;
	vt_image *image, imres;
	u16 *theBuf = NULL;
	u8 *resBuf = NULL;
	int dim[3];

	int i, v;
	vt_3m m;
	double t, a=1.0, b=0.0;
	double min, max, sum;

	int h;
	double hm;

	int r;

	m.min = m.moy = m.max = m.ect = (double)0.0;

	/*--- initialisation des parametres ---*/
	VT_InitParam( &par );
	/*--- lecture des parametres ---*/
	VT_Parse( argc, argv, &par );

	/*--- lecture de l'image d'entree ---*/
	image = _VT_Inrimage( par.names.in );
	if ( image == (vt_image*)NULL ) 
		VT_ErrorParse("unable to read input image\n", 0);

	/*--- operations eventuelles sur l'image d'entree ---*/
	if ( par.names.inv == 1 )  VT_InverseImage( image );
	if ( par.names.swap == 1 ) VT_SwapImage( image );


	dim[0] = image->dim.x;
	dim[1] = image->dim.y;
	dim[2] = image->dim.z;
	v = dim[0] * dim[1] * dim[2];


	/*--- allocations :
	  on alloue pour les types autres que UCHAR et USHORT 
	  ---*/

	switch( image->type ) {

	case UCHAR :
	case USHORT :
	case SSHORT :
	  break;

	case UINT :
	case FLOAT :
	case DOUBLE :
	  theBuf = (u16*)malloc( v * sizeof(u16) );
	  if ( theBuf == (u16*)NULL ) {
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("unable to allocate auxiliary buffer\n", 0);
	  }	  
	  break;
	  
	default :
	  VT_FreeImage( image );
	  VT_Free( (void**)&image );
	  VT_ErrorParse("such image type not handled yet\n", 0);
	}



	/*--- pre-processing ---*/
	
	switch ( image->type ) {

	case UCHAR :
	case USHORT :
	  break;

	case SSHORT :
	  {
	    s16 *buf = (s16*)image->buf;
	    u16 *auxBuf = (u16*)image->buf;
	    m.min = buf[0];
	    for ( i=0; i<v; i++ ) {
	      if ( m.min > buf[i] ) m.min = buf[i];
	      auxBuf[i] = buf[i] + 32768; 
	    }
	  }
	  break;

        case UINT :
	case FLOAT :
	case DOUBLE :
	  if ( VT_3m( image, &m ) == -1 ) {
	    free( theBuf );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("unable to compute minimum, mean and maximum\n", 0);
	  }
	  if ( m.max == m.min ) {
	    free( theBuf );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("uniform image\n", 0);
	  }
	  a = 65535.0 / ( m.max - m.min );
	  b = - m.min;

	  fprintf( stderr, " input image statistics: min=%lf - mean=%lf - max=%lf\n", m.min, m.moy, m.max );
	  fprintf( stderr, " input image normalized by (int)((I + %lf) * %lf + 0.5)\n", b, a );


	  switch ( image->type ) {
	  case UINT :
	    {
	      u32 *buf = (u32*)image->buf;
	      for ( i=0; i<v; i++ ) {
		t = ((double)buf[i] + b) * a;
		if ( t < 0 ) theBuf[i] = 0;
		else if ( t > 65535 ) theBuf[i] = 65535;
		else theBuf[i] = (int)( t + 0.5 );
	      }
	    }
	    break;
	  case FLOAT :
	    {
	      r32 *buf = (r32*)image->buf;
	      for ( i=0; i<v; i++ ) {
		t = ((double)buf[i] + b) * a;
		if ( t < 0 ) theBuf[i] = 0;
		else if ( t > 65535 ) theBuf[i] = 65535;
		else theBuf[i] = (int)( t + 0.5 );
	      }
	    }
	    break;
	  case DOUBLE :
	    {
	      r64 *buf = (r64*)image->buf;
	      for ( i=0; i<v; i++ ) {
		t = ((double)buf[i] + b) * a;
		if ( t < 0 ) theBuf[i] = 0;
		else if ( t > 65535 ) theBuf[i] = 65535;
		else theBuf[i] = (int)( t + 0.5 );
	      }
	    }
	    break;
	  default :
	    VT_ErrorParse("such image type not handled yet (but should here)\n", 0);
	  }

	  min = max = theBuf[0];
	  sum = 0;
	  for ( i=0; i<v; i++ ) {
	    if ( min > theBuf[i] ) min = theBuf[i];
	    if ( max < theBuf[i] ) max = theBuf[i];
	    sum += theBuf[i];
	  }
	  
	  fprintf( stderr, " auxi. image statistics: min=%lf - mean=%lf - max=%lf\n", min, sum/v, max );
	  
	  break;

	default :
	  VT_ErrorParse("such image type not handled yet\n", 0);
	}

	

	/*--- parameters ---*/

	switch ( image->type ) {
	case UCHAR :
	case USHORT :
	case SSHORT :
	  h = (int)( par.height + 0.5 );
	  if ( h < 1 ) h = 1;
	  break;
	case UINT :
	case FLOAT :
	case DOUBLE :
	  h = par.height * a;
	  break;
	default :
	  h = 1;
	}

	switch ( image->type ) {
	case UCHAR :
	case USHORT :
	  hm = par.heightMultiplier;
	  if ( hm <= 0.0 || hm > 1.0 ) hm = 1.0;
	  break;
	case SSHORT :
	case UINT :
	case FLOAT :
	case DOUBLE :
	  if ( m.min < 0.0 ) {
	    hm = 1.0;
	    fprintf( stderr, "%s: height multiplier set to 1.0\n", program );
	  }
	  else
	    hm = par.heightMultiplier * a;
	  break;
	default :
	  hm = 1.0;
	}

	

	/*--- processing ---*/
	
	switch ( image->type ) {
	case UCHAR :
	case USHORT :
	  r = regionalmax( image->buf, image->buf, image->type, dim, h, hm );
	  break;
	case SSHORT :
	  r = regionalmax( image->buf, image->buf, USHORT, dim, h, hm );
	  break;
	case UINT :
	case FLOAT :
	case DOUBLE :
	  r = regionalmax( theBuf, theBuf, USHORT, dim, h, hm );
	  break;
	default :
	  VT_ErrorParse("such image type not handled yet\n", 0);
	}

	
	/*--- producing the result ---*/
	VT_Image( &imres );
	VT_InitFromImage( &imres, image, par.names.out, UCHAR );
	if ( VT_AllocImage( &imres ) != 1 ) {
	  if ( theBuf != NULL ) free( theBuf );
	  VT_FreeImage( image );
	  VT_Free( (void**)&image );
	  VT_ErrorParse("unable to allocate output image\n", 0);
	}
	resBuf = (u8*)imres.buf;
	
	switch ( image->type ) {
	case UCHAR :
	  {
	    u8 *buf = (u8*)image->buf;
	    for (i=0; i<v; i++ ) 
	      resBuf[i] = ( buf[i] > 0 ) ? 255 : 0 ;
	  }
	  break;
	case USHORT :
	case SSHORT :
	  {
	    u16 *buf = (u16*)image->buf;
	    for (i=0; i<v; i++ ) 
	      resBuf[i] = ( buf[i] > 0 ) ? 255 : 0 ;
	  }
	  break;
	case UINT :
	case FLOAT :
	case DOUBLE :
	  for (i=0; i<v; i++ ) 
	    resBuf[i] = ( theBuf[i] > 0 ) ? 255 : 0 ;
	  break;
	default :
	  VT_ErrorParse("such image type not handled yet\n", 0);
	}

	
	
	/*--- liberations memoires ---*/
	if ( theBuf != NULL ) free( theBuf );
	VT_FreeImage( image );
	VT_Free( (void**)&image );

	/*--- ecriture de l'image resultat ---*/
	if ( VT_WriteInrimage( &imres ) == -1 ) {
	  VT_FreeImage( &imres );
	  VT_ErrorParse("unable to write output image 1\n", 0);
	}
	
	/*--- liberations memoires ---*/
	VT_FreeImage( &imres );

	return( 1 );
}





#ifndef NO_PROTO
static void VT_Parse( int argc, char *argv[], local_par *par )
#else
static void VT_Parse( argc, argv, par )
int argc;
char *argv[];
local_par *par;
#endif
{
  int i, nb, status;
  char text[STRINGLENGTH];
  
  if ( VT_CopyName( program, argv[0] ) != 1 )
    VT_Error("Error while copying program name", (char*)NULL);
  if ( argc == 1 ) VT_ErrorParse("\n", 0 );
  
  /*--- lecture des parametres ---*/
  i = 1; nb = 0;
  while ( i < argc ) {
    if ( argv[i][0] == '-' ) {
      if ( argv[i][1] == '\0' ) {
	if ( nb == 0 ) {
	  /*--- standart input ---*/
	  strcpy( par->names.in, "<" );
	  nb += 1;
	}
      }
      else if ( strcmp ( argv[i], "-help" ) == 0 ) {
	VT_ErrorParse("\n", 1);
      }
      else if ( strcmp ( argv[i], "-inv" ) == 0 ) {
	par->names.inv = 1;
      }
      else if ( strcmp ( argv[i], "-swap" ) == 0 ) {
	par->names.swap = 1;
      }
      else if ( strcmp ( argv[i], "-v" ) == 0 ) {
	_VT_VERBOSE_ = 1;
	regionalmax_setverbose();
      }
      else if ( strcmp ( argv[i], "-D" ) == 0 ) {
	_VT_DEBUG_ = 1;
      }
      
      /*--- seuil ---*/

      else if ( strcmp ( argv[i], "-h" ) == 0 ) {
	i += 1;
	if ( i >= argc)    VT_ErrorParse( "parsing -h...\n", 0 );
	status = sscanf( argv[i],"%lf",&(par->height) );
	if ( status <= 0 ) VT_ErrorParse( "parsing -h...\n", 0 );
      }
      else if ( strcmp ( argv[i], "-hm" ) == 0 ) {
	i += 1;
	if ( i >= argc)    VT_ErrorParse( "parsing -hm...\n", 0 );
	status = sscanf( argv[i],"%lf",&(par->heightMultiplier) );
	if ( status <= 0 ) VT_ErrorParse( "parsing -hm...\n", 0 );
      }


      /*--- unknown option ---*/
      else {
	sprintf(text,"unknown option %s\n",argv[i]);
	VT_ErrorParse(text, 0);
      }
    }
    else if ( argv[i][0] != 0 ) {
      if ( nb == 0 ) { 
	strncpy( par->names.in, argv[i], STRINGLENGTH );  
	nb += 1;
      }
      else if ( nb == 1 ) { 
	strncpy( par->names.out, argv[i], STRINGLENGTH );  
	nb += 1;
      }
      else 
	VT_ErrorParse("too much file names when parsing\n", 0 );
    }
    i += 1;
  }
  
}

#ifndef NO_PROTO
static void VT_ErrorParse( char *str, int flag )
#else
static void VT_ErrorParse( str, flag )
char *str;
int flag;
#endif
{
	(void)fprintf(stderr,"Usage : %s %s\n",program, usage);
        if ( flag == 1 ) (void)fprintf(stderr,"%s",detail);
        (void)fprintf(stderr,"Erreur : %s",str);
        exit(0);
}

#ifndef NO_PROTO
static void VT_InitParam( local_par *par )
#else
static void VT_InitParam( par )
local_par *par;
#endif
{
	VT_Names( &(par->names) );
	par->height = 1.0;
	par->heightMultiplier = 1.0;
}
