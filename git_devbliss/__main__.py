# Copyright 2014 devbliss GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import pkg_resources
import subprocess
import os
import os.path
from docopt import docopt
import re

__version__ = pkg_resources.get_distribution("git_devbliss").version

github_devbliss = pkg_resources.load_entry_point(
    "git_devbliss", "console_scripts", "github-devbliss")


def main():
    '''
Usage:
    git-devbliss ( feature | bug | refactor | research ) DESCRIPTION
    git-devbliss hotfix VERSION DESCRIPTION
    git-devbliss finish [BASE_BRANCH]
    git-devbliss release VERSION
    git-devbliss status
    git-devbliss delete [-f]
    git-devbliss issue [TITLE]
    git-devbliss review PULL_REQUEST_ID
    git-devbliss merge-button PULL_REQUEST_ID
    git-devbliss close-button PULL_REQUEST_ID
    git-devbliss cleanup

Options:
    feature, bug, refactor, research
                  Branch from master (normal branches)
    hotfix        Branch from a tag (fix a bug in an already released version)
    finish        Open a pull request for the current branch
    release       Create a new tag, commit and push
    status        List branches, pull requests, and issues
    issue         Quickly post an issue to GitHub
    delete        Delete the current branch on github.com
    review        Review a pull request with the given id
    merge-button  Merge a pull request with the given id
    close-button  Close a pull request with the given id without merging
    cleanup       Cleans up the repository
    -v --version  Print version number of git-devbliss
'''
    try:
        # check whether the pwd is a git repository
        git('rev-parse --abbrev-ref HEAD', pipe=True)

        # check whether origin points to github.com
        git('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True)
    except subprocess.CalledProcessError:
        print('Fatal: origin does not point to a github.com repository',
              file=sys.stderr)
        sys.exit(1)

    args = docopt(main.__doc__, version=__version__)
    if(args['feature']):
        branch('feature', args['DESCRIPTION'])
    elif(args['bug']):
        branch('bug', args['DESCRIPTION'])
    elif(args['refactor']):
        branch('refactor', args['DESCRIPTION'])
    elif(args['research']):
        branch('research', args['DESCRIPTION'])
    elif(args['hotfix']):
        hotfix(args['VERSION'], args['DESCRIPTION'])
    elif(args['finish']):
        finish(args['BASE_BRANCH'])
    elif(args['release']):
        release(args['VERSION'])
    elif(args['status']):
        github_devbliss(['status'])
    elif(args['delete']):
        delete(args['-f'])
    elif(args['issue']):
        github_devbliss(['issue', args['TITLE']])
    elif(args['review']):
        github_devbliss(['review', args['PULL_REQUEST_ID']])
    elif(args['merge-button']):
        github_devbliss(['merge-button', args['PULL_REQUEST_ID']])
    elif(args['close-button']):
        github_devbliss(['close-button', args['PULL_REQUEST_ID']])
    elif(args['cleanup']):
        cleanup()


def hotfix(tag, description):
    if [_tag for _tag in git('tag', pipe=True).split('\n') if tag == _tag]:
        git('fetch origin')
        git('checkout --quiet {}'.format(tag))
        git('checkout --quiet -b hotfix/{}'.format(description))
        git('push --set-upstream origin hotfix/{}'.format(description))
    else:
        print('Tag not found: {}'.format(tag), file=sys.stderr)
        print('Available tags:')
        git('tag')
        sys.exit(2)


def git(command, pipe=False):
    if pipe:
        return subprocess.check_output('git {}'.format(command),
                                       shell=True).decode()
    else:
        return os.system('git {}'.format(command))


def is_repository_clean():
    status = git('status --short --untracked-files=no | wc -l', pipe=True)
    return status.strip() == "0"


def is_synced_origin(remote_branch):
    return git('rev-parse HEAD', pipe=True) == git(
        'rev-parse origin/{}'.format(remote_branch), pipe=True)


def check_repo_toplevel():
    # check if pwd is repository root in order to run makefile hooks properly
    rev_parse = git('rev-parse --show-toplevel', pipe=True).strip()
    if os.path.abspath(rev_parse) != os.path.abspath(os.getcwd()):
        print('You need to run this command from the toplevel'
              ' of the working tree.', file=sys.stderr)
        sys.exit(2)


def call_hook(hook, env_vars=''):
    check_repo_toplevel()
    if os.path.isfile('Makefile'):
        os.system(
            '{env_vars} make {hook} || echo "Warning: Makefile has no target'
            ' named {hook}"'.format(**locals()))

        if not is_repository_clean():
            git('commit --quiet -am "Ran git devbliss {hook} hook"'.format(
                **locals()))
    else:
        print('Warning: No Makefile found. All make hooks have been skipped.',
              file=sys.stderr)


def branch(branch_type, branch_name):
    if branch_name == 'finish':
        print('You are creating a branch "{branch_type}/{branch_name}". '
              'Did you mean to type "git devbliss finish"?'.format(**locals()))
        print('You can delete this branch with "git devbliss delete'
              ' {branch_type}/{branch_name}"'.format(**locals()))

    git('checkout --quiet master')
    git('pull --quiet origin master')
    try:
        git('checkout --quiet -b {branch_type}/{branch_name}'.format(
            **locals()))
    except subprocess.CalledProcessError:
        git('checkout --quiet {branch_type}/{branch_name}'.format(
            **locals()))
    git('push --set-upstream origin {branch_type}/{branch_name}'.format(
        **locals()))


def release(version):
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print('Invalid version number', file=sys.stderr)
        sys.exit(2)

    git('fetch --quiet origin')
    branch = git('rev-parse --abbrev-ref HEAD', pipe=True)

    if not is_repository_clean():
        print('Error: Repository is not clean. Aborting.', file=sys.stderr)
        sys.exit(1)
    if not is_synced_origin('master'):
        print('Error: Local branch is not in sync with origin. Aborting.',
              file=sys.stderr)
        print('Do "git pull && git push" and try agin.', file=sys.stderr)
        sys.exit(1)

    call_hook('release', 'DEVBLISS_VERSION="{}"'.format(version))
    git('diff')
    print("Have these changes been reviewed?")
    print("[enter / ctrl+c to cancel]")
    try:
        input()
    except KeyboardInterrupt:
        sys.exit(2)
    git('commit --quiet --allow-empty -m "Release: {version}"'.format(
        **locals()))
    git('push origin {branch}'.format(**locals()))
    git('tag {version}'.format(**locals()))
    git('push --tags origin')
    if branch == 'master':
        print()
        github_devbliss(['pull-request'])


def delete(force=False):
    branch = git('rev-parse --abbrev-ref HEAD', pipe=True)
    if branch == 'master':
        print("Won't delete master branch. Aborting.", file=sys.stderr)
        sys.exit(2)
    if force or input(
            'Really delete the remote branch? [y/N] ').capitalize() == 'Y':
        git('push --delete origin {}'.format(branch))
        print('To restore the remote branch, type')
        print('    git push --set-upstream origin {}'.format(branch))
        print('To delete your local branch, type')
        print('    git checkout master && git branch -d {}'.format(branch))


def cleanup():
    git('fetch')
    print("Deleting remote tracking branches whose "
          "tracked branches on server are gone...")
    git('remote prune origin')
    print("Searching all remote branches except release "
          "that are already merged into master...")
    get_remote_merged_branches = None
    try:
        get_remote_merged_branches = git('branch -r --merged origin/master'
                                         ' | grep -v master | grep -v release',
                                         pipe=True)
    except subprocess.CalledProcessError:
        print('No remote merged branches found')
    if get_remote_merged_branches:
        print(get_remote_merged_branches)
        if input("Do you want to delete those branches on the server? [y/N]"
                 ).capitalize() == 'Y':
            print("Deleting...")
            os.system("echo '{}' | sed 's#origin/##' | xargs -I {{}}"
                      " git push origin :{{}}".format(
                          get_remote_merged_branches))
            git('remote prune origin')
        else:
            print("ok, will not delete anything.")
    print("Deleting all local branches (except current)"
          " that are already merged into local master...")
    git("branch --merged master | grep -v master "
        "| grep -v '\*' | xargs git branch -d")
    print("Checking for unmerged local branches...")
    git('branch --no-merged master')


def finish(base_branch):
    base_branch_used = bool(base_branch)
    base_branch = base_branch or 'master'
    branch = git('rev-parse --abbrev-ref HEAD', pipe=True)
    if not is_repository_clean():
        print("Error: Repository is not clean. Aborting.", file=sys.stderr)
        sys.exit(1)

    if branch not in git('branch --contains {}'.format(base_branch),
                         pipe=True):
        if 'hotfix/' in branch and not base_branch_used:
            print("Warning: Master is not merged into the current branch.")
        else:
            print("Error: Won't finish. {} is not merged into the"
                  " current branch.".format(base_branch), file=sys.stderr)
            print("Please do 'git merge {}', make sure all conflicts"
                  " are merged and try again.".format(base_branch),
                  file=sys.stderr)
            sys.exit(1)
    env_vars = 'DEVBLISS_BRANCH_TYPE=' + branch.split('/')[0]
    call_hook('finish', env_vars)
    call_hook('changelog', env_vars)
    call_hook('version', env_vars)
    git('push origin {}'.format(branch))
    print()
    args = ['pull-request']
    if base_branch:
        args = args + [base_branch]
    github_devbliss(args)
    print()
    github_devbliss(['open-pulls'])

if __name__ == '__main__':
    sys.exit(main())  # pragma nocover
