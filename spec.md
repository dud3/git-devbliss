# Version Control

Each project has one main branch, called `master`, which is,
at any given time, the focus of development. Do not create
additional branches such as `develop`, `testing`, `stable`,
or `unstable`. 

From the HEAD of master, one may create branches with the
follwing prefixes:

    bug/...
    feature/...
    refactor/...

After preparing a release, a tag should be created according
to the versioning scheme specified in this document. The tag
may only be created after appending to the changelog and ensuring
that the entire test suite runs without errors.

Once a release is made, bug fixes to that release can be
developed in branches prefixed by

    hotfix/...

The commit from which this branch stems is always one that has
a tag pointing to it, and the version number of the subsequent
release made on this branch is the same, with a patch level
added or incremented (see below).
    
## Example
                                          [1.1-1]
                              [1.1]          |
                                |  ----10----11-- hotfix/1
                                | /              \
       feature/1  ----7----8----9--               \
                 /                 \               \
    master  ----0----1----2----3----4----5----6----12----14---| HEAD
                |\
                |  ----13--------------------------------- hotfix/2
              [1.0]    |
                    [1.0-1]

In addition to master, there are three branches in this example:

 - `feature/1` is a normal feature-branch, and could also be
   a `bugfix/` or `refactor/` branch. It is made by branching from
   master (at which point, 0 was the HEAD) and merging back into
   it after making a release. Note that the release can also be made
   from master, after the branch has been merged. Tags only point
   to commits, it does not matter on what branch they're created.

        git checkout master
        git checkout -b feature/1
        ...
        git tag 1.1
        git checkout master
        git merge feature/1

 - `hotfix/1` fixes a bug in version 1.1 (consequently, the release
   that will eventually be made on it is `1.1-1`).

        git checkout 1.1
        git checkout -b hotfix/1
        ...
        git tag 1.1-1
        git checkout master
        git merge hotfix/1

 - `hotfix/2` is the same as `hotfix/1`, but it is never merged
   back into master. One important difference here is that this
   branch can never be deleted, otherwise, commits that are never
   merged into master (namely 13) would have no reference left,
   and the git garbage collector would destroy them. For this reason,
   you may wish to always merge into master.


# Version Numbers

A version number consists of two or three parts, the
major version, minor version, and patch level. The
major and minor version number may be zero, but the
patch level may not. If no patches have been applied
to a release, the version number consists only of the
former two parts.

Valid version numbers match this expression:

    ^[0-9]+\.[0-9]+(-[1-9][0-9]*)?$

### Examples

    0.0
    1.0
    1.0-1
    1.0-2
    2.9
    2.10

## Major Version

The major version indicates API compatibility. Users of
the software can always assume that upgrading to a version
with the same major version number will not break their
installation. While features may be added within one major
release cycle, they may not be removed, nor can their
behaviour change.

## Minor Version

The minor version is incremented when new features are
introduced, bugs are fixed, when tests or documentation
have been added, or they might be time based.

The rules governing incrementation of the minor version
number are left to each individual project.

## Patch Level

Once a release of the software is made, that release can
never be changed. If it becomes necessary to make changes
to an existing release, the patch level must be incremented.

For instance: when fixing a bug in version `1.2`, when the
current version might be `2.4`, a new release is made and
its version number is `1.2-1`. The fix may be back-ported
to the current development version, but not to version `2.4`.
If the bug fix is ported to version 2.4, its version number
is changed to `2.4-1` as well.

We call this kind of release a "hot fix".

# Packaging

Each release of a project must be packaged as a debian package
(3.0 native). Ideally, each project provides only one package,
whose name is the same as that of the project's SCM repository.

If projects wish to provide multiple packages, they should also
offer a meta-package with the correct name, which depends on the
other packages.

For more information, see <https://github.com/devbliss/packaging/>

## Changelog

The changelog of the debian package must be kept up to date on
every release. The version number of a package is defined only
in the changelog, not in the `control` file.

On Ubuntu, the `dch -i` command can be used to append to the
changelog and define the new version number.

## Naming

Python and Ruby extension modules have a prefix of `python-` and
`ruby-` respectively. This does not mean that every project written
in Python needs to have this prefix, but pure extension modules
should do.

# Makefiles

Each project needs to provide a `Makefile` in its top-level directory,
implementing the at least the following commands:

    make test
    make

The `make test` command should run the entire test suite. The `make`
command should result in debian source- and binary packages being built.
