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

    def _login(self, username, password, two_factor=None):
        body = {
            "scopes": ["repo"],
            "note": "git-devbliss-ng"
        }
        headers = {
            "User-Agent": "git-devbliss/ng",  # TODO
            "Content-Type": "application/json",
        }
        if two_factor:
            headers["X-GitHub-OTP"] = two_factor

        response = requests.post(
            'https://api.github.com/authorizations',
            auth=(username, password), headers=headers,
            data=json.dumps(body, sort_keys=True)
        )

        body = response.json()
        if response.status_code == 401:
            if 'message' in body and 'two-factor' in body['message']:
                return self._login(username, password, input(
                                   'Please input your two_factor code: '))
            raise ValueError("Bad credentials")
        elif response.status_code == 422:
            print('There is already a token with the name git-devbliss_ng.',
                  file=sys.stderr)
            print('If you are using git-devbliss on another computer, '
                  'please copy the ~/.github_token found on that machine'
                  ' to this one.', file=sys.stderr)
            print('If not, please log into your github account and delete'
                  ' the old token at https://github.com/settings/applications',
                  file=sys.stderr)
            sys.exit(1)
        elif response.status_code in (200, 201):
            return body["token"]
        else:
            print("Fatal: GitHub returned status " +
                  repr(response.status_code) + ":", file=sys.stderr)
            print(body, file=sys.stderr)
            sys.exit(1)

    def _interactive_login(self):
        try:
            username = input("GitHub username: ")
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
