# devbliss git extensions

## Installation

    git clone git@github.com:devbliss/workflow.git
    cd workflow
    ./install

Note: the Makefile run by the install script will write a file at `/etc/bash_completion.d/git-devbliss`,
which may or may not be sourced on your system. If bash completion doesn't work,
append the following line to your `.profile` (or `.bashrc`) file:

    source /etc/bash_completion.d/git-devbliss

### Zsh Completion

Just put the following in your .zshrc:

    fpath=(<path-to-workflow>/git-extensions/zsh_completion $fpath)
    zstyle ':completion:*:*:git:*' user-commands \
        devbliss:'devbliss git workflow' \


To make completion work at all you have to load zsh's completion module like this:

    autoload -Uz compinit
    compinit

The fpath should be set before the compinit.

## Overview

See: git help devbliss or if not installed see:
[manpage](https://github.com/devbliss/workflow/blob/master/git-extensions/man1/git-devbliss.1)

## Testing

The git-extensions are tested using the following github account.

    Horst Nuschke
    user: h-nuschke
    email: h-nuschke1@trash-mail.com
    password: h-nuschke1
    repo: git@github.com:h-nuschke/workflow_test.git

The ssh keys are applied via puppet so github can be accessed.


## Makefile hooks

You need to include a Makefile in your project, which defines entry points
for common tasks. The Makefile works like an abstraktion layer which has mainly four
advantages:

 1. Your daily work becomes easier because you won't have to adjust your habits
depending on the project.
 2. If a project is reactivated after a certain amount of time
it eases the pain of continuing.
 3. New developers have an easier start.
 4. (This is of interest here) Conventonally defined make targets make it possible to
integrate hooks in our git devbliss toolset which makes your daily work easier and more failsafe.

### Make targets

You are encouraged to implement the following targets in your Makefile:

- **test**: Run all your projects software tests
- **deb**: Build a ready to deploy Debian package
- **clean**: Clean up all messy stuff created while building your project
- **changelog**: Make sure your changelog has been updated (will be run when called 'git devbliss finish')
The best thing you can do here is to open a text editor and get used to write the changelog at time
of finishing your task. This way you will never forget to remark your changes.
- **version**: Make sure your projects version number has been incremented (will be run when called 'git devbliss release')
Implement that similar to the `changelog` target.
- **finish**: Define some tasks that have to be done before creating a pull request: e.g. formatting source files...

## Make target snippets

This section contains some snippets for the use in conjuction with the recomended make targets. You can copy/paste from here or even better add your own snippets for the benefit of others.

### Open changelog in the default editor

    .PHONY : changelog
    changelog:
    	@$${EDITOR:-"vi"} debian/changelog


### Typical maven delegation

    build:
    	mvn gwt:compile

    changelog:
    	@$${EDITOR:-"vi"} debian/changelog

    test:
    	mvn test

    clean:
    	mvn clean
