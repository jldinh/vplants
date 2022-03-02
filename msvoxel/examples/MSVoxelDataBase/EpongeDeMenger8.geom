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
    Transfo t1 {
      Translation <1,1,1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t2 { Translation <-1,1,1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t3 { Translation <1,-1,1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t4 { Translation <-1,-1,1>
      Scale <0.333333333,0.333333333,0.333333333> },

    Transfo t5 {
      Translation <1,1,-1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t6 { Translation <-1,1,-1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t7 { Translation <1,-1,-1>
      Scale <0.333333333,0.333333333,0.333333333> },
    Transfo t8 { Translation <-1,-1,-1>
      Scale <0.333333333,0.333333333,0.333333333> }
    ]
  }

Shape{ifs1,RED7}
