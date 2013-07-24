import fail

def clean_repository():
    import os
    neutral_master = 'd3e583b0cf0f3d083339f5473e9361ef5ea029f1'
    os.chdir("/home/vagrant/workflow_test")
    os.system('git stash')
    os.system('git stash drop')
    os.system("git checkout master")
    os.system("git reset --hard {}".format(neutral_master))
    os.system("git push --force origin master")
    os.system('for tag in $(git tag); do git push origin :refs/tags/$tag; done')
    os.system('for tag in $(git tag); do git tag -d $tag; done')
    os.system('for branch in $(git branch | grep -v master); do git branch -D $branch; done')
    os.system('for branch in $(git branch -r | grep -v master | sed s#origin/##); do git push --delete origin $branch; done')
    os.system('cd -')

def setup():
    import os
    import re
    from pprint import pprint
    from time import sleep
    os.system("sudo make install")
    clean_repository()
    # never remove the following line or the workflow repo will be messed up
    os.chdir("/home/vagrant/workflow_test")

    # short alias for check_output
    def sh(cmd):
        from subprocess import call
        open('/dev/shm/fail_output', 'w').close()
        with open('/dev/shm/fail_output', 'a+') as output:
            call(cmd, stderr=output, stdout=output, shell=True)
        with open('/dev/shm/fail_output', 'r') as output:
            print output.read()

    return locals()

def teardown(**globs):
    return

fail.add('./test/commands.md')
