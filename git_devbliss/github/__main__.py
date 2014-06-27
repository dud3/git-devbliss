# Copyright 2014 devbliss GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import git_devbliss.github
import time
import requests
import subprocess
import os
from docopt import docopt
import pkg_resources

__version__ = pkg_resources.get_distribution("git_devbliss").version


def get_repository():
    github = git_devbliss.github.GitHub()
    try:
        owner, repository = github.get_current_repo()
    except subprocess.CalledProcessError as e:
        sys.exit(1)
    except ValueError as e:
        print("Fatal: " + str(e), file=sys.stderr)
        sys.exit(1)
    return owner, repository


def tags(repo_path=None):
    github = git_devbliss.github.GitHub()
    if repo_path:
        owner, repository = repo_path.split("/")
    else:
        owner, repository = get_repository()
    try:
        req = github.tags(owner, repository)
    except requests.exceptions.RequestException as e:
        status, body = e.args
        print("Fatal:", status, body, file=sys.stderr)
        sys.exit(1)
    else:
        print("\n".join(sorted(tag["name"] for tag in req)))


def pull_request(base_branch, maxretries):
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    try:
        with open("pull_request.md") as f:
            pull_request_description = f.read()
    except (IOError, OSError):
        pull_request_description = ""
    maxretries = 1 if maxretries < 1 else maxretries
    while maxretries:
        try:
            req = github.pull_request(owner,
                                      repository,
                                      github.get_current_branch(),
                                      base=base_branch,
                                      body=pull_request_description)
            maxretries = 0  # we got an answer so we're happy
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                status = e.response.status_code
                body = e.response.json()
                errors = [j for j in body["errors"]
                          if j.get("message")]
                # retry in case github needs a few seconds to realize the push
                retry = [i for i in errors if str(i.get("message")).startswith(
                    "No commits between")]
                if status == 422:  # no commits between base and head branch
                    if retry:
                        maxretries = maxretries - 1
                        time.sleep(1)
                        if maxretries:
                            continue
                    if errors:
                        for i in errors:
                            print("Fatal: " + str(i.get("message") or i),
                                  file=sys.stderr)
                    else:
                        print("Fatal: " + str(body), file=sys.stderr)
                        print("Either the pull request already exists or there"
                              " are no commits between the two branches.",
                              file=sys.stderr)
                    sys.exit(1)
            else:
                raise e
    print(req["html_url"])


def pulls():
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    pulls = github.pulls(owner, repository)
    if pulls:
        print()
        print("Pull Requests:")
    for i in pulls:
        print("    #{}: {} <{}>".format(
            i["number"], i["title"], i["html_url"]))
    print()


def status():
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    branches = github.branches(owner, repository)
    print()
    print("Tracking {}/{} <https://github.com/{}/{}>".format(
        owner, repository, owner, repository))
    print()
    print("Branches:")
    for i in branches:
        url = "https://github.com/{}/{}/tree/{}".format(
            owner, repository, i["name"])
        print("    {} <{}>".format(i["name"], url))
    pulls()
    issues = [i for i in github.issues(owner, repository)
              if not i["pull_request"]["diff_url"]]
    if issues:
        print()
        print("Issues:")
        for i in issues:
            print("    #{}: {} <{}>".format(
                i["number"], i["title"], i["html_url"]))
    print()


def issue(title=None):
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    try:
        title = title or input("Title: ")
        body = ""
        print("Body (^D to finish):")
        while True:
            try:
                body += input("") + "\n"
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                sys.exit(2)
        req = github.issue(owner, repository, title, body)
    except requests.exceptions.RequestException as e:
        if e.request:
            status = e.request.status_code
            body = e.request.body
        else:
            raise e
        print("Fatal:", status, body, file=sys.stderr)
        sys.exit(1)
    print()
    print("    " + req["html_url"])
    print()


def overview(owner):
    github = git_devbliss.github.GitHub()
    first = True
    for i in github.repos(owner):
        repository = i["name"]
        pulls = github.pulls(owner, repository)
        if pulls:
            if first:
                print()
                first = False
            print(repository, "<https://github.com/{}/{}>".format(
                owner, repository))
            for p in pulls:
                print("    #{number}: {title} <{html_url}>".format(**p))
            print()


def merge_button(pull_request_no):
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    pull_request = github.get_pull_request(owner, repository, pull_request_no)
    head = pull_request['head']['ref']
    response = github.merge_button(owner, repository, pull_request_no)
    if response.get('merged'):
        output = subprocess.check_output(
            "git push --delete origin {}".format(head), shell=True)
        print("Success: {}".format(response['message']))
        print(output)
    else:
        print("Failure: {}".format(response['message']))
    print()


def review(pull_request_no):
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    pull_request = github.get_pull_request(owner, repository, pull_request_no)
    base, head = pull_request['base']['sha'], pull_request['head']['sha']
    os.system("git fetch --quiet origin")
    os.system("git diff --color=auto {}...{}".format(
        base, head))


def close_pull_request(pull_request_no):
    body = {"state": "closed"}
    github = git_devbliss.github.GitHub()
    owner, repository = get_repository()
    try:
        response = github.update_pull_request(
            owner, repository, pull_request_no, body)
        if response.get('state') == 'closed':
            print("Success: {} closed.".format(response['title']))
        else:
            print("Failure: {} not closed.".format(response['title']))
    except (ValueError, KeyError):
        print("Failure: pull request not closed.")
        print(response['message'])
    print()


def github_runner(args):
    """Devbliss Github Client

Usage:
    github-devbliss pull-request [BASE_BRANCH] [MAXRETRIES]
    github-devbliss review PULLNUMBER
    github-devbliss open-pulls
    github-devbliss merge-button PULLNUMBER
    github-devbliss close-button PULLNUMBER
    github-devbliss status
    github-devbliss issue [TITLE]
    github-devbliss tags [REPOSITORY]
    github-devbliss overview ORG

Options:
    pull-request    Start a new pull request from the
                    current branch to master
    open-pulls      List open pull requests
    review          Review the pull request with the given number
    merge-button    Merge the pull request with the given number
    close-button    Close the pull request without merging
    status          List information about the repository
    issue           Quickly post a new issue
    tags            List the current repository's tags
    overview        Show outstanding pull requests for an
                    entire organisation
"""
    try:
        args = docopt(github_runner.__doc__, version=__version__, argv=args)
        if(args['pull-request']):
            pull_request(base_branch=args['BASE_BRANCH'] or 'master',
                         maxretries=int(args['MAXRETRIES'] or 3))
        elif(args['open-pulls']):
            pulls()
        elif(args['review']):
            review(args['PULLNUMBER'])
        elif(args['merge-button']):
            merge_button(args['PULLNUMBER'])
        elif(args['close-button']):
            close_pull_request(args['PULLNUMBER'])
        elif(args['tags']):
            tags(args['REPOSITORY'])
        elif(args['status']):
            status()
        elif(args['issue']):
            issue(args['TITLE'])
        elif(args['overview']):
            overview(args['ORG'])
    except requests.exceptions.RequestException as e:
        if hasattr(e, "body"):
            try:
                message = e.body['message']
            except (KeyError, ValueError):
                pass
            except TypeError:
                print(e.body, file=sys.stderr)
            else:
                print("Error: {}".format(message), file=sys.stderr)
                sys.exit(1)
        print(str(e), file=sys.stderr)
        sys.exit(1)


def main(args=None):
    github_runner(args or sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())  # pragma nocover
