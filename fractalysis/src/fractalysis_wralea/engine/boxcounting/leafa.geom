(#

#)


:include "leaf1.app"

Cylinder disc
{
  Height 0.1
  Radius 1
}

Tapered tapered_disc {

  BaseRadius 1.0
  TopRadius 1.0

  Primitive disc

}


Scaled scaled_disc {
  Scale <200,200,200>
  Geometry disc
}

Translated leaf {
  Translation <200.0,0.0,0.0>
  Geometry scaled_disc
}
