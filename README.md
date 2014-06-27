# devbliss git extensions

git-devbliss is a command line tool which guides the developer along the
encouraged workflow used for feature development, bug fixing and hotfixing at
devbliss.

The goal of git-devbliss is to summarize certain single git operations into
semantically meaningful commands and doing sanity checks to prevent frequent
mistakes.
The tool does not replace any existing git commands nor does it
prevent the developer from using the latter the way he wants to use them.

## Requirements

- git 2.0
- python 3.4
- make


you also need pip3.4, which is included in python 3.4 (of course you can also install with your systems package manager):

    python3.4 -m ensurepip --upgrade # on debian please use `sudo apt-get install python3-pip`

do not forget to put the python package path into your system's path if it is not there yet:

    export PATH=/opt/local/Library/Frameworks/Python.framework/Versions/3.4/bin:$PATH # OSX
    
If you have an old version of git-devbliss that was installed with Makefile or macports, please uninstall that version first. Remember that bash_completion will be uninstalled as well - please refer to the 'Enabling bash completion' section below for how to restore it.

## Installation via pypi (recommended)

The installation of git-devbliss via pypi is the default installation
method. Simply type:

    sudo pip-3.4 install --upgrade git-devbliss

## Installation via GitHub

    sudo pip-3.4 install --upgrade git+ssh://git@github.com/devbliss/git-devbliss.git

## Installation via Makefile

    git clone git@github.com:devbliss/git-devbliss.git
    cd git-devbliss
    sudo make
    bin/pip install .

## Enabling bash completion

To enable BASH completion you need to source that file in your bash profile:

    source /etc/bash_completion.d/git-devbliss


## Creating a shorter command for git-devbliss

run the following command if you want a shorter command for git devbliss:
    
    git config --global alias.de devbliss

## Testing

Simply run:

    make test

This will create a python virtual environment, run all checks and tests there and generate a coverage report


## Makefile hooks

You need to include a Makefile in your project, which defines entry points for
common tasks. The Makefile works like an abstraction layer which has
four main advantages:

 1. Your daily work becomes easier because you won't have to adjust your habits
    depending on the project.
 2. If a project is reactivated after a certain amount of time it eases the
    pain of continuing.
 3. New developers have an easier start.
 4. Conventionally defined make targets make it
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
- **finish**, **version**, **changelog**:  `DEVBLISS_BRANCH_TYPE` is available that holds the branch type
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

### Using a new / multiple machines

Because the same application can't create multiple authorization tokens, you need to
copy your token to all your machines in order to use git-devbliss on them. If you have
switched machines, you can also delete the `git-devbliss/ng` application in your GitHub
application settings.


## External Dependencies

Git-Devbliss includes, depends on, or uses the following free software components:

- Python3 (http://python.org, Python Software Foundation License)
- Setuptools (https://pypi.python.org/pypi/setuptools, Python Software Foundation License)
- Docopt (https://github.com/docopt/docopt, MIT License)
- Flake8 (https://bitbucket.org/tarek/flake8/wiki/Home, MIT License)
- Python Coverage (https://bitbucket.org/ned/coveragepy, BSD License)
- Requests (https://github.com/kennethreitz/requests, Apache2 License)
