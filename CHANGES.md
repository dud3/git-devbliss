# git devbliss changelog

## 1.2.0

 - Fixed missing fetch in review command
 - Fixed wrong string splitting when getting remote branch

## 1.1.0

 - The finish command can now crate pull requests to any desired branch
 - Fixed a bug where hotfix branches that diverged
   from master coundn't be finished

## 1.0.0

 - Version Bump

## 0.14.0

 - Release hook added
 - Finish hook has its own commit
 - Fixed a bug in `--version` with macports install

## 0.13.1

 - Fixed bad substitution in `git devbliss finish`

## 0.13.0

 - Run `make version` on `finish` instead of `release`

## 0.12.0

 - Restructured source tree
 - Macports compatibility (github.com/devbliss/macports)

## 0.11.0

 - The review command no longer shows the full historic diff,
   now same as github.com

## 0.10.0

 - github commands for pull requests: review, close-button, merge-button

## 0.9.1

 - bug: version numbers used to be sorted lexicographically, preventing update

## 0.9.0

 - bug: branch to create already exists
 - bug: force delete not working

## 0.8.1

 - make sure release commit is pushed

## 0.8.0

 - retry pull request if no commits between master and feature branch
 - check if local and remote branch are in sync on release

## 0.7.0

 - no test run on release

## 0.6.0

 - new relase policy: encourage releases form feature branch
 - fixed: on update only stash and apply if working dir is dirty

## 0.5.0

 - Documentation
 - Export `DEVBLISS_BRANCH_TYPE` variable

## 0.4.0

 - Error handling for revoked authorisation

## 0.3.0

 - explicitly use python 2.7
 - bug: update script runs wrong makefile
 - bug: return to previous branch on update
 - check if pwd is repo toplevel in order to run makefile hooks properly
 - bug: username prompt on github login not displaying
 - improved update script

## 0.2.0

 - added "github-devbliss overview ORG" command
 - set DEVBLISS_VERSION environment variable in relaease command

## 0.1.1

 - better regex to grep version no from changelog

## 0.1.0

 - new 'issue' command
 - added uninstall script
 - added update script
 - update check
 - added manpage
 - added 'status' command
 - aliased git devbliss to git de
 - added native github client (python)
 - finish now checks if current branch contains master
 - add research command to git devbliss
 - create, finish and delete branches and hotfixes
 - create and list pullrequests
 - make releases
 - makefile hooks

## 0.0.0

 - Initial release
