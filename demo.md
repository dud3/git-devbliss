# Git Workflow Demo

## Check out the project

    git clone git@github.com:devbliss/git-demo.git
    cd git-demo/

## Add the first feature

    git devbliss feature hello-world
    echo "print 'hello world'" > hello.py
    git commit -am "Print hello world"
    git devbliss finish
    # REVIEW
    git pull

## Fix a bug in the current development version

    git devbliss bug python3
    echo "print('hello world')" > hello.py
    git add hello.py
    git commit -am "Python 3 compatibility"
    git devbliss finish
    # REVIEW
    git pull

## Make a release

    git devbliss release 1.0.0

## Add a readme

    git devbliss feature readme
    emacs README.md
    git commit -am "README"
    git devbliss finish

## Make a hot fix in release 1.0

    git devbliss hotfix 1.0 executable
    emacs hello.py  # shebang
    chmod a+x hello.py
    git commit -am "made the script executable"
    git devbliss finish
    # REVIEW
    git devbliss release 1.0.1

## Go back to the current HEAD

    git co master
