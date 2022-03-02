from openalea.celltissue import topen,ConfigFormat
from openalea.svgdraw import to_xml
from openalea.tissueshape import planar_mesh

#semantic associated with the tissue
cfg=ConfigFormat(globals())
cfg.add_section("tissue descr")
cfg.add("POINT")
cfg.add("WALL")
cfg.add("CELL")
cfg.add("mesh_id")

#svg descr of topological relations
svg_data = to_xml(planar_mesh() )

#writing
f=topen("tissue.zip",'w')
f.write(t)
f.write_config(cfg.config(),"config")
f.write(pos,"position","position of vertices in the tissue")
f.write_file(svg_data,"visual_descr.svg")
f.close()

