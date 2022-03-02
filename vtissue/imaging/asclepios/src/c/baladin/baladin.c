#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <unistd.h>
#include <string.h>

#include <baladin.h>
#include <matrix.h>
#include <initialisation.h>
#include <vecteur.h>
#include <py_image.h>

#define max(a,b) ((a)>(b) ? (a) : (b))
#define min(a,b) ((a)<(b) ? (a) : (b))

/*------- Definition des fonctions statiques ----------*/

static char *program = NULL;

static char *usage = "-ref <reference-image> -flo <floating-image> -res <result-image>\n\
 [-result-matrix|-mat %s] [-result-real-matrix|-real|-reel %s]\n\
 [-initial-matrix|-inivox %s] [-initial-real-matrix|-inireel %s]\n\
 [-command-line|-com %s] [-logfile|-verbosef %s] [-default-filenames|-df] [-ndf]\n\
 [-vsf %f %f %f] [-vsr %f %f %f]\n\
 [-low-threshold-reference|-ltr|-sbr %d]\n\
 [-high-threshold-reference|-htr|-shr %d]\n\
 [-low-threshold-floating|-ltf|-sbf %d] [-high-threshold-floating|-htf|-shf %d]\n\
 [-fraction-block-reference|-sr% %lf] [-fraction-block-floating|-sf% %lf]\n\
 [-transformation|-tran rigi[d]|simi[litude]|affi[ne]|spli[ne]]\n\
 [-estimator|-es ltsw|lts|lsw|ls] [-ltscut %lf]\n\
 [-similarity-measure|-similarity-si cc]\n\
 [-threshold-similarity-measure|-tsi|-ssi %lf]\n\
 [-max-iterations|-iter %d] [-rms]\n\
 [-block-sizes|-bld %d %d %d] [-block-spacing|-blp %d %d %d]\n\
 [-block-borders|-blb %d %d %d]\n\
 [-block-neighborhood-sizes|-bldv %d %d %d] [-block-steps|-blpv %d %d %d]\n\
 [-fraction-variance-blocks|-v% %lf] [-no-fraction-variance-blocks|-nov%]\n\
 [-decrement-fraction-variance-blocks|-vd% %lf]\n\
 [-minimum-fraction-variance-blocks|-vs% %lf]\n\
 [-pyramid-levels|-pyn %d] [-pyramid-finest-level|-pys %d]\n\
 [-pyramid-filtered|-pyfilt]\n\
 [-automated-version|-auto] [-inv] [-just-resample|-stop] [-h|-help|--h|--help]\n\
 [-verbose] [-no-verbose] [-vischeck] [-write_def]\n";

static char *detail = "\n\
-flo %s  # name of the image to be registered (floating image)\n\
-ref %s  # name of the reference image (still image)\n\
-res %s  # name of the result image (default is 'res.inr.gz')\n\
    this is the floating image resampled with the inverse of the result matrix\n\
    in the geometry of the reference image. If '-inv' is specified, this is\n\
    the reference image resampled with the result matrix in the geometry of the\n\
    floating one.\n\
-result-matrix|-mat           %s  # name of the result transformation \n\
    from floating to reference (voxel coordinates) (default is 'res.trsf')\n\
    M_ref = T * M_flo\n\
-result-real-matrix|-reel     %s  # name of the result transformation \n\
    (coordinates of the 'real world') (default is 'res_reel.trsf')\n\
-initial-matrix|-inivox       %s   # name of the initial transformation\n\
    (voxel coordinates) from reference to floating\n\
-initial-real-matrix|-inireel %s  # name of the initial transformation\n\
    (coordinates of the 'real world')\n\
-command-line|-com %s  # write the command line in a file\n\
-logfile|-verbosef %s  # log file name (can be 'stderr' or 'stdout')\n\
-default-filenames|-df      # use default file names for the outputs\n\
-no-default-filenames|-ndf  # do not use default file names for the outputs\n\
    assume that the user specifies them for the outputs he/she is interested in\n\
\n\
-voxel-size-floating|-vsf %lf %lf %lf  # voxel size of the floating image\n\
    overrides the one given in the image header (if any)\n\
-voxel-size-reference|-vsr %lf %lf %lf  # voxel size of the reference image\n\
    overrides the one given in the image header (if any)\n\
\n\
-low-threshold-reference|-ltr|-sbr %d   # low threshold for the reference image\n\
-high-threshold-reference|-htr|-shr %d  # high threshold for the reference image\n\
    points of the reference image that will be considered have a value strictly\n\
    superior to the low threshold and strictly inferior to the high threshold\n\
-low-threshold-floating|-ltf|-sbf %d    # low threshold for the floating image\n\
-high-threshold-floating|-htf|-shf %d   # high threshold for the floating image\n\
    points of the floating image that will be considered have a value strictly\n\
    superior to the low threshold and strictly inferior to the high threshold\n\
-fraction-block-reference|-fbr|-sr% %lf # a block of the reference image will\n\
    be considered if it contains at least this fraction of voxels with an\n\
    intensity between the low and the high threshold (default is 0.5)\n\
-fraction-block-floating|-fbf|-sf% %lf  # a block of the floating image will\n\
    be considered if it contains at least this fraction of voxels with an\n\
    intensity between the low and the high threshold (default is 0.5)\n\
\n\
-transformation|-tran %s  # type of transformation, choices are\n\
    rigi[d], simi[litude], affi[ne]\n\
-estimator|-es %s # type of estimator, choices are\n\
    ltsw: Weighted Least Trimmed Squares\n\
    lts:  Least Trimmed Squares\n\
    lsw:  Weighted Least Squares\n\
    ls:   Least Squares\n\
-ltscut %lf # cutting value for (weighted) least trimmed squares\n\
-similarity-measure|-similarity-si %s # type of similarity measure, choices are\n\
    cc: correlation coefficient\n\
    ecc: extended correlation coefficient\n\
-threshold-similarity-measure|-tsi|-ssi %lf # threshold on the similarity\n\
     measure: pairings below that threshold will not be considered\n\
-max-iterations|-iter %d # maximum number of iterations at one level of the\n\
     pyramid\n\
-rms  # use the RMS as an end condition at each pyramid level\n\
\n\
-block-sizes|-bld %d %d %d      # sizes of the blocks along X, Y, Z\n\
-block-spacing|-blp %d %d %d    # block spacing in the floating image\n\
-block-borders|-blb %d %d %d    # blocks borders: to be added twice at\n\
    each dimension for statistics computation\n\
-block-neighborhood-sizes|-bldv %d %d %d # sizes of the exploration\n\
    neighborhood around a block\n\
-block-steps|-blpv %d %d %d     # progression-step in the exploration\n\
    neighborhood\n\
-fraction-variance-blocks|-v%            %lf # consider only a fraction\n\
    of all the blocks (the ones with the highest variance) at the coarser\n\
    level of the pyramid\n\
-decrement-fraction-variance-blocks|-vd% %lf # the decrement of this fraction\n\
    from one level of the pyramid to the next (default is 0.2)\n\
-minimum-fraction-variance-blocks|-vs%   %lf # the minimum admissible value\n\
    of this fraction\n\
-no-fraction-variance-blocks|-nov%           # do not decrease the initial value\n\
    of this fraction. The constant value of the fraction is set to 1.0 but can\n\
    be changed afterwards with '-fraction-variance-blocks'\n\
\n\
-pyramid-levels|-pyn %d # number of levels of the pyramid (default is 3)\n\
-pyramid-finest-level|-pys %d # stop at the level #%d of the pyramid\n\
    (default is 0, ie stop at the finest level)\n\
-pyramid-filtered|-pyfilt # pyramid built by Gaussian (recursive) filtering\n\
\n\
-automated-version|-auto  # set parameters to standard for automated version\n\
    override the parameters already set by previous options\n\
-inv  # after matching, resample reference image instead of floating one\n\
    see -res %s\n\
-just-resample|-stop # do not match the images. Just compute the transformation\n\
    matrix from voxel sizes (and eventually input matrices)\n\
-h|-help|--h|--help # print this message\n\
 $Revision: 1.5 $ $Date: 2003/07/30 08:29:09 $ $Author: greg $\n";


typedef struct local_par {
  
  /* input parameters
     (not used elsewhere)
   */
  char *floating_image;
  char *reference_image;
  char *result_image;

  char *initial_matrix;
  char *initial_real_matrix;

  char *result_matrix;
  char *result_real_matrix;

  char *command_line;

  char *log_file;

  double vx_flo; 
  double vy_flo; 
  double vz_flo; 

  double vx_ref; 
  double vy_ref; 
  double vz_ref; 
  
  int inverse;
  int use_default_filenames;
  int stop;

  PARAM param;
} local_par;

static void __ErrorParse( char *str, int flag )
{
  (void)fprintf(stderr,"Usage: %s %s\n",program, usage);
  if ( flag == 1 ) (void)fprintf(stderr,"%s",detail);
  if ( str != NULL ) (void)fprintf(stderr,"Error: %s\n",str);
  exit( -1 );
}

void Aide_Eng();

void __Parse( int argc, char *argv[], local_par *p );

static void __InitParam( local_par *par );






int main(int argc, char *argv[])
{
  char strtmp[128];

  int i, j;
  local_par p;

  FILE *sortie;

  _MATRIX matrice_res, matrice_reel, mat_inv, mat_tmp;

  bal_image Inrimage_ref, Inrimage_flo;
  bal_image Inrimage_res;





  


  /************************************
	       ON COMMENCE
  ************************************/
  program = argv[0];
  if ( argc == 1 ) __ErrorParse( NULL, 0 );


  /* Aide complete */
  i = 1;
  while ( i < argc ){
    if ((strcmp ( argv[i], "-help") == 0) || (strcmp ( argv[i], "-h") == 0) ||
	(strcmp ( argv[i], "--help") == 0) || (strcmp ( argv[i], "--h") == 0) ) {
      /* Aide_Eng(); */
      __ErrorParse( NULL, 1 );
      exit(-1);
    }
    i++;
  }
  
  /* Parsing des arguments de la ligne de commande */
  __InitParam( &p );
  __Parse( argc, argv, &p );

  if ( p.floating_image == NULL )  __ErrorParse( "no floating image", 0 );
  if ( p.reference_image == NULL ) __ErrorParse( "no reference image", 0 );




  if ( 0 ) {
    FILE *f = fopen( "parametres.3D.new", "w" );
    BAL_PrintParameters( f, &(p.param) );
    fclose( f );
  }
  

  /* Ligne de commande sauvee dans un fichier
   */  
  if ( p.command_line != NULL || p.use_default_filenames == 1 ) {
    sortie = NULL;
    if ( p.command_line != NULL ) { 
      sortie = fopen( p.command_line, "w" );
      if ( sortie == NULL ) 
	fprintf( stderr, " unable to open '%s' for writing\n", p.command_line );
    }
    else if ( p.use_default_filenames == 1 ) {
      sprintf( strtmp, "j_ai_tape_ca.%d", getpid() );
      sortie = fopen( strtmp, "w" );
      if ( sortie == NULL ) 
	fprintf( stderr, " unable to open '%s' for writing\n", strtmp );
    }
    if ( sortie != NULL ) {
      for (i=0; i<argc; i++) {
	for ( j=0; j<strlen( argv[i] ); j++ )
	  fprintf( sortie, "%c", argv[i][j] );
	fprintf( sortie, " " );
      }
      fclose( sortie );
    }
  }




  /* Ecriture dans un fichier d'informations relatives au deroulement du programme */
  if ( p.param.verbose > 0 ) {
    if ( p.log_file != NULL ) {
      if ( strlen( p.log_file ) == 4 && strcmp( p.log_file, "NULL" ) == 0 ) 
	p.param.verbosef = NULL;
      else if ( strlen( p.log_file ) == 6 && strcmp( p.log_file, "stderr" ) == 0 )
	p.param.verbosef = stderr;
      else if ( strlen( p.log_file ) == 6 && strcmp( p.log_file, "stdout" ) == 0 )
	p.param.verbosef = stdout;
      else {
	p.param.verbosef = fopen( p.log_file, "w" );
	if ( p.param.verbosef == NULL ) {
	  fprintf( stderr, "%s: unable to open '%s' for writing, switch to 'stderr'\n", argv[0], p.log_file );
	  p.param.verbosef = stderr;
	}
      }
    }
    else if ( p.use_default_filenames == 1 ) {
      p.param.verbosef = fopen( "trace.txt", "w" );
      if ( p.param.verbosef == NULL ) {
	fprintf( stderr, "%s: unable to open 'trace.txt' for writing, switch to 'stderr'\n", argv[0] );
	p.param.verbosef = stderr;
      }
    }
  }



  /* Matrices allocation
   */
  if ( _alloc_mat( &matrice_res, 4, 4) != 1 ) {
    fprintf( stderr, "%s: error when allocating matrix #1\n", argv[0] );
    exit( -1 );
  }
  if ( _alloc_mat( &matrice_reel, 4, 4) != 1 ) {
    fprintf( stderr, "%s: error when allocating matrix #2\n", argv[0] );
    _free_mat( &matrice_res );
    exit( -1 );
  }





  if (p.param.verbosef != NULL) {
    fprintf(p.param.verbosef, "\n********* AVANT LA PYRAMIDE **********\n\n");
    fflush(p.param.verbosef);
  }

  /*** Lecture de l'image de reference 
   ***/
  if ( p.param.verbosef != NULL ) {
    fprintf(p.param.verbosef, "\tLecture de l'image %s\n", p.reference_image );
    fflush(p.param.verbosef);
  }
  if ( BAL_ReadImage( &Inrimage_ref, p.reference_image ) != 1 ) {
    BAL_FreeImage( & Inrimage_ref );
    _free_mat( &matrice_reel );
    _free_mat( &matrice_res );
    sprintf( strtmp, "can not read '%s'", p.reference_image );
    __ErrorParse( strtmp, 0 );
  }
  if ( p.vx_ref > 0 && p.vy_ref > 0 ) {
    if ( Inrimage_ref.nplanes == 1 ) {
      if ( p.param.verbosef != NULL ) {
	fprintf( p.param.verbosef, "... change pixel size of reference image" );
	fprintf( p.param.verbosef, " from (%f %f) to (%f %f)\n",
		 Inrimage_ref.vx, Inrimage_ref.vy, p.vx_ref, p.vy_ref );
	fflush(p.param.verbosef);
      }
      Inrimage_ref.vx = p.vx_ref;
      Inrimage_ref.vy = p.vy_ref;
    }
    else if ( p.vz_ref > 0.0 ) {
      if ( p.param.verbosef != NULL ) {
	fprintf( p.param.verbosef, "... change voxel size of reference image" );
	fprintf( p.param.verbosef, " from (%f %f %f) to (%f %f %f)\n",
		 Inrimage_ref.vx, Inrimage_ref.vy, Inrimage_ref.vz, 
		 p.vx_ref, p.vy_ref, p.vz_ref );
	fflush(p.param.verbosef);
      }
      Inrimage_ref.vx = p.vx_ref;
      Inrimage_ref.vy = p.vy_ref;
      Inrimage_ref.vz = p.vz_ref;
    }
  }


  /*** Lecture de l'image flottante 
   ***/
  if ( p.param.verbosef != NULL ) {
    fprintf(p.param.verbosef, "\tLecture de l'image %s\n", p.floating_image );
    fflush(p.param.verbosef);
  }
  if ( BAL_ReadImage( &Inrimage_flo, p.floating_image ) != 1 ) {
    BAL_FreeImage( & Inrimage_ref );
    _free_mat( &matrice_reel );
    _free_mat( &matrice_res );
    sprintf( strtmp, "can not read '%s'", p.floating_image );
    __ErrorParse( strtmp, 0 );
  }
  if ( p.vx_flo > 0 && p.vy_flo > 0 ) {
    if ( Inrimage_flo.nplanes == 1 ) {
      if ( p.param.verbosef != NULL ) {
	fprintf( p.param.verbosef, "... change pixel size of floating image" );
	fprintf( p.param.verbosef, " from (%f %f) to (%f %f)\n",
		 Inrimage_flo.vx, Inrimage_flo.vy, p.vx_flo, p.vy_flo );
	fflush(p.param.verbosef);
      }
      Inrimage_flo.vx = p.vx_flo;
      Inrimage_flo.vy = p.vy_flo;
    }
    else if ( p.vz_flo > 0.0 ) {
      if ( p.param.verbosef != NULL ) {
	fprintf( p.param.verbosef, "... change voxel size of floating image" );
	fprintf( p.param.verbosef, " from (%f %f %f) to (%f %f %f)\n",
		 Inrimage_flo.vx, Inrimage_flo.vy, Inrimage_flo.vz, 
		 p.vx_flo, p.vy_flo, p.vz_flo );
	fflush(p.param.verbosef);
      }
      Inrimage_flo.vx = p.vx_flo;
      Inrimage_flo.vy = p.vy_flo;
      Inrimage_flo.vz = p.vz_flo;
    }
  }





  /***
      Changement de geometrie de Image_flo vers Image_ref 
      -> initialisation de la matrice de transformation matrice_res
  ***/
  /* Matrice initiale voxel ? */
  if  ( p.initial_matrix != NULL ) {

    if ( Initialize_Matrice_Initiale( p.initial_matrix, &matrice_res ) != 1 ) {
      fprintf( stderr, "%s: error when reading '%s'\n", argv[0], p.initial_matrix );
      BAL_FreeImage( & Inrimage_flo );
      BAL_FreeImage( & Inrimage_ref );
      _free_mat( &matrice_reel );
      _free_mat( &matrice_res );
      exit( -1 );
    }

  }

  /* Matrice initiale reelle ? */
  if ( p.initial_real_matrix != NULL ) {
    if ( p.initial_matrix != NULL ) {
      fprintf( stderr, "%s: another initial matrix was already specified: '%s'\n",
	       argv[0], p.initial_matrix );
      fprintf( stderr, "\t will not use '%s'\n", p.initial_real_matrix );
    }
    else {
      
      if ( _alloc_mat( &mat_tmp, 4, 4) != 1 ) {
	fprintf( stderr, "%s: error when allocating auxiliary matrix\n", argv[0] );
	BAL_FreeImage( & Inrimage_flo );
	BAL_FreeImage( & Inrimage_ref );
	_free_mat( &matrice_reel );
	_free_mat( &matrice_res );
	exit( -1 );
      }

      if ( Initialize_Matrice_Initiale( p.initial_real_matrix, &mat_tmp ) != 1 ) {
	fprintf( stderr, "%s: error when reading '%s'\n", 
		 argv[0], p.initial_real_matrix );
	_free_mat( &mat_tmp );
	BAL_FreeImage( & Inrimage_flo );
	BAL_FreeImage( & Inrimage_ref );
	_free_mat( &matrice_reel );
	_free_mat( &matrice_res );
	exit( -1 );
      }
      /* Passage a la matrice voxel */
      MatriceReel2MatriceVoxel( &mat_tmp, &matrice_res, 
				Inrimage_ref.vx, Inrimage_ref.vy, Inrimage_ref.vz, 
				Inrimage_flo.vx, Inrimage_flo.vy, Inrimage_flo.vz );
    }
    
    fprintf(stderr, "MATRICE REELLE EN ENTREE...\n");
    for (i = 0; i < 4; i++){
      fprintf(stderr, "%f %f %f %f\n", 
	      mat_tmp.m[i*4], mat_tmp.m[1+i*4], mat_tmp.m[2+i*4], mat_tmp.m[3+i*4]); 
    }
    fprintf(stderr, "...TRANSFORMEE EN MATRICE VOXEL\n");
    for (i = 0; i < 4; i++){
      fprintf(stderr, "%f %f %f %f\n", 
	      matrice_res.m[i*4], matrice_res.m[1+i*4], matrice_res.m[2+i*4], matrice_res.m[3+i*4]); 
    }

    _free_mat( &mat_tmp );
  }
  
  /* Pas de matrice initiale ? */
  if ( p.initial_matrix == NULL && p.initial_real_matrix == NULL ) {
    ChangeGeometry( &matrice_res, 
		    Inrimage_ref.ncols, Inrimage_ref.nrows, Inrimage_ref.nplanes,
		    Inrimage_ref.vx, Inrimage_ref.vy, Inrimage_ref.vz, 
		    Inrimage_flo.ncols, Inrimage_flo.nrows, Inrimage_flo.nplanes,
		    Inrimage_flo.vx, Inrimage_flo.vy, Inrimage_flo.vz );
  }
  



  if ( p.stop != 1 ) {
    if ( Pyramidal_Block_Matching( & Inrimage_ref, & Inrimage_flo,
				   &matrice_res, &matrice_res, &p.param ) != 1 ) {
      fprintf( stderr, "%s: error when doing the registration\n", argv[0] );
    }
  }

  if ( p.param.verbosef != NULL
       && p.param.verbosef != stderr 
       && p.param.verbosef != stdout )
    fclose( p.param.verbosef );

  fprintf(stderr, "\n");

  /* Desallocation */
  




  /*** Ecriture de l'image resultat - dans son type original cette fois-ci 
       C'est pour ca que je la relis, cette fois sans convertir sur 1 octet ***/

  /* 24/01/2003 Si le nom de l'image resultat n'est pas specifie, on
     n'ecrit pas (pour Xavier - save disk space - a garder en general) */
  if ( p.result_image != NULL ||  p.use_default_filenames == 1 ) {
    
    if ( p.inverse == 1 ) {

      /* resample the reference image
       */
      if ( BAL_InitAllocImage( &Inrimage_res, NULL, Inrimage_flo.ncols,
			     Inrimage_flo.nrows, Inrimage_flo.nplanes,
			     Inrimage_ref.vdim, Inrimage_ref.type) != 1 ) {
	fprintf( stderr, "%s: unable to allocate result image\n", argv[0] );
	exit( -1 );
      }
      
      if ( BAL_Reech3DTriLin4x4( &Inrimage_ref, &Inrimage_res, matrice_res.m ) != 1 ) {
	fprintf( stderr, "%s: unable to compute result image\n", argv[0] );
	exit( -1 );
      }

      Inrimage_res.vx = Inrimage_flo.vx;
      Inrimage_res.vy = Inrimage_flo.vy;
      Inrimage_res.vz = Inrimage_flo.vz;
    
    }
    else {

      /* resample the floating image
       */
      if ( _alloc_mat( &mat_inv, 4, 4) != 1 ) {
	fprintf( stderr, "%s: error when allocating auxiliary matrix\n", argv[0] );
	BAL_FreeImage( & Inrimage_flo );
	BAL_FreeImage( & Inrimage_ref );
	_free_mat( &matrice_reel );
	_free_mat( &matrice_res );
	exit( -1 );
      }

      fprintf(stderr, "matrice_res...\n");
      for (i = 0; i < 4; i++){
      fprintf(stderr, "%f %f %f %f\n", 
	      matrice_res.m[i*4], matrice_res.m[1+i*4], matrice_res.m[2+i*4], matrice_res.m[3+i*4]); 
    }

      InverseMat4x4(matrice_res.m, mat_inv.m);
      
      if ( BAL_InitAllocImage( &Inrimage_res, NULL, Inrimage_ref.ncols,
			       Inrimage_ref.nrows, Inrimage_ref.nplanes,
			       Inrimage_flo.vdim, Inrimage_flo.type) != 1 ) {
	fprintf( stderr, "%s: unable to allocate result image\n", argv[0] );
	exit( -1 );
      }

      fprintf(stderr, "mat_inv...\n");
      for (i = 0; i < 4; i++){
      fprintf(stderr, "%f %f %f %f\n", 
	      mat_inv.m[i*4], mat_inv.m[1+i*4], mat_inv.m[2+i*4], mat_inv.m[3+i*4]); 
    }

      if ( BAL_Reech3DTriLin4x4( &Inrimage_flo, &Inrimage_res, mat_inv.m ) != 1 ) {
	fprintf( stderr, "%s: unable to compute result image\n", argv[0] );
	exit( -1 );
      }
      
      _free_mat( &mat_inv);

      Inrimage_res.vx = Inrimage_ref.vx;
      Inrimage_res.vy = Inrimage_ref.vy;
      Inrimage_res.vz = Inrimage_ref.vz;
    
    }

    if ( p.result_image != NULL ) {
      if ( BAL_WriteImage( &Inrimage_res, p.result_image ) != 1 ) {
	fprintf( stderr, "%s: unable to write result image '%s'\n", 
		 argv[0], p.result_image );
	exit( -1 );
      }
    }
    else if ( p.use_default_filenames == 1  ) {
      if ( p.stop == 1 ) {
	if ( p.inverse == 1 ) {
	  if ( BAL_WriteImage( &Inrimage_res, "geom_ima_ref.inr.gz" ) != 1 ) {
	    fprintf( stderr, "%s: unable to write result image 'geom_ima_ref.inr.gz'\n", 
		     argv[0] );
	    exit( -1 );
	  }
	}
	else {
	  if ( BAL_WriteImage( &Inrimage_res, "geom_ima_flo.inr.gz" ) != 1 ) {
	    fprintf( stderr, "%s: unable to write result image 'geom_ima_flo.inr.gz'\n", 
		     argv[0] );
	    exit( -1 );
	  }
	}
      }
      else {
	if ( BAL_WriteImage( &Inrimage_res, "res.inr.gz" ) != 1 ) {
	  fprintf( stderr, "%s: unable to write result image 'res.inr.gz'\n", 
		   argv[0] );
	  exit( -1 );
	}
      }
    }
  
    BAL_FreeImage( & Inrimage_res );
  }



  /*** Ecriture de la matrice resultat (voxel) ***/
  if ( p.result_matrix != NULL ||  p.use_default_filenames == 1 ) {
    if ( p.result_matrix != NULL ) { 
      if ( _write_mat( p.result_matrix, &matrice_res ) != 1 ) {
	fprintf( stderr, " unable to write '%s'\n", p.result_matrix );
      }
    }
    else if ( p.use_default_filenames == 1 ) {
      if ( p.stop == 1 ) {
	if ( _write_mat( "stop.trsf", &matrice_res ) != 1 )
	  fprintf( stderr, " unable to write 'stop.trsf'\n" );
      }
      else {
	if ( _write_mat( "res.trsf", &matrice_res ) != 1 )
	  fprintf( stderr, " unable to write 'res.trsf'\n" );
      }
    }
  }

  /*** Ecriture de la matrice resultat (reelle) ***/
  VoxelMatrix2RealMatrix( &matrice_res, &matrice_reel,
			  Inrimage_ref.vx, Inrimage_ref.vy, Inrimage_ref.vz,
			  Inrimage_flo.vx, Inrimage_flo.vy, Inrimage_flo.vz );
					 
  if ( p.result_real_matrix != NULL ||  p.use_default_filenames == 1 ) {
    if ( p.result_real_matrix != NULL ) { 
      if ( _write_mat( p.result_real_matrix, &matrice_reel ) != 1 ) {
	fprintf( stderr, " unable to write '%s'\n", p.result_real_matrix );
      }
    }
    else if ( p.use_default_filenames == 1 ) {
      if ( p.stop == 1 ) {
	if ( _write_mat( "stop_reel.trsf", &matrice_reel ) != 1 )
	  fprintf( stderr, " unable to write 'stop_reel.trsf'\n" );
      }
      else {
	if ( _write_mat( "res_reel.trsf", &matrice_reel ) != 1 )
	  fprintf( stderr, " unable to write 'res_reel.trsf'\n" );
      }
    }
  }


  /* Desallocations */
  BAL_FreeImage( & Inrimage_ref );
  BAL_FreeImage( & Inrimage_flo );

  _free_mat( &matrice_reel);
  _free_mat( &matrice_res);

  return( 0 );
}





void Aide_Eng()
{
  fprintf (stderr,"baladin...\n\
  -ref  <image_ref>    name of the reference image\n\
  -flo  <image_flo>    name of the image to be registered (floating image)\n\
\n\
  [-auto]    automated version with standard parameters\n\
\n\
  [-res]     %%s    name of the result image\n\
  [-mat]     %%s    name of the result matrix (voxel) (default : res.trsf)\n\
  [-reel]    %%s    name of the result matrix (real) (default : res_reel.trsf)\n\
  [-inivox]  %%s    initial transform (voxel)\n\
  [-inireel] %%s    initial transform (real)\n\
\n\
  [-tran]    %%s    type of transformation (default : rigi)\n\
                       rigid (rigi), similarity (simi), affine (affi)\n\
  [-es]      %%s    type of estimator (default : lts)\n\
                       lts : Least Trimmed Squares,  ls   : Least Squares,\n\
                       lsw : Weighted Least Squares, ltsw : Weighted Least Trimmed Squares\n\
  [-ltscut]  %%f    if es=lts or ltsw, cut [0.5..1] (default : 0.5)\n\
  [-si]      %%s    similarity measure (default : cc)\n\
                       cc : Correlation Coefficient, cr : Correlation Ratio\n\
  [-ssi]     %%f    threshold on the similarity measure [0..1] (default : 1e-7)\n\
\n\
  [-bld] %%d %%d %%d  size of the blocks in x, y, z (default : 4, 4, 4 or 1)\n\
  [-blp] %%d %%d %%d  progression-step of the block in the fix image in x, y, z (default : 3, 3, 3)\n\
  [-bldv] %%d %%d %%d dimension of the exploration neighborhood around a block (default : 3, 3, 3)\n\
  [-blpv] %%d %%d %%d progression-step in the neighborhood of a block in x, y, z (default : 1, 1, 1)\n\
\n\
  [-sbr]     %%d    low threshold for the reference image (default : -1)\n\
  [-shr]     %%d    high threshold for the reference image (default : 256)\n\
  [-sbf]     %%d    low threshold for the floating image (default : -1)\n\
  [-shf]     %%d    high threshold for the floating image (default : 256)\n\
  [-sr%%]     %%f    considers blocks for which %%f %% of the voxels (minimum) have an\n\
                   intensity between sbr and shr [0..1] (default : 0.5)\n\
  [-sf%%]     %%f    considers blocks for which %%f %% of the voxels (minimum) have an\n\
                   intensity between sbf and shf [0..1] (default : 0.5)\n\
  [-v%%]      %%f    considers the %%f %% of blocks with highest variance [0..1] (default : 1)\n\
  [-vs%%]     %%f    minimum of this pourcentage (decreases of 0.2 at each pyramid level)\n\
                   [0..1] (default : 0.5)\n\
  [-nov%%]          no selection on the blocks variance\n\
\n\
  [-pyn]     %%d    number of levels of the pyramid (default : 3)\n\
  [-pys]     %%d    stop before the %%d latest levels of the pyramid (default : 0)\n\
  [-pyfilt]        pyramid built by recursive filtering\n\
  [-iter]    %%d    maximum number of iterations for a given level of the pyramid (default : 4)\n\
  [-rms]           uses the RMS as a test for changing the pyramid level\n\
\n\
  [-vsr] %%f %%f %%f  voxel size in x,y,z of the reference image (if not in the header)\n\
  [-vsf] %%f %%f %%f  voxel size in x,y,z of the floating image (if not in the header)\n\
\n\
");
}


void __Parse( int argc, char *argv[], local_par *p )
{
  int i;
  int status;

  program = argv[0];

  for ( i=1; i<argc; i++ ) {
    
    /* image file names 
     */
    if ( strcmp ( argv[i], "-flo") == 0 && argv[i][4] == '\0' ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -flo", 0 );
      p->floating_image = argv[i];
    }
    else if ( strcmp ( argv[i], "-ref") == 0 && argv[i][4] == '\0' ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -ref", 0 );
      p->reference_image = argv[i];
    }
    else if ( strcmp ( argv[i], "-res") == 0 && argv[i][4] == '\0' ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -res", 0 );
      p->result_image = argv[i];
    }

    /* matrix file names 
     */
    else if ( strcmp ( argv[i], "-result-matrix" ) == 0 
	      || (strcmp ( argv[i], "-mat") == 0 && argv[i][4] == '\0') ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -result-matrix", 0 );
      p->result_matrix = argv[i];
    }
    else if ( strcmp ( argv[i], "-result-real-matrix" ) == 0 
	      || (strcmp ( argv[i], "-real") == 0 && argv[i][5] == '\0') 
	      || (strcmp ( argv[i], "-reel") == 0 && argv[i][5] == '\0') ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -result-real-matrix", 0 );
      p->result_real_matrix = argv[i];
    }
    else if ( strcmp ( argv[i], "-initial-matrix" ) == 0 
	      || strcmp ( argv[i], "-inivox") == 0 ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -initial-matrix", 0 );
      p->initial_matrix = argv[i];
    }
    else if ( strcmp ( argv[i], "-initial-real-matrix" ) == 0 
	      || strcmp ( argv[i], "-inireal" ) == 0 
	      || strcmp ( argv[i], "-inireel" ) == 0 ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -initial-real-matrix", 0 );
      p->initial_real_matrix = argv[i];
    }
		  
    /* other file names 
     */
    else if ( strcmp ( argv[i], "-command-line") == 0 
	      || (strcmp ( argv[i], "-com") == 0 && argv[i][4] == '\0') ){
      i++;
      if ( i >= argc) __ErrorParse( "parsing -command-line", 0 );
      p->command_line = argv[i];
    }

    else if ( strcmp ( argv[i], "-logfile" ) == 0 
	     || strcmp ( argv[i], "-verbosef") == 0 ) {
      i++;
      if ( i >= argc) __ErrorParse( "parsing -logfile", 0 );
      p->log_file = argv[i];
      if ( p->param.verbose <= 0 ) p->param.verbose = 1;
    }

    /* misc (related to file names)
     */
    else if ( strcmp ( argv[i], "-default-filenames" ) == 0 
	      || (strcmp ( argv[i], "-df" ) == 0 && argv[i][3] == '\0') ) {
      p->use_default_filenames = 1;
    }
    else if ( strcmp ( argv[i], "-no-default-filenames" ) == 0 
	      || (strcmp ( argv[i], "-ndf" ) == 0 && argv[i][4] == '\0') ) {
      p->use_default_filenames = 0;
    }

    /* specify voxel sizes
     */
    else if ( strcmp ( argv[i], "-voxel-size-reference" ) == 0 
	      || (strcmp ( argv[i], "-vsr" ) == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-reference %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vx_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-reference %lf", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-reference %lf %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vy_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-reference %lf %lf", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-reference %lf %lf %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vz_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-reference %lf %lf %lf", 0 );
    }
    else if ( strcmp ( argv[i], "-voxel-size-floating" ) == 0 
	      || (strcmp ( argv[i], "-vsf" ) == 0 && argv[i][4] == '\0') ){
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-floating %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vx_flo) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-floating %lf", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-floating %lf %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vy_flo) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-floating %lf %lf", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -voxel-size-floating %lf %lf %lf", 0 );
      status = sscanf( argv[i], "%lf", &(p->vz_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -voxel-size-floating %lf %lf %lf", 0 );
    }

    /* threshold on images
     */
    else if ( strcmp ( argv[i], "-low-threshold-reference") == 0 
	      || (strcmp ( argv[i], "-ltr") == 0 && argv[i][4] == '\0')
	      || (strcmp ( argv[i], "-sbr") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -low-threshold-reference", 0 );
      status = sscanf( argv[i], "%d", &(p->param.seuil_bas_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -low-threshold-reference", 0 );
    }
    else if ( strcmp ( argv[i], "-high-threshold-reference") == 0 
	      || (strcmp ( argv[i], "-htr") == 0 && argv[i][4] == '\0')
	      || (strcmp ( argv[i], "-shr") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -high-threshold-reference", 0 );
      status = sscanf( argv[i], "%d", &(p->param.seuil_haut_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -high-threshold-reference", 0 );
    }
    else if ( strcmp ( argv[i], "-low-threshold-floating") == 0 
	      || (strcmp ( argv[i], "-ltf") == 0 && argv[i][4] == '\0')
	      || (strcmp ( argv[i], "-sbf") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -low-threshold-floating", 0 );
      status = sscanf( argv[i], "%d", &(p->param.seuil_bas_flo) );
      if ( status <= 0 ) __ErrorParse( "parsing -low-threshold-floating", 0 );
    }
    else if ( strcmp ( argv[i], "-high-threshold-floating") == 0 
	      || (strcmp ( argv[i], "-htf") == 0 && argv[i][4] == '\0')
	      || (strcmp ( argv[i], "-shf") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -high-threshold-floating", 0 );
      status = sscanf( argv[i], "%d", &(p->param.seuil_haut_flo) );
      if ( status <= 0 ) __ErrorParse( "parsing -high-threshold-floating", 0 );
    }

    else if ( strcmp ( argv[i], "-fraction-block-reference" ) == 0 
	      || ( strcmp ( argv[i], "-fbr") == 0 && argv[i][4] == '\0')
	      || ( strcmp ( argv[i], "-sr%") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -fraction-block-reference", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.seuil_pourcent_ref) );
      if ( status <= 0 ) __ErrorParse( "parsing -fraction-block-reference", 0 );
    }
    else if ( strcmp ( argv[i], "-fraction-block-floating" ) == 0 
	      || ( strcmp ( argv[i], "-fbf") == 0 && argv[i][4] == '\0')
	      || ( strcmp ( argv[i], "-sf%") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -fraction-block-floating", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.seuil_pourcent_flo) );
      if ( status <= 0 ) __ErrorParse( "parsing -fraction-block-floating", 0 );
    }

    /* registration parameters: 
       - transformation
       - estimator
       - similarity measure
       - end condition
     */
    else if ( strcmp ( argv[i], "-transformation" ) == 0
	      || ( strcmp ( argv[i], "-tran" ) == 0 && argv[i][5] == '\0' ) ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "-transformation", 0 );
      if ( (strcmp ( argv[i], "rigid" ) == 0 && argv[i][5] == '\0')
	   || (strcmp ( argv[i], "rigi" ) == 0 && argv[i][4] == '\0') ) {
	p->param.transfo = RIGIDE;
      }
      else if ( strcmp ( argv[i], "similitude" ) == 0
		|| (strcmp ( argv[i], "simi" ) == 0 && argv[i][4] == '\0') ) {
	p->param.transfo = SIMILITUDE;
      }
      else if ( strcmp ( argv[i], "affine" ) == 0
		|| (strcmp ( argv[i], "affi" ) == 0 && argv[i][4] == '\0') ) {
	p->param.transfo = AFFINE;
      }
      else if ( strcmp ( argv[i], "spline" ) == 0
		|| (strcmp ( argv[i], "spli" ) == 0 && argv[i][4] == '\0') ) {
	p->param.transfo = SPLINE;
      }
      else {
	fprintf( stderr, "unknown transformation type: '%s'\n", argv[i] );
	__ErrorParse( "-transformation", 0 );
      }
    }
    
    else if ( strcmp ( argv[i], "-estimator") == 0
	      || (strcmp ( argv[i], "-es") == 0 && argv[i][3] == '\0') ){
      i ++;
      if ( i >= argc)    __ErrorParse( "-estimator", 0 );
      if ( (strcmp ( argv[i], "ltsw" ) == 0 && argv[i][4] == '\0')
	   || (strcmp ( argv[i], "wlts" ) == 0 && argv[i][4] == '\0') ) {
	p->param.use_lts = 1;
	p->param.estimateur = TYPE_LSSW;
      }
      else if ( strcmp ( argv[i], "lts" ) == 0 && argv[i][3] == '\0' ) {
	p->param.use_lts = 1;
	p->param.estimateur = TYPE_LS;
      }
      else if ( (strcmp ( argv[i], "lsw" ) == 0 && argv[i][3] == '\0')
		|| (strcmp ( argv[i], "wls" ) == 0 && argv[i][3] == '\0') ) {
	p->param.use_lts = 0;
	p->param.estimateur = TYPE_LSSW;
      }
      else if ( strcmp ( argv[i], "ls" ) == 0 && argv[i][2] == '\0' ) {
	p->param.use_lts = 0;
	p->param.estimateur = TYPE_LS;
      }
      else {
	fprintf( stderr, "unknown estimator type: '%s'\n", argv[i] );
	__ErrorParse( "-estimator", 0 );
      }
    }

    else if (strcmp ( argv[i], "-ltscut" ) == 0 ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "-ltscut", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.lts_cut) );
      if ( status <= 0 ) __ErrorParse( "-ltscut", 0 );
      if ( p->param.lts_cut < 0.5 || p->param.lts_cut > 1.0 )
	 __ErrorParse( "-ltscut %lf should be in [0.5 ... 1.0]", 0 );
    }

    else if ( strcmp ( argv[i], "-similarity-measure" ) == 0
	      || strcmp ( argv[i], "-similarity" ) == 0
	      || (strcmp ( argv[i], "-si" ) == 0 && argv[i][3] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "-similarity-measure", 0 );
      if ( strcmp ( argv[i], "cc" ) == 0 && argv[i][2] == '\0' ) {
	p->param.mesure = MESURE_CC;
      }
      else if ( strcmp ( argv[i], "ecc" ) == 0 && argv[i][3] == '\0' ) {
	p->param.mesure = MESURE_EXT_CC;
      }
      else if ( strcmp ( argv[i], "cr" ) == 0 && argv[i][2] == '\0' ) {
	p->param.mesure = MESURE_CR;
      }
      else if ( strcmp ( argv[i], "ccg" ) == 0 && argv[i][3] == '\0' ) {
	p->param.mesure = MESURE_CC_GRAD;
      }
      else if ( strcmp ( argv[i], "crg" ) == 0 && argv[i][3] == '\0' ) {
	p->param.mesure = MESURE_CR_GRAD;
      }
      else {
	fprintf( stderr, "unknown similarity measure: '%s'\n", argv[i] );
	__ErrorParse( "-similarity-measure", 0 );
      }
    }

    else if ( strcmp ( argv[i], "-threshold-similarity-measure" ) == 0
	      || (strcmp ( argv[i], "-tsi" ) == 0 && argv[i][4] == '\0') 
	      || (strcmp ( argv[i], "-ssi" ) == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "-threshold-similarity-measure", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.seuil_mesure) );
      if ( status <= 0 ) __ErrorParse( "-threshold-similarity-measure", 0 );

    }

    else if ( strcmp ( argv[i], "-max-iterations" ) == 0
	     || (strcmp( argv[i], "-iter" ) == 0 && argv[i][5] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "-max-iterations", 0 );
      status = sscanf( argv[i], "%d", &(p->param.nbiter) );
      if ( status <= 0 ) __ErrorParse( "-max-iterations", 0 );
    }

    else if ( strcmp ( argv[i], "-rms") == 0 && argv[i][4] == '\0' ) {
      p->param.rms = 1;
    }

    /* blocks
     */
    else if ( strcmp (argv[i], "-block-sizes" ) == 0 
	      || strcmp (argv[i], "-block-size" ) == 0 
	      || (strcmp (argv[i], "-bld") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-sizes %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_dx) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-sizes %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-sizes %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_dy) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-sizes %d %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-sizes %d %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_dz) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-sizes %d %d %d", 0 );
    }

    else if ( strcmp (argv[i], "-block-spacing" ) == 0 
	      || (strcmp (argv[i], "-blp") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-spacing %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_x) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-spacing %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-spacing %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_y) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-spacing %d %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-spacing %d %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_z) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-spacing %d %d %d", 0 );
    }

    else if ( strcmp (argv[i], "-block-borders" ) == 0 
	      || (strcmp (argv[i], "-blb") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-borders %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_border_x) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-borders %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-borders %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_border_y) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-borders %d %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-borders %d %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_border_z) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-borders %d %d %d", 0 );
    }

    else if ( strcmp (argv[i], "-block-neighborhood-sizes" ) == 0 
	      || strcmp (argv[i], "-block-neighborhood-size" ) == 0 
	      || (strcmp ( argv[i], "-bldv") == 0 && argv[i][5] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-neighborhood-sizes %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_size_neigh_x) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-neighborhood-sizes %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-neighborhood-sizes %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_size_neigh_y) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-neighborhood-sizes %d %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-neighborhood-sizes %d %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_size_neigh_z) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-neighborhood-sizes %d %d %d", 0 );
    }

    else if ( strcmp (argv[i], "-block-steps" ) == 0 
	      || strcmp (argv[i], "-block-step" ) == 0 
	      || (strcmp ( argv[i], "-blpv") == 0 && argv[i][5] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-steps %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_neigh_x) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-steps %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-steps %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_neigh_y) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-steps %d %d", 0 );
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -block-steps %d %d %d", 0 );
      status = sscanf( argv[i], "%d", &(p->param.bl_next_neigh_z) );
      if ( status <= 0 ) __ErrorParse( "parsing -block-steps %d %d %d", 0 );

    }

    else if ( strcmp( argv[i], "-fraction-variance-blocks" ) == 0 
	      || (strcmp ( argv[i], "-v%") == 0 && argv[i][3] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -fraction-variance-blocks", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.bl_pourcent_var) );
      if ( status <= 0 ) __ErrorParse( "parsing -fraction-variance-blocks", 0 );
    }
    else if ( strcmp( argv[i], "-minimum-fraction-variance-blocks" ) == 0 
	      || (strcmp ( argv[i], "-vs%") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -minimum-fraction-variance-blocks", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.bl_pourcent_var_min) );
      if ( status <= 0 ) __ErrorParse( "parsing -minimum-fraction-variance-blocks", 0 );
    }
    else if ( strcmp( argv[i], "-decrement-fraction-variance-blocks" ) == 0 
	      || (strcmp ( argv[i], "-vd%") == 0 && argv[i][4] == '\0') ) {
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -decrement-fraction-variance-blocks", 0 );
      status = sscanf( argv[i], "%lf", &(p->param.bl_pourcent_var_dec) );
      if ( status <= 0 ) __ErrorParse( "parsing -decrement-fraction-variance-blocks", 0 );
    }
    else if ( strcmp( argv[i], "-no-fraction-variance-blocks" ) == 0 
	      || (strcmp ( argv[i], "-nov%") == 0 && argv[i][5] == '\0') ) {
      p->param.bl_pourcent_var = 1.0;
      p->param.bl_pourcent_var_min = 1.0;
      p->param.bl_pourcent_var_dec = 0.0;
    }
    
    /* pyramid
     */
    else if ( strcmp ( argv[i], "-pyramid-levels" ) == 0
	      || (strcmp( argv[i], "-pyn") == 0 && argv[i][4] == '\0') ) { 
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -pyramid-levels", 0 );
      status = sscanf( argv[i], "%d", &(p->param.pyn) );
      if ( status <= 0 ) __ErrorParse( "parsing -pyramid-levels", 0 );
    }
    else if ( strcmp ( argv[i], "-pyramid-finest-level" ) == 0
	      || (strcmp( argv[i], "-pys") == 0 && argv[i][4] == '\0') ) { 
      i ++;
      if ( i >= argc)    __ErrorParse( "parsing -pyramid-finest-level", 0 );
      status = sscanf( argv[i], "%d", &(p->param.pys) );
      if ( status <= 0 ) __ErrorParse( "parsing -pyramid-finest-level", 0 );
    }
    else if ( strcmp ( argv[i], "-pyramid-filtered" ) ==0 
	      || (strcmp ( argv[i], "-pyfilt") ==0 ) ) {
      p->param.py_filt = 1;
    }

    /* misc 
     */
    else if ( strcmp ( argv[i], "-automated-version" ) == 0 
	      || (strcmp ( argv[i], "-auto" ) == 0 && argv[i][5] == '\0') ) {
      BAL_SetParametersToAuto( &(p->param) );
    }
    
    else if ( strcmp ( argv[i], "-inv" ) == 0 && argv[i][4] == '\0' ) {
      p->inverse = 1;
    }
    
    else if ( strcmp ( argv[i], "-just-resample" ) == 0 
	      || (strcmp ( argv[i], "-stop") == 0 && argv[i][5] == '\0') ) {
      p->stop = 1;
    }

    else if ( strcmp ( argv[i], "--help" ) == 0 
	      || ( strcmp ( argv[i], "-help" ) == 0 && argv[i][5] == '\0' )
	      || ( strcmp ( argv[i], "--h" ) == 0 && argv[i][3] == '\0' )
	      || ( strcmp ( argv[i], "-h" ) == 0 && argv[i][2] == '\0' ) ) {
      Aide_Eng();
      __ErrorParse( NULL, 1 );
    }
    
    else if (strcmp ( argv[i], "-verbose") == 0 && argv[i][8] == '\0' ) {
      if ( p->param.verbose <= 0 ) p->param.verbose = 1;
      else p->param.verbose ++;
    }
    else if (strcmp ( argv[i], "-no-verbose") == 0 ) {
      p->param.verbose = 0;
    }
    else if (strcmp ( argv[i], "-vischeck") == 0){
      p->param.vischeck = 1;
    }
    else if (strcmp ( argv[i], "-write_def") == 0){
      p->param.write_def = 1;
    }

    else {
      fprintf(stderr,"unknown option: '%s'\n",argv[i]);
    }
  }
  
}

static void __InitParam( local_par *p ) 
{
  /* input parameters
     (not used elsewhere)
   */
  p->floating_image = NULL;
  p->reference_image = NULL;
  p->result_image = NULL;

  p->initial_matrix = NULL;
  p->initial_real_matrix = NULL;

  p->result_matrix = NULL;
  p->result_real_matrix = NULL;

  p->command_line = NULL;

  p->log_file = NULL;

  p->vx_flo = -1.0; 
  p->vy_flo = -1.0; 
  p->vz_flo = -1.0; 

  p->vx_ref = -1.0; 
  p->vy_ref = -1.0; 
  p->vz_ref = -1.0; 

  p->inverse = 0;
  p->use_default_filenames = 1;
  p->stop = 0;

  if( 1 ) BAL_SetParametersToDefault( &(p->param) );
} 
