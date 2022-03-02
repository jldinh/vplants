import platform

system = platform.system()
if system == "Linux":
    # Note: when openSUSE build service is used, you must replace manually 'OBS_DISTNAME' 
    # and 'OBS_DISTVERSION' by the right value. 
    name, version, id = platform.dist(distname='OBS_DISTNAME', version='OBS_DISTVERSION')
    
    QTDIR="/usr"
    QT_VERSION=4
    if name == 'fedora' and \
        (version =='17' or version =='19'):
        ann_libs='ANN'
    boost_libs_suffix='-mt'