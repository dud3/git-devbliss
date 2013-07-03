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
    make[1]: Entering directory `/home/vagrant/workflow_test'
    make[1]: Leaving directory `/home/vagrant/workflow_test'
    make[1]: Entering directory `/home/vagrant/workflow_test'
    make[1]: Leaving directory `/home/vagrant/workflow_test'
    Everything up-to-date
    <BLANKLINE>
    Fatal: No commits between h-nuschke:master and h-nuschke:feature/my-feature

As you can see the finish command calls a few makefile hooks (namely:
changelog and finish) and then aborts the finish process since we haven't made
any changes.

Thus we implement a little feature and do another finish

    >>> sh("echo '#!/usr/bin/env python' > hello_world.py")
    >>> sh("git add .")
    >>> sh("git commit -m'hello world script'")
    [feature/my-feature 2dae663] hello world script
     1 file changed, 1 insertion(+)
     create mode 100644 hello_world.py
    >>> sh("echo 'print \"hello world\"' >> hello_world.py")
    >>> sh("git devbliss finish")
    Error: Repository is not clean. Aborting.

The finish command checks for the repository to be clean before the process is
started. If we commit our changes first the finish should work.

    >>> sh("git commit -am'hello world script'")

    >>> sh("git devbliss finish")

### Releasing a new version

Making a release will mainly cause a release commit with the version number in
it's commit message and a tag which is pointing to the release commit.
It is encouraged to release new features as early as possible. Therefore we can
do releases from the feature branch so the resulting tag will be merged into
the master branch as soon as the feature itself is merged.
In order to release we will have to provide the proper version number to the
command.

    >>> pass

### Posting an issue

While we implemented a new feature we might have realized that there are some
things in our software which could be improved. Here the git-devbliss issue
command comes handy.

    >>> pass

### Getting some repository information

Finally we can get some status information about our repository with the use of
git-devbliss status.

    >>> pass

## Hotfix example

A hotfix is supposed to be a bug fix in an already deployed version of our
software which contains only the needed bug fix but no new features. To get
there we branch from a given tag instead of the master. This way no new features
will be included in the resulting release. The desired tag has to be provided
for the hotfix command.

### Creating a hotfix branch

The creation of a hotfix branch only differs from the creation of a feature
branch by the provided tag to which the resulting branch refers to.

    >>> pass

### Release the hotfix

A hotfix can be finished with a regular git-devbliss finish but the
branch should definitely contain a release commit and a belonging tag.
If the branch should be merged into the master has to be decided dependent
on the masters current state and how far the fixed piece of code has changed
till the version from which the hotfix was branched.

    >>> pass

### Status information

Finally we can have another look at our repositories status and can check the
existence of our hotfix branch.

    >>> pass


