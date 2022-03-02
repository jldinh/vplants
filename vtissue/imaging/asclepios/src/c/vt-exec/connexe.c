/*************************************************************************
 * connexe.c -
 *
 * $Id: connexe.c,v 1.4 2003/06/20 09:05:09 greg Exp $
 *
 * Copyright©INRIA 1999
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: 
 * ?
 *
 * ADDITIONS, CHANGES
 *
 * - Tue Apr 11 19:07:13 MET DST 2000, Gregoire Malandain
 *   propagation de la taille du voxel
 */

#include <vt_common.h>

#include <vt_connexe.h>

#define _VT_CONNECTED  1
#define _VT_HYSTERESIS 2
#define _VT_SEEDPT     3
#define _VT_SEEDSIM    4

typedef struct local_par {
  vt_names names;
  int type_computation;
  float low_threshold;
  float high_threshold;
  vt_ipt seed;
  vt_connexe cpar;
  int type;
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

static char *usage = "[image-in] [image-out] [-sb %f [-sh %f]]\n\
\t [-con %d] [-tcc %d] [-ncc %d] [-max] [-2D] [-bin | -labels | -size | -sort]\n\
\t [-seed %d %d %d] [-seeds %s] [-inv] [-swap] [-v] [-D] [-help] [options-de-type]";

static char *detail = "\
\t if 'image-in' is equal to '-', we consider stdin\n\
\t if 'image-out' is not specified, we consider stdout\n\
\t if both are not specified, we consider stdin and stdout\n\
\t [-sb|-lt %f] # low threshold (to binarize input image)\n\
\t [-sh|-ht %f] # high threshold for hysteresis thresholding (binary input)\n\
\t [-con %d]    # connectivity (4, 6, 8, 10, 18, 26=default)\n\
\t [-tcc %d]    # minimal size of connected components\n\
\t [-ncc %d]    # maximal number of connected components\n\
\t       if the number of valid connected components is larger than this one\n\
\t       the components are sorted with respect to their size, and the\n\
\t       largest ones are retained\n\
\t [-max]       # largest connected component (binary output)\n\
\t [-2D]        # slice by slice computation\n\
\t [-bin]       # binary output\n\
\t [-label]     # labels output (grey levels)\n\
\t [-size]      # sizes output (grey levels)\n\
\t [-sort]      # labels sorted by size\n\
\t [-seed %d %d %d] # seed point\n\
\t [-seeds %s] # seeds image (uchar type)\n\
\t [-inv]      # inverse 'image-in'\n\
\t [-swap]     # swap bytes of 'image-in' (if encoded on 2 bytes)\n\
\t -v : mode verbose\n\
\t -D : mode debug\n\
\t options-de-type : -o 1    : unsigned char\n\
\t                   -o 2    : unsigned short int\n\
\t                   -o 2 -s : short int\n\
\t                   -o 4 -s : int\n\
\t                   -r      : float\n\
\t if any of those options is specified, we consider 'image-in' type\n\
\n\
 $Revision: 1.4 $ $Date: 2003/06/20 09:05:09 $ $Author: greg $\n";

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
	vt_image *image, *imres = (vt_image *)NULL;
	vt_image imtmp;
	int retour;

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

	/*--- initialisation de l'image resultat ---*/
        VT_Image( &imtmp );
	if ( par.type == CPU_UNKNOWN || par.type == image->type ) {
	  imres = image;
	  sprintf( imres->name, "%s", par.names.out );
	} else {
	  VT_InitFromImage( &imtmp, image, par.names.out, image->type );
	  if ( par.type != CPU_UNKNOWN ) imtmp.type = par.type;
	  if ( VT_AllocImage( &imtmp ) != 1 ) {
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("unable to allocate output image\n", 0);
	  }
	  imres = &imtmp;
	}

	
	switch ( par.type_computation ) {
	case _VT_SEEDSIM :
	  {
	    vt_image *seeds;
	    seeds = _VT_Inrimage( par.names.ext );
	    if ( seeds == (vt_image*)NULL ) {
	      VT_FreeImage( image );
	      VT_Free( (void**)&image );
	      if ( par.type != CPU_UNKNOWN && par.type != image->type )
		VT_FreeImage( &imtmp );
	      VT_ErrorParse("unable to read seeds image\n", 0);
	    }
	    if ( seeds->type != UCHAR ) {
	      VT_FreeImage( image );
	      VT_Free( (void**)&image );
	      if ( par.type != CPU_UNKNOWN && par.type != image->type )
		VT_FreeImage( &imtmp );
	      VT_FreeImage( seeds );
	      VT_Free( (void**)&seeds );
	      VT_ErrorParse("seeds image type should be unsigned char\n", 0);
	    }
	    retour = VT_ConnectedComponentsWithSeeds( image, imres, par.low_threshold, seeds, &(par.cpar) );
	    VT_FreeImage( seeds );
	    VT_Free( (void**)&seeds );
	    break;
	  }
	case _VT_SEEDPT :
	  retour = VT_ConnectedComponentWithOneSeed( image, imres, par.low_threshold, &(par.seed), &(par.cpar) );
	  break;
	case _VT_HYSTERESIS :
	  retour = VT_Hysteresis( image, imres, par.low_threshold, par.high_threshold, &(par.cpar) );
	  break;
	case _VT_CONNECTED :
	default :
	  retour = VT_ConnectedComponents( image, imres, par.low_threshold, &(par.cpar) );
	}

	if ( retour == -2 && (par.type_computation == _VT_SEEDSIM || par.type_computation == _VT_SEEDPT) ) {
	  switch( imres->type ) {
	  default :
	    VT_FreeImage( image );
	    if ( par.type != CPU_UNKNOWN && par.type != image->type )
	      VT_FreeImage( &imtmp );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("such result image type not handled yet\n", 0);
	  case UCHAR :
	    memset( imres->buf, 0, 
		    imres->dim.x*imres->dim.y*imres->dim.z*imres->dim.v * sizeof(unsigned char) );
	    break;
	  case USHORT :
	    memset( imres->buf, 0, 
		    imres->dim.x*imres->dim.y*imres->dim.z*imres->dim.v * sizeof(unsigned short int) );
	    break;
	  case SSHORT :
	    memset( imres->buf, 0, 
		    imres->dim.x*imres->dim.y*imres->dim.z*imres->dim.v * sizeof(short int) );
	    break;
	  }
	} 
	else if ( retour != 1 ) {
	  VT_FreeImage( image );
	  if ( par.type != CPU_UNKNOWN && par.type != image->type )
	    VT_FreeImage( &imtmp );
	  VT_Free( (void**)&image );
	  VT_ErrorParse("unable to compute output image\n", 0);
	}

	/*--- operations eventuelles sur l'image resultat ---*/
	if ( (par.names.inv == 1) && (par.cpar.type_output == VT_BINAIRE) )
	  VT_InverseImage( imres );

	/*--- ecriture de l'image resultat ---*/
        if ( VT_WriteInrimage( imres ) == -1 ) {
	  VT_FreeImage( image );
	  if ( par.type != CPU_UNKNOWN && par.type != image->type )
	    VT_FreeImage( &imtmp );
	  VT_Free( (void**)&image );
	  VT_ErrorParse("unable to write output image\n", 0);
        }
		
	/*--- liberations memoires ---*/
	VT_FreeImage( image );
	if ( par.type != CPU_UNKNOWN && par.type != image->type )
	  VT_FreeImage( &imtmp );
	VT_Free( (void**)&image );
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
    int o=0, s=0, r=0;
    char text[STRINGLENGTH];
    int local_connexite = 0;
    
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
	    /*--- arguments generaux ---*/
	    else if ( strcmp ( argv[i], "-help" ) == 0 ) {
		VT_ErrorParse("\n", 1);
	    }
	    else if ( strcmp ( argv[i], "-v" ) == 0 ) {
		_VT_VERBOSE_ = 1;
		par->cpar.verbose = 1;
	    }
	    else if ( strcmp ( argv[i], "-D" ) == 0 ) {
		_VT_DEBUG_ = 1;
	    }
	    /*--- traitement eventuel de l'image d'entree ---*/
	    else if ( strcmp ( argv[i], "-inv" ) == 0 ) {
		par->names.inv = 1;
	    }
	    else if ( strcmp ( argv[i], "-swap" ) == 0 ) {
		par->names.swap = 1;
	    }
	    /*--- dimension du traitement ---*/
	    else if ( strcmp ( argv[i], "-2D" ) == 0 ) {
		par->cpar.dim = VT_2D;
	    }
	    /*--- connexite ---*/
	    else if ( strcmp( argv[i], "-con" ) == 0 ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse(" parsing -con...\n", 0 );
	      status = sscanf( argv[i],"%d",&local_connexite );
	      if ( status <= 0 ) VT_ErrorParse(" parsing -con...\n", 0 );
	    }
	    /*--- taille minimum des composantes ---*/
	    else if ( strcmp( argv[i], "-tcc" ) == 0 ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse(" parsing -tcc...\n", 0 );
	      status = sscanf( argv[i],"%d",&(par->cpar.min_size) );
	      if ( status <= 0 ) VT_ErrorParse(" parsing -tcc...\n", 0 );
	    }
	    /*--- nombre maximum de composantes ---*/
	    else if ( strcmp( argv[i], "-ncc" ) == 0 ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse(" parsing -ncc...\n", 0 );
	      status = sscanf( argv[i],"%d",&(par->cpar.max_nbcc) );
	      if ( status <= 0 ) VT_ErrorParse(" parsing -ncc...\n", 0 );
	    }
	    /*--- la plus grande composante connexe ----*/
	    else if ( strcmp( argv[i], "-max" ) == 0 ) {
	      par->cpar.max_nbcc = 1;
	      par->cpar.type_output = VT_BINAIRE;
	    }
	    /*--- seuil(s) ---*/
	    else if ( (strcmp ( argv[i], "-sb" ) == 0) || (strcmp ( argv[i], "-lt" ) == 0) ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse( "parsing -sb|lt...\n", 0 );
	      status = sscanf( argv[i],"%f",&(par->low_threshold) );
	      if ( status <= 0 ) VT_ErrorParse( "parsing -sb|lt...\n", 0 );
	    }
	    else if ( (strcmp ( argv[i], "-sh" ) == 0) || (strcmp ( argv[i], "-ht" ) == 0) ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse( "parsing -sh|ht...\n", 0 );
	      status = sscanf( argv[i],"%f",&(par->high_threshold) );
	      if ( status <= 0 ) VT_ErrorParse( "parsing -sh|ht...\n", 0 );
	      par->type_computation = _VT_HYSTERESIS;
	      par->cpar.type_output = VT_BINAIRE;
	    }	    
	    /*--- seeds image ---*/
	    else if ( strcmp ( argv[i], "-seeds" ) == 0 ) {
	      i += 1;
	      if ( i >= argc)    VT_ErrorParse( "parsing -seeds...\n", 0 );
	      strncpy( par->names.ext, argv[i], STRINGLENGTH );
	      par->type_computation = _VT_SEEDSIM;
	      par->cpar.type_output = VT_BINAIRE;
	    }
	    /*--- seed point ---*/
	    else if ( strcmp ( argv[i], "-seed" ) == 0 ) {
	      i += 1;
	      if ( i+2 >= argc) VT_ErrorParse(" parsing -seed...\n", 0 );
	      status =           sscanf( argv[i++],"%d",&par->seed.x );
	      status = status && sscanf( argv[i++],"%d",&par->seed.y );
	      status = status && sscanf( argv[i],  "%d",&par->seed.z );
	      if ( status <= 0 ) VT_ErrorParse(" parsing -seed...\n", 0 );
	      par->type_computation = _VT_SEEDPT;
	      par->cpar.type_output = VT_BINAIRE;
	    }
	    /*--- types de sortie ---*/
	    else if ( strcmp ( argv[i], "-bin" ) == 0 ) {
		par->cpar.type_output = VT_BINAIRE;
	    }
	    else if ( strcmp ( argv[i], "-labels" ) == 0 ) {
		par->cpar.type_output = VT_GREY;
	    }
	    else if ( strcmp ( argv[i], "-size" ) == 0 ) {
		par->cpar.type_output = VT_SIZE;
	    }
	    else if ( strcmp ( argv[i], "-sort" ) == 0 ) {
		par->cpar.type_output = VT_GREY;
		par->cpar.max_nbcc = _EQUIVALENCE_ARRAY_SIZE_;
	    }
	    /*--- lecture du type de l'image de sortie ---*/
	    else if ( strcmp ( argv[i], "-r" ) == 0 ) {
		r = 1;
	    }
	    else if ( strcmp ( argv[i], "-s" ) == 0 ) {
		s = 1;
	    }
	    else if ( strcmp ( argv[i], "-o" ) == 0 ) {
		i += 1;
		if ( i >= argc)    VT_ErrorParse( "parsing -o...\n", 0 );
		status = sscanf( argv[i],"%d",&o );
		if ( status <= 0 ) VT_ErrorParse( "parsing -o...\n", 0 );
	    }
	    /*--- option inconnue ---*/
	    else {
		sprintf(text,"unknown option %s\n",argv[i]);
		VT_ErrorParse(text, 0);
	    }
	}
	/*--- saisie des noms d'images ---*/
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
    
    /*--- s'il n'y a pas assez de noms ... ---*/
    if (nb == 0) {
	strcpy( par->names.in,  "<" );  /* standart input */
	strcpy( par->names.out, ">" );  /* standart output */
    }
    if (nb == 1)
	strcpy( par->names.out, ">" );  /* standart output */

    /*--- connexite ---*/
    switch ( local_connexite ) {
    case 4 :
      par->cpar.type_connexite = N04;   break;
    case 6 :
      par->cpar.type_connexite = N06;   break;
    case 8 :
      par->cpar.type_connexite = N08;   break;
    case 10 :
      par->cpar.type_connexite = N10;   break;
    case 18 :
      par->cpar.type_connexite = N18;   break;
    case 26 :
      par->cpar.type_connexite = N26;   break;
    }

    /*--- type de l'image resultat ---*/
    if ( (o == 1) && (s == 1) && (r == 0) )  par->type = SCHAR;
    if ( (o == 1) && (s == 0) && (r == 0) ) par->type = UCHAR;
    if ( (o == 2) && (s == 0) && (r == 0) ) par->type = USHORT;
    if ( (o == 2) && (s == 1) && (r == 0) )  par->type = SSHORT;
    if ( (o == 4) && (s == 1) && (r == 0) )  par->type = INT;
    if ( (o == 0) && (s == 0) && (r == 1) )  par->type = FLOAT;
    /* if ( par->type == CPU_UNKNOWN ) VT_Warning("no specified type", program); */
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
	par->type_computation = _VT_CONNECTED;
	par->low_threshold = (float)1.0;
	par->high_threshold = (float)0.0;
	par->seed.x = par->seed.y = par->seed.z = -1;
	VT_Connexe( &(par->cpar) );
	par->type = UCHAR;
}
