from openalea.tissueshape import hexagonal_grid

db = hexagonal_grid( (4,8), "hexa")
print db.info()
db.write("tissue.zip")

