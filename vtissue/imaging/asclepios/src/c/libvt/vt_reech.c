/*************************************************************************
 * vt_reech.c -
 *
 * $Id: vt_reech.c,v 1.5 2006/04/14 08:39:32 greg Exp $
 *
 * Copyright©INRIA 1999,2000
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: 
 * 
 *
 * ADDITIONS, CHANGES
 *	
 *	
 *	
 *
 */



#include <vt_reech.h>

static int _VERBOSE_ = 0;

/* Procedure de reechantillonnage "lineaire" 3D.

   La matrice 4x4 permet le passage des coordonnees
   de l'image resultat a l'image d'entree. On calcule
   ainsi pour chaque point de l'image resultat son
   correspondant en coordonnees reelles dans l'image 
   d'entree. On interpole alors lineairement l'intensite
   pour ce point.
*/

int Reech3DTriLin4x4( vt_image *theIm, /* input image */
		      vt_image *resIm, /* result image */
		      double *mat )
{
  char *proc="Reech3DTriLin4x4";
  int theDim[3], resDim[3];
  
  if (( theIm->dim.z == 1) && ( resIm->dim.z == 1))
    return( Reech2DTriLin4x4( theIm, resIm, mat ) );
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech3DTriLin4x4_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
    case SCHAR :
      Reech3DTriLin4x4_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
  case USHORT :
      Reech3DTriLin4x4_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case SSHORT :
      Reech3DTriLin4x4_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case FLOAT :
      Reech3DTriLin4x4_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

int Reech3DTriLin4x4gb( vt_image *theIm, /* input image */
			vt_image *resIm, /* result image */
			double *mat,
			float gain,
			float bias )
{
  char *proc="Reech3DTriLin4x4gb";
  int theDim[3], resDim[3];
  
  if (( theIm->dim.z == 1) && ( resIm->dim.z == 1))
    return( Reech2DTriLin4x4( theIm, resIm, mat ) );
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech3DTriLin4x4gb_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
    case SCHAR :
      Reech3DTriLin4x4gb_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case USHORT :
      Reech3DTriLin4x4gb_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case SSHORT :
      Reech3DTriLin4x4gb_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case FLOAT :
      Reech3DTriLin4x4gb_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

/* Procedure de reechantillonnage "lineaire" 3D.

   La matrice 4x4 permet le passage des coordonnees
   de l'image resultat a l'image d'entree. On calcule
   ainsi pour chaque point de l'image resultat son
   correspondant en coordonnees reelles dans l'image 
   d'entree. On prend alors l'intensite du point le
   plus proche pour ce point.
*/

int Reech3DNearest4x4( vt_image *theIm, /* input image */
		      vt_image *resIm, /* result image */
		      double *mat )
{
  char *proc="Reech3DNearest4x4";
  int theDim[3], resDim[3];
  
  if (( theIm->dim.z == 1) && ( resIm->dim.z == 1))
    return( Reech2DNearest4x4( theIm, resIm, mat ) );
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech3DNearest4x4_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
    case SCHAR :
      Reech3DNearest4x4_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
  case USHORT :
      Reech3DNearest4x4_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case SSHORT :
      Reech3DNearest4x4_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case FLOAT :
      Reech3DNearest4x4_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

/* Procedure de reechantillonnage "lineaire" 2D.

   La matrice 4x4 permet le passage des coordonnees
   de l'image resultat a l'image d'entree. On calcule
   ainsi pour chaque point de l'image resultat son
   correspondant en coordonnees reelles dans l'image 
   d'entree. On interpole alors lineairement l'intensite
   pour ce point.

   '2D' signifie que seule la partie de la matrice
   correspondant a une transformation 2D sera prise en
   compte.
*/

int Reech2DTriLin4x4( vt_image *theIm, /* input image */
		      vt_image *resIm, /* result image */
		      double *mat )
{
  char *proc="Reech2DTriLin4x4";
  int theDim[3], resDim[3];
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech2DTriLin4x4_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
    case SCHAR :
      Reech2DTriLin4x4_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
  case USHORT :
      Reech2DTriLin4x4_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case SSHORT :
      Reech2DTriLin4x4_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case FLOAT :
      Reech2DTriLin4x4_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

int Reech2DTriLin4x4gb( vt_image *theIm, /* input image */
			vt_image *resIm, /* result image */
			double *mat,
			float gain,
			float bias )
{
  char *proc="Reech2DTriLin4x4gb";
  int theDim[3], resDim[3];
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech2DTriLin4x4gb_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
    case SCHAR :
      Reech2DTriLin4x4gb_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case USHORT :
      Reech2DTriLin4x4gb_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case SSHORT :
      Reech2DTriLin4x4gb_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  case FLOAT :
      Reech2DTriLin4x4gb_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat, gain, bias );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

/* Procedure de reechantillonnage "lineaire" 2D.

   La matrice 4x4 permet le passage des coordonnees
   de l'image resultat a l'image d'entree. On calcule
   ainsi pour chaque point de l'image resultat son
   correspondant en coordonnees reelles dans l'image 
   d'entree. On prend alors l'intensite du point le
   plus proche pour ce point.

   '2D' signifie que seule la partie de la matrice
   correspondant a une transformation 2D sera prise en
   compte.
*/

int Reech2DNearest4x4( vt_image *theIm, /* input image */
		      vt_image *resIm, /* result image */
		      double *mat )
{
  char *proc="Reech2DNearest4x4";
  int theDim[3], resDim[3];
  if ( theIm->type != resIm->type ) return( -1 );
  if ( theIm->buf == resIm->buf ) return( -1 );
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  switch ( theIm->type ) {
    case UCHAR :
      Reech2DNearest4x4_u8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
    case SCHAR :
      Reech2DNearest4x4_s8( (void*)(theIm->buf), theDim,
			   (void*)(resIm->buf), resDim, mat );
      break;
  case USHORT :
      Reech2DNearest4x4_u16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case SSHORT :
      Reech2DNearest4x4_s16( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  case FLOAT :
      Reech2DNearest4x4_r32( (void*)(theIm->buf), theDim,
			    (void*)(resIm->buf), resDim, mat );
      break;
  default :
    VT_Error( "images type unknown or not supported", proc );
    return( -1 );
  }
  return( 1 );
}

/* Procedure de reechantillonnage "avec deformation" 3D.

   Les images de deformation contiennent, pour chaque point M
   de l'image resultat, les coordonnees d'un vecteur V pointant
   sur le point reel correspondant dans l'image d'entree.
   En fait, cette image d'entree peut avoir ete transformee
   par une matrice Mat^{-1} avant le calcul des deformations,
   donc le "vrai" point reel correspondant a M est donne par : 
                  M' = Mat * (M + v).
   L'intensite de M' est interpolee lineairement.
*/

int Reech3DTriLinDefBack( vt_image *theIm, /* input image */
			  vt_image *resIm, /* result image */
			  vt_image **theDef, /* deformation images */
			  double *theMatAfter, /* transformation matrix */
			  double *theMatBefore, /* transformation matrix */
			  double gain,
			  double bias )
{
  char *proc="Reech3DTriLinDefBack";
  int theDim[3], resDim[3], defDim[3];
  double mat[16];
  r32 *theSlice = (r32*)NULL;
  r32 *bufDef[3];
  int z;
  register r32 *ts;
  register int i, dxy;
  register double b=bias;
  register double g=gain;

  if ( ( (theDef[0])->type != FLOAT ) ||
       ( (theDef[1])->type != FLOAT ) ||
       ( (theDef[2])->type != FLOAT ) ) return( -1 );
  if ( (theDef[0])->dim.x != (theDef[1])->dim.x
       || (theDef[0])->dim.x != (theDef[2])->dim.x ) return( -1 );
  if ( (theDef[0])->dim.y != (theDef[1])->dim.y
       || (theDef[0])->dim.y != (theDef[2])->dim.y ) return( -1 );
  if ( (theDef[0])->dim.z != (theDef[1])->dim.z
       || (theDef[0])->dim.z != (theDef[2])->dim.z ) return( -1 );
  if ( theMatBefore == NULL ) {
    if ( resIm->dim.x != (theDef[0])->dim.x ) return( -1 );
    if ( resIm->dim.y != (theDef[0])->dim.y ) return( -1 );
    if ( resIm->dim.z != (theDef[0])->dim.z ) return( -1 );
  }

  if ( theIm->buf == resIm->buf ) return( -1 );

  if ( theMatAfter != (double*)NULL ) {
    for ( z = 0; z < 16; z ++ ) mat[z] = theMatAfter[z];
  } else {
    for ( z = 0; z < 16; z ++ ) mat[z] = 0.0;
    mat[0] = mat[5] = mat[10] = mat[15] = 1.0;
  }

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;
  
  defDim[0] = (theDef[0])->dim.x;
  defDim[1] = (theDef[0])->dim.y;
  defDim[2] = (theDef[0])->dim.z;
  
  dxy = resDim[0] * resDim[1];

  if ( resIm->type != FLOAT ) {
    theSlice = (r32*)VT_Malloc( (unsigned int)(dxy * sizeof(r32)) );
    if ( theSlice == (r32*)NULL ) {
      VT_Error("allocation failed", proc );
      return( -1 );
    }
  }

  for ( z = 0; z < resDim[2]; z ++ ) {
    if ( (_VERBOSE_ != 0) || (_VT_VERBOSE_ != 0) || (_VT_DEBUG_ != 0) )
      fprintf( stderr, "Processing slice %d\r", z );
    if ( resIm->type == FLOAT ) {
      theSlice = (r32*)(resIm->buf);
      theSlice += z * dxy;
    }
    bufDef[0] = (r32*)(theDef[0]->buf);
    bufDef[1] = (r32*)(theDef[1]->buf);
    bufDef[2] = (r32*)(theDef[2]->buf);
    /* computation of slice #z of result image */
    switch ( theIm->type ) {
    case UCHAR :
      ReechTriLinDefBack_u8 ( (void*)(theIm->buf), theDim,
			      theSlice, resDim,
			      bufDef, defDim, mat, theMatBefore, z );
      break;
    case SCHAR :
      ReechTriLinDefBack_s8 ( (void*)(theIm->buf), theDim,
			      theSlice, resDim,
			      bufDef, defDim, mat, theMatBefore, z );
      break;
    case USHORT :
      ReechTriLinDefBack_u16 ( (void*)(theIm->buf), theDim,
			       theSlice, resDim,
			       bufDef, defDim, mat, theMatBefore, z );
      break;
    case SSHORT :
      ReechTriLinDefBack_s16 ( (void*)(theIm->buf), theDim,
			       theSlice, resDim,
			       bufDef, defDim, mat, theMatBefore, z );
      break;
    case FLOAT :
      ReechTriLinDefBack_r32 ( (void*)(theIm->buf), theDim,
			       theSlice, resDim,
			       bufDef, defDim, mat, theMatBefore, z );
      break;
    default :
      if ( resIm->type != FLOAT ) VT_Free( (void**)&theSlice );
      VT_Error( "input image type unknown or not supported", proc );
      return( -1 );
    }
    /* transformation with gain and bias */
    ts = theSlice;

    if ( (bias != 0.0 ) && (gain != 1.0 ) ) {
      for ( i = 0; i < dxy; i++, ts++ ) 
	*ts = (float)( (*ts * g) + b );
    } else if ( (gain != 1.0 ) && (bias == 0.0 ) ) {
      for ( i = 0; i < dxy; i++, ts++ ) 
	*ts *= (float)( g );
    } else if ( (gain == 1.0 ) && (bias != 0.0 ) ) {
      for ( i = 0; i < dxy; i++, ts++ ) 
	*ts += (float)( b );
    }

    /* conversion into type of result image */
    switch ( resIm->type ) {
    case SCHAR : 
      {
	s8 *resBuf = (s8 *)resIm->buf;
	resBuf += (z*dxy);
	Convert_r32_to_s8( theSlice, resBuf, dxy );
      }
      break;
    case UCHAR : 
      {
	u8 *resBuf = (u8 *)resIm->buf;
	resBuf += (z*dxy);
	Convert_r32_to_u8( theSlice, resBuf, dxy );
      }
      break;
    case SSHORT : 
      {
	s16 *resBuf = (s16 *)resIm->buf;
	resBuf += (z*dxy);
	Convert_r32_to_s16( theSlice, resBuf, dxy );
      }
      break;
    case USHORT : 
      {
	u16 *resBuf = (u16 *)resIm->buf;
	resBuf += (z*dxy);
	Convert_r32_to_u16( theSlice, resBuf, dxy );
      }
      break;
    case FLOAT : 
      break;
    default :
      if ( resIm->type != FLOAT ) VT_Free( (void**)&theSlice );
      VT_Error( "output image type unknown or not supported", proc );
      return( -1 );
    }
  }
  if ( resIm->type != FLOAT ) VT_Free( (void**)&theSlice );
  return( 1 );
}

/* Procedure de reechantillonnage "avec deformation" 3D.

   Les images de deformation contiennent, pour chaque point M
   de l'image resultat, les coordonnees d'un vecteur V pointant
   sur le point reel correspondant dans l'image d'entree.
   En fait, cette image d'entree peut avoir ete transformee
   par une matrice Mat^{-1} avant le calcul des deformations,
   donc le "vrai" point reel correspondant a M est donne par : 
                  M' = Mat * (M + v).
   On prend l'intensite du plus proche voisin de M'.
*/

int Reech3DNearestDefBack( vt_image *theIm, /* input image */
			  vt_image *resIm, /* result image */
			  vt_image **theDef, /* deformation images */
			  double *theMatAfter, /* transformation matrix */ 
			  double *theMatBefore /* transformation matrix */ )
{
  char *proc="Reech3DNearestDefBack";
  int theDim[3], resDim[3], defDim[3];
  double mat[16];
  r32 *bufDef[3];
  int z;
  register int dxy;

  if ( theIm->type != resIm->type ) return( -1 );
  if ( ( (theDef[0])->type != FLOAT ) ||
       ( (theDef[1])->type != FLOAT ) ||
       ( (theDef[2])->type != FLOAT ) ) return( -1 );
  if ( (theDef[0])->dim.x != (theDef[1])->dim.x
       || (theDef[0])->dim.x != (theDef[2])->dim.x ) return( -1 );
  if ( (theDef[0])->dim.y != (theDef[1])->dim.y
       || (theDef[0])->dim.y != (theDef[2])->dim.y ) return( -1 );
  if ( (theDef[0])->dim.z != (theDef[1])->dim.z
       || (theDef[0])->dim.z != (theDef[2])->dim.z ) return( -1 );
  if ( theMatBefore == NULL ) {
    if ( resIm->dim.x != (theDef[0])->dim.x ) return( -1 );
    if ( resIm->dim.y != (theDef[0])->dim.y ) return( -1 );
    if ( resIm->dim.z != (theDef[0])->dim.z ) return( -1 );
  }

  if ( theMatAfter != (double*)NULL ) {
    for ( z = 0; z < 16; z ++ ) mat[z] = theMatAfter[z];
  } else {
    for ( z = 0; z < 16; z ++ ) mat[z] = 0.0;
    mat[0] = mat[5] = mat[10] = mat[15] = 1.0;
  }

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;
  
  defDim[0] = (theDef[0])->dim.x;
  defDim[1] = (theDef[0])->dim.y;
  defDim[2] = (theDef[0])->dim.z;
  
  dxy = resDim[0] * resDim[1];

  for ( z = 0; z < resDim[2]; z ++ ) {
    if ( (_VERBOSE_ != 0) || (_VT_VERBOSE_ != 0) || (_VT_DEBUG_ != 0) )
      fprintf( stderr, "Processing slice %d\r", z );
    bufDef[0] = (r32*)(theDef[0]->buf);
    bufDef[1] = (r32*)(theDef[1]->buf);
    bufDef[2] = (r32*)(theDef[2]->buf);
    /* computation of slice #z of result image */
    switch ( theIm->type ) {
    case UCHAR :
      {
	u8 *resSlice = (u8 *)resIm->buf;
	resSlice += (z*dxy);
	ReechNearestDefBack_u8 ( (void*)(theIm->buf), theDim,
				 resSlice, resDim,
				 bufDef, defDim, mat, theMatBefore, z );
      }
      break;
    case SCHAR :
      {
	s8 *resSlice = (s8 *)resIm->buf;
	resSlice += (z*dxy);
	ReechNearestDefBack_s8 ( (void*)(theIm->buf), theDim,
				 resSlice, resDim,
				 bufDef, defDim, mat, theMatBefore, z );
      }
      break;
    case USHORT :
      {
	u16 *resSlice = (u16 *)resIm->buf;
	resSlice += (z*dxy);
	ReechNearestDefBack_u16 ( (void*)(theIm->buf), theDim,
				  resSlice, resDim,
				  bufDef, defDim, mat, theMatBefore, z );
      }
      break;
    case SSHORT :
      {
	s16 *resSlice = (s16 *)resIm->buf;
	resSlice += (z*dxy);
	ReechNearestDefBack_s16 ( (void*)(theIm->buf), theDim,
				  resSlice, resDim,
				  bufDef, defDim, mat, theMatBefore, z );
      }
      break;
    case FLOAT :
      {
	r32 *resSlice = (r32 *)resIm->buf;
	resSlice += (z*dxy);
	ReechNearestDefBack_r32 ( (void*)(theIm->buf), theDim,
				  resSlice, resDim,
				  bufDef, defDim, mat, theMatBefore, z );
      }
      break;
    default :
      VT_Error( "input image type unknown or not supported", proc );
      return( -1 );
    }
  }
  return( 1 );
}




/* Procedure de reechantillonnage 3D avec des splines cubiques

   La matrice 4x4 permet le passage des coordonnees
   de l'image resultat a l'image d'entree. On calcule
   ainsi pour chaque point de l'image resultat son
   correspondant en coordonnees reelles dans l'image 
   d'entree. 
*/

int Reech3DCSpline4x4( vt_image *theIm, /* input image */
		      vt_image *resIm, /* result image */
		      double *mat )
{
  char *proc="Reech3DCSpline4x4";
  int theDim[3], resDim[3];
  int derivative[3] = {0, 0, 0};
  
  if (( theIm->dim.v != 1) || ( resIm->dim.v != 1)) return( -1 );

  theDim[0] = theIm->dim.x;
  theDim[1] = theIm->dim.y;
  theDim[2] = theIm->dim.z;

  resDim[0] = resIm->dim.x;
  resDim[1] = resIm->dim.y;
  resDim[2] = resIm->dim.z;

  if ( ReechCSpline4x4( (void*)(theIm->buf), theIm->type, theDim,
			(void*)(resIm->buf), resIm->type, resDim, 
			mat, derivative ) != 1 ) {
    if ( _VERBOSE_ )
      fprintf( stderr, "%s: error when resampling\n", proc );
    return( -1 );
  }

  return( 1 );
}








void Reech3D_verbose ( )
{
  _VERBOSE_ = 1;
  Reech4x4_verbose();
}

void Reech3D_noverbose ( )
{
  _VERBOSE_ = 0;
  Reech4x4_noverbose();
}
