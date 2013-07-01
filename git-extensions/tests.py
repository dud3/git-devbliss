import fail

def clean_repository():
    pass

def setup():
    import os
    clean_repository()
    os.system("make install")
    #os.chdir("/home/vagrant/workflow_test")
    return locals()

def teardown(**globs):
    return

fail.add('./test/commands.md')
