import fail

def clean_repository():
    pass

def setup():
    import os
    from subprocess import check_output
    clean_repository()
    os.system("sudo make install > /dev/null")
    # never remove the following line or the workflow repo will be messed up
    os.chdir("/home/vagrant/workflow_test")
    return locals()

def teardown(**globs):
    return

fail.add('./test/commands.md')
