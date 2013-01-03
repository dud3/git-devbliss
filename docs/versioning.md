# Versioning

## Request for comments

Version numbers are used to convey information about changes
in the software, relative to another version. There are three
parts to a version number, the last of which is optional.

These are all valid:

    0.0
    1.2-1
    3.7-41
    4.0

## Semantics

 1. The first part of the version number identifies the
    **major version**. The major version *must* change
    when there are backwards-incompatible changes to the
    API of the software, i.e. when an upgrade would mean
    that all current deployments of the software would
    stop working properly.

    This number may not change because of mere additions
    to the API, unless they break existing code in some
    way.

 2. The second part is the **minor version*. This number
    is incremented every time there are changes to the
    software which warrant a new release.

    You are free to specify how often this number is
    incremented. Usually, it will depend on how often
    you need a new release of the software.

 3. The **patch level** is optional, and is appened to
    the version number after a dash (`-`). It is used
    to indicate a release that contains additional bug
    fixes, and which is based upon a specific, possibly
    older, release of the software.

    For instance: Version `2.0-1` is based upon version
    `2.0`, but with an additional bug fix. Version `3.2`
    *may or may not* contain this fix.

## Syntax

A version number is defined by the following expression:

    ^ [0-9]+ \. [0-9]+ ( - [1-9][0-9]* )? $

Version numbers *may not* contain additional identifiers,
such as `rc.1`, `testing`, or anything else that does not
match the expression above.

## Specification

 1. A version number consists of three positive integers,
    a period (`.`) between the first two, and an ascii minus
    (`-`) between the second and third. The three integers
    are called major version, minor version and patch level.

 2. The third number may be left out, in which case the
    ascii minus character needs to be left out as well.

 3. The major and minor versions increase over time, and
    they do not overflow. For instance, release 1.9 is
    followed by release 1.10 (not necessarily 2.0).

 4. Once a version has been released, it's code may not
    be changed unless the version number is changed as well.

 5. A minor release, in which the minor release number was
    incremented but the major release number was not changed,
    indicates that the software can be safely upgraded to
    the newer version.

 6. A major release indicates that upgrading to the newer
    version will break existing installations.

 7. Hot fixes, in which the patch level will be incremented,
    are fully API compatible.

 8. The patch level must be reset when a the minor
    version is incremented. The first patch level is
    empty, meaning the version number only has two parts.

 9. The minor version and patch level must be reset when the
    major version is incremented.
