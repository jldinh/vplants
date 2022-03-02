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
  Depth 3
  Geometry box
  TransfoList
    [
    Transfo t0 {
      Scale <0.5,0.5,0.5>
		},
    Transfo t1 {
      Translation <0.75,0.75,0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t2 { Translation <-0.75,0.75,0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t3 { Translation <0.75,-0.75,0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t4 { Translation <-0.75,-0.75,0.75>
      Scale <0.25,0.25,0.25> },

    Transfo t5 {
      Translation <0.75,0.75,-0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t6 { Translation <-0.75,0.75,-0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t7 { Translation <0.75,-0.75,-0.75>
      Scale <0.25,0.25,0.25> },
    Transfo t8 { Translation <-0.75,-0.75,-0.75>
      Scale <0.25,0.25,0.25> }
    ]
  }

Shape{ifs1,RED7}
