/*************************************************************************
 * vt_3m.c -
 *
 * $Id: vt_3m.c,v 1.3 2000/08/25 17:58:08 greg Exp $
 *
 * Copyright INRIA
 *
 * AUTHOR:
 * Gregoire Malandain (greg@sophia.inria.fr)
 * 
 * CREATION DATE: 
 * ?
 *
 * ADDITIONS, CHANGES
 *
 * - Fri Aug 25 18:15:02 MET DST 2000 (Gregoire Malandain)
 *   Ajout du calcul de l'ecart-type
 *
 * * Thu May  4 2000 (Gregoire Malandain)
 *   add DOUBLE type in VT_3m()
 *
 */


#include <vt_3m.h>

int VT_3m( vt_image *im /* image whose min, mean and max have to be computed */,
	   vt_3m *m  /* structure containing these 3 numbers */ )
{
  register int z, s;
  int size;
  register double ec, mi, me, ma, v;
  
  if ( (im == (vt_image *)NULL) || (im->buf == (void*)NULL) ) {
    VT_Error( "NULL image or NULL buffer image", "VT_3m" );
    return( 0 );
  }
  z = im->dim.z;
  size = im->dim.x * im->dim.y;
  if ( (z <= 0) || (size <= 0) ) {
    VT_Error( "Bad dimensions of image", "VT_3m" );
    return( 0 );
  }
  
  m->min = m->moy = m->max = m->ect = (double)0.0;
  
  /* on calcule une moyenne par plan, que l'on somme */
  /* dans m->moy, pour eviter de manipuler de trop   */
  /* grands nombres                                  */
  
  switch ( im->type ) {
  case SCHAR :
        {
	s8 *b;
	b = (s8 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case UCHAR :
        {
	u8 *b;
	b = (u8 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case SSHORT :
        {
	s16 *b;
	b = (s16 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case USHORT :
        {
	u16 *b;
	b = (u16 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case INT :
        {
	i32 *b;
	b = (i32 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case UINT :
        {
	u32 *b;
	b = (u32 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case FLOAT :
        {
	r32 *b;
	b = (r32 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    case DOUBLE :
        {
	r64 *b;
	b = (r64 *)(im->buf);
	mi = ma = (double)(*b);
	while ( z-- > 0 ) {
	    me = ec = (double)0.0;
	    s = size;
	    while( s-- > 0 ) {
		v = (double)(*b++);
		me += v;   ec += v*v;
		if ( v > ma ) ma = v;
		else if ( v < mi ) mi = v;
	    }
	    m->moy += me / (double)(size);
	    m->ect += ec / (double)(size);
	}}
	break;
    default :
	VT_Error( "image type unknown or not supported", "VT_3m" );
	return( 0 );
    }
    
    if ( im->dim.z > 1 ) {
      m->moy /= (double)(im->dim.z);
      m->ect /= (double)(im->dim.z);
    }
    m->ect -= m->moy * m->moy;
    m->ect = sqrt( m->ect );
    m->min = mi;
    m->max = ma;
    return( 1 );
}
