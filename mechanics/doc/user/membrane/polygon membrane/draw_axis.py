lay = SVGLayer("frame",size,size,"layer0")
sc.append(lay)

elm = SVGPath("Ox")
elm.move_to(10,size - 10)
elm.line_to(10 + sca,size - 10)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
lay.append(elm)

elm = SVGPath("Oxhead")
elm.move_to(sca,size - 15)
elm.line_to(10 + sca,size - 10)
elm.line_to(sca,size - 5)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
lay.append(elm)

elm = SVGText(20 + sca - fw,size - 10 + fh,"x",fontsize,"xaxis")
elm.set_fill( (255,0,0) )
lay.append(elm)

elm = SVGPath("Oy")
elm.move_to(10,size - 10)
elm.line_to(10,size - 10 - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
lay.append(elm)

elm = SVGPath("Oyhead")
elm.move_to(5,size - sca)
elm.line_to(10,size - 10 - sca)
elm.line_to(15,size - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
lay.append(elm)

elm = SVGText(10 - fw,size - 30 - sca + fh,"y",fontsize,"yaxis")
elm.set_fill( (0,255,0) )
lay.append(elm)

