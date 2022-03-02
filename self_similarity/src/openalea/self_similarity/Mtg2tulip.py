def write_tlp_from_mtg(name, g, t0=1, properties=[]):
    
    nodes=g.vertices(t0)
    
    f=open(name, "w")
    f.write("(tlp \"2.0\"\n")
    f.write("(nodes ")
    for n in nodes:
        f.write(str(n)+ " ")
    f.write(")\n")
    count_edges=0
    for n in nodes:
        for e in g.children(n):
            count_edges+=1
            f.write("(edge " + str(count_edges) + " " + str(n) + " " + str(e) + ")\n")
    for prop in properties:
        f.write("(property 0 int \""+prop[0]+"\"\n")
        f.write("\t(default \""+str(prop[2])+"\" \"0\")\n")
        for node in nodes:
            f.write("\t(node " + str(node) + str(" \"") + str(prop[1].get(node, prop[2])) + "\")\n")
        f.write(")\n") 
    f.write(")")
    f.close()


# =========================================
# Example
# pp={}
# for n in nodes:
#     if n in g1:
#         pp[n]=1
#     elif n in g2:
#         pp[n]=2
# def_val=0
# prop=['name prop', pp, def_val]
# write_tlp_from_mtg('test.tlp', g, [prop])
# =========================================