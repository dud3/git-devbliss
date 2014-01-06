# Generating a description file for the pull requst.
This feature should be used, for code reviews, in order to generate a description file, typically a checklist
for project specific requirments, for example if coding standards have been followed, or if documentation has been provided by
the original coder(s)

Let us simply make a new branch, and create a pull request for it. At the end of that, the description should be viewable.

    >>> sh("git devbliss feature test-show-pull-request-description")
    To git@github.com:h-nuschke/workflow_test.git
     * [new branch]      feature/test-show-pull-request-description -> feature/test-show-pull-request-description
    Branch feature/test-show-pull-request-description set up to track remote branch feature/test-show-pull-request-description from origin.
    
Now we create some dummy file and do a git devbliss finish to generate a pull request
We should get the message, that a PullRequest.md file is missing.
   >>> sh("echo 'I am some test text' > dummy.txt")
   >>> sh("git add .")
   >>> sh("git commit -m'dummy text file'")
   [feature/test-show-pull-request-description ...] dummy text file
    1 file changed, 1 insertion(+)
    create mode 100644 dummy.txt
   >>> sh("git devbliss finish")
   To ...
   >>> with open("/dev/shm/fail_output", "r") as f:
   ...     pull = re.search(r"#(\d+).*test-show-pull-request-description", f.read()).group(1)
   >>> hub = GitHub()
   >>> pull_request = hub.get_pull_request('h-nuschke', 'workflow_test', pull)
   >>> pprint(pull_request['body'])
   u'No PullRequest.md found'
   >>> sh("git devbliss delete -f")
   To git@github.com:h-nuschke/workflow_test.git
    - [deleted]         feature/test-show-pull-request-description

Now let us create a PullRequest.md file, and expect the correct content to be in te pull_request body.
   >>> sh("echo 'I am some test text' > PullRequest.md")
   >>> sh("git add .")
   >>> sh("git commit -m'pull request file'")
   [feature/test-show-pull-request-description ...] pull request file
    1 file changed, 1 insertion(+)
    create mode 100644 PullRequest.md
   >>> sh("git devbliss finish")
   To ...
   >>> with open("/dev/shm/fail_output", "r") as f:
   ...     pull = re.search(r"#(\d+).*test-show-pull-request-description", f.read()).group(1)
   >>> hub = GitHub()
   >>> pull_request = hub.get_pull_request('h-nuschke', 'workflow_test', pull)
   >>> pprint(pull_request['body'])
   u'I am some test text\n'
   >>> sh("git devbliss delete -f")
   To git@github.com:h-nuschke/workflow_test.git
    - [deleted]         feature/test-show-pull-request-description
