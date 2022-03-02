(# -Geom File-
 ###############################################
 #
 # IFS
 #
 # Author : O. Puech
 #
 ###############################################
 #)

Box box
  {
  Size <1,1,1>
  }


IFS ifs1
  {
  Depth 5
  Geometry box
  TransfoList
    [
    Transfo t1 {
      Translation <1,1,1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t2 { Translation <-1,1,1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t3 { Translation <1,-1,1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t4 { Translation <-1,-1,1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},

    Transfo t5 {
      Translation <1,1,-1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t6 { Translation <-1,1,-1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t7 { Translation <1,-1,-1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		},
    Transfo t8 { Translation <-1,-1,-1>
      Scale <0.333333333,0.333333333,0.333333333> 
	EulerRotation
        {
        Azimuth 30
        Elevation 30
        }
		}
    ]
  }

Shape{ifs1,RED7}
