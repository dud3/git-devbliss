import fail

def clean_repository():
    pass

def setup():
    import os
    clean_repository()
    os.system("sudo make install > /dev/null")
    #os.chdir("/home/vagrant/workflow_test")
    return locals()

def teardown(**globs):
    return

fail.add('./test/commands.md')
