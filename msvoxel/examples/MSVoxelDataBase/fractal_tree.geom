(#
  A fractal tree with 

- 7 axillary ellipsis 
- 1 apical ellipsis

All ellipsis are identical

Length of an ellipsis = 1
Distance from soil to basis of apical ellipsis = 3

Phyllotaxy = 60 (1/6)

Up to Depth 4

#)

:include "leaf1.app"

Sphere sphere
{
  Radius 1
  Slices 4
  Stacks 4
}

Scaled ellipsis {
  Scale <0.5,0.5,1.0>
  Geometry sphere  
}

Translated translated_ellipsis{
  Translation <0.0,0.0,1>
  Geometry ellipsis
}


(#
Tapered tapered_ellipsis
{
  BaseRadius 1.0
  TopRadius 1.0
  Primitive Scaled { 
    Scale <1.0,1.0,2.0>
    Geometry Sphere
    {
      Radius 1
      Slices 4
      Stacks 4
    }
  }
}
#)


IFS fractal_tree
{
  Depth 3
  Geometry translated_ellipsis
  TransfoList
    [
    Transfo {
      Translation <0,0,3.5>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        }
      },
    Transfo {
      Translation <0,0,0.5>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        }
      },    
    Transfo {
      Translation <0,0,1>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 60
        }
      },
    Transfo {
      Translation <0,0,1.5>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 120
        }
      },
    Transfo {
      Translation <0,0,2>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 180
        }
      },
    Transfo {
      Translation <0,0,2.5>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 240
        }
      },
    Transfo {
      Translation <0,0,3>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 300
        }
      },
    Transfo {
      Translation <0,0,3.5>
      Scale <1/2,1/2,1/2>
      EulerRotation
        {
        Elevation 45
        Azimuth 360
        }
      }

    ]
}

Shape {
  Geometry fractal_tree
  Appearance green2
}
