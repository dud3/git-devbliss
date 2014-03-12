# devbliss git extensions

git-devbliss is a command line tool which guides the developer along the
encouraged workflow used for feature development, bug fixing and hotfixing at
devbliss.

The goal of git-devbliss is to summarize certain single git operations into
semantically meaningful commands and doing sanity checks to prevent frequent
mistakes.
The tool does not replace any existing git commands nor does it
prevent the developer from using the latter the way he wants to use them.

## Installation via MacPorts

The installation of git-devbliss via MacPorts is the default installation
method. If you havn't already enabled the devbliss MacPorts repository on you
Mac follow [this howto](https://github.com/devbliss/macports/blob/master/README.md).

and then type:

    sudo port selfupdate
    sudo port install git-devbliss

To enable BASH completion you have to source the file
`/opt/local/etc/bash_completion.d/git-devbliss`. To permanently enable the
completion add the following line to your `~/.profile`.

    source /opt/local/etc/bash_completion.d/git-devbliss

## Installation via Makefile (discouraged)

    git clone git@github.com:devbliss/git-devbliss.git
    cd git-devbliss
    ./configure sudo make install

Note: the Makefile run by the install script will write a file at
`/etc/bash_completion.d/git-devbliss`, which may or may not be sourced on your
system. If bash completion doesn't work, append the following line to your
`.profile` (or `.bashrc`) file:

    source /etc/bash_completion.d/git-devbliss

### Zsh Completion (you don't need that if you are using BASH)

Just put the following in your .zshrc:

    fpath=(<path-to-workflow>/zsh_completion $fpath) zstyle
    ':completion:*:*:git:*' user-commands \    devbliss:'devbliss git workflow'
    \


To make completion work at all you have to load zsh's completion module like
this:

    autoload -Uz compinit compinit

The fpath should be set before the compinit.

## Overview

See: git help devbliss or if not installed see:
[manpage](https://github.com/devbliss/git-devbliss/blob/master/man1/git-devbliss.1)

## Testing

The git-extensions are tested using the following github account.

    Horst Nuschke user: h-nuschke email: h-nuschke1@trash-mail.com password:
    h-nuschke1 repo: git@github.com:h-nuschke/workflow_test.git

The ssh keys are applied via puppet so github can be accessed.

## Implementing a new feature

To implement a new feature, change the git-devbliss code and install it in the virtual machine:
  - vagrant up
  - vagrant ssh
  - ./configure
  - sudo make install # optional, is done by make test anyways
  - make test

## Makefile hooks

You need to include a Makefile in your project, which defines entry points for
common tasks. The Makefile works like an abstraktion layer which has mainly
four advantages:

 1. Your daily work becomes easier because you won't have to adjust your habits
    depending on the project.
 2. If a project is reactivated after a certain amount of time it eases the
    pain of continuing.
 3. New developers have an easier start.
 4. (This is of interest here) Conventonally defined make targets make it
    possible to integrate hooks in our git devbliss toolset which makes your
    daily work easier and more failsafe.

### Make targets

You are encouraged to implement the following targets in your Makefile:

- **test**: Run all your projects software tests
- **deb**: Build a ready to deploy Debian package
- **clean**: Clean up all messy stuff created while building your project
- **changelog**: Make sure your changelog has been updated (will be run when
  called 'git devbliss finish') The best thing you can do here is to open a
  text editor and get used to write the changelog at time of finishing your
  task. This way you will never forget to remark your changes
- **version**: Make sure your projects version number has been incremented
  (will be run when called 'git devbliss finish') Implement that similar to the
  `changelog` target
- **finish**: Define some tasks that have to be done before creating a pull
  request: e.g. formatting source files...
- **release**: Called upon git-devbliss release

Depending on the git-devbliss command used, there is one of two bash variables
available:
- **finish**:  `DEVBLISS_BRANCH_TYPE` is available that holds the branch type
  value (`feature`, `bug`, `hotfix`, `research` or `refactor`)
- **release**: `DEVBLISS_VERSION` is available that carries the version number
  used with the release command

## Make target snippets

This section contains some snippets for the use in conjuction with the
recomended make targets. You can copy/paste from here or even better add your
own snippets for the benefit of others.

### Open changelog in the default editor

    changelog:
    	@$${EDITOR:-"vi"} debian/changelog

    .PHONY: changelog

### Typical maven delegation

    build:
    	mvn gwt:compile

    changelog:
    	@$${EDITOR:-"vi"} debian/changelog

    test:
    	mvn test

    clean:
    	mvn clean

## GitHub login

The github api client (`github-devbliss` in your path) will ask you for a username
and password in order to log in to GitHub. The resulting authorization token is then
stored at `~/.github_token`.

### Using multiple machines

Because the same application can't create multiple authorization tokens, you need to
copy your token to all your machines in order to use git-devbliss on them. If you have
switched machines, you can also delete the `git-devbliss/ng` application in your GitHub
application settings.

### Two-Factor Authentication

If you use two-factor authentication,
[create a new access token](https://github.com/settings/tokens/new) in your github
application settings (enabling only the "repo" scope) and write it to
`~/.github_token`. You will then be able to log in without a username and password.
