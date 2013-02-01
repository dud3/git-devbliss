#!/usr/bin/env python

from __future__ import print_function

import json
import os
import httplib
import getpass
import base64
import subprocess
import sys


class GitHub (object):

    def __init__(self, token_file="~/.github_token"):
        self.token_file = os.path.abspath(os.path.expanduser(token_file))
        if not os.path.exists(self.token_file):
            token = self._interactive_login()
            with open(self.token_file, "w") as f:
                f.write(token)
        self.token = open(self.token_file).read().strip()

    def _login(self, username, password):
        body = json.dumps({"note": "git-devbliss-ng", "scopes": ["repo"]}, indent=0)
        conn = httplib.HTTPSConnection("api.github.com")
        conn.request("POST", "/authorizations", body, headers={
            "User-Agent": "git-devbliss/ng",  # TODO
            "Content-Type": "application/json", "Content-Length": str(len(body)),
            "Authorization": "basic " + base64.encodestring(
                    ":".join((username, password))).strip(), })
        resp = conn.getresponse()
        if resp.status == 401:
            raise ValueError("Bad credentials")
        return json.loads(resp.read())["token"]

    def _interactive_login(self):
        username = raw_input("GitHub username: ")
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
        if resp.status >= 300:
            raise httplib.HTTPException(resp.status, resp.reason, resp.read())
        return json.load(resp)

    def pulls(self, owner, repository):
        return self._request("GET", "/repos/"
            "{}/{}/pulls".format(owner, repository))

    def issues(self, owner, repository):
        return self._request("GET", "/repos/"
            "{}/{}/issues".format(owner, repository))

    def issue(self, owner, repository, title, body):
        return self._request("POST", "/repos/"
            "{}/{}/issues".format(owner, repository), json.dumps({
                "title": title,
                "body": body or None,
            }))

    def branches(self, owner, repository):
        return self._request("GET", "/repos/"
            "{}/{}/branches".format(owner, repository))

    def orgs(self, org):
        return self._request("GET", "/orgs/{}".format(org))

    def events(self, org):
        return self._request("GET", "/orgs/{}/events".format(org))

    def repos(self, org):
        return self._request("GET", "/orgs/{}/repos".format(org))

    def pull_request(self, owner, repository, head, base="master", title="", body=""):
        return self._request("POST", "/repos/{}/{}/pulls".format(owner, repository),
            json.dumps({"title": title or head, "body": body or "",
                "head": head, "base": base}, indent=0))

    def get_current_repo(self):
        owner, repository = subprocess.check_output("git remote -v", shell=True).split(
            "git@github.com:")[1].split(".git (")[0].split("/") or (None, None)
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


def pull_request():
    github = GitHub()
    owner, repository = get_repository()
    try:
        req = github.pull_request(owner, repository, github.get_current_branch())
    except httplib.HTTPException as e:
        status, reason, body = e.args
        if status == 422:
            for i in (j for j in json.loads(body)["errors"] if j.get("message")):
                print("Fatal: " + str(i.get("message") or i))
        else:
            print("Fatal:", status, reason)
        sys.exit(1)
    print(req["html_url"])


def status():
    github = GitHub()
    owner, repository = get_repository()
    branches = github.branches(owner, repository)
    print()
    print("Tracking {}/{} <https://github.com/{}/{}>".format(owner, repository, owner, repository))
    print()
    print("Branches:")
    for i in branches:
        url = "https://github.com/{}/{}/tree/{}".format(
            owner, repository, i["name"])
        print("    {} <{}>".format(i["name"], url))
    pulls = github.pulls(owner, repository)
    if pulls:
        print()
        print("Pull Requests:")
    for i in pulls:
        print("    {} <{}>".format(i["title"], i["html_url"]))
    issues = [i for i in github.issues(owner, repository)
        if not i["pull_request"]["diff_url"]]
    if issues:
        print()
        print("Issues:")
        for i in issues:
            print("    {} <{}>".format(i["title"], i["html_url"]))
    print()


def issue():
    github = GitHub()
    owner, repository = get_repository()
    try:
        title = raw_input("Title: ") if len(sys.argv) == 2 else sys.argv[-1]
        req = github.issue(owner, repository, title, None)
    except httplib.HTTPException as e:
        status, reason, body = e.args
        print("Fatal:", status, reason)
        sys.exit(1)
    print(req["html_url"])


def main(args):
    usage = """Devbliss Github Client

Usage:
    {} [pull-request]

Options:
    pull-request    Start a new pull request from the
                    current branch to master""".format(sys.argv[0])
    if args[:1] == ["pull-request"]:
        pull_request()
        sys.exit(0)
    if args[:1] == ["status"] and len(args) == 1:
        status()
        sys.exit(0)
    if args[:1] == ["issue"] and len(args) in (1, 2):
        issue()
        sys.exit(0)
    print(usage)
    sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
