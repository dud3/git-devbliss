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

Zsh has no proper default location for custom completion scripts. So just grep the
comletion file in the zsh_completion/ subdirectory an put it in some place in your
`$fpath`. Here is a useful example which employs a completion directory in your `~`:

    mkdir ~/.zsh_completion
    echo "fpath=(~/.zsh_completion $fpath)" >> ~/.zshrc
    cp zsh_completion/_git-devbliss ~/.zsh_completion/

You might already have an fpath vaiable set in your `.zshrc`. In this case you better
just append the ~/.zsh_completion/.
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
