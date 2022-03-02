
def get_shared_data(file, share_path='data'):
    from os.path import join as pj
    from openalea.deploy.shared_data import get_shared_data_path
    import vplants.flowerdemo
    shared_data_path = get_shared_data_path(vplants.flowerdemo.__path__, share_path=share_path)
    return pj(shared_data_path, file)

def get_shared_image(file):
    from os.path import join as pj
    return get_shared_data(file,pj('data','image'))

def get_shared_model(file):
    from os.path import join as pj
    return get_shared_data(file,pj('data','model'))


__WITH_HELP = True
def display_help(): return __WITH_HELP
def set_help_display(enabled): 
    global __WITH_HELP
    __WITH_HELP = enabled