import json
import os
import getpass
import subprocess
import sys
import os.path
import requests


class GitHub (object):

    interactive = False

    def __init__(self, token_file="~/.github_token"):
        self.token_file = os.path.abspath(os.path.expanduser(token_file))
        if not os.path.exists(self.token_file):
            self._interactive_login()
        with open(self.token_file) as f:
            self.token = f.read().strip()

    def _login(self, username, password):
        body = {
            "scopes": ["repo"],
            "note": "devbliss"
        }
        response = requests.post(
            'https://api.github.com/authorizations',
            auth=(username, password), headers={
                "User-Agent": "git-devbliss/ng",  # TODO
                "Content-Type": "application/json",
            },
            data=json.dumps(body, sort_keys=True)
        )

        body = response.json()
        if response.status_code == 401:
            raise ValueError("Bad credentials")
        elif response.status_code == 422:
            print('Fatal: GitHub retured your git-devbliss token '
                  'already exists.', file=sys.stderr)
            print('Login to your github account and delete the old token.',
                  file=sys.stderr)
            print('  https://github.com/settings/applications',
                  file=sys.stderr)
            sys.exit(1)
        elif response.status_code in (200, 201):
            return body["token"]
        else:
            print("Fatal: GitHub returned status " +
                  repr(response.status_code) + ":", file=sys.stderr)
            print(json.dumps(body, indent=4), file=sys.stderr)
            sys.exit(1)

    def _interactive_login(self):
        try:
            print("GitHub username: ", file=sys.stderr, end='')
            sys.stderr.flush()
            username = input("")
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
        with open(self.token_file, "w") as f:
            f.write(token)
        return token

    def _request(self, method, path, body=None, host="https://api.github.com"):
        response = requests.request(method, host + path, data=body, headers={
            "Authorization": "bearer " + self.token,
            "User-Agent": "git-devbliss/ng",  # TODO
            "Content-Type": "application/json",
        })
        response_body = response.json()
        if response.status_code == 401:
            self.token = self._interactive_login()
            return self._request(method, path, body, host)
        if response.status_code in (301, ):  # TODO: 302, 307, 308
            path = response.headers['location']
            return self._request(method, path, body, host)
        if response.status_code >= 300:
            e = requests.exceptions.RequestException(
                response.status_code, response.reason)
            e.body = response_body
            raise e
        return response_body

    def pulls(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/pulls".format(owner, repository))

    def issues(self, owner, repository):
        return self._request("GET", "/repos/"
                             "{}/{}/issues".format(owner, repository))

    def issue(self, owner, repository, title, body):
        return self._request(
            "POST", "/repos/{}/{}/issues".format(owner, repository),
            json.dumps({"title": title, "body": body or None}, sort_keys=True))

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
                        "base": base}, sort_keys=True))

    def get_pull_request(self, owner, repository, pull_request_no):
        return self._request("GET", "/repos/{}/{}/pulls/{}".format(
            owner, repository, pull_request_no))

    def merge_button(self, owner, repository, pull_request_no):
        return self._request("PUT", "/repos/{}/{}/pulls/{}/merge".format(
            owner, repository, pull_request_no), json.dumps({}))

    def update_pull_request(self, owner, repository, pull_request_no, body):
        return self._request("PATCH", "/repos/{}/{}/pulls/{}".format(
            owner, repository, pull_request_no), json.dumps(
                body, sort_keys=True))

    def get_current_repo(self):
        try:
            owner, repository = subprocess.check_output(
                "git remote -v", shell=True).decode().split(
                ":")[1].split()[0].split("/")
        except IndexError:
            raise ValueError("Could not find a valid github remote")
        return owner, repository.split(".git")[0]

    def get_current_branch(self):
        return subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD", shell=True).strip().decode()
