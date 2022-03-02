import sys
from openalea.celltissue import TissueDB

db = TissueDB()
db.read(sys.argv[1])

print db.info()

