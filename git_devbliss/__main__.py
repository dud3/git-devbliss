import sys
import pkg_resources
import subprocess
import os
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
    git-devbliss review <pull-request-id>
    git-devbliss merge-button <pull-request-id>
    git-devbliss close-button <pull-request-id>
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
        status()
    elif(args['delete']):
        delete(args['-f'])
    elif(args['issue']):
        issue(args['TITLE'])
    elif(args['review']):
        review(args['<pull-request-id>'])
    elif(args['merge-button']):
        merge_button(args['<pull-request-id>'])
    elif(args['close-button']):
        close_button(args['<pull-request-id>'])
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


def status():
    github_devbliss(['status'])


def issue(title):
    github_devbliss(['issue', title])


def review(pull_request_id):
    github_devbliss(['review', 'pull_request_id'])


def merge_button(pull_request_id):
    github_devbliss(['merge-button', 'pull_request_id'])


def close_button(pull_request_id):
    github_devbliss(['close-button', 'pull_request_id'])


def git(command, pipe=False):
    if pipe:
        return subprocess.check_output('git {}'.format(command),
                                       shell=True).decode()
    else:
        return os.system('git {}'.format(command))


def is_repository_clean():
    status = git('status --short --untracked-files=no | wc -l')
    return status.strip() == "0"


def is_synced_origin(remote_branch):
    diff = git('diff origin/{remote_branch} | wc -l'.format(
        remote_branch=remote_branch), pipe=True)
    if diff.strip() != "0":
        return False
    log = git('log origin/{remote_branch}..HEAD -- | wc -l'.format(
        remote_branch=remote_branch), pipe=True)
    if log.strip() != "0":
        return False
    return True


def check_repo_toplevel():
    # check if pwd is repository root in order to run makefile hooks properly
    rev_parse = git('rev-parse --show-toplevel', pipe=True)

    if rev_parse != os.getcwd():
        print('You need to run this command from the toplevel'
              ' of the working tree.', file=sys.stderr)
        sys.exit(2)


def call_hook(hook, env_vars=''):
    check_repo_toplevel()
    if os.file.exists('Makefile'):
        os.system('{env_vars} make {hook} '
                  '|| echo "Warning: Makefile has no target named {}'.format(
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
    branch = git('rev-parse --abrev-rev HEAD', pipe=True)

    if not is_repository_clean():
        print('Error: Repository is not clean. Aborting.', file=sys.stderr)
        sys.exit(1)
    if not is_synced_origin():
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
    if not is_repository_clean():
        git('commit --quiet -am "Ran git devbliss release hook"')
    git('commit --quiet --allow-empty -m "Release: {version}"'.format(
        **locals()))
    git('push origin {branch}'.format(**locals()))
    git('tag {version}'.format(**locals()))
    git('push --tags origin')
    git('push origin {branch}'.format(**locals()))
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


def finish(base_branch):
    pass


def cleanup():
    pass
"""


function finish {
    local base_branch=${1-}
    check_repo_toplevel # neccessary to run makefile hooks
    local branch=`git rev-parse --abbrev-ref HEAD`
    if ! is_repository_clean; then
        echo "Error: Repository is not clean. Aborting." >> /dev/stderr
        exit 1
    fi
    if ! git branch --contains master | grep "$branch" > /dev/null; then
        if [[ $branch = hotfix/* ]]; then
            echo "Warning: Master is not merged into the current branch." > /dev/stderr
        else
            echo "Error: Won't finish. Master is not merged into the current branch." > /dev/stderr
            echo "Please do 'git merge master', make sure all conflicts are merged and try again." > /dev/stderr
            exit 1
        fi
    fi
    export DEVBLISS_BRANCH_TYPE=`echo $branch | sed -e 's#\([^/]*\)/.*#\1#g'`
    makefile_hooks finish
    if ! is_repository_clean; then
        git commit --quiet -am "Ran git devbliss finish hook"
    fi
    makefile_hooks changelog
    if ! is_repository_clean; then
        git commit --quiet -am "Ran git devbliss changelog hook"
    fi
    makefile_hooks version
    if ! is_repository_clean; then
        git commit --quiet -am "Ran git devbliss version hook"
    fi
    git push origin $branch
    echo
    github-devbliss pull-request ${base_branch-}
    echo
    github-devbliss open-pulls
}

function cleanup {

    git fetch
    echo "Deleting remote tracking branches whose tracked branches on server are gone..."
    git remote prune origin
    echo "Searching all remote branches except release that are already merged into master..."
    get_remote_merged_branches=`git branch -r --merged origin/master | grep -v master | grep -v release`
    echo "$get_remote_merged_branches" | grep '\w' && read -p "Do you want to delete those branches on the server? [y/N] " -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Deleting..."
        echo "$get_remote_merged_branches" | sed 's#origin/##' | xargs -I {} git push origin :{}
        git remote prune origin
    else
        if [ "" = "$get_remote_merged_branches" ]
        then
            echo "nothing to do."
        else
            echo "ok, will not delete anything."
        fi
    fi
    echo "Deleting all local branches (except current) that are already merged into local master..."
    git branch --merged master | grep -v master | grep -v '\*' | xargs git branch -d
    echo "Checking for unmerged local branches..."
    git branch --no-merged master

}


elif is_branch_command $1; then
    branch $1 $2
"""

if __name__ == '__main__':
    sys.exit(main())
