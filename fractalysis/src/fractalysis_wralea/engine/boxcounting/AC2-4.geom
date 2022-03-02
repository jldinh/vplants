(#
Fractal tree AC2: Similar to AC1 with one more layer of branches

Unit = cm

- a leaf = a flat cylinder with circular section 
- Initial leaf : radius = 200 cm

First step of the IFS:

- 7 axillary leaves (6 opposite leaves + 1 at the top)
- scale factor = 1/3
- All leaves are identical

Phyllotaxy = 90 (1/4)

Fractal dimension = Ln7/Ln3 = 1.77 

At depth 5 the radius of a leaf is:

r5 = 200/3^5= 200/243 = 0.82 cm
which makes a surface of s4 = 2.13 cm2

#)

:include "leaf1.app"


TriangleSet leaftriangle
{
	PointList [<0,0,0>, <3,0,0>, <1.5,2,0>]
	IndexList [ [0,1,2] ]

	Solid True
}

Scaled leaf {
  Scale <200,200,200>
  Geometry leaftriangle
}


IFS fractal_tree
{
  Depth 4
  Geometry leaf
  TransfoList
    [
    Transfo {
      Translation <0,0,250>
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
        Azimuth 90
        }
      },
    Transfo {
      Translation <0,0,0>
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
        Azimuth 360
        }
      },
    Transfo {
      Translation <0,0,200>
      Scale <1/3,1/3,1/3>
      EulerRotation
        {
        Elevation 45
        Azimuth 270
        }
      },
    Transfo {
      Translation <0,0,200>
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
