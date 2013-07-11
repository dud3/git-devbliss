#!/usr/bin/env python2.7

from __future__ import print_function

import json
import os
import time
import httplib
import getpass
import base64
import subprocess
import sys


class GitHub (object):

    interactive = False

    def __init__(self, token_file="~/.github_token"):
        self.token_file = os.path.abspath(os.path.expanduser(token_file))
        if not os.path.exists(self.token_file):
            token = self._interactive_login()
            with open(self.token_file, "w") as f:
                f.write(token)
        self.token = open(self.token_file).read().strip()

    def _login(self, username, password):
        body = json.dumps(
            {"note": "git-devbliss-ng", "scopes": ["repo"]}, indent=0)
        conn = httplib.HTTPSConnection("api.github.com")
        conn.request("POST", "/authorizations", body, headers={
            "User-Agent": "git-devbliss/ng",  # TODO
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "Authorization": "basic " + base64.encodestring(
                ":".join((username, password))).strip(), })
        resp = conn.getresponse()
        if resp.status == 401:
            raise ValueError("Bad credentials")
        return json.loads(resp.read())["token"]

    def _interactive_login(self):
        try:
            print("GitHub username: ", file=sys.stderr, end='')
            sys.stderr.flush()
            username = raw_input("")
        except KeyboardInterrupt:
            print()
            sys.exit(1)
        password = getpass.getpass("GitHub password: ")
        try:
            token = self._login(username, password)
            if not token.strip():
                raise ValueError("Bad credentials")
        except ValueError as e:
            print("Fatal: " + str(e), file=sys.stderr)
            sys.exit(2)
        return token

    def _request(self, method, path, body=None, host="api.github.com"):
        conn = httplib.HTTPSConnection(host)
        conn.request(method, path, body, headers={
            "Authorization": "bearer " + self.token,
            "User-Agent": "git-devbliss/ng",  # TODO
        })
        resp = conn.getresponse()
        if resp.status == 401 and self.interactive:
            try:
                self.token = self._interactive_login()
                with open(self.token_file, "w") as f:
                    f.write(self.token)
                return self._request(method, path, body, host)
            except (IOError, OSError) as e:
                print(str(e), file=sys.stderr)
                sys.exit(1)
        if resp.status in (301, ):  # TODO: 302, 307, 308
            path = resp.getheader(
                "Location", None) or resp.getheader("location")
            return self._request(method, path, body, host)
        if resp.status >= 300:
            e =  httplib.HTTPException(resp.status, resp.reason)
            e.body = resp.read()
            raise e
        return json.load(resp)

    def pulls(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/pulls".format(owner, repository))

    def issues(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/issues".format(owner, repository))

    def issue(self, owner, repository, title, body):
        return self._request("POST", "/repos/"
                             "{}/{}/issues".format(owner, repository),
                             json.dumps(
                                 {"title": title,
                                  "body": body or None,
                                  }))

    def branches(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/branches".format(owner, repository))

    def tags(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/tags".format(owner, repository))

    def orgs(self, org):
        return self._request("GET", "/orgs/{}".format(org))

    def events(self, org):
        return self._request("GET", "/orgs/{}/events".format(org))

    def repos(self, org):
        return self._request("GET", "/orgs/{}/repos?per_page=500".format(org))

    def pull_request(self, owner, repository, head, base="master",
                     title="", body=""):
        return self._request("POST", "/repos/{}/{}/pulls".format(
            owner, repository),
            json.dumps({"title": title or head,
                        "body": body or "",
                        "head": head,
                        "base": base},
                       indent=0))

    def get_pull_request(self, owner, repository, pull_request_no):
        return self._request("GET", "/repos/{}/{}/pulls/{}".format(
            owner, repository, pull_request_no))

    def merge_button(self, owner, repository, pull_request_no):
        return self._request("PUT", "/repos/{}/{}/pulls/{}/merge".format(
            owner, repository, pull_request_no),
            json.dumps({}))

    def update_pull_request(self, owner, repository, pull_request_no, body):
        return self._request("PATCH", "/repos/{}/{}/pulls/{}".format(
            owner, repository, pull_request_no),
            json.dumps(body))

    def get_current_repo(self):
        owner, repository = subprocess.check_output(
            "git remote -v", shell=True).split("git@github.com:")[1].split(
                ".git (")[0].split("/") or (None, None)
        if owner is None:
            raise ValueError("Not a git repository")
        return owner, repository

    def get_current_branch(self):
        return subprocess.check_output("git rev-parse "
                                       "--abbrev-ref HEAD", shell=True).strip()


def get_repository():
    github = GitHub()
    try:
        owner, repository = github.get_current_repo()
    except subprocess.CalledProcessError as e:
        sys.exit(1)
    except ValueError:
        print("Fatal: " + str(e), file=sys.stderr)
        sys.exit(1)
    return owner, repository


def tags():
    github = GitHub()
    if len(sys.argv) == 3:
        owner, repository = sys.argv[-1].split("/")
    else:
        owner, repository = get_repository()
    try:
        req = github.tags(owner, repository)
    except httplib.HTTPException as e:
        status, reason, body = e.args
        print("Fatal:", status, reason, file=sys.stderr)
        sys.exit(1)
    print("\n".join(sorted(tag["name"] for tag in req)))
    sys.exit(0)


def pull_request():
    github = GitHub()
    owner, repository = get_repository()
    maxretrys = 3 if len(sys.argv) < 3 else int(sys.argv[-1])
    while maxretrys:
        try:
            req = github.pull_request(
                owner, repository, github.get_current_branch())
            maxretrys = 0 # we got an answer so we're happy
        except httplib.HTTPException as e:
            if len(e.args) == 3:
                status, reason, body = e.args
                errors = [j for j in json.loads(body)["errors"]
                          if j.get("message")]
                # retry in case github needs a few seconds to realize the push
                retry = [i for i in errors if str(i.get("message")).startswith(
                    "No commits between")]
            else:
                status, reason = e.args
                errors = []
                retry = 0  # int because it's an int in the if case too
            if status == 422:  # means no commits between base and head branch
                if retry:
                    maxretrys = maxretrys - 1
                    time.sleep(1)
                    if maxretrys:
                        continue
                if errors:
                    for i in errors:
                        print("Fatal: " + str(i.get("message") or i),
                              file=sys.stderr)
                else:
                    print("Fatal: " + str(reason), file=sys.stderr)
                    print("Either the pull request already exists or there are"
                          " no commits between the two branches.", file=sys.stderr)
                sys.exit(1)
            else:
                raise e
    print(req["html_url"])

def pulls():
    github = GitHub()
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
    github = GitHub()
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


def issue():
    github = GitHub()
    owner, repository = get_repository()
    try:
        title = raw_input("Title: ") if len(sys.argv) == 2 else sys.argv[-1]
        body = ""
        print("Body (^D to finish):")
        while True:
            try:
                body += raw_input("") + "\n"
            except EOFError:
                break
            except KeyboardInterrupt():
                print()
                sys.exit(2)
        req = github.issue(owner, repository, title, body)
    except httplib.HTTPException as e:
        status, reason, body = e.args
        print("Fatal:", status, reason, file=sys.stderr)
        sys.exit(1)
    print()
    print("    " + req["html_url"])
    print()


def overview():
    github = GitHub()
    owner = sys.argv[-1]
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
    github = GitHub()
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
    github = GitHub()
    owner, repository = get_repository()
    pull_request = github.get_pull_request(owner, repository, pull_request_no)
    base, head = pull_request['base']['ref'], pull_request['head']['ref']
    os.system("git diff --color=auto origin/{} origin/{}".format(
        base, head), shell=True)

def close_pull_request(pull_request_no):
    body = {"state": "closed"}
    github = GitHub()
    owner, repository = get_repository()
    response = github.update_pull_request(
        owner, repository, pull_request_no, body)
    if response.get('state') == 'closed':
        print("Success: {}".format(response['message']))
    else:
        print("Failure: {}".format(response['message']))
    print()

def main(args):
    GitHub.interactive = True
    usage = """Devbliss Github Client

Usage:
    {name} pull-request [MAXRETRYS]
    {name} review PULLNUMBER
    {name} open-pulls
    {name} merge-button PULLNUMBER
    {name} close-button PULLNUMBER
    {name} status
    {name} issue [TITLE]
    {name} tags [REPOSITORY]
    {name} overview ORG

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
                    entire organisation""".format(name=sys.argv[0])

    try:
        if args[:1] == ["pull-request"] and len(args) in (1, 2):
            pull_request()
            sys.exit(0)
        if args[:1] == ["open-pulls"] and len(args) == 1:
            pulls()
            sys.exit(0)
        if args[:1] == ["review"] and len(args) == 2:
            review(args[1])
            sys.exit(0)
        if args[:1] == ["merge-button"] and len(args) == 2:
            merge_button(args[1])
            sys.exit(0)
        if args[:1] == ["close-button"] and len(args) == 2:
            close_pull_request(args[1])
            sys.exit(0)
        if args[:1] == ["tags"] and len(args) == 1:
            tags()
            sys.exit(0)
        if args[:1] == ["tags"] and len(args) == 2 and "/" in args[-1]:
            tags()
            sys.exit(0)
        if args[:1] == ["status"] and len(args) == 1:
            status()
            sys.exit(0)
        if args[:1] == ["issue"] and len(args) in (1, 2):
            issue()
            sys.exit(0)
        if args[:1] == ["overview"] and len(args) == 2:
            overview()
            sys.exit(0)
        print(usage, file=sys.stderr)
        sys.exit(2)
    except httplib.HTTPException as e:
        if hasattr(e, "body"):
            try:
                message = json.loads(e.body)['message']
            except (KeyError, ValueError):
                pass
            else:
                print("Error: {}".format(message), file=sys.stderr)
                sys.exit(1)
        print(str(e))
        sys.exit(1)




if __name__ == '__main__':
    main(sys.argv[1:])

