Cylinder c1 {

  Radius 5

  Height 10

  Slices 32

}

Translated c2 { 
   Translation <0,0,10>
   Geometry Tapered {
    Primitive c1 
    BaseRadius 10 
    TopRadius 2
  }
}	

Translated c3 { Translation <0,0,15> Geometry c2 }

Sphere s1 { Radius 6
	Slices 32
 }


