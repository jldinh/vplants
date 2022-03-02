#ifndef _vt_seuil_h_
#define _vt_seuil_h_

#ifdef __cplusplus
extern "C" {
#endif

#include <vt_common.h>

#ifndef NO_PROTO
extern int VT_Threshold( vt_image *im1, vt_image *im2, float thres );
extern int VT_Threshold2( vt_image *im1, vt_image *im2, float thres1, float thres2 );
extern int VT_GreyThreshold( vt_image *im1, vt_image *im2, float thres );
extern int VT_GreyThreshold2( vt_image *im1, vt_image *im2, float thres1, float thres2 );
#else
extern int VT_Threshold();
extern int VT_Threshold2();
extern int VT_GreyThreshold();
extern int VT_GreyThreshold2();
#endif /* NO_PROTO */

#ifdef __cplusplus
}
#endif

#endif /* _vt_seuil_h_ */
