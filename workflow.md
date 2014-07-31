# Version Control Workflow

## Introduction

This document describes the recommended workflow for using git and git-devbliss.

## Branches

Each project has one main branch, called `master`, which is, at any given time, the focus of development. Do not create
additional branches such as `develop`, `testing`, `stable`, or `unstable`. From the HEAD of master, one may create
branches with the follwing prefixes:

    bug/...
    feature/...
    refactor/...
    research/...

After preparing a release, a tag should be created according to the versioning scheme specified in
[semantic versioning](http://semver.org/). The tag may only be created after appending to the changelog
and ensuring that the entire test suite runs without errors.

Once a release is made, bug fixes to that release can be developed in branches prefixed by

    hotfix/...

The commit from which this branch stems is always one that has a tag pointing to it, and the version number of the
subsequent release made on this branch is the same, with a patch level incremented (see below).

## Example
                                          [1.1.1]
                              [1.1.0]        |
                                |  ----10----11-- hotfix/1
                                | /              \
       feature/1  ----7----8----9--               \
                 /                 \               \
    master  ----0----1----2----3----4----5----6----12----14---| HEAD
                |\
                |  ----13--------------------------------- hotfix/2
              [1.0.0]  |
                    [1.0.1]

In addition to master, there are three branches in this example:

 - `feature/1` is a normal feature-branch, and could also be a `bug/` or `refactor/` branch. It is made by branching
   from master (at which point, 0 was the HEAD) and merging back into it after making a release. Note that the release
   can also be made from master, after the branch has been merged. Tags only point to commits, it does not matter on
   what branch they're created.

        git checkout master
        git checkout -b feature/1
        ...
        git tag 1.1.0
        git checkout master
        git merge feature/1

 - `hotfix/1` fixes a bug in version 1.1.0 (consequently, the release that will eventually be made on it is `1.1.1`).

        git checkout 1.1.0
        git checkout -b hotfix/1
        ...
        git tag 1.1.1
        git checkout master
        git merge hotfix/1

 - `hotfix/2` is the same as `hotfix/1`, but it is never merged back into master. Note that, for branches which will
   not be merged into master, a tag has to exist at the last commit in order to prevent the git garbage collector from
   deleteting any commits.

Note: after the code has been reviewed and merged, the branch should be deleted by the reviewer. You may re-use old
local branches, but should always expect the remote branch to be deleted. Because the branch can be restored by
checking out the merge-commit, no information is lost.

## Review

When a feature branch (including `feature/`, `bug/`, `research/`, and `refactor/`) is finished and ready to be merged
into master, a pull request should be issued on github, upon which the code review process starts.

Code review consists in another developer reviewing the code line by line. Every single commit should be reviewd, and
no code may be merged (or pushed) into master without proper peer review.

If a hotfix branch should not be merge into the master branch, the author can substitute a compare-view link on GitHub
for the pull request that would normally be used. After reviewing the code, the author can tag the last commit with the
hotfix version number and delete the hotfix branch.

## Git Extensions

This Branching Strategy is supported by [the `git-devbliss` tool](https://github.com/devbliss/git-devbliss).
