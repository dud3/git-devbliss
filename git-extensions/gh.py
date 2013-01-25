
from __future__ import print_function
import getpass
import os
import urllib2
import json
import base64
import subprocess

import libsaas.http
import libsaas.services.github as github


def login(filename="~/.gh-token", max_retries=3):
    path = os.path.expanduser(filename)
    if not os.path.exists(path):
        open(path, "w").close()
    try:
        token = open(path).read().strip()
        gh = github.GitHub(token)
        gh.issues().get()
        return token
    except (IOError, libsaas.http.HTTPError) as e:
        if isinstance(e, libsaas.http.HTTPError) and token:
            print("incorrect username or password")
        username = raw_input("Github.com username: ")
        password = getpass.getpass("Github.com password: ")
        body = json.dumps({"note": "git-devbliss", "scopes": ["repo"]}).encode()
        request = urllib2.Request("https://api.github.com/authorizations", data=body)
        auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic " + auth)
        try:
            fp = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print(e.code)
            if e.code == 403:
                print("Fatal: incorrent username or password.")
            raise
        with open(path, "w") as f:
            f.write(json.loads(fp.read())[u"token"])
        if max_retries:
            return login(max_retries=max_retries - 1)
        raise


def get_current_repository():
    p = subprocess.check_output("git remote -v", shell=True)
    return p.split("github.com:")[1].split(".git")[0].split("/")

def main(token):
    gh = github.GitHub(token)
    user, repo = get_current_repository()
    repo = gh.repo(user, repo)
    issues = [i for i in repo.issues().get() if i.get("pull_request")]
    if issues:
        print()
        print("Open Pull Requests:")
        print()
        for i in issues:
            print("   ", i["title"])
            print("   ", "    <" + i["url"] + ">")
            print()


if __name__ == '__main__':
    try:
        token = login()
        main(token)
    except:
        exit(1)
