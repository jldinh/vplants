def blue_color_vertex(vertex,nb_pattern):
    if vertex == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = vertex % nb_pattern
        if v < nb_pattern/3. :
            return 0
        else :
            if v < nb_pattern/2. :
                return int(v * 255 /step)%255
            else :
                if v < 5*nb_pattern/6. :
                    return 255
                else :
                    return 255 - int(v * 255 /step)%255

def green_color_vertex(vertex,nb_pattern):
    if vertex == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = vertex % nb_pattern
        if v < nb_pattern/6. :
            return int(v * 255 /step)%255
        else :
            if v < nb_pattern/2. :
                return 255
            else :
                if v < 2*nb_pattern/3. :
                    return 255 - int(v * 255 /step)%255
                else :
                    return 0


def red_color_vertex(vertex,nb_pattern):
    if vertex == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = vertex % nb_pattern
        if v < nb_pattern/6. :
            return 255
        else :
            if v < nb_pattern/3. :
                return 255-int(v * 255 /step)%255
            else :
                if v < 2*nb_pattern/3. :
                    return 0
                else :
                    if v<5*nb_pattern/6. :
                        return int(v * 255 /step)%255
                    else :
                        return 255