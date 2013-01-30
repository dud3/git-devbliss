# devbliss git extensions

## Installation

    git clone git@github.com:devbliss/workflow.git
    cd workflow/git-extensions/
    sudo make install

Note: the makefile will write a file at `/etc/bash_completion.d/git-devbliss`,
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

    Usage:
        git devbliss [feature | bug | refactor] DESCRIPTION
        git devbliss hotfix VERSION DESCRIPTION
        git devbliss finish
        git devbliss release VERSION
        git devbliss delete [-f]

    Commands:
        feature, bug, refactor:
                  Branch from master (normal branches)
        hotfix:   Branch from a tag (fix a bug in an already released version)
        finish:   Open a pull request for the current branch
        release:  Create a new tag, commit and push
        delete:   Discard the current branch and delete the remote branch

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

### make targets

You are encouraged to implement the following targets in your Makefile:

- **test**: Run all your projects software tests (will be run when called 'git devbliss release')
- **deb**: Build a ready to deploy Debian package
- **clean**: Clean up all messy stuff created while building your project
- **changes**: Make sure your changelog has been updated (will be run when called 'git devbliss finish')  
The best thing you can do here is to open a text editor and get used to write the changelog at time
of finishing your task. This way you will never forget to remark your changes.
- **version**: Make sure your projects version number has been incremented (will be run when called 'git devbliss finish')  
Implement that similar to the changes target.

## make target snippets

This section contains some snippets for the use in conjuction with the recomended make targets. You can copy/paste from here or even better add your own snippets for the benefit of others.

### open changelog in the default editor

    define changelog_cmd
        changelog="CHANGES.md"
        if [ -z "$$EDITOR" ]; then
            EDITOR=vi
        fi
        ch_hash=$$(sha1sum $$changelog)
        $$EDITOR $$changelog
        ch_hash_new=$$(sha1sum $$changelog)
        if [ "$$ch_hash" == "$$ch_hash_new" ]; then
            echo "Operation aborted due to missing changelog entry" > /dev/stderr
            exit 1
        fi
    endef
    export changelog_cmd
    .PHONY : changelog
    changelog:
        @bash -c "$$changelog_cmd"

