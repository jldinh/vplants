#!/usr/bin/env python
"""povexprort.py

This module exports a VPython scene as POV-Ray scene description code.
Lights and camera location from the current visual scene are included.
Optionally, you may specify a list of include files, and pov textures for
objects.
For an example of its use, see 'povexample.py'
convex objects are not exported.

ruth chabay, carnegie mellon university (rchabay@andrew.cmu.edu)
v1.0 2000-12-17

Markus Gritsch (gritsch@iue.tuwien.ac.at)
v.1.1   2001-03-09
* replaced 'scene' by 'display' everywhere
* added spheres at the joints of a curve
* consistent pov_texture usage in process_arrow() also for the shaft
* ambient light, light sources, up, and fov are now handled correctly
* some cosmetic changes to the code
v.1.1.1 2001-03-22
* added 'shadowless' keyword to export()

Ruth Chabay
2001-06-23
hack to fix error in export_curve introduced by Python 2.1
now can't assign obj.color = array(...)

Markus Gritsch (gritsch@iue.tuwien.ac.at)
v.1.2   2001-11-23
* added 'xy_ratio' and 'custom_text' keywords to export()
* the pov-strings are now directly written to a file

Bruce Sherwood
2004-07-18
add dictionary ("legal") for identifying an object so that
povexport will continue to work with the new Boost-based VPython
which changes the details returned by object.__class__

Bruce Sherwood
2005-06-27
in export_curve, move del's into if, otherwise empty curve gives error
use scene.range to scale values to about 10, because
POV-Ray dies with very large (or very small?) numbers (e.g. 1e10)

Bruce Sherwood
2005-07-22
corrected the new scaling (see 2005-06-27) for frame handling

Bruce Sherwood
2005-07-26
corrected the new scaling (see 2005-06-27) of shaft in arrow

Bruce Sherwood
2005-12-06
corrected error in reporting the name of an unsupported object

NOTE: when changing this module please change the following string:

:version: 2006-05-15 15:21:06CEST
:author: ??, szymon stoma
"""
POVEXPORT_VERSION = "povexport 2006-08-11 12:31:23CEST"


from visual import *
from string import rfind
from tissueSystemVisualisationVisual import *

legal = {frame:'frame', sphere:'sphere', box:'box', cylinder:'cylinder',
                   curve:'curve', ring:'ring', arrow:'arrow',
                   cone:'cone',VMassVisual:'sphere',VSpringVisual:'cylinder',faces:'triangle',VSphereCellVisual:'sphere',VIdentitySphereCellVisual:'sphere',VPumpVisual:'arrow'}
ihat=vector(1, 0, 0)
jhat=vector(0, 1, 0)
khat=vector(0, 0, 1)
displayscale = 1.0 # global scale factor to adjust scene.range to 100

def version():
    return POVEXPORT_VERSION

def getpolar(a):
    # a is a vector
    # find rotation angles (standard polar coord)
    xy = sqrt(a.x**2 + a.y**2)
    theta = atan2(xy, a.z)
    phi = atan2(a.y, a.x)
    return [theta, phi]

def process_frame(a, code):
    # add in frame rotations & translations (may be nested)
    frame_code = ''
    fr = a.frame
    while fr:
        # orientation of frame.axis
        ang = getpolar(fr.axis)
        theta=ang[0]
        phi=ang[1]
        aup = fr.up*1.0
        # find rotation around x-axis (if fr.up <> jhat)
        # "undo" theta & phi rotations so can find alpha
        aup = rotate(aup, axis=khat, angle=-phi)
        aup = rotate(aup, axis=jhat, angle=pi/2.0-theta)
        a_sin = dot(cross(jhat, norm(aup)), ihat)
        a_cos = dot(norm(aup), jhat)
        alpha = atan2(a_sin, a_cos)
        frx=alpha*180./pi
        fry=-90+theta*180./pi
        frz=phi*180./pi
        rrot = '    rotate <%f, %f, %f>\n'
        ttrn = '    translate <%f, %f, %f>\n'
        frame_code += rrot % (frx, fry, frz)
        frame_code += ttrn % (displayscale*fr.x, displayscale*fr.y, displayscale*fr.z)
        fr = fr.frame

    # insert frame_code at end (these rot's must be done last)
    end = rfind(code, '}')
    code = code[:end] + frame_code + code[end:]
    return code

def add_texture(a, code):
    # add in user-specified texture (will override color)
    if hasattr(a, 'pov_texture'):
        tstring = '    texture { '+ a.pov_texture + ' }\n'
        end = rfind(code, '}')
        code = code[:end] + tstring + code[end:]
    return code

def export_sphere(a):
    sphere_template = """
sphere {
    <%(posx)f, %(posy)f, %(posz)f>, %(radius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    object_code = sphere_template % { 'posx':displayscale*a.x, 'posy':displayscale*a.y, 'posz':displayscale*a.z,
                                      'radius':displayscale*a.radius,
                                      'red':a.red, 'green':a.green, 'blue':a.blue }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code

def export_box(a):
    # create box at origin along x-axis
    # then rotate around x,y,z axes
    # then translate to final location
    box_template = """
box {
    <%(posx)f, %(posy)f, %(posz)f>, <%(pos2x)f, %(pos2y)f, %(pos2z)f>
    pigment {color rgb <%(red)f, %(green)f, %(blue)f>}
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    # find rotations
    ang = getpolar(a.axis)
    theta = ang[0]
    phi = ang[1]
    # find rotation around x-axis (if a.up <> jhat)
    # "undo" theta & phi rotations so can find alpha
    aup = a.up*1.0
    aup = rotate(aup, axis=khat, angle=-phi)
    aup = rotate(aup, axis=jhat, angle=pi/2.0-theta)
    a_sin = dot(cross(jhat, norm(aup)), ihat)
    a_cos = dot(norm(aup), jhat)
    alpha = atan2(a_sin, a_cos)
    # pos of visual box is at center
    # generate two opposite corners for povray
    pos1=-displayscale*a.size / 2.0
    pos2=+displayscale*a.size / 2.0

    object_code = box_template % { 'posx':pos1.x, 'posy':pos1.y, 'posz':pos1.z,
                                   'pos2x':pos2.x, 'pos2y':pos2.y, 'pos2z':pos2.z,
                                   'rotx':alpha*180./pi, 'roty':-90.+theta*180./pi, 'rotz':phi*180./pi,
                                   'transx':displayscale*a.x, 'transy':displayscale*a.y, 'transz':displayscale*a.z,
                                   'red':a.red, 'green':a.green, 'blue':a.blue }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export_triangle(a):
    triangle_template="""
triangle {
    <%(posx)f, %(posy)f, %(posz)f>, <%(pos2x)f, %(pos2y)f, %(pos2z)f>, <%(pos3x)f, %(pos3y)f, %(pos3z)f>
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    p1=displayscale*a.pos[0]
    p2=displayscale*a.pos[1]
    p3=displayscale*a.pos[2]
    object_code = triangle_template % { 'posx':p1[0], 'posy':p1[1], 'posz':p1[2],
                                        'pos2x':p2[0], 'pos2y':p2[1], 'pos2z':p2[2],
                                        'pos3x':p3[0], 'pos3y':p3[1], 'pos3z':p3[2],
                                        'red':a.color[ 0 ][0], 'green':a.color[ 0 ][1], 'blue':a.color[ 0 ][2],
                                         }
    object_code = process_frame(a, object_code)
    return object_code

def export_cylinder(a):
    cylinder_template = """
cylinder {
    <%(posx)f, %(posy)f, %(posz)f>,<%(pos2x)f, %(pos2y)f, %(pos2z)f>, %(radius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    endpt1=displayscale*a.pos
    endpt2=displayscale*(a.pos+a.axis)
    object_code = cylinder_template % { 'posx':endpt1.x, 'posy':endpt1.y, 'posz':endpt1.z,
                                        'pos2x':endpt2.x, 'pos2y':endpt2.y, 'pos2z':endpt2.z,
                                        'red':a.red, 'green':a.green, 'blue':a.blue,
                                        'radius':displayscale*a.radius }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code

def export_curve(a):
    object_code = ''
    if len(a.pos) > 1:
        ii = 0
        while ii < len(a.pos)-1:
            endpt1 = a.pos[ii]
            endpt2 = a.pos[ii+1]
            if a.radius > 0:
                rr = a.radius
            else:
                rr = mag(endpt1-endpt2)/200.
            # create a dummy cylinder to export
            ccyl = cylinder(pos=endpt1, axis=(endpt2-endpt1),
                            radius=rr, color=tuple(a.color[ii]),
                            frame=a.frame, visible=0)
            csph = sphere(pos=endpt1, radius=rr, color=tuple(a.color[ii]),
                          frame=a.frame, visible=0)
            if hasattr(a, 'pov_texture'):
                ccyl.pov_texture = a.pov_texture
                csph.pov_texture = a.pov_texture
            object_code += export_cylinder(ccyl) + export_sphere(csph)
            ii = ii+1
        endpt1 = a.pos[ii]
        csph = sphere(pos=endpt1, radius=rr, color=tuple(a.color[ii]),
                      frame=a.frame, visible=0)
        if hasattr(a, 'pov_texture'):
            csph.pov_texture = a.pov_texture
        object_code += export_sphere(csph)
        del(ccyl)
        del(csph)
    return object_code

def export_ring(a):
    torus_template = """
torus {
    %(radius)f, %(minorradius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
    rotate <0.0, 0.0, -90.0> // align with x-axis
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    ang = getpolar(a.axis)
    theta = ang[0]
    phi = ang[1]
    object_code = torus_template % { 'radius':displayscale*a.radius, 'minorradius':displayscale*a.thickness,
                                     'transx':displayscale*a.x, 'transy':displayscale*a.y, 'transz':displayscale*a.z,
                                     'rotx':0.0, 'roty':-90.+theta*180./pi, 'rotz':phi*180./pi,
                                     'red':a.red, 'green':a.green, 'blue':a.blue }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code

def export_arrow(a):
    pyramid_template = """
object {Pyramid
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
    scale <%(scalex)f, %(scaley)f, %(scalez)f>
    rotate <0, 0, -90> // align with x-axis
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    al = displayscale*a.length
    hl = displayscale*a.headlength
    sl = al-hl # length of shaft
    hw = displayscale*a.headwidth
    sw = displayscale*a.shaftwidth
    # head is a pyramid
    ppos = displayscale*(a.pos+a.axis*(sl/al))
    ang = getpolar(a.axis)
    theta=ang[0]
    phi=ang[1]
    m1 = pyramid_template % { 'scalex':hw, 'scaley':hl, 'scalez':hw,
                              'rotx':0., 'roty':-90.+theta*180./pi, 'rotz':phi*180./pi,
                              'red':a.red, 'green':a.green, 'blue':a.blue,
                              'transx':ppos.x, 'transy':ppos.y, 'transz':ppos.z }
    m1 = process_frame(a, m1)
    m1 = add_texture(a, m1)

    # shaft is a box; need to create a dummy box
    abox = box(pos=(a.pos+a.axis*(sl/al)/2.0), axis=(a.axis*(sl/al)),
               up = a.up, width=a.shaftwidth, height=a.shaftwidth,
               color=a.color, frame=a.frame, visible = 0)
    m2 = export_box(abox)
    m2 = add_texture(a, m2)
    del(abox)
    # concatenate pyramid & box
    object_code = m1 + m2
    return object_code

def export_cone(a):
    cone_template = """
cone {
    <%(posx)f, %(posy)f, %(posz)f>, %(radius)f
    <%(pos2x)f, %(pos2y)f, %(pos2z)f>, %(minorradius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    pos2 = displayscale*(a.pos+a.axis)
    object_code = cone_template % { 'radius':displayscale*a.radius, 'minorradius':0.0,
                                    'posx':displayscale*a.x, 'posy':displayscale*a.y, 'posz':displayscale*a.z,
                                    'pos2x':pos2.x, 'pos2y':pos2.y, 'pos2z':pos2.z,
                                    'red':a.red, 'green':a.green, 'blue':a.blue }
    object_code = process_frame(a,object_code)
    object_code = add_texture(a,object_code)
    return object_code

def export(display=None, filename=None, include_list=None, xy_ratio=4./3., custom_text='', shadowless=0, prefix_folder=""):
    global displayscale
    if display == None:         # no display specified so find active display
        dummy = sphere(visible=0)
        display = dummy.display
        del(dummy)

    scenefilename = prefix_folder + display.title + '.pov'
    camerafilename = prefix_folder + display.title + '.pov.camera'
    filename = prefix_folder + display.title + '.pov.scene'
    
    if include_list == None:
        include_text = ''
    else:
        include_text = '\n'
        for x in include_list:
            include_text = include_text + '#include "'+ x + '"\n'

    initial_comment = """// povray code generated by povexport.py
"""

    pyramid_def = """
// Four-sided pyramid from shapes2.inc, slightly modified.
#declare Pyramid = union {
    triangle { <-1, 0, -1>, <+1, 0, -1>, <0, 1, 0> }
    triangle { <+1, 0, -1>, <+1, 0, +1>, <0, 1, 0> }
    triangle { <-1, 0, +1>, <+1, 0, +1>, <0, 1, 0> }
    triangle { <-1, 0, +1>, <-1, 0, -1>, <0, 1, 0> }
    triangle { <-1, 0, -1>, <-1, 0, +1>, <1, 0, 1> }
    triangle { <-1, 0, -1>, <+1, 0, -1>, <1, 0, 1> }
    scale <.5, 1, .5>        // so height = width = 1
}
"""

    ambient_template = """
global_settings { ambient_light rgb <%(amb)f, %(amb)f, %(amb)f> }
"""

    background_template = """
background { color rgb <%(red)f, %(green)f, %(blue)f> }
"""

    light_template = """
light_source { <%(posx)f, %(posy)f, %(posz)f>
    color rgb <%(int)f, %(int)f, %(int)f>
}
"""

    camera_template = """
camera {
    right <-%(xyratio)f, 0, 0>      //visual uses right-handed coord. system
    location <%(posx)f, %(posy)f, %(posz)f>
    sky <%(upx)f, %(upy)f, %(upz)f>
    look_at <%(pos2x)f, %(pos2y)f, %(pos2z)f>
    angle %(fov)f
    rotate <0, 0, 0>
}
"""

    scene_template = """
    #include "%(camera_file)s"
    #include "%(scene_file)s"
"""
    # begin povray setup
    file = open(filename, 'wt')
    camerafile = open(camerafilename, 'wt')
    scenefile = open(scenefilename, 'wt' )
    scenefile.write( scene_template % {'camera_file': camerafilename, 'scene_file': filename})

    file.write( initial_comment + include_text + custom_text + pyramid_def )
    file.write( ambient_template % { 'amb':display.ambient } )# deleted * 10
    file.write( background_template % { 'red':display.background[0],
                                        'green':display.background[1],
                                        'blue':display.background[2] } )

    displayscale = 10.0/max(display.range) # bring all values into POV-Ray legal range

    for i in arange(len(display.lights)): # reproduce visual lighting (not ideal, but good approximation)
        light = display.lights[i] # vector in direction of light
        intensity = mag(light) # intensity of light (all lights are white)
        pos = norm(light) * 1000.0 # far away to simulate parallel light
        light_code = light_template % { 'posx':pos.x, 'posy':pos.y, 'posz':pos.z,
                                        'int':intensity*5/3. }
        if shadowless:
            # insert frame_code at end (these rot's must be done last)
            end = rfind(light_code, '}')
            light_code = light_code[:end] + '    shadowless\n' + light_code[end:]

        file.write( light_code )

    cpos = displayscale*display.mouse.camera
    ctr = displayscale*display.center
    cup = display.up
    camerafile.write( camera_template % { 'xyratio':xy_ratio,
                                    'posx':cpos.x, 'posy':cpos.y, 'posz':cpos.z,
                                    'upx':cup.x, 'upy':cup.y, 'upz':cup.z,
                                    'pos2x':ctr.x, 'pos2y':ctr.y, 'pos2z':ctr.z,
                                    'fov':display.fov*180/pi } )

    for obj in display.objects:
        key = obj.__class__
        if legal.has_key(key):
            obj_name = legal[key]
            if obj_name != 'frame':
                function_name = 'export_' + obj_name
                function = globals().get(function_name)
                object_code = function(obj)
                file.write( object_code )
        else:
            print 'WARNING: export function for ' + str(obj.__class__) + ' not implemented'

    file.close()
    camerafile.close()
    scenefile.close()
    
    return 'The export() function no longer returns the scene as an\n' \
           'endless POV-Ray string, but saves it to a file instead.'


if __name__ == '__main__':
    print __doc__
