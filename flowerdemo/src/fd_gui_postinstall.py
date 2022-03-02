# Postinstall scripts


def install():
    
    from openalea.deploy.shortcut import create_win_shortcut, set_win_reg, create_fd_shortcut
    import sys
    from os.path import join as pj

    winexe = sys.executable
    winexe = winexe.replace('python.exe', 'pythonw.exe')
    create_win_shortcut(name = 'Flower Demo',
                        target = winexe,
                        arguments = '"'+pj(sys.prefix, 'Scripts', 'flowerdemo-script.pyw')+'"',
                        startin = "", 
                        icon = "",
                        description = "Flower Demo",
                        menugroup = "OpenAlea")
        
    create_win_shortcut(name = 'Simplified Flower Demo',
                        target = winexe,
                        arguments = '"'+pj(sys.prefix, 'Scripts', 'flowerdemo3-script.pyw')+'"',
                        startin = "", 
                        icon = "",
                        description = "Simplified Flower Demo",
                        menugroup = "OpenAlea")
      


def uninstall():
    pass

if __name__ == '__main__':
    install()