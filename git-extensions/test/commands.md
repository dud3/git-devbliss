# git-devbliss command line integration test

This is a test of the git-devbliss command line. Therefore it is a simple test
which ensures that the commands work like expected. Since git-devbliss is
closely interacting with github it is also a test of our github-devbliss
python script which is tested here implicitly.

For the tests of the proper collaboration with github we created a fake account
on github which is only used for testing purpose.

The following procedure is supposed to be a real world example which describes
the regular life cycle of branches.

## Help check

Before we start with anything else lets check if we get the proper help screen
increase of wrong command line syntax.

    >>> sh("git devbliss these are to many and wrong parameters")
    Usage:
        git devbliss [feature | bug | refactor | research] DESCRIPTION
        git devbliss hotfix VERSION DESCRIPTION
        git devbliss finish
        git devbliss release VERSION
        git devbliss status
        git devbliss delete [-f]
        git devbliss issue [TITLE]
    <BLANKLINE>
    Options:
        feature, bug, refactor, research
        Branch from master (normal branches)
        hotfix        Branch from a tag (fix a bug in an already released version)
        finish        Open a pull request for the current branch
        release       Create a new tag, commit and push
        status        List branches, pull requests, and issues
        issue         Quickly post an issue to GitHub
        delete        Delete the current branch on github.com
        -v --version  Print version number of git-devbliss

## A regular branch life cycle

### Doing some research

If we want to do some experiments with our software we and just initiate a
research branch with git-devbliss research. This will pull the remote master,
create a local branch, will do a checkout to it and push it to the remote.

    >>> sh("git devbliss research my-experiment")
    To git@github.com:h-nuschke/workflow_test.git
     * [new branch]      research/my-experiment -> research/my-experiment
    Branch research/my-experiment set up to track remote branch research/my-experiment from origin.

### Delete a branch

When we finished our research we probably want to delete the branch since we
were just experimenting and never intended to merge the research branch into
our master branch. This can be done by git-devbliss delete. It will delete the
current branch remotely but will keep the local branch so it can be restored if
necessary.

    >>> sh("git devbliss delete -f")
    To git@github.com:h-nuschke/workflow_test.git
     - [deleted]         research/my-experiment

### Implementing a feature

Now the real work starts similar to the creation of the research branch.
Instead of git-devbliss research we use git-devbliss feature. The same
procedure is done with git-devbliss bug in case of a bug.

    >>> sh("git devbliss feature my-feature")
    To git@github.com:h-nuschke/workflow_test.git
     * [new branch]      feature/my-feature -> feature/my-feature
    Branch feature/my-feature set up to track remote branch feature/my-feature from origin.

### Finishing the feature branch

When the feature is ready we simply type git-devbliss finish. This will check
if the master current master branch is integrated in the feature branch and
will then push the feature branch to the remote side and open a pull request.

Let's do the finish

    >>> sh("git devbliss finish")
    Everything up-to-date
    <BLANKLINE>
    Fatal: Unprocessable Entity
    Possibly pull request already exists.

As you can see the finish command calls a few makefile hooks (namely:
changelog and finish) and then aborts the finish process since we haven't made
any changes.

Thus we implement a little feature and do another finish

    >>> sh("echo '#!/usr/bin/env python' > hello_world.py")
    >>> sh("git add .")
    >>> sh("git commit -m'hello world script'")
    [feature/my-feature ...] hello world script
     1 file changed, 2 deletions(-)
    >>> sh("echo 'print \"hello world\"' >> hello_world.py")
    >>> sh("git devbliss finish")
    Error: Repository is not clean. Aborting.

The finish command checks for the repository to be clean before the process is
started. If we commit our changes first the finish should work.

    >>> sh("git commit -am'hello world script'")
    [feature/my-feature ...] hello world script
     1 file changed, 1 insertion(+)

    >>> sh("git devbliss finish")
    To git@github.com:h-nuschke/workflow_test.git
       ...  feature/my-feature -> feature/my-feature
    <BLANKLINE>
    https://github.com/h-nuschke/workflow_test/pull/...
    <BLANKLINE>
    <BLANKLINE>
    Pull Requests:
        #...: feature/my-feature <https://github.com/h-nuschke/workflow_test/pull/...>

Meanwhile another team member started a new feature and implements some code.

    >>> sh("git devbliss feature another-feature")
    To git@github.com:h-nuschke/workflow_test.git
     * [new branch]      feature/another-feature -> feature/another-feature
    Branch feature/another-feature set up to track remote branch feature/another-feature from origin.
    >>> sh("echo '#!/usr/bin/env python' > another-feature.py")
    >>> sh("git add .")
    >>> sh("git commit -m'hello world script'")
    [feature/another-feature ...] hello world script
     1 file changed, 1 insertion(+)
     create mode 100644 another-feature.py

The feature is ready and the branch can be finished. But a short moment before
the first branch gets merged which causes the finish command to complain about
the feature branch is not containing the current master.

    >>> sh("git checkout master")
    Switched to branch 'master'
    >>> sh("git merge feature/my-feature")
    Updating ...
    Fast-forward
     hello_world.py |    1 -
     1 file changed, 1 deletion(-)
    >>> sh("git checkout -")
    Switched to branch 'feature/another-feature'
    Your branch is ahead of 'origin/feature/another-feature' by 1 commit.
    >>> sh("git devbliss finish")
    Please do 'git pull origin master', make sure all conflicts are merged and try again.

If we now merge the master in our feature branch the finish command will work.

    >>> sh("git merge master")
    Merge made by the 'recursive' strategy.
     hello_world.py |    1 -
     1 file changed, 1 deletion(-)
    >>> sh("git devbliss finish")
    To git@github.com:h-nuschke/workflow_test.git
       ...  feature/another-feature -> feature/another-feature
    <BLANKLINE>
    https://github.com/h-nuschke/workflow_test/pull/...
    <BLANKLINE>
    <BLANKLINE>
    Pull Requests:
        #...: feature/another-feature <https://github.com/h-nuschke/workflow_test/pull/...>
        #...: feature/my-feature <https://github.com/h-nuschke/workflow_test/pull/...>

### Releasing a new version

Making a release will mainly cause a release commit with the version number in
it's commit message and a tag which is pointing to the release commit.
It is encouraged to release new features as early as possible. Therefore we can
do releases from the feature branch so the resulting tag will be merged into
the master branch as soon as the feature itself is merged.
In order to release we will have to provide the proper version number to the
command.

Like the finish command the release command will abort if the local repository
is dirty.

    >>> sh("git checkout feature/my-feature")
    Switched to branch 'feature/my-feature'
    >>> sh("echo 'print \"hello world\"' >> hello_world.py")
    >>> sh("yes 2> /dev/null | git devbliss release 0.0.0")
    0.0.0
    Error: Repository is not clean. Aborting.

The release command also checks if the local branch is in sync with the origin.
If we commit our changes and don't push them to the origin we can provoke this
very behaviour.

    >>> sh("git commit -am'cool new stuff'")
    [feature/my-feature ...] cool new stuff
     1 file changed, 1 insertion(+)

    >>> sh("yes 2> /dev/null | git devbliss release 0.0.0")
    0.0.0
    Error: Local branch is not in sync with origin. Aborting.
    Do 'git pull && git push' and try agin.

We now push our changes and the release should word then.

    >>> sh("git push")
    To git@github.com:h-nuschke/workflow_test.git
       ...  master -> master

    >>> sh("yes 2> /dev/null | git devbliss release 0.0.0")
    0.0.0
    Have these changes been reviewed?
    [enter / ctrl+c to cancel]
    To git@github.com:h-nuschke/workflow_test.git
       ...  feature/my-feature -> feature/my-feature
    To git@github.com:h-nuschke/workflow_test.git
     * [new tag]         0.0.0 -> 0.0.0
    Everything up-to-date
    <BLANKLINE>
    Fatal: Unprocessable Entity
    Possibly pull request already exists.

The error at the end of the output is normal in this case since a pull request
already exists from the finish command.

## Hotfix example

A hotfix is supposed to be a bug fix in an already deployed version of our
software which contains only the needed bug fix but no new features. To get
there we branch from a given tag instead of the master. This way no new features
will be included in the resulting release. The desired tag has to be provided
for the hotfix command.
For the test we first need to checkout the master branch and merge our feature
branch in order to get tag on our master branch.

    >>> sh("git checkout master")
    Switched to branch 'master'
    >>> sh("git merge feature/my-feature")
    Updating ...
    Fast-forward
     hello_world.py |    1 +
     1 file changed, 1 insertion(+)

### Creating a hotfix branch

The creation of a hotfix branch only differs from the creation of a feature
branch by the provided tag to which the resulting branch refers to.

    >>> sh("git devbliss hotfix 0.0.0 mean-bug-on-live")
    0.0.0
    To git@github.com:h-nuschke/workflow_test.git
     * [new branch]      hotfix/mean-bug-on-live -> hotfix/mean-bug-on-live
    Branch hotfix/mean-bug-on-live set up to track remote branch hotfix/mean-bug-on-live from origin.

    >>> sh("echo 'print \"hello world\"' >> hello_world.py")
    >>> sh("git commit -am'more cool new stuff'")
    [hotfix/mean-bug-on-live ...] more cool new stuff
     1 file changed, 1 insertion(+)
    >>> sh("git push")
    To git@github.com:h-nuschke/workflow_test.git
       ...  master -> master


### Release the hotfix

A hotfix can be finished with a regular git-devbliss finish but the
branch should definitely contain a release commit and a belonging tag.
If the branch should be merged into the master has to be decided dependent
on the masters current state and how far the fixed piece of code has changed
till the version from which the hotfix was branched.

    >>> sh("yes 2> /dev/null | git devbliss release 0.0.1")
    0.0.1
    Have these changes been reviewed?
    [enter / ctrl+c to cancel]
    To git@github.com:h-nuschke/workflow_test.git
       ...  hotfix/mean-bug-on-live -> hotfix/mean-bug-on-live
    To git@github.com:h-nuschke/workflow_test.git
     * [new tag]         0.0.1 -> 0.0.1
    Everything up-to-date
    <BLANKLINE>
    https://github.com/h-nuschke/workflow_test/pull/...


