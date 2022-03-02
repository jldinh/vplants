# Test file

from openalea.self_similarity.Main import create_mtg, compression

# Simulated MTG: fractal trees
m=8
model=["0","1","1.1","1.1.1","2","2.1","2.2","2.2.1","2.2.2","3","3.1"]
name="FractalTree/Tree"+model[m]+"/fractal2.mtg"

# Compression
g=create_mtg(name)
distance=compression(g)
print("Distance between tree and NEST")
print(distance)

print("Find Tulip files in 'share/data/DataOut/tulip'")
print("Find MTG files in 'share/data/DataOut/tmp_trees'")
