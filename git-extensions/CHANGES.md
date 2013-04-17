# git devbliss changelog

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
