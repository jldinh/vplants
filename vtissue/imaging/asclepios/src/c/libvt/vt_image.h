#ifndef _vt_image_h_
#define _vt_image_h_

#ifdef __cplusplus
extern "C" {
#endif

#include <vt_typedefs.h>

/* Les differentes representations liees a l'architecture.
 */
typedef enum {
  CPU_UNKNOWN = 0,
  LITTLEENDIAN = 1,
  BIGENDIAN = 2
} CpuType;

extern CpuType MY_CPU;

#define TXT_LENGTH 2048

typedef struct vt_gis {
  float dt;       /* dimension temporelle */
  int off_bool;   /* offset */
  int off;     
  int roi_bool;   /* specification d'une ROI */
  vt_4tpt roi1;
  vt_4tpt roi2;
  int ref_bool;   /* specification d'une image de reference */
  char ref_name[STRINGLENGTH];
  vt_4tpt ref;
  int mod_bool;   /* specification de la modalite d'acquisition */
  char mod_name[STRINGLENGTH];
  int dir_bool;   /* specification de la direction d'acquisition */
  char dir_name[STRINGLENGTH];
  int or_bool;   /* specification de l'orientation d'acquisition */
  char or_name[STRINGLENGTH];
  int ca_bool;   /* position de CA */
  vt_ipt ca;
  int cp_bool;   /* position de CA */
  vt_ipt cp;
  int ip_bool;   /* coefficients du plan inter-hemispherique */
  vt_4fpt ip;
  int td_bool;   /* coefficients de Talairach */
  vt_4tpt td1;
  vt_4tpt td2;
  int txt_bool;  /* texte eventuel */
  char txt[TXT_LENGTH];
} vt_gis;

/* Structure image.

   Cette structure contient les champs suivants :

   char name[STRINGLENGTH] : le nom de l'image
        ("<" = standard input, ">" = standard output)
	
   int type : le type de l'image

   vt_4vpt dim : les dimensions de l'image
           v = dimension vectorielle,
           x = dimension selon X,
           y = dimension selon Y,
           z = dimension selon Z.

   vt_4vpt private_dim : dimensions pre-calculees
           v = dim.v,
	   x = dim.v * dim.x,
	   y = dim.v * dim.x * dim.y,
	   z = dim.v * dim.x * dim.y * dim.z.

   int cpu : CPU sur lequel a ete cree l'image

   void ***array : buffer a 3 dimensions
        la valeur d'un point est
        ((cast***)(array))[z][y][x*dimv+v]

   void *buf : buffer a 1 dimension (non-inclus dans le precedent)
        la valeur d'un point est
        ((cast*)(buf))[v + x*dv + y*dv*dx + z*dv*dx*dy]
 */

typedef struct vt_image {
  char name[STRINGLENGTH];
  ImageType type;
  vt_4vpt dim; /* dimension of image */
  vt_fpt siz;  /* voxel size */
  vt_fpt off;  /* translation or offset */
  vt_fpt rot;  /* rotation */
  vt_ipt ctr;
  CpuType cpu;
  void ***array;
  void *buf;
  
  /** User defined strings array. The user can use any internal purpose string.
      Each string is written at then end of header after a '#' character. */
  char **user;
  /** Number of user defined strings */
  unsigned int nuser;


} vt_image;

#include <vt_unix.h>
#include <vt_error.h>
#include <vt_names.h>

extern void   VT_Image( vt_image *image );
extern void   VT_InitFromImage( vt_image *image, vt_image *ref, char *name, int type );
extern void   VT_InitImage( vt_image *i, char *n, int x, int y, int z, int t );
extern int    VT_AllocImage( vt_image *image );
extern int    VT_AllocArray( vt_image *image );

extern void   VT_FreeImage( vt_image *image );

extern void    VT_InitVImage( vt_image *i, char *n, int v, int x, int y, int z, int t );
extern void VT_SetImageOffset( vt_image *image,
			double x,
			double y,
			double z );

extern void VT_SetImageRotation( vt_image *image,
			double x,
			double y,
			double z );


extern int     VT_SizeImage( vt_image *image );

extern int VT_Test1Image( vt_image *im, char *proc );
extern int VT_Test1VImage( vt_image *im, char *proc );
extern int VT_STest1Image( vt_image *im, char *proc );
extern int VT_Test2Image( vt_image *im1, vt_image *im2, char *proc );

#ifdef __cplusplus
}
#endif

#endif /* _vt_image_h_ */
