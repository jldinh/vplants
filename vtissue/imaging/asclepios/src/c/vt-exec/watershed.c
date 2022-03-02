/*************************************************************************
 * watershed.c -
 *
 * $Id$
 *
 * Copyright©INRIA 1999
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: Mon Jul 21 10:09:48 CEST 2008
 * 
 *
 * ADDITIONS, CHANGES
 *
 */

#include <vt_common.h>
#include <watershed.h>

typedef struct local_par {
  vt_names names;
  enumLabelChoice choice;
  int nPointsToBeAllocated;
  int type;
} local_par;




/*------- Definition des fonctions statiques ----------*/
static void VT_Parse( int argc, char *argv[], local_par *par );
static void VT_ErrorParse( char *str, int l );
static void VT_InitParam( local_par *par );





static char *usage = "[image-markers] [image-gradient] [image-out]\n\
\t [-labelchoice|-l  first|min|most] [-iterations %d] [-memory|-m %d]\n\
\t [-v] [-nv] [-D] [-help]";

static char *detail = "\
\t image-markers: labeled markers image\n\
\t image-gradient: gradient image (unsigned char or unsigned short int)\n\
\t image-out: result image, will be of the same type than image-markers\n\
\t -labelchoice|-l %s: method to choose the label in case of conflicts\n\
\t\t first: the label of the point that puts the actual point in the list\n\
\t\t\t (historical (and default) behavior)\n\
\t\t min: the label of smallest value\n\
\t\t most: the label that is the most represented in the neighborhood\n\
\t -memory|-m %d: size of the bunch of points to be allocated when required\n\
\t\t setting it low allows a better memory management (at the detriment of speed)\n\
\t\t setting it high allows a better computational times (at the detriment of speed)\n\
\t -iterations %d: maximal number of iterations to be performed\n\
\t -v : mode verbose\n\
\t -D : mode debug\n\
\n\
 $Revision: 1.1 $ $Date: 2001/05/09 15:56:44 $ $Author: greg $\n";

static char program[STRINGLENGTH];






int main( int argc, char *argv[] )
{
  local_par par;
  vt_image *image, *imgrad, imres;
  int theDim[3];
  int m;

  /*--- initialisation des parametres ---*/
  VT_InitParam( &par );
  
  /*--- lecture des parametres ---*/
  VT_Parse( argc, argv, &par );
  
  /*--- lecture de l'image d'entree ---*/
  image = _VT_Inrimage( par.names.in );
  imgrad = _VT_Inrimage( par.names.ext );
  theDim[0] = image->dim.x;
  theDim[1] = image->dim.y;
  theDim[2] = image->dim.z;

  
  /*--- initialisation de l'image resultat ---*/
  VT_Image( &imres );
  VT_InitFromImage( &imres, image, par.names.out, image->type );

  if ( par.type != CPU_UNKNOWN ) imres.type = par.type;
  if ( VT_AllocImage( &imres ) != 1 ) {
    VT_FreeImage( image );
    VT_Free( (void**)&image );
    VT_ErrorParse("unable to allocate output image\n", 0);
  }
  if ( par.nPointsToBeAllocated > 0 ) {
    watershed_setNumberOfPointsForAllocation( par.nPointsToBeAllocated );
  }
  else {
    /* rule of thumb 
       nb voxels / (nb gradient levels * 50)
    */
    m = (int)( (double)theDim[0]*theDim[1]*theDim[2] / (256*50) );
    if ( m > watershed_getNumberOfPointsForAllocation() ) {
      if ( _VT_VERBOSE_ ) {
	fprintf( stderr, "%s: bunch of allocated points, change %d for %d\n",
		 program, watershed_getNumberOfPointsForAllocation(), m );
      }
      watershed_setNumberOfPointsForAllocation( m );
    }
  }
  watershed_setlabelchoice( par.choice );
  watershed( imgrad->buf, imgrad->type,
	     image->buf, imres.buf, image->type, theDim );


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








static void VT_Parse( int argc, 
		      char *argv[], 
		      local_par *par )
{
  int i, nb, status;
  int m=0, o=0, s=0, r=0;
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
      /*---  ---*/
      else if ( strcmp ( argv[i], "-labelchoice" ) == 0 || strcmp ( argv[i], "-l" ) == 0 ) {
	i += 1;
	if ( i >= argc)    VT_ErrorParse( "parsing -labelchoice...\n", 0 );
	if ( strcmp ( argv[i], "first" ) == 0 ) {
	  par->choice = _FIRST_ENCOUNTERED_NEIGHBOR_;
	}
	else if ( strcmp ( argv[i], "min" ) == 0 ) {
	  par->choice = _MIN_LABEL_;
	}
	else if ( strcmp ( argv[i], "most" ) == 0 ) {
	  par->choice = _MOST_REPRESENTED_;
	}
	else {
	  VT_ErrorParse( "parsing -labelchoice...\n", 0 );
	}
      }

      else if ( strcmp ( argv[i], "-memory" ) == 0 || strcmp ( argv[i], "-m" ) == 0 ) {
	i += 1;
	if ( i >= argc)    VT_ErrorParse( "parsing -m...\n", 0 );
	status = sscanf( argv[i],"%d",&(par->nPointsToBeAllocated) );
	if ( status <= 0 ) VT_ErrorParse( "parsing -m...\n", 0 );
      }

      else if ( strcmp ( argv[i], "-iterations" ) == 0 ) {
	i += 1;
	if ( i >= argc)    VT_ErrorParse( "parsing -iterations...\n", 0 );
	status = sscanf( argv[i],"%d",&m );
	if ( status <= 0 ) VT_ErrorParse( "parsing -iterations...\n", 0 );
	watershed_setMaxNumberOfIterations( m );
      }

      /*--- arguments generaux ---*/
      else if ( strcmp ( argv[i], "-help" ) == 0 ) {
	VT_ErrorParse("\n", 1);
      }
      else if ( strcmp ( argv[i], "-nv" ) == 0 ) {
	watershed_setnoverbose();
	_VT_VERBOSE_ = 0;
      }
      else if ( strcmp ( argv[i], "-v" ) == 0 ) {
	watershed_setverbose();
	_VT_VERBOSE_ = 1;
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
	strncpy( par->names.ext, argv[i], STRINGLENGTH );  
	nb += 1;
      }
       else if ( nb == 2 ) {
	strncpy( par->names.out, argv[i], STRINGLENGTH );  
	nb += 1;
      }
     else 
	VT_ErrorParse("too much file names when parsing\n", 0 );
    }
    i += 1;
  }
  

  if (nb < 3 ) {
    VT_ErrorParse("not enoughgrep Pa file names when parsing\n", 0 );
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






static void VT_ErrorParse( char *str, int flag )
{
  (void)fprintf(stderr,"Usage : %s %s\n",program, usage);
  if ( flag == 1 ) (void)fprintf(stderr,"%s",detail);
  (void)fprintf(stderr,"Erreur : %s",str);
  exit(0);
}








static void VT_InitParam( local_par *par )
{
  VT_Names( &(par->names) );
  par->choice = _FIRST_ENCOUNTERED_NEIGHBOR_;
  par->nPointsToBeAllocated = -1;
  par->type = CPU_UNKNOWN;
}
