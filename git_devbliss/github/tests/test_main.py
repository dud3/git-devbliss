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

import pkg_resources
import unittest
import unittest.mock
from unittest.mock import call
import requests
import sys
import subprocess


main = pkg_resources.load_entry_point(
    "git_devbliss", "console_scripts", "github-devbliss")


@unittest.mock.patch("builtins.print")
class MainTest(unittest.TestCase):

    @unittest.mock.patch("git_devbliss.github.GitHub.issues")
    @unittest.mock.patch("git_devbliss.github.GitHub.pulls")
    @unittest.mock.patch("git_devbliss.github.GitHub.branches")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_status(self, init, get_current_repo, branches, pulls, issues,
                    print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        branches.return_value = [{'name': 'master'}, {'name': 'test_branch'}]
        pulls.return_value = [
            {"number": 0, "title": "test_pull", "html_url": "test_pull_url"}
        ]
        issues.return_value = [
            {
                "number": 0,
                "title": "test_issue",
                "html_url": "test_issue_url",
                "pull_request": {"diff_url": ""}
            },
            {
                "number": 0,
                "title": "test_issue_invisible",
                "html_url": "test_issue_url",
                "pull_request": {"diff_url": "test_diff_url"}
            },
        ]
        main(['status'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        branches.assert_called_with('test_user', 'test_repo')
        pulls.assert_called_with('test_user', 'test_repo')
        issues.assert_called_with('test_user', 'test_repo')
        print_function.assert_has_calls([
            call(),
            call('Tracking test_user/test_repo'
                 ' <https://github.com/test_user/test_repo>'),
            call(),
            call('Branches:'),
            call('    master'
                 ' <https://github.com/test_user/test_repo/tree/master>'),
            call('    test_branch'
                 ' <https://github.com/test_user/test_repo/tree/test_branch>'),
            call(),
            call('Pull Requests:'),
            call('    #0: test_pull <test_pull_url>'),
            call(),
            call(),
            call('Issues:'),
            call('    #0: test_issue <test_issue_url>'),
            call()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.pulls")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_open_pulls(self, init, get_current_repo, pulls,
                        print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        pulls.return_value = [
            {"number": 0, "title": "test_pull", "html_url": "test_pull_url"}
        ]
        main(['open-pulls'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        pulls.assert_called_with('test_user', 'test_repo')
        print_function.assert_has_calls([
            call(),
            call('Pull Requests:'),
            call('    #0: test_pull <test_pull_url>'),
            call()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.pulls")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_open_pulls_value_error(self, init, get_current_repo, pulls,
                                    print_function):
        init.return_value = None
        get_current_repo.side_effect = ValueError('test_error')
        pulls.return_value = [
            {"number": 0, "title": "test_pull", "html_url": "test_pull_url"}
        ]
        with self.assertRaises(SystemExit):
            main(['open-pulls'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        print_function.assert_called_with('Fatal: test_error', file=sys.stderr)

    @unittest.mock.patch("git_devbliss.github.GitHub.pulls")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_open_pulls_subproc_error(self, init, get_current_repo, pulls,
                                      print_function):
        init.return_value = None
        get_current_repo.side_effect = subprocess.CalledProcessError(
            'test_error', cmd='test_cmd')
        pulls.return_value = [
            {"number": 0, "title": "test_pull", "html_url": "test_pull_url"}
        ]
        with self.assertRaises(SystemExit):
            main(['open-pulls'])
        init.assert_called_with()
        get_current_repo.assert_called_with()

    @unittest.mock.patch("git_devbliss.github.GitHub.issue")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_issue(self, init, get_current_repo, input_function,
                   issue, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')

        input.side_effect = [
            "test_title",
            "my description part 1",
            "my description part 2",
            EOFError,
        ]
        issue.return_value = {'html_url': 'test_issue_url'}
        main(['issue'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        issue.assert_called_with(
            'test_user', 'test_repo', 'test_title',
            'my description part 1\nmy description part 2\n')

        print_function.assert_has_calls([
            call('Body (^D to finish):'),
            call(),
            call('    test_issue_url'),
            call()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.issue")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_issue_interrupt(self, init, get_current_repo, input_function,
                             issue, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')

        input.side_effect = [
            "test_title",
            "my description part 1",
            "my description part 2",
            KeyboardInterrupt,
        ]
        issue.return_value = {'html_url': 'test_issue_url'}
        with self.assertRaises(SystemExit):
            main(['issue'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        print_function.assert_has_calls([
            call('Body (^D to finish):'),
            call(),
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.issue")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_issue_http_error(self, init, get_current_repo, input_function,
                              issue, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')

        input.side_effect = [
            "test_title",
            "my description part 1",
            "my description part 2",
            EOFError,
        ]
        issue.side_effect = requests.exceptions.RequestException(
            400, 'test_error')
        with self.assertRaises(SystemExit):
            main(['issue'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        print_function.assert_called_with(
            '[Errno 400] test_error', file=sys.stderr)

    @unittest.mock.patch("git_devbliss.github.GitHub.issue")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_issue_http_error_with_request(
            self, init, get_current_repo, input_function, issue,
            print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')

        input.side_effect = [
            "test_title",
            "my description part 1",
            "my description part 2",
            EOFError,
        ]

        response = unittest.mock.Mock()
        body = unittest.mock.Mock()
        response.json = body
        response.status_code = 400
        body.return_value = {'test_error'}
        issue.side_effect = requests.exceptions.RequestException(
            400, response=response)
        with self.assertRaises(SystemExit):
            main(['issue'])
        init.assert_called_with()
        get_current_repo.assert_called_with()

    @unittest.mock.patch("git_devbliss.github.GitHub.issue")
    @unittest.mock.patch("builtins.input")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_issue_with_name(self, init, get_current_repo, input_function,
                             issue, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        input.side_effect = [
            "my description part 1",
            "my description part 2",
            EOFError,
        ]
        issue.return_value = {'html_url': 'test_issue_url'}
        main(['issue', 'test_issue_by_parameter'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        issue.assert_called_with(
            'test_user', 'test_repo', 'test_issue_by_parameter',
            'my description part 1\nmy description part 2\n')
        print_function.assert_has_calls([
            call('Body (^D to finish):'),
            call(),
            call('    test_issue_url'),
            call()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.repos")
    @unittest.mock.patch("git_devbliss.github.GitHub.pulls")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_overview(self, init, pulls, repos,
                      print_function):
        init.return_value = None
        repos.return_value = [{'name': 'repo1'}, {'name': 'repo2'}]
        pulls.return_value = [
            {"number": 0, "title": "test_pull", "html_url": "test_pull_url"}
        ]
        main(['overview', 'test_user'])
        init.assert_called_with()
        repos.assert_called_with('test_user')
        pulls.assert_has_calls([
            call('test_user', 'repo1'),
            call('test_user', 'repo2'),
        ], any_order=True)
        print_function.assert_has_calls([
            call(),
            call('repo1', '<https://github.com/test_user/repo1>'),
            call('    #0: test_pull <test_pull_url>'),
            call(),
            call('repo2', '<https://github.com/test_user/repo2>'),
            call('    #0: test_pull <test_pull_url>'),
            call()
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.tags")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_tags(self, init, tags, get_current_repo,
                  print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        tags.return_value = [{'name': 'tag1'}, {'name': 'tag2'}]
        main(['tags'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        tags.assert_called_with('test_user', 'test_repo')
        print_function.assert_has_calls([
            call('tag1\ntag2')
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.tags")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_tags_with_repository(self, init, tags, print_function):
        init.return_value = None
        tags.return_value = [{'name': 'tag1'}, {'name': 'tag2'}]
        main(['tags', 'test_user/test_repo'])
        init.assert_called_with()
        tags.assert_called_with('test_user', 'test_repo')
        print_function.assert_has_calls([
            call('tag1\ntag2')
        ])

    @unittest.mock.patch("git_devbliss.github.GitHub.tags")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_tags_http_error(self, init, tags, print_function):
        init.return_value = None
        tags.side_effect = requests.exceptions.RequestException(
            400, 'Error',)
        with self.assertRaises(SystemExit):
            main(['tags', 'test_user/test_repo'])
        init.assert_called_with()
        tags.assert_called_with('test_user', 'test_repo')
        print_function.assert_called_with('Fatal:', 400, 'Error',
                                          file=sys.stderr)

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("git_devbliss.github.GitHub.merge_button")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_merge_button(self, init, get_current_repo,
                          get_pull_request, merge_button,
                          check_output, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.return_value = {'head': {'ref': 'test_ref'}}
        merge_button.return_value = {'merged': True, 'message': 'test_message'}
        check_output.return_value = 'test_git_output_deleted_remote_ref'

        main(['merge-button', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')
        merge_button.assert_called_with('test_user', 'test_repo', '333')
        check_output.assert_called_with("git push --delete origin test_ref",
                                        shell=True)

        print_function.assert_has_calls([
            call('Success: test_message'),
            call('test_git_output_deleted_remote_ref'),
            call()
        ])

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("git_devbliss.github.GitHub.merge_button")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_merge_button_error(self, init, get_current_repo,
                                get_pull_request, merge_button,
                                check_output, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.return_value = {'head': {'ref': 'test_ref'}}
        merge_button.return_value = {'message': 'test_message'}

        main(['merge-button', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')
        merge_button.assert_called_with('test_user', 'test_repo', '333')
        print_function.assert_has_calls([
            call('Failure: test_message'),
            call()
        ])

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("git_devbliss.github.GitHub.update_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_close_button(self, init, get_current_repo,
                          update_pull_request,
                          check_output, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        update_pull_request.return_value = {'state': 'closed',
                                            'title': 'test_title',
                                            'message': 'test_message'}
        check_output.return_value = 'test_git_output_deleted_remote_ref'

        main(['close-button', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        update_pull_request.assert_called_with('test_user', 'test_repo', '333',
                                               {'state': 'closed'})
        print_function.assert_has_calls([
            call('Success: test_title closed.'),
            call()
        ])

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("git_devbliss.github.GitHub.update_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_close_button_failure(self, init, get_current_repo,
                                  update_pull_request,
                                  check_output, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        update_pull_request.return_value = {'state': 'unknown',
                                            'title': 'test_title',
                                            'message': 'test_message'}
        check_output.return_value = 'test_git_output_deleted_remote_ref'

        main(['close-button', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        update_pull_request.assert_called_with('test_user', 'test_repo', '333',
                                               {'state': 'closed'})
        print_function.assert_has_calls([
            call('Failure: test_title not closed.'),
            call()
        ])

    @unittest.mock.patch("subprocess.check_output")
    @unittest.mock.patch("git_devbliss.github.GitHub.update_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_close_button_exception(self, init, get_current_repo,
                                    update_pull_request,
                                    check_output, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        update_pull_request.return_value = {'message': 'test_message'}
        check_output.return_value = 'test_git_output_deleted_remote_ref'

        main(['close-button', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        update_pull_request.assert_called_with('test_user', 'test_repo', '333',
                                               {'state': 'closed'})
        print_function.assert_has_calls([
            call('Failure: pull request not closed.'),
            call('test_message'),
            call()
        ])

    @unittest.mock.patch("os.system")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_review(self, init, get_current_repo,
                    get_pull_request, system,
                    print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.return_value = {'head': {'sha': 'head_sha'},
                                         'base': {'sha': 'base_sha'}}
        system.side_effect = [
            'test_git_fetch_output',
            'test_git_diff_output'
        ]

        main(['review', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')
        system.assert_has_calls([
            call("git fetch --quiet origin"),
            call("git diff --color=auto base_sha...head_sha")
        ])

    @unittest.mock.patch("os.system")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_review_http_error(self, init, get_current_repo,
                               get_pull_request, system,
                               print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.side_effect = requests.exceptions.RequestException(
            400, 'test_error'
        )
        get_pull_request.side_effect.body = 'lala'
        with self.assertRaises(SystemExit):
            main(['review', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')

    @unittest.mock.patch("os.system")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_review_http_error_with_body(self, init, get_current_repo,
                                         get_pull_request, system,
                                         print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.side_effect = requests.exceptions.RequestException(
            400, 'test_error'
        )
        get_pull_request.side_effect.body = {"message": "test_message"}
        with self.assertRaises(SystemExit):
            main(['review', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')

    @unittest.mock.patch("os.system")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_review_http_error_with_body_no_message(
            self, init, get_current_repo, get_pull_request, system,
            print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_pull_request.side_effect = requests.exceptions.RequestException(
            400, 'test_error'
        )
        get_pull_request.side_effect.body = {"nomessage": "test_message"}
        with self.assertRaises(SystemExit):
            main(['review', '333'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_pull_request.assert_called_with('test_user', 'test_repo', '333')

    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("git_devbliss.github.GitHub.pull_request")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_branch")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_pull_request(
            self, init, get_current_repo, get_current_branch,
            pull_request, sleep, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_current_branch.return_value = 'test_branch'
        pull_request.return_value = {'html_url': 'test_pull_url'}
        with unittest.mock.patch('builtins.open', unittest.mock.mock_open(
                                 read_data='test_data_from_markdown')):
            main(['pull-request', 'test-mainline-branch', '3'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_current_branch.assert_called_with()
        pull_request.assert_called_with('test_user',
                                        'test_repo',
                                        'test_branch',
                                        base='test-mainline-branch',
                                        body='test_data_from_markdown')

    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("git_devbliss.github.GitHub.pull_request")
    @unittest.mock.patch("builtins.open")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_branch")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_pull_request_error(
            self, init, get_current_repo, get_current_branch, open_function,
            pull_request, sleep, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_current_branch.return_value = 'test_branch'
        pull_request.side_effect = [
            requests.exceptions.RequestException(400),
            {'html_url': 'test_pull_url'}
        ]
        open_function.side_effect = IOError()
        with self.assertRaises(SystemExit):
            main(['pull-request', 'test-mainline-branch', '3'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_current_branch.assert_called_with()
        open_function.assert_called_with('pull_request.md')
        pull_request.assert_called_with('test_user',
                                        'test_repo',
                                        'test_branch',
                                        base='test-mainline-branch',
                                        body='')

    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("git_devbliss.github.GitHub.pull_request")
    @unittest.mock.patch("builtins.open")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_branch")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_pull_request_repeat_error(
            self, init, get_current_repo, get_current_branch, open_function,
            pull_request, sleep, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_current_branch.return_value = 'test_branch'
        response = unittest.mock.Mock()
        body = unittest.mock.Mock()
        response.json = body
        response.status_code = 422
        body.return_value = {"errors": [{"message": "No commits between"}]}
        pull_request.side_effect = [
            requests.exceptions.RequestException(
                422, response=response),
            {'html_url': 'test_pull_url'}
        ]
        open_function.side_effect = IOError()
        main(['pull-request', 'test-mainline-branch', '3'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_current_branch.assert_called_with()
        open_function.assert_called_with('pull_request.md')
        pull_request.assert_called_with('test_user',
                                        'test_repo',
                                        'test_branch',
                                        base='test-mainline-branch',
                                        body='')

    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("git_devbliss.github.GitHub.pull_request")
    @unittest.mock.patch("builtins.open")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_branch")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_pull_request_repeat_error_out_of_tries(
            self, init, get_current_repo, get_current_branch, open_function,
            pull_request, sleep, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_current_branch.return_value = 'test_branch'
        response = unittest.mock.Mock()
        body = unittest.mock.Mock()
        response.json = body
        response.status_code = 422
        body.return_value = {"errors": [{"message": "No commits between"}]}
        pull_request.side_effect = [
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
        ]
        open_function.side_effect = IOError()
        with self.assertRaises(SystemExit):
            main(['pull-request', 'test-mainline-branch', '3'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_current_branch.assert_called_with()
        open_function.assert_called_with('pull_request.md')
        pull_request.assert_called_with('test_user',
                                        'test_repo',
                                        'test_branch',
                                        base='test-mainline-branch',
                                        body='')

    @unittest.mock.patch("time.sleep")
    @unittest.mock.patch("git_devbliss.github.GitHub.pull_request")
    @unittest.mock.patch("builtins.open")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_branch")
    @unittest.mock.patch("git_devbliss.github.GitHub.get_current_repo")
    @unittest.mock.patch("git_devbliss.github.GitHub.__init__")
    def test_pull_request_repeat_error_out_of_tries_no_errors(
            self, init, get_current_repo, get_current_branch, open_function,
            pull_request, sleep, print_function):
        init.return_value = None
        get_current_repo.return_value = ('test_user', 'test_repo')
        get_current_branch.return_value = 'test_branch'
        response = unittest.mock.Mock()
        body = unittest.mock.Mock()
        response.json = body
        response.status_code = 422
        body.return_value = {"errors": []}
        pull_request.side_effect = [
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
            requests.exceptions.RequestException(
                422, response=response),
        ]
        open_function.side_effect = IOError()
        with self.assertRaises(SystemExit):
            main(['pull-request', 'test-mainline-branch', '3'])
        init.assert_called_with()
        get_current_repo.assert_called_with()
        get_current_branch.assert_called_with()
        open_function.assert_called_with('pull_request.md')
        pull_request.assert_called_with('test_user',
                                        'test_repo',
                                        'test_branch',
                                        base='test-mainline-branch',
                                        body='')
