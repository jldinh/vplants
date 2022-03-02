#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include <vecteur.h>
#include <mesure.h>

#define RETURNED_VALUE_ON_ERROR -2



static int _verbose_ = 1;
static int _debug_ = 0;
#define _OLD_BEHAVIOR_ 1
















/***
    Calcul du champ d'appariements par blocs - 3D

    On parcours l'image flottante, et pour chaque bloc, un voisinage dans 
    l'image de reference est explore (a l'aide de blocs)
***/
void CalculChampVecteur3D ( FIELD *field,
			    bal_image *inrimage_flo, BLOCS *blocs_flo,
			    bal_image *inrimage_ref, BLOCS *blocs_ref,
			    PARAM *param )
{
  char *proc = "CalculChampVecteur3D";
  int a, b, c, u, v, w, i, ind_Buvw;
  int i_max = 0;
  int j_max = 0; 
  int k_max = 0;
  int pourcent, pourcent_old;

  double measure_max, measure_0;
  double measure_default = -2.0;
  double *measures = NULL;
  int xmeas, ymeas, xymeas, zmeas;
  int x, y, z,  minx, miny, minz;
  int n_pairs;

  double demi_bl_dx = (double) (param->bl_dx) / 2.0;
  double demi_bl_dy = (double) (param->bl_dy) / 2.0;
  double demi_bl_dz = (double) (param->bl_dz) / 2.0; 
  
  int minu, maxu;
  int minv, maxv;
  int minw, maxw;

  n_pairs = field->n_pairs = 0;

  xmeas = 1+(2*param->bl_size_neigh_x)/param->bl_next_neigh_x;
  ymeas = 1+(2*param->bl_size_neigh_y)/param->bl_next_neigh_y;
  zmeas = 1+(2*param->bl_size_neigh_z)/param->bl_next_neigh_z;
  xymeas = xmeas * ymeas;
  measures = (double*)malloc( xmeas * ymeas * zmeas * sizeof( double ) );
  if ( measures == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate measures array\n", proc );
    return;
  }
  /***
      Passe sur les blocs retenus de l'image flottante, et exploration
      d'un voisinage de chaque bloc dans l'image de reference 

      Rappel: a, b, c : origine du bloc
  ***/
  pourcent_old = 0;

  for (i=0; i<blocs_flo->n_valid_blocks; i++) {
    a = blocs_flo->p_bloc[i]->a;      
    b = blocs_flo->p_bloc[i]->b;      
    c = blocs_flo->p_bloc[i]->c;

    /*    fprintf(stderr," \r");*/
    pourcent = i*100/blocs_flo->n_valid_blocks;
    if ( pourcent_old != pourcent ) {
#ifdef _OLD_BEHAVIOR_
      fprintf( stderr," %d%%\r", pourcent );
#else
      if ( param->verbose > 0 && param->verbosef != NULL ) {
	if ( param->verbosef == stderr )
	  fprintf( param->verbosef," %d%%\r", pourcent );
	else 
	  fprintf( param->verbosef," %d%%\n", pourcent );
      }
#endif
      pourcent_old = pourcent;
    }

    
    /***
	Pour un bloc donne dans l'image flottante, on calcule la mesure de
	similarite avec un certain nombre de blocs de l'image de reference
	
	Pas de progression : bl_next_neigh_? 
	
	Dimensions du voisinage d'exploration : - bl_size_neigh ... bl_size_neigh
    ***/
    for ( x=xmeas*ymeas*zmeas-1; x>=0; x-- ) measures[x] = measure_default;

    minu = a-param->bl_size_neigh_x;
    maxu = a+param->bl_size_neigh_x;
    minv = b-param->bl_size_neigh_y;
    maxv = b+param->bl_size_neigh_y;
    minw = c-param->bl_size_neigh_z;
    maxw = c+param->bl_size_neigh_z;

    minx = miny = minz = 0;

    while ( minu < 0 ) { minu += param->bl_next_neigh_x; minx ++; }
    while ( minv < 0 ) { minv += param->bl_next_neigh_y; miny ++; }
    while ( minw < 0 ) { minw += param->bl_next_neigh_z; minz ++ ; }
    if ( maxu >= blocs_ref->n_blocks_x ) maxu = blocs_ref->n_blocks_x - 1;
    if ( maxv >= blocs_ref->n_blocks_y ) maxv = blocs_ref->n_blocks_y - 1;
    if ( maxw >= blocs_ref->n_blocks_z ) maxw = blocs_ref->n_blocks_z - 1;
    
    for ( u = minu, x = minx; u <= maxu; u += param->bl_next_neigh_x, x++ )
    for ( v = minv, y = miny; v <= maxv; v += param->bl_next_neigh_y, y++ )
    for ( w = minw, z = minz; w <= maxw; w += param->bl_next_neigh_z, z++ ) {

      /* index of  B(u,v,w) in blocs_ref->bloc 
	 this is linked to the building of blocs_ref
	 cf Allocate_Blocks()
      */
#ifdef _OLD_BEHAVIOR_
      ind_Buvw = w + (v + u * blocs_ref->n_blocks_y) * blocs_ref->n_blocks_z;
#else
      ind_Buvw = u + (v + w * blocs_ref->n_blocks_y) * blocs_ref->n_blocks_x;
#endif

      /* bloc B(u,v,w) actif ? */
      if ( blocs_ref->bloc[ind_Buvw].valid != 1 ) continue;
      
      measures[z*xymeas+y*xmeas+x] = Similarite3D( blocs_flo->p_bloc[i], 
						   &(blocs_ref->bloc[ind_Buvw]),
						   inrimage_flo, inrimage_ref, param );
    
    }
    
    /* it may happens that the NULL displacement has not be considered
     */
    measure_0 = measure_default;
    if ( param->bl_size_neigh_x % param->bl_next_neigh_x != 0
	 || param->bl_size_neigh_y % param->bl_next_neigh_y != 0
	 || param->bl_size_neigh_z % param->bl_next_neigh_z != 0 ) {
      
#ifdef _OLD_BEHAVIOR_
      ind_Buvw = c + (b + a * blocs_ref->n_blocks_y) * blocs_ref->n_blocks_z;
#else
      ind_Buvw = c + (b + a * blocs_ref->n_blocks_y) * blocs_ref->n_blocks_x;
#endif
      if ( blocs_ref->bloc[ind_Buvw].valid == 1 )
	measure_0 = Similarite3D( blocs_flo->p_bloc[i], 
				  &(blocs_ref->bloc[ind_Buvw]),
				  inrimage_flo, inrimage_ref, param );
    }
    else {
      measure_0 = measures[ (param->bl_size_neigh_z/param->bl_next_neigh_z)*xymeas
			  + (param->bl_size_neigh_y/param->bl_next_neigh_y)*xmeas
			  + (param->bl_size_neigh_x/param->bl_next_neigh_x) ];
    }
    
    /* choice of the "best" pairing
     */
    measure_max = measure_0;
    k_max = c;
    j_max = b;
    i_max = a;

    for ( u = minu, x = minx; u <= maxu; u += param->bl_next_neigh_x, x++ )
    for ( v = minv, y = miny; v <= maxv; v += param->bl_next_neigh_y, y++ )
    for ( w = minw, z = minz; w <= maxw; w += param->bl_next_neigh_z, z++ ) {
      if ( measures[z*xymeas+y*xmeas+x] > measure_max ) {
	measure_max = measures[z*xymeas+y*xmeas+x];
	k_max = w;
	j_max = v;
	i_max = u;
      }
    }

    /* is it "best" enough ?
     */
    if ( (measure_max > param->seuil_mesure) ) {
      switch( field -> type ) {
      default :
	if ( _verbose_ )
	  fprintf (stderr, "%s: such field type not handled in switch\n", proc );
	free( measures );
	return;
      case _ScalarWeighted2DDisplacement_ :
	{
	  typeScalarWeighted2DDisplacement *thePairs = 
	    (typeScalarWeighted2DDisplacement *)field->pairs;
	  thePairs[n_pairs].x = a + demi_bl_dx;
	  thePairs[n_pairs].y = b + demi_bl_dy;
	  thePairs[n_pairs].u = i_max - a;
	  thePairs[n_pairs].v = j_max - b;
	  thePairs[n_pairs].rho = measure_max;
	  n_pairs ++;
	}
	break;
      case _ScalarWeighted3DDisplacement_ :
	{
	  typeScalarWeighted3DDisplacement *thePairs = 
	    (typeScalarWeighted3DDisplacement *)field->pairs;
	  thePairs[n_pairs].x = a + demi_bl_dx;
	  thePairs[n_pairs].y = b + demi_bl_dy;
	  thePairs[n_pairs].z = c + demi_bl_dz;
	  thePairs[n_pairs].u = i_max - a;
	  thePairs[n_pairs].v = j_max - b;
	  thePairs[n_pairs].w = k_max - c;
	  thePairs[n_pairs].rho = measure_max;
	  n_pairs ++;
	}
	break;
      }
    }
  }

  free( measures );
  field->n_pairs = n_pairs;
  
  if ( 0 && param->verbose >= 1 ) {
    fprintf(stderr,"\nIl y avait %d couples\n", blocs_flo->n_valid_blocks);
    fprintf(stderr,"On a gardé %d couples, soit %.2f%%\n",
	    field->n_pairs, (double)(field->n_pairs*100)/(double)(blocs_flo->n_valid_blocks));
  }
}


void CalculChampVecteur2D ( FIELD *field,
			       bal_image *inrimage_flo, BLOCS *blocs_flo,
			       bal_image *inrimage_ref, BLOCS *blocs_ref,
			       PARAM *param )
{
  char *proc = "CalculChampVecteur2D";
  int a, b, u, v, i, ind_Buv;
  int i_max = 0;
  int j_max = 0;
  int pourcent, pourcent_old;

  double measure_max, measure_0;
  double measure_default = -2.0;
  double *measures = NULL;
  int xmeas, ymeas;
  int x, y, minx, miny;
  int n_pairs;

  double demi_bl_dx = (double) (param->bl_dx) / 2.0;
  double demi_bl_dy = (double) (param->bl_dy) / 2.0;

  int minu, maxu;
  int minv, maxv;

  n_pairs = field->n_pairs = 0;

  xmeas = 1+(2*param->bl_size_neigh_x)/param->bl_next_neigh_x;
  ymeas = 1+(2*param->bl_size_neigh_y)/param->bl_next_neigh_y;
  measures = (double*)malloc( xmeas * ymeas * sizeof( double ) );
  if ( measures == NULL ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: unable to allocate measures array\n", proc );
    return;
  }
  /***
      Passe sur les blocs retenus de l'image flottante, et exploration
      d'un voisinage de chaque bloc dans l'image de reference 

      Rappel: a, b : origine du bloc
  ***/
  pourcent_old = 0;

  for (i=0; i<blocs_flo->n_valid_blocks; i++) { 
    a = blocs_flo->p_bloc[i]->a;      
    b = blocs_flo->p_bloc[i]->b;

    /*    fprintf(stderr," \r");*/
    pourcent = i*100/blocs_flo->n_valid_blocks;
    if ( pourcent_old != pourcent ) {
#ifdef _OLD_BEHAVIOR_
      fprintf( stderr," %d%%\r", pourcent );
#else
      if ( param->verbose > 0 && param->verbosef != NULL ) {
	if ( param->verbosef == stderr )
	  fprintf( param->verbosef," %d%%\r", pourcent );
	else 
	  fprintf( param->verbosef," %d%%\n", pourcent );
      }
#endif
      pourcent_old = pourcent;
    }

    /***
	Pour un bloc donne dans l'image flottante, on calcule la mesure de
	similarite avec un certain nombre de blocs de l'image de reference
	
	Pas de progression : bl_next_neigh_? 
	
	Dimensions du voisinage d'exploration : - bl_size_neigh ... bl_size_neigh
    ***/
    for ( x=xmeas*ymeas-1; x>=0; x-- ) measures[x] = measure_default;

    minu = a-param->bl_size_neigh_x;
    maxu = a+param->bl_size_neigh_x;
    minv = b-param->bl_size_neigh_y;
    maxv = b+param->bl_size_neigh_y;

    minx = miny = 0;

    while ( minu < 0 ) { minu += param->bl_next_neigh_x; minx ++; }
    while ( minv < 0 ) { minv += param->bl_next_neigh_y; miny ++; }
    if ( maxu >= blocs_ref->n_blocks_x ) maxu = blocs_ref->n_blocks_x - 1;
    if ( maxv >= blocs_ref->n_blocks_y ) maxv = blocs_ref->n_blocks_y - 1;
    
    for ( u = minu, x = minx; u <= maxu; u += param->bl_next_neigh_x, x++ )
    for ( v = minv, y = miny; v <= maxv; v += param->bl_next_neigh_y, y++ ) {

      /* index of  B(u,v) in blocs_ref->bloc 
	 this is linked to the building of blocs_ref
	 cf Allocate_Blocks()
      */
#ifdef _OLD_BEHAVIOR_
      ind_Buv = v + u * blocs_ref->n_blocks_y;
#else
      ind_Buv = u + v * blocs_ref->n_blocks_x;
#endif
	  
      /* bloc B(u,v) actif ? */
      if ( blocs_ref->bloc[ind_Buv].valid != 1 ) continue;

      measures[y*xmeas+x] = Similarite2D( blocs_flo->p_bloc[i], 
					  &(blocs_ref->bloc[ind_Buv]),
					  inrimage_flo, inrimage_ref,
					  param );
    }

    
    /* it may happens that the NULL displacement has not be considered
     */
    measure_0 = measure_default;
    if ( param->bl_size_neigh_x % param->bl_next_neigh_x != 0
	 || param->bl_size_neigh_y % param->bl_next_neigh_y != 0 ) {
      
#ifdef _OLD_BEHAVIOR_
      ind_Buv = b + a * blocs_ref->n_blocks_y;
#else
      ind_Buv = b + a * blocs_ref->n_blocks_y;
#endif
      if ( blocs_ref->bloc[ind_Buv].valid == 1 )
	measure_0 = Similarite2D( blocs_flo->p_bloc[i], 
				  &(blocs_ref->bloc[ind_Buv]),
				  inrimage_flo, inrimage_ref, param );
    }
    else {
      measure_0 = measures[ (param->bl_size_neigh_y/param->bl_next_neigh_y)*xmeas
			  + (param->bl_size_neigh_x/param->bl_next_neigh_x) ];
    }
    
    /* choice of the "best" pairing
     */
    measure_max = measure_0;
    j_max = b;
    i_max = a;

    for ( u = minu, x = minx; u <= maxu; u += param->bl_next_neigh_x, x++ )
    for ( v = minv, y = miny; v <= maxv; v += param->bl_next_neigh_y, y++ ) {
      if ( measures[y*xmeas+x] > measure_max ) {
	measure_max = measures[y*xmeas+x];
	j_max = v;
	i_max = u;
      }
    }

    /* is it "best" enough ?
     */
    if ( (measure_max > param->seuil_mesure) ) {
      switch( field -> type ) {
      default :
	if ( _verbose_ )
	  fprintf (stderr, "%s: such field type not handled in switch\n", proc );
	free( measures );
	return;
      case _ScalarWeighted2DDisplacement_ :
	{
	  typeScalarWeighted2DDisplacement *thePairs = 
	    (typeScalarWeighted2DDisplacement *)field->pairs;
	  thePairs[n_pairs].x = a + demi_bl_dx;
	  thePairs[n_pairs].y = b + demi_bl_dy;
	  thePairs[n_pairs].u = i_max - a;
	  thePairs[n_pairs].v = j_max - b;
	  thePairs[n_pairs].rho = measure_max;
	  n_pairs ++;
	}
	break;
      case _ScalarWeighted3DDisplacement_ :
	{
	  typeScalarWeighted3DDisplacement *thePairs = 
	    (typeScalarWeighted3DDisplacement *)field->pairs;
	  thePairs[n_pairs].x = a + demi_bl_dx;
	  thePairs[n_pairs].y = b + demi_bl_dy;
	  thePairs[n_pairs].z = 0.0;
	  thePairs[n_pairs].u = i_max - a;
	  thePairs[n_pairs].v = j_max - b;
	  thePairs[n_pairs].w = 0.0;
	  thePairs[n_pairs].rho = measure_max;
	  n_pairs ++;
	}
	break;
      }
    }
  }

  free( measures );
  field->n_pairs = n_pairs;
  
  if ( 0 && param->verbose >= 1 ) {
    fprintf(stderr,"\nIl y avait %d couples\n", blocs_flo->n_valid_blocks);
    fprintf(stderr,"On a gardé %d couples, soit %.2f%%\n",
	    field->n_pairs, (double)(field->n_pairs*100)/(double)(blocs_flo->n_valid_blocks));
  }
}


/***
    Calcul du champ de vecteurs entre Image_ref et Image_flo
    - chapeau du calcul 2D ou 3D
***/
void CalculChampVecteurs (FIELD *field,
			  bal_image *inrimage_flo, BLOCS *blocs_flo,
			  bal_image *inrimage_ref, BLOCS *blocs_ref,
			  PARAM *param )
{
  if (inrimage_ref->nplanes  == 1)
    CalculChampVecteur2D (field, 
			  inrimage_flo, blocs_flo, inrimage_ref, blocs_ref,
			  param );
  else
    CalculChampVecteur3D (field,
			  inrimage_flo, blocs_flo, inrimage_ref, blocs_ref,
			  param );
}















int CalculAttributsBlocsWithNoBorders_2D (bal_image *inrimage, 
			     BLOCS *blocs, 
			     int seuil_bas, int seuil_haut, double percent,
			     PARAM *param )

{
  char *proc = "CalculAttributsBlocsWithNoBorders_2D";

  int n;
  int n_passive_voxels;  
  int n_max_passive_voxels = (int)
    ( (percent) * (double)blocs->block_size_x * (double)blocs->block_size_y + 0.5);
  int n_valid_blocks = 0;

  int n_pts = blocs->block_size_x * blocs->block_size_y;

  int dimx = inrimage->ncols;
  int a, b, i, j;
  int posx, posy;

  double sum, moy;
  
  /* it is implicitly assumed that blocks are included
     in the image.
     Do tests on the intensity value only when needed.
  */

#define _ATTRIBUTES_2D_NO_TEST_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      blocs->bloc[n].inclus = 1; \
      blocs->bloc[n].valid = 1; \
      moy = sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) \
        sum += buf[posx]; \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) \
        sum += (buf[posx] - moy)*(buf[posx] - moy); \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
    } \
    blocs->n_valid_blocks = blocs->n_blocks; \
    n_valid_blocks = blocs->n_blocks; \
  }

#define _ATTRIBUTES_2D_TEST_MIN_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      n_pts = 0;   moy = sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas ) n_passive_voxels ++; \
        else { sum += buf[posx];   n_pts ++; } \
      } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas ) continue; \
	sum += (buf[posx] - moy)*(buf[posx] - moy); \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define _ATTRIBUTES_2D_TEST_MIN_MAX_ {  \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      n_pts = 0;   moy = sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) n_passive_voxels ++; \
        else { sum += buf[posx];   n_pts ++; } \
      } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) continue; \
	sum += (buf[posx] - moy)*(buf[posx] - moy); \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define  _ATTRIBUTES_2D_(_MIN_,_MAX_) { \
    if ( seuil_bas < _MIN_ && seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_2D_NO_TEST_ \
    } \
    else if ( seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_2D_TEST_MIN_ \
    } \
    else { \
      _ATTRIBUTES_2D_TEST_MIN_MAX_ \
    } \
  }

  switch ( inrimage->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such image type is not handled yet\n", proc );
    return( RETURNED_VALUE_ON_ERROR );
  case VT_UNSIGNED_CHAR : 
    {
      unsigned char *buf = inrimage->data;
      _ATTRIBUTES_2D_( 0, 255 )
    }
    break;
  case VT_UNSIGNED_SHORT : 
    {
      unsigned short int *buf = inrimage->data;
      _ATTRIBUTES_2D_( 0, 65535 )
    }
    break;
  case VT_SIGNED_SHORT : 
    {
      short int *buf = inrimage->data;
      _ATTRIBUTES_2D_( -32768, 32767 )
    }
    break;
  }


#ifdef _OLD_BEHAVIOR_
  /* the formulas for the number of blocks was wrong
     some of the new blocks have to to discarded
     to get exactly the same behavior
  */
  for ( n=0; n<blocs->n_blocks; n++ ) {
    if ( blocs->bloc[n].a >= inrimage->ncols - blocs->block_size_x 
	 || blocs->bloc[n].b >= inrimage->nrows - blocs->block_size_y ) {
      if ( blocs->bloc[n].valid ) {
	blocs->bloc[n].valid = 0;
	blocs->bloc[n].var  = 0;
	n_valid_blocks --;
      }
    }
  }
  blocs->n_valid_blocks = n_valid_blocks;
#endif


  return( blocs->n_blocks );
}



int CalculAttributsBlocsWithBorders_2D (bal_image *inrimage, 
			     BLOCS *blocs, 
			     int seuil_bas, int seuil_haut, double percent,
			     PARAM *param )

{
  char *proc = "CalculAttributsBlocsWithBorders_2D";

  int n;
  int n_passive_voxels;  
  int n_max_passive_voxels = (int)
    ( (percent) * (double)blocs->block_size_x * (double)blocs->block_size_y + 0.5);
  int n_valid_blocks = 0;

  int n_pts;

  int dimx = inrimage->ncols;
  int dimxy = dimx * inrimage->nrows;
  int a, b, i, j;
  int posx, posy;

  double sum, moy;
  
  /* it is implicitly assumed that blocks are included
     in the image.
     Do tests on the intensity value only when needed.
  */

#define _ATTRIBUTES_2D_WB_NO_TEST_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      blocs->bloc[n].inclus = 1; \
      blocs->bloc[n].valid = 1; \
      n_pts = 0;   moy = sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  sum += buf[posx]; \
	  n_pts ++; \
	} \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  sum += (buf[posx] - moy)*(buf[posx] - moy); \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
    } \
    blocs->n_valid_blocks = blocs->n_blocks; \
    n_valid_blocks = blocs->n_blocks; \
  }

#define _ATTRIBUTES_2D_WB_TEST_MIN_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
	for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	  if ( buf[posx] <= seuil_bas ) n_passive_voxels ++; \
	} \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      n_pts = 0;   moy = sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  if ( buf[posx] <= seuil_bas ) continue; \
	  sum += buf[posx]; \
	  n_pts ++; \
	} \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  if ( buf[posx] <= seuil_bas ) continue; \
	  sum += (buf[posx] - moy)*(buf[posx] - moy); \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define _ATTRIBUTES_2D_WB_TEST_MIN_MAX_ {  \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      for (j = 0, posy = b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
	for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	  if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut )  \
	    n_passive_voxels ++; \
	} \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      n_pts = 0;   moy = sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut )  \
	  sum += buf[posx]; \
	  n_pts ++; \
	} \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( j = 0, posy = (b-blocs->block_border_y)*dimx; \
	      j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
	if ( posy < 0 || posy >= dimxy ) continue; \
	for ( i = 0, posx = posy + a - blocs->block_border_x; \
              i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
          if ( posx < 0 || posx >= dimxy ) continue; \
	  if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut )  \
	  sum += (buf[posx] - moy)*(buf[posx] - moy); \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define  _ATTRIBUTES_2D_WB_(_MIN_,_MAX_) { \
    if ( seuil_bas < _MIN_ && seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_2D_WB_NO_TEST_ \
    } \
    else if ( seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_2D_WB_TEST_MIN_ \
    } \
    else { \
      _ATTRIBUTES_2D_WB_TEST_MIN_MAX_ \
    } \
  }

  switch ( inrimage->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such image type is not handled yet\n", proc );
    return( RETURNED_VALUE_ON_ERROR );
  case VT_UNSIGNED_CHAR : 
    {
      unsigned char *buf = inrimage->data;
      _ATTRIBUTES_2D_WB_( 0, 255 )
    }
    break;
  case VT_UNSIGNED_SHORT : 
    {
      unsigned short int *buf = inrimage->data;
      _ATTRIBUTES_2D_WB_( 0, 65535 )
    }
    break;
  case VT_SIGNED_SHORT : 
    {
      short int *buf = inrimage->data;
      _ATTRIBUTES_2D_WB_( -32768, 32767 )
    }
    break;
  }


#ifdef _OLD_BEHAVIOR_
  /* the formulas for the number of blocks was wrong
     some of the new blocks have to to discarded
     to get exactly the same behavior
  */
  for ( n=0; n<blocs->n_blocks; n++ ) {
    if ( blocs->bloc[n].a >= inrimage->ncols - blocs->block_size_x 
	 || blocs->bloc[n].b >= inrimage->nrows - blocs->block_size_y ) {
      if ( blocs->bloc[n].valid ) {
	blocs->bloc[n].valid = 0;
	blocs->bloc[n].var  = 0;
	n_valid_blocks --;
      }
    }
  }
  blocs->n_valid_blocks = n_valid_blocks;
#endif


  return( blocs->n_blocks );
}



int CalculAttributsBlocs_2D (bal_image *inrimage, 
			     BLOCS *blocs, 
			     int seuil_bas, int seuil_haut, double percent,
			     PARAM *param )

{
  char *proc = "CalculAttributsBlocs_2D";

  if ( blocs->block_border_x < 0 || blocs->block_border_y < 0 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: negative values of blocks borders\n", proc );
    return( 0 );
  }

  if ( blocs->block_border_x == 0 && blocs->block_border_y == 0 ) 
    return( CalculAttributsBlocsWithNoBorders_2D( inrimage, blocs, seuil_bas, 
						  seuil_haut, percent, param ) );

  return( CalculAttributsBlocsWithBorders_2D( inrimage, blocs, seuil_bas, 
					      seuil_haut, percent, param ) );
}



int CalculAttributsBlocsWithNoBorders_3D ( bal_image *inrimage, BLOCS *blocs, 
				 int seuil_bas, int seuil_haut, double percent,
				 PARAM *param )

{
  char *proc = "CalculAttributsBlocsWithNoBorders_3D";

  int n;
  int n_passive_voxels;  
  int n_max_passive_voxels = (int)
    ( (percent) * (double)blocs->block_size_x * (double)blocs->block_size_y 
      * (double)blocs->block_size_z + 0.5);
  int n_valid_blocks = 0;

  int n_pts = blocs->block_size_x * blocs->block_size_y * blocs->block_size_z;

  int dimx = inrimage->ncols;
  int dimxy = dimx * inrimage->nrows;
  int a, b, c, i, j, k;
  int posx, posy, posz;

  double sum, moy;

  /* it is implicitly assumed that blocks are included
     in the image.
     Do tests on the intensity value only when needed.
  */

#define _ATTRIBUTES_3D_NO_TEST_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      blocs->bloc[n].inclus = 1; \
      blocs->bloc[n].valid = 1; \
      moy = sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) \
	sum += buf[posx]; \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) \
	sum += (buf[posx] - moy)*(buf[posx] - moy); \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
    } \
    blocs->n_valid_blocks = blocs->n_blocks; \
    n_valid_blocks = blocs->n_blocks; \
  }

#define _ATTRIBUTES_3D_TEST_MIN_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      n_pts = 0;   moy = sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas ) n_passive_voxels ++; \
        else { sum += buf[posx];   n_pts ++; } \
      } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      n_pts = 0;   moy = sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas ) continue; \
	sum += (buf[posx] - moy)*(buf[posx] - moy); \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define _ATTRIBUTES_3D_TEST_MIN_MAX_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      n_pts = 0;   moy = sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) n_passive_voxels ++; \
        else { sum += buf[posx];   n_pts ++; } \
      } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      n_pts = 0;   moy = sum = 0.0; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
      for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
      for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) continue; \
	sum += (buf[posx] - moy)*(buf[posx] - moy); \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define  _ATTRIBUTES_3D_(_MIN_,_MAX_) { \
    if ( seuil_bas < _MIN_ && seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_3D_NO_TEST_ \
    } \
    else if ( seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_3D_TEST_MIN_ \
    } \
    else { \
      _ATTRIBUTES_3D_TEST_MIN_MAX_ \
    } \
  }

  switch ( inrimage->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such image type is not handled yet\n", proc );
    return( RETURNED_VALUE_ON_ERROR );
  case VT_UNSIGNED_CHAR : 
    {
      unsigned char *buf = (unsigned char*)inrimage->data;
      _ATTRIBUTES_3D_( 0, 255 )
    }
    break;
  case VT_UNSIGNED_SHORT : 
    {
      unsigned short int *buf = (unsigned short int*)inrimage->data;
      _ATTRIBUTES_3D_( 0, 65535 )
    }
    break;
  case VT_SIGNED_SHORT : 
    {
      short int *buf = (short int*)inrimage->data;
      _ATTRIBUTES_3D_( -32768, 32767 )
    }
    break;
  }


#ifdef _OLD_BEHAVIOR_
  /* the formulas for the number of blocks was wrong
     some of the new blocks have to to discarded
     to get exactly the same behavior
  */
  for ( n=0; n<blocs->n_blocks; n++ ) {
    if ( blocs->bloc[n].a >= inrimage->ncols - blocs->block_size_x 
	 || blocs->bloc[n].b >= inrimage->nrows - blocs->block_size_y 
	 || blocs->bloc[n].c >= inrimage->nplanes - blocs->block_size_z) {
      if ( blocs->bloc[n].valid ) {
	blocs->bloc[n].valid = 0;
	blocs->bloc[n].var  = 0;
	n_valid_blocks --;
      }
    }
  }
  blocs->n_valid_blocks = n_valid_blocks;
#endif


  return( blocs->n_blocks );
}



int CalculAttributsBlocsWithBorders_3D ( bal_image *inrimage, BLOCS *blocs, 
				 int seuil_bas, int seuil_haut, double percent,
				 PARAM *param )

{
  char *proc = "CalculAttributsBlocsWithBorders_3D";

  int n;
  int n_passive_voxels;  
  int n_max_passive_voxels = (int)
    ( (percent) * (double)blocs->block_size_x * (double)blocs->block_size_y 
      * (double)blocs->block_size_z + 0.5);
  int n_valid_blocks = 0;

  int n_pts;

  int dimx = inrimage->ncols;
  int dimxy = dimx * inrimage->nrows;
  int dimxyz = dimxy * inrimage->nplanes;
  int a, b, c, i, j, k;
  int posx, posy, posz;

  double sum, moy;
  
  /* it is implicitly assumed that blocks are included
     in the image.
     Do tests on the intensity value only when needed.
  */

#define _ATTRIBUTES_3D_WB_NO_TEST_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      blocs->bloc[n].inclus = 1; \
      blocs->bloc[n].valid = 1; \
      n_pts = 0;   moy = sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    sum += buf[posx]; \
	    n_pts ++; \
	  } \
	} \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    sum += (buf[posx] - moy)*(buf[posx] - moy); \
	  } \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
    } \
    blocs->n_valid_blocks = blocs->n_blocks; \
    n_valid_blocks = blocs->n_blocks; \
  }

#define _ATTRIBUTES_3D_WB_TEST_MIN_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
	for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
	  for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	    if ( buf[posx] <= seuil_bas ) n_passive_voxels ++; \
	  } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      n_pts = 0;   moy = sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    if ( buf[posx] <= seuil_bas ) continue; \
	    sum += buf[posx]; \
	    n_pts ++; \
	  } \
	} \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    if ( buf[posx] <= seuil_bas ) continue; \
	    sum += (buf[posx] - moy)*(buf[posx] - moy); \
	  } \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define _ATTRIBUTES_3D_WB_TEST_MIN_MAX_ { \
    for ( n=0; n<blocs->n_blocks; n++ ) { \
      n_passive_voxels = 0; \
      a = blocs->bloc[n].a; \
      b = blocs->bloc[n].b; \
      c = blocs->bloc[n].c; \
      for (k = 0, posz = c*dimxy; k<blocs->block_size_z; k++, posz+=dimxy ) \
	for (j = 0, posy = posz + b*dimx; j<blocs->block_size_y; j++, posy+=dimx ) \
	  for (i = 0, posx = posy + a; i<blocs->block_size_x; i++, posx ++ ) { \
	    if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) n_passive_voxels ++; \
	  } \
      blocs->bloc[n].inclus = ( n_passive_voxels == 0 ) ? 1 : 0; \
      blocs->bloc[n].valid = ( n_passive_voxels < n_max_passive_voxels ) ? 1 : 0; \
      if ( blocs->bloc[n].valid == 0 ) { \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      n_pts = 0;   moy = sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) continue; \
	    sum += buf[posx]; \
	    n_pts ++; \
	  } \
	} \
      } \
      if ( n_pts == 0 ) { \
	blocs->bloc[n].valid = 0; \
	blocs->bloc[n].var = 0.0; \
	continue; \
      } \
      blocs->bloc[n].moy  = moy = sum / (double)n_pts; \
      sum = 0.0; \
      for ( k = 0, posz = (c-blocs->block_border_z)*dimxy; \
            k<blocs->block_size_z+2*blocs->block_border_z; k++, posz+=dimxy ) { \
        if ( posz < 0 || posz >= dimxyz ) continue; \
	for ( j = 0, posy = posz + (b-blocs->block_border_y)*dimx; \
              j<blocs->block_size_y+2*blocs->block_border_y; j++, posy+=dimx ) { \
          if ( posy < 0 || posy >= dimxyz ) continue; \
	  for ( i = 0, posx = posy + a - blocs->block_border_x; \
                i<blocs->block_size_x+2*blocs->block_border_x; i++, posx ++ ) { \
            if ( posx < 0 || posx >= dimxyz ) continue; \
	    if ( buf[posx] <= seuil_bas || buf[posx] >= seuil_haut ) continue; \
	    sum += (buf[posx] - moy)*(buf[posx] - moy); \
	  } \
	} \
      } \
      blocs->bloc[n].diff = sum; \
      blocs->bloc[n].var  = sum / (double)n_pts; \
      n_valid_blocks ++; \
    } \
    blocs->n_valid_blocks = n_valid_blocks; \
  }

#define  _ATTRIBUTES_3D_WB_(_MIN_,_MAX_) { \
    if ( seuil_bas < _MIN_ && seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_3D_WB_NO_TEST_ \
    } \
    else if ( seuil_haut > _MAX_ ) { \
      _ATTRIBUTES_3D_WB_TEST_MIN_ \
    } \
    else { \
      _ATTRIBUTES_3D_WB_TEST_MIN_MAX_ \
    } \
  }

  switch ( inrimage->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such image type is not handled yet\n", proc );
    return( RETURNED_VALUE_ON_ERROR );
  case VT_UNSIGNED_CHAR : 
    {
      unsigned char *buf = (unsigned char*)inrimage->data;
      _ATTRIBUTES_3D_WB_( 0, 255 )
    }
    break;
  case VT_UNSIGNED_SHORT : 
    {
      unsigned short int *buf = (unsigned short int*)inrimage->data;
      _ATTRIBUTES_3D_WB_( 0, 65535 )
    }
    break;
  case VT_SIGNED_SHORT : 
    {
      short int *buf = (short int*)inrimage->data;
      _ATTRIBUTES_3D_WB_( -32768, 32767 )
    }
    break;
  }


#ifdef _OLD_BEHAVIOR_
  /* the formulas for the number of blocks was wrong
     some of the new blocks have to to discarded
     to get exactly the same behavior
  */
  for ( n=0; n<blocs->n_blocks; n++ ) {
    if ( blocs->bloc[n].a >= inrimage->ncols - blocs->block_size_x 
	 || blocs->bloc[n].b >= inrimage->nrows - blocs->block_size_y 
	 || blocs->bloc[n].c >= inrimage->nplanes - blocs->block_size_z) {
      if ( blocs->bloc[n].valid ) {
	blocs->bloc[n].valid = 0;
	blocs->bloc[n].var  = 0;
	n_valid_blocks --;
      }
    }
  }
  blocs->n_valid_blocks = n_valid_blocks;
#endif


  return( blocs->n_blocks );
}



int CalculAttributsBlocs_3D (bal_image *inrimage, 
			     BLOCS *blocs, 
			     int seuil_bas, int seuil_haut, double percent,
			     PARAM *param )

{
  char *proc = "CalculAttributsBlocs_3D";

  if ( blocs->block_border_x < 0 || blocs->block_border_y < 0 || blocs->block_border_z < 0 ) {
    if ( _verbose_ ) 
      fprintf( stderr, "%s: negative values of blocks borders\n", proc );
    return( 0 );
  }
  if ( blocs->block_border_x == 0 && blocs->block_border_y == 0 && blocs->block_border_z == 0 ) 
    return( CalculAttributsBlocsWithNoBorders_3D( inrimage, blocs, seuil_bas, 
						  seuil_haut, percent, param ) );

  return( CalculAttributsBlocsWithBorders_3D( inrimage, blocs, seuil_bas, 
					      seuil_haut, percent, param ) );
}



/***
    Calcul des attributs des blocs associes a une image a un niveau donne de la pyramide 
    - chapeau du calcul 2D ou 3D
***/

int CalculAttributsBlocs (bal_image *inrimage, BLOCS *blocks,
			  int seuil_bas, int seuil_haut, float seuil_pourcent, PARAM *param )
{
  int nb_blocs;

  if ( inrimage->nplanes == 1 )
    nb_blocs = 
      CalculAttributsBlocs_2D( inrimage, blocks, 
			       seuil_bas, seuil_haut, seuil_pourcent, param );
  else
    nb_blocs =
      CalculAttributsBlocs_3D( inrimage, blocks, 
			       seuil_bas, seuil_haut, seuil_pourcent, param );
  return( nb_blocs );
}










