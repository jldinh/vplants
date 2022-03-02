(#
Fractal tree AC1:

Unit = cm

- a leaf = a flat cylinder with circular section 
- Initial leaf : radius = 200 cm

First step of the IFS:

- 9 axillary leaves (8 opposite leaves + 1 at the top)
- scale factor = 1/3
- All leaves are identical

Phyllotaxy = 90 (1/4)

Fractal dimension = Ln9/Ln3 = 2 

At depth 4 the radius of a leaf is:

r4 = 200/3^4= 200/81 = 2.47 cm
which makes a surface of s4 = 19.15 cm2

#)


:include "leafa.geom"

IFS fractal_tree
{
  Depth 4
  Geometry leaf
  TransfoList
    [
    Transfo {
      Translation <0,0,200>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        }
      },
    Transfo {
      Translation <0,0,0>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 0
        }
      },
    Transfo {
      Translation <0,0,0>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 180
        }
      },
    Transfo {
      Translation <0,0,50>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 90
        }
      },
    Transfo {
      Translation <0,0,50>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 270
        }
      },
    Transfo {
      Translation <0,0,100>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 180
        }
      },
    Transfo {
      Translation <0,0,100>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 0
        }
      },
    Transfo {
      Translation <0,0,150>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 270
        }
      },
    Transfo {
      Translation <0,0,150>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 90
        }
      }

    ]
}

Shape {
  Geometry fractal_tree
  Appearance green2
}
