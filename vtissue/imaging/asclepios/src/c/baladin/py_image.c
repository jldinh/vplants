
#include <stdlib.h>
#include <stdio.h>
#include <math.h>



#include <py_image.h>
#include <vecteur.h>
#include <initialisation.h>



static int ComputeSubsampledImage( bal_image *image_ref, 
				   bal_image *image_ref_sub, 
				   PARAM *param, 
				   double sigma_filtre, 
				   _MATRIX *matrice_ref_sub );

static double ComputeRMS (_MATRIX *mat_avant, _MATRIX *mat_apres, 
				  double dx_ref, double dy_ref, double dz_ref, int dz_ref_sub );


#define max(a,b) ((a)>(b) ? (a) : (b))

static int _verbose_ = 1;
static int _trace_ = 1;
static int _debug_ = 0;

#define _OLD_BEHAVIOR_ 1
#define _MAX_LEVELS_ 30



int Pyramidal_Block_Matching( bal_image *theInrimage_ref,
			      bal_image *theInrimage_flo,
			      _MATRIX *theMat_init, /* initial matrix
						       (P_ref = M_init * P_flo),
						       after inversion, allow 
						       to resample the floating
						       image in the geometry of
						       the reference image.
						       NULL if none */
			      _MATRIX *theMat_result,
			      PARAM *theParam )
{
  char *proc = "Pyramidal_Block_Matching";
  PARAM param;
  _MATRIX Mat_result;

  int max_tx_ty_tz;
#ifdef _OLD_BEHAVIOR_
  float multiple_2 = 0.0;
#else
  double multiple_2 = 0.0;
#endif
  int n_levels;
  int res_level[_MAX_LEVELS_];
  int l, level, i;
  double sigma_filtre = 1.0;

  _MATRIX Mat_subsample;
  bal_image *Inrimage_ref, Inrimage_ref_sub;
  int sub_dimx, sub_dimy, sub_dimz;
  bal_image *Inrimage_flo, Inrimage_flo_tmp;


  if ( theMat_result == NULL || theMat_result->c != 4 
       || theMat_result->l != 4 || theMat_result->m == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, 
	       "%s: result matrix is not allocated or has bad dimensions\n", 
	       proc );
    return( -1 );
  }
  if ( theParam == NULL ) {
    if ( _verbose_ )  
      fprintf( stderr, "%s: switch to default parameters\n", proc );
    BAL_SetParametersToDefault( &param );
  }
  else {
    param = *theParam;
  }

  /* Matrix initialisations
   */
  if ( _alloc_mat( &Mat_result, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #1\n", proc );
    return( -1 );
  }
  if ( theMat_init != NULL ) {
    if ( theMat_init->c != 4 || theMat_init->l != 4 || theMat_init->m == NULL ) {
      if ( _verbose_ )
	fprintf( stderr, "%s: bad initial transformation, ignore it\n", proc );
      ChangeGeometry( &Mat_result,
		      theInrimage_ref->ncols,   theInrimage_ref->nrows, 
		      theInrimage_ref->nplanes, theInrimage_ref->vx, 
		      theInrimage_ref->vy,      theInrimage_ref->vz, 
		      theInrimage_flo->ncols,   theInrimage_flo->nrows, 
		      theInrimage_flo->nplanes, theInrimage_flo->vx, 
		      theInrimage_flo->vy,      theInrimage_flo->vz );
    }
    else {
      _copy_mat( theMat_init, &Mat_result );
    }
  }
  
  if ( _alloc_mat( &Mat_subsample, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #2\n", proc );
    _free_mat( & Mat_result );
    return( -1 );
  }

  /*** Controle sur la taille des blocs dans la pyramide ***/

  /* Consistance entre size_neigh_? et next_neigh_? 
     Ici on s'assure que dans le voisinage d'un bloc,
     Au moins 3 blocs seront explores
     selon chaque axe, i.e. 27 blocs en 3D, 9 blocs en 2D */
  if ( 3 * param.bl_next_neigh_x > ( 2 * param.bl_size_neigh_x ) )
    param.bl_next_neigh_x = max ( (int)((2 * param.bl_size_neigh_x + 1) / 3) ,1 );
  if ( 3 * param.bl_next_neigh_y > ( 2 * param.bl_size_neigh_y ) )
    param.bl_next_neigh_y = max ( (int)((2 * param.bl_size_neigh_y + 1) / 3) ,1 );
  if ( 3 * param.bl_next_neigh_z > ( 2 * param.bl_size_neigh_z ) )
    param.bl_next_neigh_z = max ( (int)((2 * param.bl_size_neigh_z + 1) / 3) ,1 );

  if ( theInrimage_ref->nplanes == 1 ) {
    param.bl_dz = 1; 
    param.bl_next_z = 1; 
    param.bl_next_neigh_z = 1; 
    param.bl_size_neigh_z = 0;
  }
  /*
  param.dz_ref = theInrimage_ref->nplanes;
  */

  if (param.verbosef != NULL) {
    fprintf(param.verbosef, "\tDimensions du bloc : %d %d %d\n", 
	    param.bl_dx, param.bl_dy, param.bl_dz);
    fprintf(param.verbosef, "\tPas de progression du bloc dans l'image fixe en x, y, z : %d %d %d\n", 
	    param.bl_next_x, param.bl_next_y, param.bl_next_z);
    fprintf(param.verbosef, "\tPas de progression dans le voisinage d'un bloc en x, y, z : %d %d %d\n", 
	    param.bl_next_neigh_x, param.bl_next_neigh_y, param.bl_next_neigh_z);
     fprintf(param.verbosef, "\tDimension du voisinage d'exploration autour d'un bloc : %d %d %d\n", 
	    param.bl_size_neigh_x, param.bl_size_neigh_y, param.bl_size_neigh_z);
     fflush(param.verbosef);
  }

  
  /*** DEBUT DE LA PYRAMIDE ***/
  
  if (param.verbosef != NULL) {
    fprintf(param.verbosef, "\n********** DEBUT DE LA PYRAMIDE **********\n");
    fflush(param.verbosef);
  }
  
  /* Calcul du nombre de niveaux de la pyramide :

     max(dx_ref, dy_ref, dz_ref) = 2^N -> N reel ( N = multiple_2 )
     
     Si N entier (a EPSILON pres)
        n_levels = (int) N 
     Sinon
        n_levels = (int) N + 1

     Parametres en ligne : 
        pyn : nombre de niveaux dans la pyramide
	pys : on ne traite pas les pys derniers niveaux

     Puis on calcule les resolutions successives de la pyramide
        POUR i de 0 a (pyn - pys - 2)
          res_level[i] = (int) 2.0^(n_levels - param.pyn + 1 + i)
        SI pys != 0 
          res_level[pyn - pys - 1] = (int) 2.0^(n_levels - param.pys )
	SINON
	  res_level[pyn - pys - 1] = max(dx_ref, dy_ref, dz_ref)


     Exemples : max = 680 -> n_levels = 10
                avec pyn = 5, pys = 2 -> res_level[0,1,2,3] = 64, 128, 256

		max = 256 -> n_levels = 8
		avec pyn = 4, pys = 0 -> res_level[0,1,2,3] = 32, 64, 128, 256
  */



  max_tx_ty_tz = max ( max( theInrimage_ref->ncols, theInrimage_ref->nrows ), 
		       theInrimage_ref->nplanes );
  multiple_2 = log((double)(max_tx_ty_tz)) / log(2.0);

  if ( ( multiple_2 - (int) multiple_2 ) < EPSILON )
    n_levels = (int)( multiple_2 );
  else
    n_levels = (int)( multiple_2 + 1 );

  /* Niveau le plus haut : minimum 32 */
  if ( (int) pow(2.0, (double) (n_levels - param.pyn + 1) ) < 32 )
    param.pyn = n_levels - 4;

  /* Coherence des parametres pyn et pys */
  if ( param.pys >= (param.pyn - 1) )
    param.pys = param.pyn - 1;

  if ( param.pyn-param.pys >= _MAX_LEVELS_ ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: too many pyramide levels (%d).\n", 
	       proc, param.pyn-param.pys );
    _free_mat( & Mat_subsample );
    _free_mat( & Mat_result );
    return( -1 );
  }

  /* Calcul des resolutions successives dans la pyramide */
  for (l=0; l<param.pyn-param.pys-1; l++)
    res_level[l] = (int) pow(2.0, (double) (n_levels - param.pyn + 1 + l) );
  if ( param.pys != 0 )
    res_level[param.pyn-param.pys-1] = 
      (int) pow(2.0, (double) (n_levels - param.pys ) );
  else
    res_level[param.pyn-param.pys-1] = max_tx_ty_tz;

  /* Parametre utilise pour calculer level et sigma_filtre dans la pyramide */
  param.sub = 0;

  if ( param.verbosef != NULL ) {
    fprintf(param.verbosef, "\nAvant le while (pyramide == 1)\n");
    fprintf(param.verbosef, "\tparam.pyn : %d\n", param.pyn);
    fprintf(param.verbosef, "\tparam.pys : %d\n", param.pys);
    fprintf(param.verbosef, "\tmax_tx_ty_tz : %d\n", max_tx_ty_tz);
    fprintf(param.verbosef, "\tmultiple_2 : %f\n", multiple_2);
    /* fprintf(param.verbosef, "\tparam.sub : %d\n", param.sub); */
    fprintf(param.verbosef, "\tparam.sub : 0\n" );
    fprintf(param.verbosef, "\tparam.bl_pourcent_var : %f\n", 
	    param.bl_pourcent_var);
    fprintf(param.verbosef, "\tparam.bl_pourcent_var_min : %f\n", 
	    param.bl_pourcent_var_min);
    for (i=0; i<param.pyn-param.pys; i++)
      fprintf(param.verbosef, "res_level[%d] = %d\n", i, res_level[i]);
    fflush(param.verbosef);
  }

  /* allocation of the auxiliary floating image (if necessary)
   */
  BAL_InitImage( &Inrimage_flo_tmp, NULL, 0, 0, 0, 0, theInrimage_flo->type );
  if ( param.py_filt ) {
    if ( BAL_InitAllocImage( &Inrimage_flo_tmp, "image_flo_tmp.inr", 
			     theInrimage_flo->ncols, theInrimage_flo->nrows, 
			     theInrimage_flo->nplanes, theInrimage_flo->vdim,
			     theInrimage_flo->type ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to allocate auxiliary floating image\n", 
		 proc );
      _free_mat( &Mat_subsample );
      _free_mat( &Mat_result );
      return( -1 );
    }
    Inrimage_flo =  &Inrimage_flo_tmp;
  }
  else {
    Inrimage_flo = theInrimage_flo;
  }


  /* pyramide 
   */
  for ( l=0; l<param.pyn-param.pys; l++ ) {
    
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\n****** Debut du : while (pyramide == 1)\n");
      fflush(param.verbosef);
    }

    /*** Apres le premier passage ***/
    if ( l > 0 ) {
      if ( theInrimage_flo->nplanes == 1 ) {
	param.bl_next_neigh_z = 1; param.bl_size_neigh_z = 0;
      }
      (void)Param_MiseAJour( & param  );
    }

    if ( l == 0 ) {
      if (param.verbosef != NULL) {
	fprintf(param.verbosef, "\n*** Au premier passage : 0\n" );
	fprintf( param.verbosef, "\tpyramide : 1\n" );
	fflush(param.verbosef);
      }
    }

    /*** Taille maximale des images a ce niveau de la pyramide ***/
    level = res_level[param.sub];
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\nlevel : %d\n", level );
      fflush(param.verbosef);
    }

    /*** Pyramide filtree ? Dimension du filtre pour passer de l'image originale 
	 a l'image courante, avec sigma == 2.0                                ***/
    if ( param.py_filt == 1 ) {
      sigma_filtre = 2.0 * sqrt ( multiple_2 - l - n_levels + param.pyn - 1 );
      if (param.verbosef != NULL) {
	fprintf(param.verbosef, "\nsigma_filtre : %f\n", sigma_filtre);
	fflush(param.verbosef);
      }
    }

    /***
	Calcul de l'image de reference a la resolution de la pyramide
    ***/
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\n*** Calcul de l'image de reference a la resolution de la pyramide\n");
      fflush(param.verbosef);
    }
    
    if ( level < max_tx_ty_tz ) {

      sub_dimx = theInrimage_ref->ncols;
      sub_dimy = theInrimage_ref->nrows;
      sub_dimz = theInrimage_ref->nplanes;
      if ( sub_dimx > level ) sub_dimx = level;
      if ( sub_dimy > level ) sub_dimy = level;
      if ( sub_dimz > level ) sub_dimz = level;

      if ( BAL_InitAllocImage( &Inrimage_ref_sub, "image_ref_sub.inr", 
			       sub_dimx, sub_dimy, sub_dimz, theInrimage_ref->vdim,
			       theInrimage_ref->type ) != 1 ) {
	if ( _verbose_ )
	  fprintf( stderr, "%s: unable to allocate the subsampled reference image\n", proc );
	if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );
	_free_mat( &Mat_subsample );
	_free_mat( &Mat_result );
	_copy_mat( &Mat_result , theMat_result );
	return( -1 );
      }

      Inrimage_ref_sub.vx = theInrimage_ref->vx 
	* theInrimage_ref->ncols / Inrimage_ref_sub.ncols;
      Inrimage_ref_sub.vy = theInrimage_ref->vy
	* theInrimage_ref->nrows / Inrimage_ref_sub.nrows;
      Inrimage_ref_sub.vz = theInrimage_ref->vz 
	* theInrimage_ref->nplanes / Inrimage_ref_sub.nplanes;

      if ( ComputeSubsampledImage( theInrimage_ref, &Inrimage_ref_sub,
				   &param, sigma_filtre, &Mat_subsample ) != 1 ) {
	if ( _verbose_ )
	  fprintf( stderr, "%s: unable to compute the subsampled reference image\n", proc );
	BAL_FreeImage( & Inrimage_ref_sub );
	if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );
	_free_mat( &Mat_subsample );
	_free_mat( &Mat_result );
	_copy_mat( &Mat_result , theMat_result );
	return( -1 );
      }

      Inrimage_ref = &Inrimage_ref_sub;
    }
    else {
      for ( i=0; i<16; i++ ) Mat_subsample.m[i] = 0.0;
      for ( i=0; i<4; i++ )  Mat_subsample.m[i+4*i] = 1.0;

      Inrimage_ref = theInrimage_ref;
    }
    
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\ndx_ref_sub = %d\tdy_ref_sub = %d\tdz_ref_sub = %d\n",
	      Inrimage_ref->ncols, Inrimage_ref->nrows, Inrimage_ref->nplanes );
      fprintf(param.verbosef, "vx_ref_sub = %f\tvy_ref_sub = %f\tvz_ref_sub = %f\n",
	      Inrimage_ref->vx, Inrimage_ref->vy, Inrimage_ref->vz );
      fflush(param.verbosef);
    }

    /* filtering of the auxiliary floating image (if necessary
     */
    if ( param.py_filt ) {
      if ( sigma_filtre > EPSILON ) { 
	if ( BAL_SmoothImageIntoImage( theInrimage_flo, &Inrimage_flo_tmp,
				       GAUSSIAN_FIDRICH, sigma_filtre ) != 1 ) {
	  if ( _verbose_ ) 
	    fprintf( stderr, "%s: unable to filter floating image\n", proc );
	  if ( level < max_tx_ty_tz ) BAL_FreeImage( & Inrimage_ref_sub );
	  if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );
	  _free_mat( &Mat_subsample );
	  _free_mat( &Mat_result );
	  _copy_mat( &Mat_result , theMat_result );
	  return( -1 );
	}
      }
      else {
	if ( BAL_CopyImage( theInrimage_flo, &Inrimage_flo_tmp ) != 1 ) {
	  if ( _verbose_ ) 
	    fprintf( stderr, "%s: unable to copy floating image\n", proc );
	  if ( level < max_tx_ty_tz ) BAL_FreeImage( & Inrimage_ref_sub );
	  if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );
	  _free_mat( &Mat_subsample );
	  _free_mat( &Mat_result );
	  _copy_mat( &Mat_result , theMat_result );
	  return( -1 );
	}
      }
    }

#ifdef _OLD_BEHAVIOR_
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\n*** Calcul de l'image flottante a la resolution de la pyramide\n");
      fprintf(param.verbosef, "\nflag->geometry = 1\n" );
      fprintf(param.verbosef, "\ndx_flo_sub = %d\tdy_flo_sub = %d\tdz_flo_sub = %d\n",
	      Inrimage_ref->ncols, Inrimage_ref->nrows, Inrimage_ref->nplanes );
      fprintf(param.verbosef, "vx_flo_sub = %f\tvy_flo_sub = %f\tvz_flo_sub = %f\n",
	      Inrimage_ref->vx, Inrimage_ref->vy, Inrimage_ref->vz );
      fflush(param.verbosef);
    }
#endif


    /*** 
	 DEBUT DU RECALAGE A UN NIVEAU DONNE entre Inrimage_flo_sub et Inrimage_ref_sub
	 
	 Coeur de l'algorithme 
    ***/
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\n\n****** DEBUT DU RECALAGE A UN NIVEAU DONNE\n\n");
      fflush(param.verbosef);
    }

    if ( Block_Matching( Inrimage_ref, Inrimage_flo, theInrimage_flo->type,
			 &Mat_subsample, &Mat_result, &param, l ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to do the matching at level %d \n", 
		 proc, level );
      if ( level < max_tx_ty_tz ) BAL_FreeImage( & Inrimage_ref_sub );
      if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );
      _free_mat( &Mat_subsample );
      _free_mat( &Mat_result );
      _copy_mat( &Mat_result , theMat_result );
      return( -1 );
    }


    if ( level < max_tx_ty_tz ) BAL_FreeImage( & Inrimage_ref_sub );
    
    if (param.verbosef != NULL) {
      fprintf(param.verbosef, "\nFIN while (pyramide == 1)\n\n");
      fflush(param.verbosef);
    }

  } /* end of pyramide */

  /* copy result transformation
   */
  _copy_mat( &Mat_result , theMat_result );

  /* some desallocations
   */
  if ( param.py_filt ) BAL_FreeImage( &Inrimage_flo_tmp );



  /* ... */


  _free_mat( & Mat_subsample );
  _free_mat( & Mat_result );
  return( 1 );
}










/* Block Matching at one level
 */
int Block_Matching( bal_image *theInrimage_ref, /* reference image 
						   (may be subsampled) */
		    bal_image *theInrimage_flo, /* floating image
						   (in its original geometry,
						   may be filtered) */
		    VOXELTYPE theType_flo, /* original floating image type */   
		    _MATRIX *theMat_subsample, /* allow to compute a (subsampled)
						  reference image from the
						  original one 
						  R_sub = MAT_sub * R_orig
					       */
		    _MATRIX *theMat_result, /* allow to compute a floating
					       image from the original
					       reference one
					       R_orig = MAT_res * F_orig
					    */
		    PARAM *param,
		    int level )
{
  char *proc = "Block_Matching";
  bal_image Inrimage_flo_sub;
  _MATRIX Mat_result;
  _MATRIX Mat_inv;

  FIELD field;
  BLOCS blocs_ref, blocs_flo;

  int nb_blocs_ref, nb_blocs_flo;
  int n_iteration;
  
  _MATRIX Mat_previous_result;
  double rms_threshold, rms = RMS_ERROR;
  int i;
  _MATRIX Mat_inc_real_trsf;
  _MATRIX Mat_inc_voxel_trsf;
  double scale;

  char image_name[SIZE_NAME];
  char field_name[SIZE_NAME];

  /* Matrix initialisations
   */
  if ( _alloc_mat( &Mat_result, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #1\n", proc );
    return( -1 );
  }
  
  if ( _alloc_mat( &Mat_inv, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #2\n", proc );
    _free_mat( & Mat_result );
    return( -1 );
  }

  if ( theMat_subsample == NULL )
    _copy_mat( theMat_result, &Mat_result );
  else 
    _mult_mat( theMat_subsample, theMat_result, &Mat_result );



  /* subsampled floating image
   */
  BAL_InitImage( &Inrimage_flo_sub, NULL, 0, 0, 0, 0, theType_flo );
  if ( BAL_InitAllocImage( &Inrimage_flo_sub, "image_flo_sub.inr.gz", 
			   theInrimage_ref->ncols, theInrimage_ref->nrows, 
			   theInrimage_ref->nplanes, theInrimage_flo->vdim,
			   theType_flo ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate subsampled image\n", proc );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }
  Inrimage_flo_sub.vx = theInrimage_ref->vx;
  Inrimage_flo_sub.vy = theInrimage_ref->vy;
  Inrimage_flo_sub.vz = theInrimage_ref->vz;




  /* write subsampled reference image
   */
  if ( param->vischeck == 1 ) {
    sprintf( image_name, "ref_py_%d.inr.gz", level );
    if ( BAL_WriteImage( theInrimage_ref, image_name ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to write subsampled reference image\n", proc );
      BAL_FreeImage( & Inrimage_flo_sub );
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );
    }
  }


  
  /* Allocations:
     - the block sizes are the same for both images  -> param->bl_d[x,y,z]
     - the spacing between blocks in the *floating* image is given by 
       param->bl_next_[x,y,z]
     - the spacing between blocks in the *refernce* image is 1
  */
  if ( Allocate_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref, 
				     & Inrimage_flo_sub, theInrimage_ref,
				     param ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate field and blocks\n", proc );
    BAL_FreeImage( & Inrimage_flo_sub );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }



  /* pre-computations
     Compute attributes of the reference blocks
   */
  nb_blocs_ref = CalculAttributsBlocs( theInrimage_ref, &blocs_ref, 
				       param->seuil_bas_ref, param->seuil_haut_ref,
				       param->seuil_pourcent_ref, param );
  if ( nb_blocs_ref <= 0 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to pre-compute reference blocks attributes\n", proc );
    Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
    BAL_FreeImage( & Inrimage_flo_sub );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }
  if (param->verbosef != NULL) {
    fprintf(param->verbosef, "Nombre de blocs_ref actifs\t=\t%d\n",blocs_ref.n_valid_blocks);
    fflush(param->verbosef);
  }
  
  /* Write on disk the reference image with the active voxels only
     they are defined as the voxels included in the active blocks
     ie the blocks with the 'active' flag set to 1
     Thus, all blocks are considered
  */
  if ( param->write_def == 1 || param->vischeck == 1 ) {
    sprintf( image_name, "blocs_actifs_ref_py_%d.inr.gz", level );
    WriteImageVoxelsActifs( param, blocs_ref.n_blocks, &blocs_ref, theInrimage_ref,
			    image_name, param->seuil_bas_ref, param->seuil_haut_ref );
  }

  /* RMS threshold
   */
  rms_threshold = theInrimage_ref->vx / 3.0;
  if ( rms_threshold > theInrimage_ref->vy / 3.0 ) 
    rms_threshold = theInrimage_ref->vy / 3.0;
#ifdef _OLD_BEHAVIOR_
  if ( rms_threshold > theInrimage_ref->vz / 3.0 ) 
    rms_threshold = theInrimage_ref->vz / 3.0;
#else
  if ( theInrimage_ref->nplanes > 1 && rms_threshold > theInrimage_ref->vz / 3.0 ) 
    rms_threshold = theInrimage_ref->vz / 3.0;
#endif


  /* update params: should disappear (soon I hope)
   */
  param->sub = level;
  /*
  param->dz_ref_sub = theInrimage_ref->nplanes;
  */
  
  /* last allocations
   */
  if ( _alloc_mat( &Mat_previous_result, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #3\n", proc );
    Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
    BAL_FreeImage( & Inrimage_flo_sub );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }
  if ( _alloc_mat( &Mat_inc_real_trsf, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #4\n", proc );
    _free_mat( & Mat_previous_result );
    Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
    BAL_FreeImage( & Inrimage_flo_sub );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }
  if ( _alloc_mat( &Mat_inc_voxel_trsf, 4, 4) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #5\n", proc );
    _free_mat( & Mat_inc_real_trsf );
    _free_mat( & Mat_previous_result );
    Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
    BAL_FreeImage( & Inrimage_flo_sub );
    _free_mat( & Mat_inv );
    _free_mat( & Mat_result );
    return( -1 );
  }
  
  /* registration loop
   */
  n_iteration = 0;
  do {
    
    if (param->verbosef != NULL) {
      fprintf(param->verbosef,"                    Itération %d       Niveau %d      Taille %dx%dx%d\n", 
	      n_iteration+1, level, 
	      theInrimage_ref->ncols, theInrimage_ref->nrows, theInrimage_ref->nplanes );
      fflush(param->verbosef);
    }
    else 
      fprintf(stderr,"                    Itération %d       Niveau %d      Taille %dx%dx%d", 
	      n_iteration+1, level,
	      theInrimage_ref->ncols, theInrimage_ref->nrows, theInrimage_ref->nplanes );
    
    /* compute resampled floating image
     */
    if ( InverseMat4x4( Mat_result.m, Mat_inv.m ) != 4 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: warning, transformation matrix is not invertible\n",
		 proc );
    }
    if ( BAL_Reech3DTriLin4x4( theInrimage_flo, 
			       &Inrimage_flo_sub, Mat_inv.m ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to subsample floating image\n", proc );
      _free_mat( & Mat_inc_voxel_trsf );
      _free_mat( & Mat_inc_real_trsf );
      _free_mat( & Mat_previous_result );
      Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
      BAL_FreeImage( & Inrimage_flo_sub );
      if ( n_iteration > 0 ) {
	if ( theMat_subsample == NULL )
	  _copy_mat( &Mat_result, theMat_result );
	else {
	  if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	    if ( _verbose_ ) 
	      fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		       proc );
	  }
	  _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	}
      }
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );
    }
    
    /* write subsampled floating image
     */
    if ( n_iteration == 0 && param->vischeck == 1 ) {
      sprintf( image_name, "flo_py_%d.inr.gz", level );
      if ( BAL_WriteImage( &Inrimage_flo_sub, image_name ) != 1 ) {
	if ( _verbose_ ) 
	  fprintf( stderr, "%s: unable to write resampled floating image\n", proc );
	_free_mat( & Mat_inc_voxel_trsf );
	_free_mat( & Mat_inc_real_trsf );
	_free_mat( & Mat_previous_result );
	Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
	BAL_FreeImage( & Inrimage_flo_sub );
	if ( n_iteration > 0 ) {
	  if ( theMat_subsample == NULL )
	    _copy_mat( &Mat_result, theMat_result );
	  else {
	    if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	      if ( _verbose_ ) 
		fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
			 proc );
	    }
	    _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	  }
	}
	_free_mat( & Mat_inv );
	_free_mat( & Mat_result );
	return( -1 );
      }
    }

    /* Save result transformation for RMS calculation
     */
    if ( param->rms == 1 ) 
      _copy_mat( &Mat_result, &Mat_previous_result );
    
    /* Compute attributes of the floating blocks
     */
    nb_blocs_flo = CalculAttributsBlocs( &Inrimage_flo_sub, &blocs_flo, 
					 param->seuil_bas_flo, param->seuil_haut_flo,
					 param->seuil_pourcent_flo, param );
    if ( nb_blocs_flo <= 0 ) {
      if ( _verbose_ )
	fprintf( stderr, "%s: unable to pre-compute floating blocks attributes\n", proc );
      _free_mat( & Mat_inc_voxel_trsf );
      _free_mat( & Mat_inc_real_trsf );
      _free_mat( & Mat_previous_result );
      Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
      BAL_FreeImage( & Inrimage_flo_sub );
      if ( n_iteration > 0 ) {
	if ( theMat_subsample == NULL )
	  _copy_mat( &Mat_result, theMat_result );
	else {
	  if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	    if ( _verbose_ ) 
	      fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		       proc );
	  }
	  _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	}
      }
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );
    }
    if (param->verbosef != NULL) {
      fprintf(param->verbosef, "Nombre de blocs_flo\t=\t%d\t, actifs apres seuils\t=\t%d\n",
	      nb_blocs_flo, blocs_flo.n_valid_blocks);
      fflush(param->verbosef);
    }

    /* Tri des blocs_flo selon la variance blocs_flo.p_bloc[i]->var */ 
    Sort_Blocks_WRT_Variance( &blocs_flo, param );

    /* Write on disk the reference image with the active voxels only
       they are defined as the voxels included in the active blocks
       Here (please note that it is different from the reference image)
       the active blocks are the "most significant" blocks, ie the
       blocks with the largest variance and are a subset of the blocks
       with the 'active' flag set to 1
    */
    if ( n_iteration == 0 && (param->write_def == 1 || param->vischeck == 1) ) {
      sprintf( image_name, "blocs_actifs_flo_py_%d.inr.gz", level );
      WriteImageVoxelsActifs( param, blocs_flo.n_valid_blocks, &blocs_flo, &Inrimage_flo_sub, 
			      image_name, param->seuil_bas_flo, param->seuil_haut_flo );
    }

    /* Compute the displacement field
     */
    CalculChampVecteurs( &field, &Inrimage_flo_sub, &blocs_flo,
			 theInrimage_ref, &blocs_ref, param );
    if (param->verbosef != NULL) {
      fprintf(param->verbosef, "Nombre de voxels apparies : %d\n", field.n_pairs ); 
      fflush(param->verbosef);
    }
    if ( field.n_pairs <= 0 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: empty displacement field\n", proc );
      _free_mat( & Mat_inc_voxel_trsf );
      _free_mat( & Mat_inc_real_trsf );
      _free_mat( & Mat_previous_result );
      Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
      BAL_FreeImage( & Inrimage_flo_sub );
      if ( n_iteration > 0 ) {
	if ( theMat_subsample == NULL )
	  _copy_mat( &Mat_result, theMat_result );
	else {
	  if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	    if ( _verbose_ ) 
	      fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		       proc );
	  }
	  _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	}
      }
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );      
    }
    
    /* the previous displacement field is computed with voxel coordinates
       transform it into "real" coordinates
    */
    switch( field.type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      _free_mat( & Mat_inc_voxel_trsf );
      _free_mat( & Mat_inc_real_trsf );
      _free_mat( & Mat_previous_result );
      Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
      BAL_FreeImage( & Inrimage_flo_sub );
      if ( n_iteration > 0 ) {
	if ( theMat_subsample == NULL )
	  _copy_mat( &Mat_result, theMat_result );
	else {
	  if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	    if ( _verbose_ ) 
	      fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		       proc );
	  }
	  _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	}
      }
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );      
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)field.pairs;
	for(i = 0; i < field.n_pairs; i++){
	  thePairs[i].x *= theInrimage_ref->vx;
	  thePairs[i].y *= theInrimage_ref->vy;
	  thePairs[i].u *= theInrimage_ref->vx;
	  thePairs[i].v *= theInrimage_ref->vy;
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field.pairs;
	for(i = 0; i < field.n_pairs; i++){
	  thePairs[i].x *= theInrimage_ref->vx;
	  thePairs[i].y *= theInrimage_ref->vy;
	  thePairs[i].z *= theInrimage_ref->vz;
	  thePairs[i].u *= theInrimage_ref->vx;
	  thePairs[i].v *= theInrimage_ref->vy;
	  thePairs[i].w *= theInrimage_ref->vz;
	}
      }
      break;
    }
    
    /* compute the "real" transformation 
     */
    scale = Estimate_Transformation( &Mat_inc_real_trsf, &field, param, (n_iteration==0) );
    

    if ( scale <= 0 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: incremental transformation computation failed\n", proc );
      _free_mat( & Mat_inc_voxel_trsf );
      _free_mat( & Mat_inc_real_trsf );
      _free_mat( & Mat_previous_result );
      Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
      BAL_FreeImage( & Inrimage_flo_sub );
      if ( n_iteration > 0 ) {
	if ( theMat_subsample == NULL )
	  _copy_mat( &Mat_result, theMat_result );
	else {
	  if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
	    if ( _verbose_ ) 
	      fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		       proc );
	  }
	  _mult_mat( &Mat_inv, &Mat_result, theMat_result );
	}
      }
      _free_mat( & Mat_inv );
      _free_mat( & Mat_result );
      return( -1 );      
    }

    /*** Ecriture du champ de vecteurs au format MATLAB, superpose sur l'image flottante courante
	   lors de la premiere iteration a ce niveau de la pyramide ***/
    if ( param->write_def == 1 && n_iteration == 0 ) {
      sprintf( image_name, "blocs_actifs_flo_py_%d.inr.gz", level );
      sprintf( field_name, "def_%d.m", level );
      CreateFileDef( & field, image_name, field_name );
    }

    /* compute the "voxel" transformation 
     */
    MatriceReel2MatriceVoxel( &Mat_inc_real_trsf, &Mat_inc_voxel_trsf,
			      theInrimage_ref->vx, theInrimage_ref->vy,
			      theInrimage_ref->vz, Inrimage_flo_sub.vx,
			      Inrimage_flo_sub.vy, Inrimage_flo_sub.vz );

    /* update the "voxel" transformation matrix
     */
    _mult_mat( &Mat_inc_voxel_trsf, &Mat_result, &Mat_inv );
    _copy_mat( &Mat_inv, &Mat_result );
    
    /* End condition */
    if (param->rms == 1) {
      rms = ComputeRMS( &Mat_previous_result, &Mat_result,
				(theInrimage_ref->ncols-1)*theInrimage_ref->vx,
				(theInrimage_ref->nrows-1)*theInrimage_ref->vy,
				(theInrimage_ref->nplanes-1)*theInrimage_ref->vz,
				theInrimage_ref->nplanes );
    }

    n_iteration++;
  } while ( n_iteration < param->nbiter && ( param->rms == 0 || rms > rms_threshold ) );

  fprintf(stderr, "\n");
  if (param->transfo == SIMILITUDE)
    fprintf(stderr, "echelle = %f\n", scale );


  /* some desallocations
   */
  _free_mat( & Mat_inc_voxel_trsf );
  _free_mat( & Mat_inc_real_trsf );
  _free_mat( & Mat_previous_result );


  /* compute the new result matrix
     compose the current result matrix 
     with the inverse of the subsampling matrix
   */
  if ( theMat_subsample == NULL )
    _copy_mat( &Mat_result, theMat_result );
  else {
    if ( InverseMat4x4( theMat_subsample->m, Mat_inv.m ) != 4 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: warning, subsampling matrix is not invertible\n",
		 proc );
    }
    _mult_mat( &Mat_inv, &Mat_result, theMat_result );
  }

  Free_Field_Blocs_Mesures( &field, &blocs_flo, &blocs_ref );
  BAL_FreeImage( & Inrimage_flo_sub );
  _free_mat( & Mat_inv );
  _free_mat( & Mat_result );
  return( 1 );
}









/*
 * Computation of a subsampled image that is already allocated
 *
 */
static int ComputeSubsampledImage( bal_image *image_ref, 
			    bal_image *image_ref_sub, 
			    PARAM *param, 
			    double sigma_filtre, 
			    _MATRIX *matrice_ref_sub )
{
  char *proc = "ComputeSubsampledImage";
  bal_image image_ref_tmp;
  double mat_inv[16];


  if ( image_ref_sub->ncols == image_ref->ncols
       && image_ref_sub->nrows == image_ref->nrows
       && image_ref_sub->nplanes == image_ref->nplanes ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: input and output images should have different dimensions\n",
	       proc );
    return( -1 );
  }

  /*** Matrice de changement de geometrie entre image_ref et image_ref_sub ***/
  ChangeGeometry ( matrice_ref_sub,
		   image_ref_sub->ncols, image_ref_sub->nrows, 
		   image_ref_sub->nplanes,
		   image_ref_sub->vx, image_ref_sub->vy, image_ref_sub->vz,
		   image_ref->ncols, image_ref->nrows, image_ref->nplanes,
		   image_ref->vx, image_ref->vy, image_ref->vz );

  InverseMat4x4( matrice_ref_sub->m, mat_inv );


  if ( param->py_filt == 1 ) {
    if ( BAL_InitAllocImage( &image_ref_tmp, "image_ref_tmp",
			     image_ref->ncols, image_ref->nrows, 
			     image_ref->nplanes, image_ref->vdim, 
			     image_ref->type ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to allocate auxiliary image\n", proc );
      return( -1 );
    }

    image_ref_tmp.vx = image_ref->vx;
    image_ref_tmp.vy = image_ref->vy;
    image_ref_tmp.vz = image_ref->vz;
    
    if ( sigma_filtre > EPSILON ) { 
      if ( BAL_SmoothImageIntoImage( image_ref, &image_ref_tmp, 
				     GAUSSIAN_FIDRICH, sigma_filtre) != 1 ) {
	if ( _verbose_ ) 
	  fprintf( stderr, "%s: unable to filter auxiliary image\n", proc );
	BAL_FreeImage( &image_ref_tmp );
	return( -1 );
      }
    }
    else {
      if ( BAL_CopyImage( image_ref, &image_ref_tmp ) != 1 ) {
	if ( _verbose_ ) 
	  fprintf( stderr, "%s: unable to copy reference image\n", proc );
	BAL_FreeImage( &image_ref_tmp );
	return( -1 );
      }
    }

    if ( BAL_Reech3DTriLin4x4( &image_ref_tmp, image_ref_sub, mat_inv ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to subsample image\n", proc );
      BAL_FreeImage( &image_ref_tmp );
      return( -1 );
    }
    BAL_FreeImage( &image_ref_tmp );

  }

  else {
    if ( BAL_Reech3DTriLin4x4( image_ref, image_ref_sub, mat_inv ) != 1 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to subsample image\n", proc );
      return( -1 );
    }
  }

  return( 1 );
}













/* Calcul la RMS aux 8 coins d'une image entre 2 matrices - 3D */
static double ComputeRMS_3D (_MATRIX *previous_mat, 
			      _MATRIX *current_mat, 
			      double c1x, double c1y, double c1z, /* corner #1 */
			      double c2x, double c2y, double c2z  /* corner #2 */
			      )
{
  char *proc = "ComputeRMS_3D";
  double erreur = 0.0;
  _MATRIX diff;
  _MATRIX X;
  _MATRIX Y;
  
  if ( previous_mat->l != 4 || previous_mat->c != 4 || previous_mat->m == NULL
       || current_mat->l != 4 || current_mat->c != 4 || current_mat->m == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: bad parameters\n ", proc );
    return( -1.0 );
  }
  
  if ( _alloc_mat( &diff, 4, 4 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate matrix\n ", proc );
    return( -1.0 );
  }
  if ( _alloc_mat( &X, 4, 1 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate vector #1\n ", proc );
    _free_mat( &diff );
    return( -1.0 );
  }
  if ( _alloc_mat( &Y, 4, 1 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate vector #2\n ", proc );
    _free_mat( &X );
    _free_mat( &diff );
    return( -1.0 );
  }

  _sub_mat( previous_mat, current_mat, &diff );
  X.m[3] = 1.0;

  X.m[0] = c1x;    X.m[1] = c1y;   X.m[2] = c1z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c1y;   X.m[2] = c1z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c1x;    X.m[1] = c2y;   X.m[2] = c1z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c2y;   X.m[2] = c1z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c1x;    X.m[1] = c1y;   X.m[2] = c2z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c1y;   X.m[2] = c2z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c1x;    X.m[1] = c2y;   X.m[2] = c2z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c2y;   X.m[2] = c2z;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  erreur = sqrt( erreur / 8.0 );

  _free_mat( &Y );
  _free_mat( &X );
  _free_mat( &diff );

  return( erreur );
}

/* Calcul la RMS aux 8 coins d'une image entre 2 matrices - 2D */
static double ComputeRMS_2D (_MATRIX *previous_mat, 
			      _MATRIX *current_mat, 
			      double c1x, double c1y, /* corner #1 */
			      double c2x, double c2y  /* corner #2 */
			      )
{
  char *proc = "ComputeRMS_2D";
  double erreur = 0.0;
  _MATRIX diff;
  _MATRIX X;
  _MATRIX Y;
  
  if ( previous_mat->l != 4 || previous_mat->c != 4 || previous_mat->m == NULL
       || current_mat->l != 4 || current_mat->c != 4 || current_mat->m == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: bad parameters\n ", proc );
    return( -1.0 );
  }
  
  if ( _alloc_mat( &diff, 4, 4 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate matrix\n ", proc );
    return( -1.0 );
  }
  if ( _alloc_mat( &X, 4, 1 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate vector #1\n ", proc );
    _free_mat( &diff );
    return( -1.0 );
  }
  if ( _alloc_mat( &Y, 4, 1 ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate vector #2\n ", proc );
    _free_mat( &X );
    _free_mat( &diff );
    return( -1.0 );
  }

  _sub_mat( previous_mat, current_mat, &diff );
  diff.m[8] = diff.m[9] = diff.m[10] = diff.m[11] = 0.0;
  X.m[2] = 0.0;
  X.m[3] = 1.0;

  X.m[0] = c1x;    X.m[1] = c1y;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c1y;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c1x;    X.m[1] = c2y;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  X.m[0] = c2x;    X.m[1] = c2y;
  _mult_mat( &diff, &X, &Y );
  erreur += Y.m[0] * Y.m[0] + Y.m[1] * Y.m[1] + Y.m[2] * Y.m[2] + Y.m[3] * Y.m[3];
    
  erreur = sqrt( erreur / 4.0 );

  _free_mat( &Y );
  _free_mat( &X );
  _free_mat( &diff );

  return( erreur );
}

/* Calcul la RMS aux coins d'une image entre 2 matrices - chapeau 2D et 3D */
static double ComputeRMS (_MATRIX *mat_avant, _MATRIX *mat_apres, 
			   double dx_ref, double dy_ref, double dz_ref, int dz_ref_sub )
{
  double erreur = 0.0;

  if ( dz_ref_sub == 1 )
    erreur = ComputeRMS_2D (mat_avant, mat_apres, 0, 0, dx_ref, dy_ref );
  else
    erreur = ComputeRMS_3D (mat_avant, mat_apres, 0, 0, 0, dx_ref, dy_ref, dz_ref);
 
  return ( erreur );       
}















/*--------------------------------------------------*
 *
 * BLOCKS and FIELDS management
 *
 *--------------------------------------------------*/



/* comparaison de deux variables de type P_BLOC avec la variance 
 */
int Compare_P_BLOC ( const void * a, const void * b )
{
  BLOC **aov = (BLOC **) a;
  BLOC **bov = (BLOC **) b;

  if ( (*aov)->var  >  (*bov)->var )
    return (-1);
  if ( (*aov)->var  <  (*bov)->var )
    return (1);
  return (0);
}



/***
    Tri des blocs_flo selon la variance blocs_flo.p_bloc[i]->var 
***/
void Sort_Blocks_WRT_Variance( BLOCS * blocks, PARAM *param )
{
  int i;
  int last = blocks->n_blocks;
  BLOC *tmp;

  /* active blocks are in [0, last-1]
     a block is active if 
     - it is enough points (active == 1)
     - it is not constant  (var > 0.0)
   */
  
  for ( i = 0; 
	i < blocks->n_blocks
	  && blocks->p_bloc[i]->valid == 1 
	  && blocks->p_bloc[i]->var > 0.0;
	i ++ )
    ;
  
  if ( i < blocks->n_blocks ) {
    while ( i < last ) {
      if ( blocks->p_bloc[i]->valid == 1 &&
	   blocks->p_bloc[i]->var > 0.0 ) {
	i ++;
      }
      else {
	/* switch i and last-1 */
	tmp                    = blocks->p_bloc[i];
	blocks->p_bloc[i]      = blocks->p_bloc[last-1];
	blocks->p_bloc[last-1] = tmp;
	last --;
      }
    }
  }

  blocks->n_valid_blocks = last;

  if (param->verbosef != NULL) {
    fprintf(param->verbosef, 
	    "Nombre de blocs_flo avec variances non nulles = %d\n",
	    blocks->n_valid_blocks);
    fflush(param->verbosef);
  }

  /* on ne trie donc que les blocs de variance non nulle */
  qsort ( blocks->p_bloc, blocks->n_valid_blocks, sizeof (BLOC *), & Compare_P_BLOC);

  /* pourcent = bl_pourcent_var * blocs_flo.n_valid_blocks 
     par exemple 40 % des blocs actifs, i.e. avec une variance non nulle */
  blocks->n_valid_blocks = (int) (blocks->n_valid_blocks * param->bl_pourcent_var);
  if (param->verbosef != NULL) {
    fprintf(param->verbosef, "Nombre de blocs_flo avec les plus fortes variances : %d\n", 
	    blocks->n_valid_blocks);
    fflush(param->verbosef);
  }

  return;
}


/***
    Allocation de memoire a un niveau donne de la pyramide : champ et blocs Image_flo, Image_ref

    Dans Ima_flo, les blocs sont espaces de bl_next -> dim_mem_champ_flo

    Dans Ima_ref, les blocs sont espaces de bl_next_neigh qui est un parametre relatif,
    donc on calcule les attributs de tous les blocs de Ima_ref
    -> dim_mem_champ_ref

    DEVRAIT dependre de la dimension des images (cf Allocate_Field())
 ***/



void Init_Blocks( BLOCS *blocks ) 
{
  blocks->bloc            = (BLOC *)NULL;
  blocks->n_valid_blocks = 0;
  blocks->p_bloc          = (BLOC **)NULL;

  blocks->n_blocks   = 0;
  blocks->n_blocks_x = 0;
  blocks->n_blocks_y = 0;
  blocks->n_blocks_z = 0;

  blocks->block_size_x = 0;
  blocks->block_size_y = 0;
  blocks->block_size_z = 0;

  blocks->block_step_x = 0;
  blocks->block_step_y = 0;
  blocks->block_step_z = 0;
}




void Free_Blocks( BLOCS *blocks ) 
{
  if ( blocks->bloc != NULL ) free( blocks->bloc );
  if ( blocks->p_bloc != NULL ) free( blocks->p_bloc );
  Init_Blocks( blocks );
}




int Allocate_Blocks( BLOCS *blocks, 
		     /* image dimensions */
		     int dimx, int dimy, int dimz,
		     /* blocks dimensions */
		     int sizex, int sizey, int sizez,
		     /* blocks spacing */
		     int stepx, int stepy, int stepz,
		     /* block borders */
		     int borderx, int bordery, int borderz )
{
  char * proc = "Allocate_Blocks";
  int o;
  int i, x, y, z;

  Init_Blocks( blocks );

  blocks->n_blocks_x = 0;
  if ( dimx-sizex >= 0 ) 
    blocks->n_blocks_x = (dimx-sizex) / stepx + 1;
  blocks->n_blocks_y = 0;
  if ( dimy-sizey >= 0 ) 
    blocks->n_blocks_y = (dimy-sizey) / stepy + 1;
  if ( dimz == 1 ) {
    blocks->n_blocks_z = 1;
  }
  else {
    blocks->n_blocks_z = 0;
    if ( dimz-sizez >= 0 ) 
      blocks->n_blocks_z = (dimz-sizez) / stepz + 1;
  }
  blocks->n_blocks = blocks->n_blocks_x * blocks->n_blocks_y * blocks->n_blocks_z;
  
  /* old formula */
  if ( dimz == 1 ) {
    if ( stepx == 1 && stepy == 1 ) {
      o = (dimx - sizex)*(dimy - sizey);
    }
    else {
      o = (dimy - sizey - 1) / stepy + 
	( (dimx - sizex - 1) / stepx) * 
	( (dimy - sizey - 1) / stepy + 1) + 1;
    }
  }
  else {
    if ( stepx == 1 && stepy == 1 && stepz == 1 ) {
      o = (dimx - sizex)*(dimy - sizey)*(dimz - sizez);
    }
    else {
      o = (dimz - sizez - 1) / stepy +
      ( (dimy - sizey - 1) / stepy ) *
      ( (dimz - sizez - 1) / stepz + 1) +
      ( (dimx - sizex - 1) / stepx ) *
      ( (dimy - sizey - 1) / stepy + 1) *
      ( (dimz - sizez - 1) / stepz + 1) + 1;
    }
  }

  if ( _trace_ ) {
    if ( o != blocks->n_blocks ) {
      fprintf( stderr, "%s: allocate %d blocks instead of (formerly) %d\n",
	       proc, blocks->n_blocks, o );
      fprintf( stderr, "\t image dims  = [%d %d %d]", dimx, dimy, dimz );
      fprintf( stderr, " block sizes = [%d %d %d]", sizex, sizey, sizez );
      fprintf( stderr, " block steps = [%d %d %d]\n", stepx, stepy, stepz );
    }
  }
  
  blocks->bloc = ( BLOC * ) calloc ( blocks->n_blocks, sizeof ( BLOC ) );
  if ( blocks->bloc == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate blocks\n", proc );
    Init_Blocks( blocks );
    return( -1 );
  }
  
  blocks->p_bloc = ( BLOC ** ) calloc ( blocks->n_blocks, sizeof ( BLOC* ) );
  if ( blocks->p_bloc == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate blocks pointers\n", proc );
    free( blocks->bloc );
    Init_Blocks( blocks );
    return( -1 );
  }

#ifdef _OLD_BEHAVIOR_
  if ( dimz == 1 ) {
    for ( i = 0, x = 0; x < dimx+1-sizex; x += stepx )
    for ( y = 0; y < dimy+1-sizey; y += stepy, i++ ) {
      blocks->p_bloc[i] = &(blocks->bloc[i]);
      blocks->bloc[i].a = x;
      blocks->bloc[i].b = y;
      blocks->bloc[i].c = 0;
    }
  }
  else {
    for ( i = 0, x = 0; x < dimx+1-sizex; x += stepx )
    for ( y = 0; y < dimy+1-sizey; y += stepy )
    for ( z = 0; z < dimz+1-sizez; z += stepz, i++ ) {
      blocks->p_bloc[i] = &(blocks->bloc[i]);
      blocks->bloc[i].a = x;
      blocks->bloc[i].b = y;
      blocks->bloc[i].c = z;
    }
  }
#else
  if ( dimz == 1 ) {
    for ( i = 0, y = 0; y < dimy+1-sizey; y += stepy )
    for ( x = 0; x < dimx+1-sizex; x += stepx, i++  ) {
      blocks->p_bloc[i] = &(blocks->bloc[i]);
      blocks->bloc[i].a = x;
      blocks->bloc[i].b = y;
      blocks->bloc[i].c = 0;
    }
  }
  else {
    for ( i = 0, z = 0; z < dimz+1-sizez; z += stepz )
    for ( y = 0; y < dimy+1-sizey; y += stepy )
    for ( x = 0; x < dimx+1-sizex; x += stepx, i++ ) {
      blocks->p_bloc[i] = &(blocks->bloc[i]);
      blocks->bloc[i].a = x;
      blocks->bloc[i].b = y;
      blocks->bloc[i].c = z;
    }
  }
#endif

  blocks->block_size_x = sizex;
  blocks->block_size_y = sizey;
  blocks->block_size_z = sizez;

  blocks->block_step_x = stepx;
  blocks->block_step_y = stepy;
  blocks->block_step_z = stepz;

  blocks->block_border_x = borderx;
  blocks->block_border_y = bordery;
  blocks->block_border_z = borderz;

  if ( blocks->block_border_x < 0 ) blocks->block_border_x = 0;
  if ( blocks->block_border_y < 0 ) blocks->block_border_y = 0;
  if ( blocks->block_border_z < 0 ) blocks->block_border_z = 0;

  return( 1 );
}



int Allocate_Field_Blocs_Mesures( FIELD *field, 
				  BLOCS *blocs_flo, 
				  BLOCS *blocs_ref, 
				  bal_image *image_flo, 
				  bal_image *image_ref, 
				  PARAM *param )
{
  char * proc = "Allocate_Field_Blocs_Mesures";
  enumFieldType type = _UnknownField_;
  
  if ( Allocate_Blocks( blocs_flo, 
			image_flo->ncols,image_flo->nrows, image_flo->nplanes, 
			param->bl_dx, param->bl_dy, param->bl_dz,
			param->bl_next_x, param->bl_next_y, 
			param->bl_next_z,
			param->bl_border_x, param->bl_border_y, 
			param->bl_border_z ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate floating blocks\n", proc );
    return( -1 );
  }
  
  /* the step between two successive blocks is implicitly 1
     for the reference blocks
   */
  if ( Allocate_Blocks( blocs_ref, 
			image_ref->ncols,image_ref->nrows, image_ref->nplanes, 
			param->bl_dx, param->bl_dy, param->bl_dz,
			1, 1, 1,
			param->bl_border_x, param->bl_border_y, 
			param->bl_border_z ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate reference blocks\n", proc );
    Free_Blocks( blocs_flo );
    return( -1 );
  }
  
  if ( image_flo->nplanes == 1 
       || param->bl_next_neigh_z == 0
       || param->bl_size_neigh_z == 0 ) {
    switch( param->estimateur ) {
    default :
      break;
    case TYPE_LS :
    case TYPE_LSSW :
      type = _ScalarWeighted2DDisplacement_;
      break;
    }
  }
  else {
    switch( param->estimateur ) {
    default :
      break;
    case TYPE_LS :
    case TYPE_LSSW :
      type = _ScalarWeighted3DDisplacement_;
      break;
    }
  }

  if ( Allocate_Field( field, type, blocs_flo->n_blocks ) != 1 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate field\n", proc );
    Free_Blocks( blocs_ref );
    Free_Blocks( blocs_flo );
    return( -1 );
  }

  if (param->verbosef != NULL) {
    fprintf(param->verbosef, "Blocs ref\t=\t%d\nBlocs flo\t=\t%d\n", 
	    blocs_ref->n_blocks, blocs_flo->n_blocks );  
    fflush(param->verbosef);
  }

  return( 1 );
}

    
void Free_Field_Blocs_Mesures( FIELD *field, BLOCS *blocs_flo, BLOCS *blocs_ref )
{
  Free_Field( field );
  Free_Blocks( blocs_ref );
  Free_Blocks( blocs_flo );
}











/*--------------------------------------------------*
 *
 * MISC
 *
 *--------------------------------------------------*/


/***
    Ecrit l'image contenant les voxels actifs lors du recalage
 ***/
void  WriteImageVoxelsActifs( PARAM *param, int n_blocks, BLOCS *blocs, 
			      bal_image *Inrimage_sub, char *nom_image,
			      int seuil_bas, int seuil_haut)
{
  bal_image Inrimage_tmp;
  int i, a, b, c, u, v, w;

  if ( BAL_InitAllocImage( &Inrimage_tmp, NULL, 
			   Inrimage_sub->ncols, Inrimage_sub->nrows,
			   Inrimage_sub->nplanes, Inrimage_sub->vdim,
			   Inrimage_sub->type) != 1 )
    return;

  if ( 0 ) {
    fprintf( stderr, "WriteImageVoxelsActifs: image = '%s'\n", nom_image );
    fprintf( stderr, "\t seuils = %d %d\n", seuil_bas, seuil_haut );
    fprintf( stderr, "\t nb blocs a ecrire = %d\n", n_blocks );
  }

#define _WRITE2D( TYPE ) {                     \
  for (i=0; i<n_blocks; i++)                   \
    if ( blocs->p_bloc[i]->valid == 1) {       \
      a = blocs->p_bloc[i]->a; b = blocs->p_bloc[i]->b; \
      for (u=0; u<blocs->block_size_x; u++)           \
      for (v=0; v<blocs->block_size_y; v++) {         \
	j = ((TYPE***)Inrimage_sub->array)[0][b+v][a+u];  \
	if ( j > seuil_bas && j < seuil_haut ) \
	  ((TYPE***)Inrimage_tmp.array)[0][b+v][a+u] = j; \
      }                                        \
    }                                          \
  }

#define _WRITE3D( TYPE ) {                        \
    for (i=0; i<n_blocks; i++)                    \
      if ( blocs->p_bloc[i]->valid == 1) {        \
	a = blocs->p_bloc[i]->a; b = blocs->p_bloc[i]->b; c = blocs->p_bloc[i]->c; \
	for (u=0; u<blocs->block_size_x; u++)            \
	for (v=0; v<blocs->block_size_y; v++)            \
	for (w=0; w<blocs->block_size_z; w++) {          \
	  j = ((TYPE***)Inrimage_sub->array)[c+w][b+v][a+u]; \
	  if ( j > seuil_bas && j < seuil_haut )  \
	    ((TYPE***)Inrimage_tmp.array)[c+w][b+v][a+u] = j; \
	}                                         \
      }                                           \
  }

#define _WRITE( TYPE ) {  \
    TYPE j;               \
    if ( Inrimage_sub->nplanes == 1 ) {  \
      _WRITE2D( TYPE )    \
    }                     \
    else {                \
      _WRITE3D( TYPE )    \
    }                     \
  }

  switch( Inrimage_sub->type ) {
  default :
    fprintf( stderr, "WriteImageVoxelsActifs: such image type not handled yet\n" );
    BAL_FreeImage( &Inrimage_tmp );
    return;
    break;
  case VT_UNSIGNED_CHAR :
    _WRITE( unsigned char )
    break;
  case VT_UNSIGNED_SHORT :
    _WRITE( unsigned short int )
    break;
  case VT_SIGNED_SHORT :
    _WRITE( short int )
    break;
  }

  Inrimage_tmp.vx = Inrimage_sub->vx;
  Inrimage_tmp.vy = Inrimage_sub->vy;
  Inrimage_tmp.vz = Inrimage_sub->vz;

  BAL_WriteImage( &Inrimage_tmp, nom_image);
  BAL_FreeImage( &Inrimage_tmp );

  return;
}
