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

import unittest
import unittest.mock
import git_devbliss.github
import sys
from unittest.mock import call
import requests


class GitHubTest(unittest.TestCase):

    @unittest.mock.patch("os.path.exists")
    def test_init_with_file(self, exists):
        exists.return_value = True
        with unittest.mock.patch(
                'builtins.open', unittest.mock.mock_open(
                    read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')
        exists.assert_called_with(gh.token_file)

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_interrupt(self, exists, input_function, getpass,
                            print_function):
        exists.return_value = False
        input_function.side_effect = KeyboardInterrupt()
        with self.assertRaises(SystemExit):
            git_devbliss.github.GitHub()

        print_function.assert_called_with()
        input_function.assert_has_calls([
            call('GitHub username: '),
        ])

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_401(self, exists, input_function, getpass, post,
                      print_function):
        exists.return_value = False
        input_function.return_value = 'test_username'
        getpass.return_value = 'test_pass'
        json_function = unittest.mock.Mock()
        json_function.return_value = '{"test_json": "blub"}'
        post.return_value = unittest.mock.Mock()
        post.return_value.json = json_function
        post.return_value.status_code = 401
        m = unittest.mock.mock_open()
        with unittest.mock.patch('__main__.open', m, create=True):
            with self.assertRaises(SystemExit):
                git_devbliss.github.GitHub()
        post.assert_has_calls([
            call('https://api.github.com/authorizations',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass'),
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}'),
            call().json()
        ])

        input_function.assert_has_calls([
            call('GitHub username: '),
        ])
        print_function.assert_called_with('Fatal: Bad credentials',
                                          file=sys.stderr)

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_422(self, exists, input_function, getpass, post,
                      print_function):
        exists.return_value = False
        input_function.return_value = 'test_username'
        getpass.return_value = 'test_pass'
        json_function = unittest.mock.Mock()
        json_function.return_value = '{"test_json": "blub"}'
        post.return_value = unittest.mock.Mock()
        post.return_value.json = json_function
        post.return_value.status_code = 422
        m = unittest.mock.mock_open()
        with unittest.mock.patch('__main__.open', m, create=True):
            with self.assertRaises(SystemExit):
                git_devbliss.github.GitHub()
        post.assert_has_calls([
            call('https://api.github.com/authorizations',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass'),
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}'),
            call().json()
        ])
        input_function.assert_has_calls([
            call('GitHub username: '),
        ])

        print_function.assert_has_calls([
            call('There is already a token with the name git-devbliss_ng.',
                 file=sys.stderr),
            call('If you are using git-devbliss on another computer, please '
                 'copy the ~/.github_token found on that machine to this one.',
                 file=sys.stderr),
            call('If not, please log into your github account and delete the'
                 ' old token at https://github.com/settings/applications',
                 file=sys.stderr)
        ])

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_404(self, exists, input_function, getpass, post,
                      print_function):
        exists.return_value = False
        input_function.return_value = 'test_username'
        getpass.return_value = 'test_pass'
        json_function = unittest.mock.Mock()
        json_function.return_value = '{"test_json": "blub"}'
        post.return_value = unittest.mock.Mock()
        post.return_value.json = json_function
        post.return_value.status_code = 404
        m = unittest.mock.mock_open()
        with unittest.mock.patch('__main__.open', m, create=True):
            with self.assertRaises(SystemExit):
                git_devbliss.github.GitHub()

        post.assert_has_calls([
            call('https://api.github.com/authorizations',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass'),
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}'),
            call().json()
        ])
        input_function.assert_has_calls([
            call('GitHub username: '),
        ])
        print_function.assert_has_calls([
            call('Fatal: GitHub returned status 404:', file=sys.stderr),
            call('{"test_json": "blub"}', file=sys.stderr)
        ])

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_no_token(self, exists, input_function, getpass, post,
                           print_function):
        exists.return_value = False
        input_function.return_value = 'test_username'
        getpass.return_value = 'test_pass'
        json_function = unittest.mock.Mock()
        json_function.return_value = {"token": ""}
        post.return_value = unittest.mock.Mock()
        post.return_value.json = json_function
        post.return_value.status_code = 200
        m = unittest.mock.mock_open()
        with unittest.mock.patch('__main__.open', m, create=True):
            with self.assertRaises(SystemExit):
                git_devbliss.github.GitHub()

        post.assert_has_calls([
            call('https://api.github.com/authorizations',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass'),
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}'),
            call().json()
        ])
        input_function.assert_has_calls([
            call('GitHub username: '),
        ])
        print_function.assert_has_calls([
            call('Fatal: Bad credentials', file=sys.stderr)
        ])

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init(self, exists, input_function, getpass, post,
                  print_function):
        exists.return_value = False
        input_function.return_value = 'test_username'
        getpass.return_value = 'test_pass'
        json_function = unittest.mock.Mock()
        json_function.return_value = {"token": "test_token"}
        post.return_value = unittest.mock.Mock()
        post.return_value.json = json_function
        post.return_value.status_code = 200
        m = unittest.mock.mock_open(read_data='test_token')
        with unittest.mock.patch('builtins.open', m, create=True):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')
            exists.assert_called_with(gh.token_file)
            m.assert_has_calls([
                call(gh.token_file, 'w'),
                call().__enter__(),
                call().write('test_token'),
                call().__exit__(None, None, None),
                call(gh.token_file),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ])
        handle = m()
        handle.write.assert_called_once_with('test_token')

        post.assert_has_calls([

            call('https://api.github.com/authorizations',
                 headers={'Content-Type': 'application/json',
                          'User-Agent': 'git-devbliss/ng'},
                 auth=('test_username', 'test_pass'),
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}'),
            call().json()
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch("builtins.print")
    @unittest.mock.patch("requests.post")
    @unittest.mock.patch("getpass.getpass")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("os.path.exists")
    def test_init_two_factor(self, exists, input_function, getpass, post,
                             print_function):
        exists.return_value = False
        input_function.side_effect = ['test_username', 'two_factor_code']
        getpass.return_value = 'test_pass'
        json_function1 = unittest.mock.Mock()
        json_function2 = unittest.mock.Mock()
        json_function1.return_value = {
            "documentation_url": "https://developer.github.com/v3/auth"
            "#working-with-two-factor-authentication",
            "message": "Must specify two-factor authentication OTP code."}
        json_function2.return_value = {'token': 'test_token'}
        post1 = unittest.mock.Mock()
        post2 = unittest.mock.Mock()
        post.side_effect = [post1, post2]
        post1.json = json_function1
        post2.json = json_function2
        post1.status_code = 401
        post2.status_code = 201
        m = unittest.mock.mock_open(read_data='test_token')
        with unittest.mock.patch('builtins.open', m, create=True):
            gh = git_devbliss.github.GitHub()
            m.assert_has_calls([
                call(gh.token_file, 'w'),
                call().__enter__(),
                call().write('test_token'),
                call().__exit__(None, None, None),
                call(gh.token_file),
                call().__enter__(),
                call().read(),
                call().__exit__(None, None, None)
            ])
        handle = m()
        handle.write.assert_called_once_with('test_token')

        post.assert_has_calls([
            call('https://api.github.com/authorizations',
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass')),
            call('https://api.github.com/authorizations',
                 data='{"note": "git-devbliss-ng", "scopes": ["repo"]}',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'X-GitHub-OTP': 'two_factor_code',
                          'Content-Type': 'application/json'},
                 auth=('test_username', 'test_pass'))
        ])
        input_function.assert_has_calls([
            call('GitHub username: '),
            call('Please input your two_factor code: ')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch("requests.request")
    @unittest.mock.patch("os.path.exists")
    def test_request_400(self, exists, request):
        exists.return_value = True
        request.return_value = unittest.mock.Mock()
        request.return_value.status_code = 400
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')
            with self.assertRaises(requests.exceptions.RequestException):
                gh._request('test_method', 'test_path',
                            'test_body', 'test_host')
        exists.assert_called_with(gh.token_file)
        request.assert_has_calls([
            call('test_method', 'test_hosttest_path',
                 headers={'User-Agent': 'git-devbliss/ng',
                          'Content-Type': 'application/json',
                          'Authorization': 'bearer test_token'},
                 data='test_body'),
            call().json()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub._interactive_login")
    @unittest.mock.patch("requests.request")
    @unittest.mock.patch("os.path.exists")
    def test_request_401(self, exists, request, login):
        exists.return_value = True
        mock_401 = unittest.mock.Mock()
        mock_401.status_code = 401

        mock_200 = unittest.mock.Mock()
        mock_200.status_code = 200
        request.side_effect = [mock_401, mock_200]
        login.return_value = 'test_token'
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')
            gh._request('test_method', 'test_path',
                        'test_body', 'test_host')

        request.assert_has_calls([
            call('test_method', 'test_hosttest_path',
                 headers={'Content-Type': 'application/json',
                          'User-Agent': 'git-devbliss/ng',
                          'Authorization': 'bearer test_token'},
                 data='test_body'),
            call('test_method', 'test_hosttest_path',
                 headers={'Content-Type': 'application/json',
                          'User-Agent': 'git-devbliss/ng',
                          'Authorization': 'bearer test_token'},
                 data='test_body'),
        ])
        exists.assert_called_with(gh.token_file)

    @unittest.mock.patch("requests.request")
    @unittest.mock.patch("os.path.exists")
    def test_request_301(self, exists, request):
        exists.return_value = True
        mock_301 = unittest.mock.Mock()
        mock_301.status_code = 301
        mock_301.headers = {'location': 'test_location'}

        mock_200 = unittest.mock.Mock()
        mock_200.status_code = 200

        request.side_effect = [mock_301, mock_200]
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')
            gh._request('test_method', 'test_path',
                        'test_body', 'test_host')
        request.assert_has_calls([
            call('test_method', 'test_hosttest_path', headers={
                'Content-Type': 'application/json',
                'Authorization': 'bearer test_token',
                'User-Agent': 'git-devbliss/ng'},
                data='test_body'),
            call('test_method', 'test_hosttest_location', headers={
                'Content-Type': 'application/json',
                'Authorization': 'bearer test_token',
                'User-Agent': 'git-devbliss/ng'},
                data='test_body'),
        ])
        exists.assert_called_with(gh.token_file)

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_pulls(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.pulls('test_user', 'test_repo')
            request.assert_called_once_with(
                'GET', '/repos/test_user/test_repo/pulls')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_issues(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.issues('test_user', 'test_repo')
            request.assert_called_once_with(
                'GET', '/repos/test_user/test_repo/issues')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_issue(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.issue('test_user', 'test_repo', 'test_title', 'test_body')
            request.assert_called_once_with(
                'POST', '/repos/test_user/test_repo/issues',
                '{"body": "test_body", "title": "test_title"}')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_branches(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.branches('test_user', 'test_repo')
            request.assert_called_once_with(
                'GET', '/repos/test_user/test_repo/branches')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_tags(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.tags('test_user', 'test_repo')
            request.assert_called_once_with(
                'GET', '/repos/test_user/test_repo/tags')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_orgs(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.orgs('test_org')
            request.assert_called_once_with(
                'GET', '/orgs/test_org')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_events(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.events('test_org')
            request.assert_called_once_with(
                'GET', '/orgs/test_org/events')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_repos(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.repos('test_org')
            request.assert_called_once_with(
                'GET', '/orgs/test_org/repos?per_page=500')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_pull_request(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.pull_request('test_user', 'test_repo', 'test_head',
                            'test_base', 'test_title', 'test_body')
            request.assert_called_once_with(
                'POST', '/repos/test_user/test_repo/pulls',
                '{"base": "test_base", "body": "test_body", '
                '"head": "test_head", "title": "test_title"}')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_get_pull_request(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.get_pull_request('test_user', 'test_repo', 333)
            request.assert_called_once_with(
                'GET', '/repos/test_user/test_repo/pulls/333')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_merge_button(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.merge_button('test_user', 'test_repo', 333)
            request.assert_called_once_with(
                'PUT', '/repos/test_user/test_repo/pulls/333/merge', '{}')

    @unittest.mock.patch("git_devbliss.github.GitHub._request")
    @unittest.mock.patch("os.path.exists")
    def test_update_pull_request(self, exists, request):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.update_pull_request('test_user', 'test_repo', 333, 'test_body')
            request.assert_called_once_with(
                'PATCH', '/repos/test_user/test_repo/pulls/333', '"test_body"')

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("os.path.exists")
    def test_get_current_repo(self, exists, check_output):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            check_output.return_value = b'git@github.com:test_user/test_repo'
            gh.get_current_repo()
            check_output.assert_called_once_with(
                'git remote -v', shell=True)

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("os.path.exists")
    def test_get_current_branch(self, exists, check_output):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            gh.get_current_branch()
            check_output.assert_called_once_with(
                'git rev-parse --abbrev-ref HEAD', shell=True)

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("os.path.exists")
    def test_get_current_repo_error(self, exists, check_output):
        exists.return_value = True
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_token')):
            gh = git_devbliss.github.GitHub()
            self.assertEqual(gh.token, 'test_token')

            check_output.return_value = b''
            with self.assertRaises(ValueError):
                gh.get_current_repo()
            check_output.assert_called_once_with(
                'git remote -v', shell=True)
