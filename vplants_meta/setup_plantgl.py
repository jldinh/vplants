from setuptools import setup, find_packages

setup(
    name = 'PlantGL',
    version = '2.8.3' ,
    description = 'Install VPlants.PlantGL', 
    long_description = '',
    author = 'VirtualPlants team',
    author_email = 'christophe dot pradal at cirad dot fr',
    url = 'http://www-sop.inria.fr/virtualplants/',
    license = 'Cecill',

    # Dependencies
    install_requires = ['VPlants.PlantGL==2.8.3'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    )
