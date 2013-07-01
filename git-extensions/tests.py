import fail

def clean_repository():
    import os
    os.chdir("/home/vagrant/workflow_test")
    os.system("git checkout master")
    os.system('for branch in $(git branch | grep -v master); do git branch -D $branch; done')
    os.system('for branch in $(git branch -r | grep -v master | sed s#origin/##); do git push --delete origin $branch; done')
    os.system('cd -')

def setup():
    import os
    from pprint import pprint
    from subprocess import check_output
    os.system("sudo make install > /dev/null")
    clean_repository()
    # never remove the following line or the workflow repo will be messed up
    os.chdir("/home/vagrant/workflow_test")

    # short alias for check_output
    def _(cmd):
        print check_output(cmd, shell=True)

    return locals()

def teardown(**globs):
    return

fail.add('./test/commands.md')
