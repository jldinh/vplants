/*************************************************************************
 * morpho.c -
 *
 * $Id: morpho.c,v 1.7 2006/04/14 08:37:38 greg Exp $
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
#include <vt_morpho.h>
#include <morphotools.h>

typedef enum {
  VT_DILATION = 1,
  VT_EROSION = 2,
  VT_CLOSING = 3,
  VT_OPENING  = 4,
  VT_CLOSINGHAT  = 5,
  VT_OPENINGHAT  = 6,
  VT_CONTRAST = 7
} TypeOperation;





typedef struct local_par {
  vt_names names;
  TypeOperation type_operation;
  int nb_iterations; 
  Neighborhood connexite;
  DimType dim;
  int binary_mode;
  int radius;
} local_par;






static int Neighborhood2Int ( Neighborhood N )
{
  int connectivity = 26;
  switch ( N ) {
  case N04 :
    connectivity = 4; break;
  case N06 :
    connectivity = 6; break;
  case N08 :
    connectivity = 8; break;
  case N10 :
    connectivity = 10; break;
  case N18 :
    connectivity = 18; break;
  case N26 :
    connectivity = 26; break;
  }
  return( connectivity );
}



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

static char *usage = "[image-in] [image-out] [-i %d] [-con %d | -elt %s]\n\
\t [-dil | -ero | -fer | -clo | -ouv | -ope]\n\
\t [-hfer | -hclo | -houv | -hope]\n\
\t [-contrast]\n\
\t [-2D] [-bin] [-radius | -R %d]\n\
\t [-inv] [-swap] [-v] [-D] [-help] [options-de-type]";

static char *detail = "\
\t if 'image-in' is equal to '-', we consider stdin\n\
\t if 'image-out' is not specified, we consider stdout\n\
\t if both are not specified, we consider stdin and stdout\n\
\t [-dil]      # dilation (default)\n\
\t [-ero]      # erosion\n\
\t [-fer,-clo] # closing (dilation then erosion)\n\
\t [-ouv,-ope] # opening (erosion then dilation)\n\
\t [-hfer,-hclo] # hat transform (closing - 'image-in')\n\
\t [-houv,-hope] # inverse hat transform ('image-in' - opening)\n\
\t [-contrast] # contrast enhancement\n\
\t [-i %d]     # iterations number\n\
\t [-con %d]   # structuring element (connectivity): 4, 6, 8, 10, 26\n\
\t             # default = 26\n\
\t [-elt %s]   # user-defined structuring element\n\
\t       the file has to begin with the dimension of the box\n\
\t       which contains the structuring element, eg:\n\
\t       'XDIM=3'\n\
\t       'YDIM=3'\n\
\t       'ZDIM=1'\n\
\t       lines beginning with '#' are ignored\n\
\t       points of the structuring element are indicated with positive\n\
\t       numbers except for the center which should be indicated with '+'\n\
\t       if it belongs to the SE, else with '-'. Eg:\n\
\t       '1 1 1'\n\
\t       '1 + 1'\n\
\t       '1 1 1'\n\
\t       is the classical 3x3 dilation\n\
\t [-2D]       # slice by slice computation\n\
\t [-inv]      # inverse 'image-in'\n\
\t [-swap]     # swap bytes of 'image-in' (if encoded on 2 bytes)\n\
\t -v : mode verbose\n\
\t -D : mode debug\n\
\n\
 $Revision: 1.7 $ $Date: 2006/04/14 08:37:38 $ $Author: greg $\n";

static char program[STRINGLENGTH];

#if defined(_ANSI_)
int main( int argc, char *argv[] )
#else
int main( argc, argv )
int argc;
char *argv[];
#endif
{
	local_par par;
	vt_image *image, imtmp, imres;
	Neighborhood local_connexite;
	typeStructuringElement SE;
	int theDim[3];
	
	/*--- initialisation des parametres ---*/
	VT_InitParam( &par );
	initStructuringElement( &SE );

	/*--- lecture des parametres ---*/
	VT_Parse( argc, argv, &par );

	/*--- lecture de l'image d'entree ---*/
	image = _VT_Inrimage( par.names.in );
	if ( image == (vt_image*)NULL ) 
		VT_ErrorParse("unable to read input image\n", 0);

	/*--- operations eventuelles sur l'image d'entree ---*/
	if ( par.names.inv == 1 )  VT_InverseImage( image );
	if ( par.names.swap == 1 ) VT_SwapImage( image );

	
	if ( par.names.ext[0] != '\0' ) {
	  if ( readStructuringElement( par.names.ext, &SE ) != 1 ) {
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("unable to read structuring element\n", 0);
	  }
	}
	SE.nbIterations = par.nb_iterations;
	local_connexite = par.connexite;
	if ( par.dim == TwoD ) {
	  SE.dimension = 2;
	  switch ( par.connexite ) {	
	  default :
	    break;
	  case N06 :
	    local_connexite = N04;
	    break;
	  case N10 :
	  case N18 :
	  case N26 :
	    local_connexite = N08;
	  }
	}
	SE.connectivity = Neighborhood2Int( local_connexite );
	if ( par.radius > 0 ) SE.radius = par.radius;
	if ( par.binary_mode ) useBinaryMorphologicalOperations();
	theDim[0] = image->dim.x;
	theDim[1] = image->dim.y;
	theDim[2] = image->dim.z;


	/*--- initialisation de l'image resultat ---*/
        VT_Image( &imres );
	VT_InitFromImage( &imres, image, par.names.out, image->type );
        if ( VT_AllocImage( &imres ) != 1 ) {
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("unable to allocate output image\n", 0);
        }
	
	
	switch ( par.type_operation ) {

	case VT_CONTRAST :

	  VT_Image( &imtmp );
	  VT_InitFromImage( &imtmp, image, "tmp.inr", image->type );
          if ( VT_AllocImage( &imtmp ) != 1 ) {
	      VT_FreeImage( &imres );
 	      freeStructuringElement( &SE );
	      VT_FreeImage( image );
	      VT_Free( (void**)&image );
	      VT_ErrorParse("unable to allocate auxiliary image\n", 0);
          }

	  if ( morphologicalDilation( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imtmp );
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (contrast)\n", 0);
	  }
	  if ( morphologicalErosion( image->buf, imtmp.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imtmp );
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (contrast)\n", 0);
	  }
  
          switch ( image->type ) {
          case UCHAR :
            {
              u8 *ori = (u8 *)image->buf;
              u8 *dil = (u8 *)imres.buf;
              u8 *ero = (u8 *)imtmp.buf;
              u8 *res = (u8 *)imres.buf;
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, ori++, ero++, dil++, res++ ) {
                if ( (*dil)-(*ori) > (*ori)-(*ero) ) 
	          *res = *ero;
                else if ( (*dil)-(*ori) < (*ori)-(*ero) )
                  *res = *dil;
                else
                  *res = *ori;
              }
            }
            break;
          case USHORT :
            {
              u16 *ori = (u16 *)image->buf;
              u16 *dil = (u16 *)imres.buf;
              u16 *ero = (u16 *)imtmp.buf;
              u16 *res = (u16 *)imres.buf;
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, ori++, ero++, dil++, res++ ) {
                if ( (*dil)-(*ori) > (*ori)-(*ero) ) 
	          *res = *ero;
                else if ( (*dil)-(*ori) < (*ori)-(*ero) )
                  *res = *dil;
                else
                  *res = *ori;
              }
            }
            break;
          case SSHORT :
            {
              s16 *ori = (s16 *)image->buf;
              s16 *dil = (s16 *)imres.buf;
              s16 *ero = (s16 *)imtmp.buf;
              s16 *res = (s16 *)imres.buf;
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, ori++, ero++, dil++, res++ ) {
                if ( (*dil)-(*ori) > (*ori)-(*ero) ) 
	          *res = *ero;
                else if ( (*dil)-(*ori) < (*ori)-(*ero) )
                  *res = *dil;
                else
                  *res = *ori;
              }
            }
            break;
	  default :
	    VT_FreeImage( &imtmp );
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("output image type unknown or not supported (contrast)\n", 0);
          }

	  break;

	case VT_CLOSINGHAT :
	  
	  if ( morphologicalDilation( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (closing hat)\n", 0);
	  }
	  if ( morphologicalErosion( imres.buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (closing hat)\n", 0);
	  }
	  
	  switch ( image->type ) {
	  case UCHAR :
	    {
	      u8 *in = (u8 *)(image->buf);
	      u8 *out = (u8 *)(imres.buf);
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, in++, out++ )
		*out -= *in;
	    }
	    break;
	  case SSHORT :
	    {
	      s16 *in = (s16 *)(image->buf);
	      s16 *out = (s16 *)(imres.buf);
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, in++, out++ )
		*out -= *in;
	    }
	    break;
	  default :
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("output image type unknown or not supported (closing hat)\n", 0);
	  }
	  break;

	case VT_OPENINGHAT :
	  
	  if ( morphologicalErosion( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (opening hat)\n", 0);
	  }
	  if ( morphologicalDilation( imres.buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (opening hat)\n", 0);
	  }

	  switch ( image->type ) {
	  case UCHAR :
	    {
	      u8 *in = (u8 *)(image->buf);
	      u8 *out = (u8 *)(imres.buf);
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, in++, out++ )
		*out = *in - *out;
	    }
	    break;
	  case SSHORT :
	    {
	      s16 *in = (s16 *)(image->buf);
	      s16 *out = (s16 *)(imres.buf);
	      register int i, v;
	      v = image->dim.x * image->dim.y * image->dim.z;
	      for ( i = 0; i < v ; i++, in++, out++ )
		*out = *in - *out;
	    }
	    break;
	  default :
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("output image type unknown or not supported\n", 0);
	  }
	  break;

	case VT_CLOSING :
	  
	  if ( morphologicalDilation( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (closing)\n", 0);
	  }
	  if ( morphologicalErosion( imres.buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (closing)\n", 0);
	  }
	  break;

	case VT_OPENING :
	  
	  if ( morphologicalErosion( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (opening)\n", 0);
	  }
	  if ( morphologicalDilation( imres.buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (opening)\n", 0);
	  }
	  break;


	case VT_EROSION :
	  if ( morphologicalErosion( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in erosion (opening)\n", 0);
	  }
	  break;

	case VT_DILATION :
	default :
	  if ( morphologicalDilation( image->buf, imres.buf, image->type, theDim, &SE ) != 1 ) {
	    VT_FreeImage( &imres );
	    freeStructuringElement( &SE );
	    VT_FreeImage( image );
	    VT_Free( (void**)&image );
	    VT_ErrorParse("error in dilation (closing)\n", 0);
	  }
	}

	/*--- ecriture de l'image resultat ---*/
        if ( VT_WriteInrimage( &imres ) == -1 ) {
                VT_FreeImage( image );
                VT_FreeImage( &imres );
                VT_Free( (void**)&image );
                VT_ErrorParse("unable to write output image\n", 0);
        }
		
	/*--- liberations memoires ---*/
	VT_FreeImage( image );
        VT_FreeImage( &imres );
	VT_Free( (void**)&image );
	return( 1 );
}

#if defined(_ANSI_)
static void VT_Parse( int argc, char *argv[], local_par *par )
#else
static void VT_Parse( argc, argv, par )
int argc;
char *argv[];
local_par *par;
#endif
{
    int i, nb, status;
    int connexite = 0;
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
	    /*--- arguments generaux ---*/
	    else if ( strcmp ( argv[i], "-help" ) == 0 ) {
		VT_ErrorParse("\n", 1);
	    }
	    else if ( strcmp ( argv[i], "-v" ) == 0 ) {
	      _VT_VERBOSE_ = 1;
	      MorphoTools_verbose();
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

	    /*--- traitement ---*/
	    else if ( strcmp ( argv[i], "-dil" ) == 0 ) {
		par->type_operation = VT_DILATION;
	    }
	    else if ( strcmp ( argv[i], "-ero" ) == 0 ) {
		par->type_operation = VT_EROSION;
	    }
	    else if ( (strcmp ( argv[i], "-fer" ) == 0) || (strcmp ( argv[i], "-clo" ) == 0) ) {
		par->type_operation = VT_CLOSING;
	    }
	    else if ( (strcmp ( argv[i], "-ouv" ) == 0) || (strcmp ( argv[i], "-ope" ) == 0) ) {
		par->type_operation = VT_OPENING;
	    }
	    else if ( (strcmp ( argv[i], "-hfer" ) == 0) || (strcmp ( argv[i], "-hclo" ) == 0) ) {
		par->type_operation = VT_CLOSINGHAT;
	    }
	    else if ( (strcmp ( argv[i], "-houv" ) == 0) || (strcmp ( argv[i], "-hope" ) == 0) ) {
		par->type_operation = VT_OPENINGHAT;
	    }
	    else if ( strcmp ( argv[i], "-contrast" ) == 0 ) {
		par->type_operation = VT_CONTRAST;
	    }

	    else if ( strcmp ( argv[i], "-bin" ) == 0 ) {
	      par->binary_mode = 1;
	    }
	    else if ( strcmp ( argv[i], "-2D" ) == 0 ) {
	      par->dim = TwoD;
	    }

	    else if ( strcmp ( argv[i], "-elt" ) == 0 ) {
		i += 1;
		if ( i >= argc)    VT_ErrorParse( "parsing -elt...\n", 0 );
		strncpy( par->names.ext, argv[i], STRINGLENGTH );  
	    }

	    else if ( strcmp ( argv[i], "-radius" ) == 0 || strcmp ( argv[i], "-R" ) == 0) {
		i += 1;
		if ( i >= argc)    VT_ErrorParse( "parsing -radius...\n", 0 );
		status = sscanf( argv[i],"%d",&par->radius );
		if ( status <= 0 ) VT_ErrorParse( "parsing -radius...\n", 0 );
	    }

	    else if ( strcmp ( argv[i], "-i" ) == 0 ) {
		i += 1;
		if ( i >= argc)    VT_ErrorParse( "parsing -i...\n", 0 );
		status = sscanf( argv[i],"%d",&par->nb_iterations );
		if ( status <= 0 ) VT_ErrorParse( "parsing -i...\n", 0 );
	    }

	    else if ( strcmp ( argv[i], "-con" ) == 0 ) {
		i += 1;
		if ( i >= argc)    VT_ErrorParse( "parsing -con...\n", 0 );
		status = sscanf( argv[i],"%d",&connexite );
		if ( status <= 0 ) VT_ErrorParse( "parsing -con...\n", 0 );
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
    
    /*--- type de connexite ---*/
    switch ( connexite ) {
    case 4 :
	par->connexite = N04;   break;
    case 6 :
	par->connexite = N06;   break;
    case 8 :
	par->connexite = N08;   break;
    case 10 :
	par->connexite = N10;   break;
    case 18 :
	par->connexite = N18;   break;
    case 26 :
	par->connexite = N26;   break;
    }
}

#if defined(_ANSI_)
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

#if defined(_ANSI_)
static void VT_InitParam( local_par *par )
#else
static void VT_InitParam( par )
local_par *par;
#endif
{
  VT_Names( &(par->names) );
  par->type_operation = VT_DILATION;
  par->nb_iterations = 1;
  par->connexite = N26;
  par->dim = ThreeD;
  par->binary_mode = 0;
  par->radius = 0;
}
