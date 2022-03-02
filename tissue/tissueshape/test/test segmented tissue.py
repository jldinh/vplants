from openalea.image import read_inrimage
from openalea.tissueshape import extract_graph_tissue

im = read_inrimage("segmentation.inr.gz")

db = extract_graph_tissue(im,True)

print db.info()

db.write("tissue.zip")

