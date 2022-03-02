

#include <mesure.h>

static int _verbose_ = 1;

#define _CORRELATION_COEFFICIENT_ERROR_VALUE_ -2
#define _MISC_ERROR_VALUE_ -10



/*--------------------------------------------------
 *
 * EXPORTED PROCEDURES
 *
 *
 --------------------------------------------------*/

/* return a small value that can not be returned
   for a real "measure"
*/
double SimilarityErrorValue( enumTypeMesure m )
{
  switch( m ) {
  default :
    return( _MISC_ERROR_VALUE_ );
  case MESURE_EXT_CC :
  case MESURE_CC :
    return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
  }
  return( _MISC_ERROR_VALUE_ );
}




static double CorrelationCoefficient3D( BLOC *bloc_flo, BLOC *bloc_ref,
					bal_image *inrimage_flo, 
					bal_image *inrimage_ref, 
					PARAM *param )
{
  char *proc = "CorrelationCoefficient3D";

  int i, j, k;

  int fpos, fposz, fposy;
  int fdxy = inrimage_flo->ncols * inrimage_flo->nrows;
  int fdx  = inrimage_flo->ncols;
  int rpos, rposz, rposy;
  int rdxy = inrimage_ref->ncols * inrimage_ref->nrows;
  int rdx  = inrimage_ref->ncols;

  int a = bloc_flo->a;
  int b = bloc_flo->b;
  int c = bloc_flo->c;
  int u = bloc_ref->a;
  int v = bloc_ref->b;
  int w = bloc_ref->c;

  int npts;
  double flo_moy, flo_sum, ref_moy, ref_sum;
  double rho, Ir2xIp2;

  /* all points of both blocks are used in the computation
     they are above their respective thresholds
  */
#define _MESURE_3D_CC_FLO_INC_REF_INC {                         \
    rho = 0.0; flo_moy = bloc_flo->moy; ref_moy = bloc_ref->moy;    \
    for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
      for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	   j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  rho += (flo_buf[ fpos ] - flo_moy) * (ref_buf[ rpos ] - ref_moy); \
	}                                                       \
    Ir2xIp2 = bloc_flo->diff * bloc_ref->diff;                  \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* check which points of both blocks are used in the computation
     such points are above their respective thresholds
  */
#define _MESURE_3D_CC_FLO_INC_REF_NON_INC(_RMAX_) {             \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_ref <= _RMAX_ ) {                    \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                     \
	  }                                                       \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                     \
	  }                                                       \
    }                                                             \
    else {                                                        \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
             j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
             j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                   \
	  }                                                     \
    }                                                           \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_3D_CC_FLO_NON_INC_REF_INC(_FMAX_) {             \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_flo <= _FMAX_ ) {                    \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy)  \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	         (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                     \
	  }                                                       \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy)  \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	         (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                     \
	  }                                                       \
    }                                                             \
    else {                                                        \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                     \
	  }                                                       \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                     \
	  }                                                       \
    }                                                           \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_3D_CC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) {  \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_ref <= _RMAX_ && param->seuil_haut_flo <= _FMAX_ ) { \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)    \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	         (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	         (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)    \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	         (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	         (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                   \
	  }                                                     \
    }                                                           \
    else {                                                      \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
              flo_sum += flo_buf[ fpos ]; \
              ref_sum += ref_buf[ rpos ]; \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
              flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
              ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
              rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	    }                                                   \
	  }                                                     \
    }                                                           \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* 
     Les 2 blocs sont-ils complets dans les images (par rapport aux seuils sur I) ? 
     
     Sinon, il faut calculer le nombre de voxels actifs communs aux 2 blocs et 
     recalculer moyenne, variance pour le coefficient de correlation
  */

#define _MESURE_3D_CC(_RMAX_,_FMAX_) {            \
    if ( bloc_flo->inclus ) {                     \
      if ( bloc_ref->inclus ) _MESURE_3D_CC_FLO_INC_REF_INC \
	_MESURE_3D_CC_FLO_INC_REF_NON_INC(_RMAX_) \
    }                                             \
    if ( bloc_ref->inclus ) {                     \
      _MESURE_3D_CC_FLO_NON_INC_REF_INC(_FMAX_)   \
    }                                             \
    _MESURE_3D_CC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) \
  }



  switch ( inrimage_flo->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such floating image type is not handled yet\n", proc );
    return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
  case VT_UNSIGNED_CHAR :
    {
      unsigned char *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 255, 255 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 32767, 255 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 65535, 255 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_SIGNED_SHORT :
    {
      short int *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 255, 32767 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 32767, 32767 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 65535, 32767 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_UNSIGNED_SHORT :
    {
      unsigned short int *flo_buf = inrimage_flo->data;
	
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 255, 65535 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  signed short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 32767, 65535 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_CC( 65535, 65535 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  } /* switch ( inrimage_flo->type ) */

  return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
}





static double ExtendedCorrelationCoefficient3D( BLOC *bloc_flo, BLOC *bloc_ref,
					bal_image *inrimage_flo, 
					bal_image *inrimage_ref, 
					PARAM *param )
{
  char *proc = "ExtendedCorrelationCoefficient3D";

  int i, j, k;

  int fpos, fposz, fposy;
  int fdxy = inrimage_flo->ncols * inrimage_flo->nrows;
  int fdx  = inrimage_flo->ncols;
  int rpos, rposz, rposy;
  int rdxy = inrimage_ref->ncols * inrimage_ref->nrows;
  int rdx  = inrimage_ref->ncols;

  int a = bloc_flo->a;
  int b = bloc_flo->b;
  int c = bloc_flo->c;
  int u = bloc_ref->a;
  int v = bloc_ref->b;
  int w = bloc_ref->c;

  int npts = param->bl_dx * param->bl_dy * param->bl_dz;
  double rho, Ir2xIp2, moyab, moyuv;

  /* all points of both blocks are used in the computation
     they are above their respective thresholds
  */
#define _MESURE_3D_ECC_FLO_INC_REF_INC {                         \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;    \
    for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
      for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	   j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	}                                                       \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var;                \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* check which points of both blocks are used in the computation
     such points are above their respective thresholds
  */
#define _MESURE_3D_ECC_FLO_INC_REF_NON_INC(_RMAX_) {             \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_ref <= _RMAX_ ) {                    \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                     \
	  }                                                       \
    }                                                             \
    else {                                                        \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
             j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
    }                                                           \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_3D_ECC_FLO_NON_INC_REF_INC(_FMAX_) {             \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_flo <= _FMAX_ ) {                    \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy)  \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	         (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                     \
	  }                                                       \
    }                                                             \
    else {                                                        \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
    }                                                           \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_3D_ECC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) {  \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_ref <= _RMAX_ && param->seuil_haut_flo <= _FMAX_ ) { \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)    \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	         (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	         (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	         (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
    }                                                           \
    else {                                                      \
      for (k = 0, fposz = c*fdxy, rposz = w*rdxy; k < param->bl_dz; k++, fposz += fdxy, rposz += rdxy) \
        for (j = 0, fposy = fposz + b*fdx, rposy = rposz + v*rdx; \
	     j < param->bl_dy; j++, fposy += fdx, rposy += rdx)   \
	  for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	    if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
              rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	      npts ++;                                            \
	    }                                                   \
	  }                                                     \
    }                                                           \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* 
     Les 2 blocs sont-ils complets dans les images (par rapport aux seuils sur I) ? 
     
     Sinon, il faut calculer le nombre de voxels actifs communs aux 2 blocs et 
     recalculer moyenne, variance pour le coefficient de correlation
  */

#define _MESURE_3D_ECC(_RMAX_,_FMAX_) {            \
    if ( bloc_flo->inclus ) {                     \
      if ( bloc_ref->inclus ) _MESURE_3D_ECC_FLO_INC_REF_INC \
	_MESURE_3D_ECC_FLO_INC_REF_NON_INC(_RMAX_) \
    }                                             \
    if ( bloc_ref->inclus ) {                     \
      _MESURE_3D_ECC_FLO_NON_INC_REF_INC(_FMAX_)   \
    }                                             \
    _MESURE_3D_ECC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) \
  }



  switch ( inrimage_flo->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such floating image type is not handled yet\n", proc );
    return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
  case VT_UNSIGNED_CHAR :
    {
      unsigned char *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 255, 255 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 32767, 255 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 65535, 255 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_SIGNED_SHORT :
    {
      short int *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 255, 32767 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 32767, 32767 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 65535, 32767 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_UNSIGNED_SHORT :
    {
      unsigned short int *flo_buf = inrimage_flo->data;
	
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 255, 65535 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  signed short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 32767, 65535 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_3D_ECC( 65535, 65535 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  } /* switch ( inrimage_flo->type ) */

  return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
}





/***
    Calcul de la mesure de similarité entre B(a,b,c) et B(u,v,w), 
    a, b, c, u, v, w origines des blocs 
***/
double Similarite3D( BLOC *bloc_flo, BLOC *bloc_ref,
		     bal_image *image_flo, bal_image *image_ref,
		     PARAM *param )
{
  char *proc = "Similarite3D";
  switch (param->mesure) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such measure is not implemented yet\n", proc );
    return( _MISC_ERROR_VALUE_ );
  case MESURE_CC :
    return( CorrelationCoefficient3D( bloc_flo, bloc_ref, image_flo, image_ref, param ) );
  case MESURE_EXT_CC :
    return( ExtendedCorrelationCoefficient3D( bloc_flo, bloc_ref, image_flo, image_ref, param ) );

    /*      A REVOIR PLUS TARD... E.B. 26/04/2002
	    case MESURE_CR: 
	    for (i=0;i<256;i++) {
	    cond.sum[i] = 0;
	    cond.square[i] = 0;
	    cond.Npoints[i] = 0;
	    }
	    cond.Ntotal = 0;
	    cond.sum_total = 0;
	    cond.square_total = 0;
	    
	    for (k=0; k < param->bl_dz; k++)
	    for (i = 0; i < param->bl_dx; i++)
	    for (j = 0; j < param->bl_dy; j++) {
	    
	    pos     = (w+k)*(dy_ref*dx_ref) + u + i + dx_ref*(v + j);
	    pos_ref = (c+k)*(dy_ref*dx_ref) + a + i + dx_ref*(b + j);
	    
	    i_ref_bas  = max(param->seuil_bas_flo,  flo_buf[pos_ref]);
	    i_ref_haut = min(param->seuil_haut_flo, flo_buf[pos_ref]);
	    i_flo_bas  = max(param->seuil_bas_ref,  ref_buf[pos]);
	    i_flo_haut = min(param->seuil_haut_ref, ref_buf[pos]);
	    
	    if (i_ref_bas == param->seuil_bas_flo)
	    nb_voxels_seuil_flo++;
	    if (i_ref_haut == param->seuil_haut_flo) 
	    nb_voxels_seuil_flo++;
	    if (i_flo_bas == param->seuil_bas_ref)
	    nb_voxels_seuil_ref++;
	    if (i_flo_haut == param->seuil_haut_ref) 
	    nb_voxels_seuil_ref++;
	    
	    if ( (nb_voxels_seuil_flo < nb_voxels_max_flo) &&
	    (nb_voxels_seuil_ref < nb_voxels_max_ref) ) { 
	    
	    cond.sum[flo_buf[pos_ref]]     += (double) ref_buf[pos];
	    cond.square[flo_buf[pos_ref]]  += (double) ref_buf[pos] * (double) ref_buf[pos];
	    cond.Npoints[flo_buf[pos_ref]] += 1.0;
	    cond.sum_total                 += (double) ref_buf[pos];
	    cond.square_total              += (double) ref_buf[pos] * (double) ref_buf[pos];
	    cond.Ntotal                    += 1.0;
	    } 
	    else 
	    return( RETURNED_VALUE_ON_ERROR );
	    }
	    
	    sigma = cond.square_total - (cond.sum_total * cond.sum_total) / cond.Ntotal;
	    
	    for(i=0;i<256;i++)
	    if(cond.Npoints[i] != 0)
	    PiSi += cond.square[i] - (cond.sum[i] * cond.sum[i]) / cond.Npoints[i]; 
	    
	    return (1 - PiSi/sigma);
	    break;
	    
	    case MESURE_OM: 
	    Init_OM(u, v, w, inrimage_ref , param, dx_ref, dy_ref, dz_ref, om2);
	    
	    for (i = 0; i<64; i++)
	    for (i=0; i<64; i++)
	    s[inv_rank_I1[om2[i].rank]] = i;
	    
	    for (i=1; i<65; i++) {
	    d[i-1] = i;
	    for (j = 0; j<i; j++)
	    if ( (s[j] +1) <= i)
	    d[i-1]--;
	    if (maxd <= d[i-1])
	    maxd = d[i-1];
	    }
	    
	    return ( 1.0 - 2.0*(float)(maxd) / (float)((int)(64.0/2.0)) );
	    break;
    */
    
  }
  return( _MISC_ERROR_VALUE_ );
}









/* Beware, this function return the square
   correlation coefficient.
   CC = sum ( (i-E[i])*(j-E[j]) / (SD[i]*SD[j]) )
   with SD[i] = standard deviation de i = sqrt( variance[i] )
*/
static double CorrelationCoefficient2D( BLOC *bloc_flo, BLOC *bloc_ref,
					bal_image *inrimage_flo, 
					bal_image *inrimage_ref, 
					PARAM *param )
{
  char *proc = "CorrelationCoefficient2D";

  int i, j;

  int fpos, fposy;
  int fdx  = inrimage_flo->ncols;
  int rpos, rposy;
  int rdx  = inrimage_ref->ncols;

  int a = bloc_flo->a;
  int b = bloc_flo->b;
  int u = bloc_ref->a;
  int v = bloc_ref->b;


  int npts;
  double flo_moy, flo_sum, ref_moy, ref_sum;
  double rho, Ir2xIp2;

  /* all points of both blocks are used in the computation
     they are above their respective thresholds
  */
#define _MESURE_2D_CC_FLO_INC_REF_INC {                       \
    rho = 0.0; flo_moy = bloc_flo->moy; ref_moy = bloc_ref->moy;  \
    for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
      for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	rho += (flo_buf[ fpos ] - flo_moy) * (ref_buf[ rpos ] - ref_moy); \
      }                                                       \
    Ir2xIp2 = bloc_flo->diff * bloc_ref->diff;                \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* check which points of both blocks are used in the computation
     such points are above their respective thresholds
  */
#define _MESURE_2D_CC_FLO_INC_REF_NON_INC(_RMAX_) {             \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_ref <= _RMAX_ ) {                    \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                            \
	  }                                                     \
	}                                                       \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                     \
	}                                                       \
    }                                                           \
    else {                                                      \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                            \
	  }                                                   \
	}                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                   \
	}                                                     \
    }                                                           \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_2D_CC_FLO_NON_INC_REF_INC(_FMAX_) {             \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_flo <= _FMAX_ ) {                    \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	       (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                            \
	  }                                                     \
	}                                                       \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	       (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                     \
	}                                                       \
    }                                                           \
    else {                                                      \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
        for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                          \
	  }                                                   \
	}                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
        for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                   \
	}                                                     \
    }                                                         \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_2D_CC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) {  \
    npts = 0; \
    flo_moy = ref_moy = 0.0; \
    flo_sum = ref_sum = 0.0; \
    if ( param->seuil_haut_ref <= _RMAX_ && param->seuil_haut_flo <= _FMAX_ ) { \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	       (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	       (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                          \
	  }                                                   \
	}                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	       (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	       (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                   \
	}                                                     \
     }                                                         \
    else {                                                    \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
            flo_sum += flo_buf[ fpos ]; \
            ref_sum += ref_buf[ rpos ]; \
	    npts ++;                                          \
	  }                                                   \
	}                                                     \
      if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
      flo_moy = flo_sum / (double)npts; \
      ref_moy = ref_sum / (double)npts; \
      rho = flo_sum = ref_sum = 0.0; \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
            flo_sum += (flo_buf[ fpos ] - flo_moy)*(flo_buf[ fpos ] - flo_moy); \
            ref_sum += (ref_buf[ rpos ] - ref_moy)*(ref_buf[ rpos ] - ref_moy); \
            rho     += (flo_buf[ fpos ] - flo_moy)*(ref_buf[ rpos ] - ref_moy); \
	  }                                                   \
	}                                                     \
    }                                                         \
    Ir2xIp2 = flo_sum * ref_sum; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / Ir2xIp2 ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* 
     Les 2 blocs sont-ils complets dans les images (par rapport aux seuils sur I) ? 
     
     Sinon, il faut calculer le nombre de voxels actifs communs aux 2 blocs et 
     recalculer moyenne, variance pour le coefficient de correlation
  */

#define _MESURE_2D_CC(_RMAX_,_FMAX_) {            \
    if ( bloc_flo->inclus ) {                     \
      if ( bloc_ref->inclus ) _MESURE_2D_CC_FLO_INC_REF_INC \
	_MESURE_2D_CC_FLO_INC_REF_NON_INC(_RMAX_) \
    }                                             \
    if ( bloc_ref->inclus ) {                     \
      _MESURE_2D_CC_FLO_NON_INC_REF_INC(_FMAX_)   \
    }                                             \
    _MESURE_2D_CC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) \
  }



  switch ( inrimage_flo->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such floating image type is not handled yet\n", proc );
    return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
  case VT_UNSIGNED_CHAR :
    {
      unsigned char *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 255, 255 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 32767, 255 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 65535, 255 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_SIGNED_SHORT :
    {
      short int *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 255, 32767 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 32767, 32767 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 65535, 32767 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_UNSIGNED_SHORT :
    {
      unsigned short int *flo_buf = inrimage_flo->data;
	
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 255, 65535 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  signed short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 32767, 65535 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_CC( 65535, 65535 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  } /* switch ( inrimage_flo->type ) */

  return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
}





static double ExtendedCorrelationCoefficient2D( BLOC *bloc_flo, BLOC *bloc_ref,
					bal_image *inrimage_flo, 
					bal_image *inrimage_ref, 
					PARAM *param )
{
  char *proc = "ExtendedCorrelationCoefficient2D";

  int i, j;

  int fpos, fposy;
  int fdx  = inrimage_flo->ncols;
  int rpos, rposy;
  int rdx  = inrimage_ref->ncols;

  int a = bloc_flo->a;
  int b = bloc_flo->b;
  int u = bloc_ref->a;
  int v = bloc_ref->b;


  int npts = param->bl_dx * param->bl_dy;
  double rho, Ir2xIp2, moyab, moyuv;

  /* all points of both blocks are used in the computation
     they are above their respective thresholds
  */
#define _MESURE_2D_ECC_FLO_INC_REF_INC {                      \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
      for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
      }                                                     \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var;                \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* check which points of both blocks are used in the computation
     such points are above their respective thresholds
  */
#define _MESURE_2D_ECC_FLO_INC_REF_NON_INC(_RMAX_) {          \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_ref <= _RMAX_ ) {                  \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (ref_buf[rpos] > param->seuil_bas_ref) &&        \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {      \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                            \
	  }                                                     \
	}                                                       \
    }                                                           \
    else {                                                      \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( ref_buf[rpos] > param->seuil_bas_ref ) {         \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                          \
	  }                                                   \
	}                                                     \
    }                                                           \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );         \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_2D_ECC_FLO_NON_INC_REF_INC(_FMAX_) {             \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_flo <= _FMAX_ ) {                    \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&        \
	       (flo_buf[fpos] < param->seuil_haut_flo) ) {      \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                            \
	  }                                                     \
	}                                                       \
    }                                                           \
    else {                                                      \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
        for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( flo_buf[fpos] > param->seuil_bas_flo ) {         \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                            \
	  }                                                   \
	}                                                     \
    }                                                         \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );       \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

#define _MESURE_2D_ECC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) {  \
    npts = 0;                                                 \
    rho = 0.0; moyab = bloc_flo->moy; moyuv = bloc_ref->moy;  \
    if ( param->seuil_haut_ref <= _RMAX_ && param->seuil_haut_flo <= _FMAX_ ) { \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) &&      \
	       (flo_buf[fpos] < param->seuil_haut_flo) &&     \
	       (ref_buf[rpos] > param->seuil_bas_ref) &&      \
	       (ref_buf[rpos] < param->seuil_haut_ref) ) {    \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                            \
	  }                                                   \
	}                                                     \
    }                                                         \
    else {                                                    \
      for (j = 0, fposy = b*fdx, rposy = v*rdx; j < param->bl_dy; j++, fposy += fdx, rposy += rdx) \
	for (i = 0, fpos = fposy + a, rpos = rposy + u; i < param->bl_dx; i++, fpos++, rpos++ ) { \
	  if ( (flo_buf[fpos] > param->seuil_bas_flo) && (ref_buf[rpos] > param->seuil_bas_ref) ) { \
            rho += (flo_buf[ fpos ] - moyab) * (ref_buf[ rpos ] - moyuv); \
	    npts ++;                                            \
	  }                                                   \
	}                                                     \
    }                                                         \
    if ( npts == 0 ) return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );       \
    Ir2xIp2 = bloc_flo->var * bloc_ref->var; \
    return( ( Ir2xIp2 > EPSILON ) ? ( (rho*rho) / (npts*npts*Ir2xIp2) ) : _CORRELATION_COEFFICIENT_ERROR_VALUE_ ); \
  }

  /* 
     Les 2 blocs sont-ils complets dans les images (par rapport aux seuils sur I) ? 
     
     Sinon, il faut calculer le nombre de voxels actifs communs aux 2 blocs et 
     recalculer moyenne, variance pour le coefficient de correlation
  */

#define _MESURE_2D_ECC(_RMAX_,_FMAX_) {            \
    if ( bloc_flo->inclus ) {                     \
      if ( bloc_ref->inclus ) _MESURE_2D_ECC_FLO_INC_REF_INC \
	_MESURE_2D_ECC_FLO_INC_REF_NON_INC(_RMAX_) \
    }                                             \
    if ( bloc_ref->inclus ) {                     \
      _MESURE_2D_ECC_FLO_NON_INC_REF_INC(_FMAX_)   \
    }                                             \
    _MESURE_2D_ECC_FLO_NON_INC_REF_NON_INC(_RMAX_,_FMAX_) \
  }



  switch ( inrimage_flo->type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such floating image type is not handled yet\n", proc );
    return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
  case VT_UNSIGNED_CHAR :
    {
      unsigned char *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 255, 255 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 32767, 255 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 65535, 255 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_SIGNED_SHORT :
    {
      short int *flo_buf = inrimage_flo->data;
      
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 255, 32767 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 32767, 32767 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 65535, 32767 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  case VT_UNSIGNED_SHORT :
    {
      unsigned short int *flo_buf = inrimage_flo->data;
	
      switch ( inrimage_ref->type ) {
      default :
	if ( _verbose_ )
	  fprintf( stderr, "%s: such reference image type is not handled yet\n", proc );
	return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
      case VT_UNSIGNED_CHAR :
	{
	  unsigned char *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 255, 65535 )
	}
	break;
      case VT_SIGNED_SHORT :
	{
	  signed short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 32767, 65535 )
	}
	break;
      case VT_UNSIGNED_SHORT :
	{
	  unsigned short int *ref_buf = inrimage_ref->data;
	  _MESURE_2D_ECC( 65535, 65535 )
	}
	break;
      } /* switch ( inrimage_ref->type ) */
    }
    break;
  } /* switch ( inrimage_flo->type ) */

  return( _CORRELATION_COEFFICIENT_ERROR_VALUE_ );
}





/***
    Calcul de la mesure de similarité entre B(a,b) et B(u,v), a, b, u, v origines des blocs 
***/
double Similarite2D( BLOC *bloc_flo, BLOC *bloc_ref,
		     bal_image *image_flo, bal_image *image_ref,
		     PARAM *param )
{
  char *proc = "Similarite2D";
  switch (param->mesure) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: such measure is not implemented yet\n", proc );
    return( _MISC_ERROR_VALUE_ );
  case MESURE_CC :
    return( CorrelationCoefficient2D( bloc_flo, bloc_ref, image_flo, image_ref, param ) );

  case MESURE_EXT_CC :
    return( ExtendedCorrelationCoefficient2D( bloc_flo, bloc_ref, image_flo, image_ref, param ) );
  
    /* A REVOIR PLUS TARD... E.B. 26/04/2002
      case MESURE_CR: 
      for (i=0;i<256;i++) {
      cond.sum[i] = 0;
      cond.square[i] = 0;
      cond.Npoints[i] = 0;
      }
      cond.Ntotal = 0;
      cond.sum_total = 0;
      cond.square_total = 0;
      
      for (i = 0; i < param->bl_dx; i++)
      for (j = 0, 
      pos      = u + i + v*rdx,
      pos_ref  = a + i + b*fdx;
      j < param->bl_dy; 
      j++, 
      pos     += dx_ref,
      pos_ref += dx_ref) {
      
      i_ref_bas  = max(param->seuil_bas_flo,  flo_buf[pos_ref]);
      i_ref_haut = min(param->seuil_haut_flo, flo_buf[pos_ref]);
      i_flo_bas  = max(param->seuil_bas_ref,  ref_buf[pos]);
      i_flo_haut = min(param->seuil_haut_ref, ref_buf[pos]);
      
      if (i_ref_bas == param->seuil_bas_flo)
      nb_voxels_seuil_flo++;
      if (i_ref_haut == param->seuil_haut_flo) 
      nb_voxels_seuil_flo++;
      if (i_flo_bas == param->seuil_bas_ref)
      nb_voxels_seuil_ref++;
      if (i_flo_haut == param->seuil_haut_ref) 
      nb_voxels_seuil_ref++;
      
      if ( (nb_voxels_seuil_flo < nb_voxels_max_flo) &&
      (nb_voxels_seuil_ref < nb_voxels_max_ref) ) { 
      
      cond.sum[flo_buf[pos_ref]]     += (double)ref_buf[pos];
      cond.square[flo_buf[pos_ref]]  += (double)ref_buf[pos] * (double)ref_buf[pos];
      cond.Npoints[flo_buf[pos_ref]] += 1.0;
      cond.sum_total                 += (double)ref_buf[pos];
      cond.square_total              += (double)ref_buf[pos] * (double)ref_buf[pos];
      cond.Ntotal                    += 1.0;
      } 
      else {
      return( RETURNED_VALUE_ON_ERROR ); 
      }
      }
      
      sigma = cond.square_total - (cond.sum_total*cond.sum_total)/cond.Ntotal;
      
      for(i=0;i<256;i++)
      if(cond.Npoints[i]!=0)
      PiSi += cond.square[i] - (cond.sum[i]*cond.sum[i])/cond.Npoints[i]; 
      
      return (1 - PiSi/sigma);
      
      break;
    */
  } /* switch (param->mesure) */
  
  return( _MISC_ERROR_VALUE_ );
}
