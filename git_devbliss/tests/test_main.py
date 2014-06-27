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
import subprocess
import sys
import git_devbliss

git_devbliss_main = pkg_resources.load_entry_point(
    "git_devbliss", "console_scripts", "git-devbliss")


@unittest.mock.patch("builtins.print")
class MainTest(unittest.TestCase):

    @unittest.mock.patch('os.system')
    def test_git(self, system, print_function):
        git_devbliss.__main__.git('test cmd')
        system.assert_has_calls([
            call('git test cmd')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('subprocess.check_output')
    def test_git_pipe(self, check_output, print_function):
        git_devbliss.__main__.git('test cmd', pipe=True)
        check_output.assert_has_calls([
            call('git test cmd', shell=True),
            call().decode()
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_main(self, git, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('os.path.abspath')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_toplevel_failure(self, git, abspath, print_function):
        git.return_value = '/User/test_user/test_repo'
        abspath.side_effect = [
            '/User/test_user/test_repo',
            '/User/test_user/test_repo/subpath'
        ]
        with self.assertRaises(SystemExit):
            git_devbliss.__main__.check_repo_toplevel()
        git.assert_has_calls([
            call('rev-parse --show-toplevel', pipe=True),
        ])
        print_function.assert_has_calls([
            call('You need to run this command from the toplevel'
                 ' of the working tree.', file=sys.stderr)
        ])

    @unittest.mock.patch('os.path.abspath')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_toplevel(self, git, abspath, print_function):
        git.return_value = '/User/test_user/test_repo'
        abspath.side_effect = [
            '/User/test_user/test_repo',
            '/User/test_user/test_repo'
        ]
        git_devbliss.__main__.check_repo_toplevel()
        git.assert_has_calls([
            call('rev-parse --show-toplevel', pipe=True),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('os.system')
    @unittest.mock.patch('os.path.isfile')
    @unittest.mock.patch('git_devbliss.__main__.git')
    @unittest.mock.patch('git_devbliss.__main__.is_repository_clean')
    @unittest.mock.patch('git_devbliss.__main__.check_repo_toplevel')
    def test_hook_no_makefile(self, toplevel, repo_clean, git, isfile,
                              system_function, print_function):
        toplevel.return_value = True
        isfile.return_value = False
        repo_clean.return_value = False
        git_devbliss.__main__.call_hook('test_hook', 'test_env')
        print_function.assert_has_calls([
            call('Warning: No Makefile found. All make hooks have'
                 ' been skipped.', file=sys.stderr)
        ])

    @unittest.mock.patch('os.system')
    @unittest.mock.patch('os.path.isfile')
    @unittest.mock.patch('git_devbliss.__main__.git')
    @unittest.mock.patch('git_devbliss.__main__.is_repository_clean')
    @unittest.mock.patch('git_devbliss.__main__.check_repo_toplevel')
    def test_hook_unclean(self, toplevel, repo_clean, git, isfile,
                          system_function, print_function):
        toplevel.return_value = True
        isfile.return_value = True
        repo_clean.return_value = False
        git_devbliss.__main__.call_hook('test_hook', 'test_env')
        git.assert_has_calls([
            call('commit --quiet -am "Ran git devbliss test_hook hook"')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('os.system')
    @unittest.mock.patch('os.path.isfile')
    @unittest.mock.patch('git_devbliss.__main__.git')
    @unittest.mock.patch('git_devbliss.__main__.is_repository_clean')
    @unittest.mock.patch('git_devbliss.__main__.check_repo_toplevel')
    def test_hook_clean(self, toplevel, repo_clean, git, isfile,
                        system_function, print_function):
        toplevel.return_value = True
        isfile.return_value = True
        repo_clean.return_value = True
        git_devbliss.__main__.call_hook('test_hook', 'test_env')
        self.assertEqual(git.call_count, 0)
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_main_error(self, git, print_function):
        git.side_effect = subprocess.CalledProcessError('3', 'git')
        with self.assertRaises(SystemExit):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
        ])
        print_function.assert_has_calls([
            call('Fatal: origin does not point to a github.com repository',
                 file=sys.stderr)
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_feature(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'feature', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b feature/test'),
            call('push --set-upstream origin feature/test')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_feature_branch_exists(self, git, print_function):
        git.side_effect = [
            '',
            '',
            '',
            '',
            subprocess.CalledProcessError(2, 'git'),
            '',
            '',
        ]
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'feature', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b feature/test'),
            call('checkout --quiet feature/test'),
            call('push --set-upstream origin feature/test')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_feature_finish(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'feature', 'finish']):
            git_devbliss_main()

        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b feature/finish'),
            call('push --set-upstream origin feature/finish')
        ])
        print_function.assert_has_calls([
            call('You are creating a branch "feature/finish".'
                 ' Did you mean to type "git devbliss finish"?'),
            call('You can delete this branch with "git devbliss'
                 ' delete feature/finish"')
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_bug(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'bug', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b bug/test'),
            call('push --set-upstream origin bug/test')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_research(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'research', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b research/test'),
            call('push --set-upstream origin research/test')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_refactor(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'refactor', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('checkout --quiet master'),
            call('pull --quiet origin master'),
            call('checkout --quiet -b refactor/test'),
            call('push --set-upstream origin refactor/test')
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_hotfix_tag_not_found(self, git, print_function):
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'hotfix', 'test_rev', 'test']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('tag', pipe=True),
        ])
        print_function.assert_has_calls([
            call('Tag not found: test_rev', file=sys.stderr),
            call('Available tags:')
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_hotfix(self, git, print_function):
        git.side_effect = [
            '',
            '',
            'master\ntest_rev\nanother_rev',
            '',
            '',
            '',
            '',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'hotfix', 'test_rev', 'test']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('tag', pipe=True),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_finish_not_merged(self, git, print_function):
        git.side_effect = [
            '',
            '',
            'some_branch',
            '0',
            '',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'finish', 'annegret']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('branch --contains annegret', pipe=True)
        ])
        print_function.assert_has_calls([
            call("Error: Won't finish. annegret is not merged into the"
                 " current branch.", file=sys.stderr),
            call("Please do 'git merge annegret', make sure all conflicts"
                 " are merged and try again.", file=sys.stderr)
        ])

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.call_hook')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_finish(self, git, call_hook, github, print_function):
        git.side_effect = [
            '',
            '',
            'feature/some_branch',
            '0',
            'feature/some_branch',
            ''
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'finish', 'annegret']):
            git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('branch --contains annegret', pipe=True)
        ])
        call_hook.assert_has_calls([
            call('finish', 'DEVBLISS_BRANCH_TYPE=feature'),
            call('changelog', 'DEVBLISS_BRANCH_TYPE=feature'),
            call('version', 'DEVBLISS_BRANCH_TYPE=feature')
        ])
        github.assert_has_calls([
            call(['pull-request', 'annegret']),
            call(['open-pulls'])
        ])
        print_function.assert_has_calls([
            call(),
            call()
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_finish_unclean(self, git, print_function):
        git.side_effect = [
            '',
            '',
            'some_branch',
            '4',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'finish', 'annegret']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
        ])
        print_function.assert_has_calls([
            call('Error: Repository is not clean. Aborting.', file=sys.stderr)
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_release_invalid_version(self, git, print_function):
        git.side_effect = [
            '',
            '',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'release', 'annegret']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
        ])
        print_function.assert_has_calls([
            call('Invalid version number', file=sys.stderr)
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_release_unclean(self, git, print_function):
        git.side_effect = [
            '',
            '',
            '',
            'some_branch',
            '4',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'release', '1.0.0']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch --quiet origin'),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True)
        ])
        print_function.assert_has_calls([
            call('Error: Repository is not clean. Aborting.', file=sys.stderr)
        ])

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_release_unmerged(self, git, print_function):
        git.side_effect = [
            '',
            '',
            '',
            'some_branch',
            '0',
            'sha-1',
            'sha-2'
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'release', '1.0.0']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch --quiet origin'),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('rev-parse HEAD', pipe=True),
            call('rev-parse origin/master', pipe=True)
        ])
        print_function.assert_has_calls([
            call('Error: Local branch is not in sync with origin. Aborting.',
                 file=sys.stderr),
            call('Do "git pull && git push" and try agin.', file=sys.stderr)
        ])

    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.call_hook')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_release_cancel(self, git, call_hook, input_function,
                            print_function):
        git.side_effect = [
            '',
            '',
            '',
            'some_branch',
            '0',
            'sha-1',
            'sha-1',
            ''
        ]
        input_function.side_effect = KeyboardInterrupt()
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'release', '1.0.0']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch --quiet origin'),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('rev-parse HEAD', pipe=True),
            call('rev-parse origin/master', pipe=True),
            call('diff')
        ])
        call_hook.assert_has_calls([
            call('release', 'DEVBLISS_VERSION="1.0.0"')
        ])
        print_function.assert_has_calls([
            call('Have these changes been reviewed?'),
            call('[enter / ctrl+c to cancel]')
        ])

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.call_hook')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_release(self, git, call_hook, input_function,
                     github_devbliss, print_function):
        git.side_effect = [
            '',
            '',
            '',
            'master',
            '0',
            'sha-1',
            'sha-1',
            '',
            '',
            '',
            '',
            '',
            ''
        ]
        input_function.return_value = ''
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'release', '1.0.0']):
            git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch --quiet origin'),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('rev-parse HEAD', pipe=True),
            call('rev-parse origin/master', pipe=True),
            call('diff'),
            call('commit --quiet --allow-empty -m "Release: 1.0.0"'),
            call('push origin master'),
            call('tag 1.0.0'),
            call('push --tags origin'),
        ])
        call_hook.assert_has_calls([
            call('release', 'DEVBLISS_VERSION="1.0.0"')
        ])
        github_devbliss.assert_has_calls([
            call(['pull-request'])
        ])
        print_function.assert_has_calls([
            call('Have these changes been reviewed?'),
            call('[enter / ctrl+c to cancel]')
        ])

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_status(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'status']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['status']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_issue(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'issue']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['issue', None]),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_issue_with_title(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'issue',
                                 'title']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['issue', 'title']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_review(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'review',
                                 'pull_id']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['review', 'pull_id']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_merge_button(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'merge-button',
                                 'pull_id']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['merge-button', 'pull_id']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_close_button(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'close-button',
                                 'pull_id']):
            git_devbliss_main()
        github.assert_has_calls([
            call(['close-button', 'pull_id']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_delete_master(self, git, print_function):
        git.side_effect = [
            '',
            '',
            'master',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'delete']):
            with self.assertRaises(SystemExit):
                git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True)
        ])
        print_function.assert_has_calls([
            call("Won't delete master branch. Aborting.", file=sys.stderr),
        ])

    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_delete_cancel(self, git, input_function, print_function):
        git.side_effect = [
            '',
            '',
            'test-branch',
        ]
        input_function.return_value = ''
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'delete']):
            git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True)
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_delete_yes(self, git, input_function, print_function):
        git.side_effect = [
            '',
            '',
            'test-branch',
            ''
        ]
        input_function.return_value = 'y'
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'delete']):
            git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('push --delete origin test-branch')
        ])
        print_function.assert_has_calls([
            call('To restore the remote branch, type'),
            call('    git push --set-upstream origin test-branch'),
            call('To delete your local branch, type'),
            call('    git checkout master && git branch -d test-branch')
        ])

    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_delete_force(self, git, input_function, print_function):
        git.side_effect = [
            '',
            '',
            'test-branch',
            ''
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'delete', '-f']):
            git_devbliss_main()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('push --delete origin test-branch')
        ])
        self.assertEqual(input_function.call_count, 0)
        print_function.assert_has_calls([
            call('To restore the remote branch, type'),
            call('    git push --set-upstream origin test-branch'),
            call('To delete your local branch, type'),
            call('    git checkout master && git branch -d test-branch')
        ])

    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_cleanup_no_remote_merged(self, git, input_function,
                                      print_function):
        git.side_effect = [
            '',
            '',
            '',
            '',
            subprocess.CalledProcessError(2, 'git'),
            '',
            '',
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'cleanup']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch'),
            call('remote prune origin'),
            call('branch -r --merged origin/master | grep -v master'
                 ' | grep -v release', pipe=True),
            call("branch --merged master | grep -v master | grep -v "
                 "'\\*' | xargs git branch -d"),
            call('branch --no-merged master')
        ])
        self.assertEqual(input_function.call_count, 0)
        print_function.assert_has_calls([
            call('Deleting remote tracking branches whose tracked'
                 ' branches on server are gone...'),
            call('Searching all remote branches except release'
                 ' that are already merged into master...'),
            call('No remote merged branches found'),
            call('Deleting all local branches (except current)'
                 ' that are already merged into local master...'),
            call('Checking for unmerged local branches...')
        ])

    @unittest.mock.patch('os.system')
    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_cleanup_canceled(self, git, input_function, system,
                              print_function):
        git.side_effect = [
            '',
            '',
            '',
            '',
            'remote_merged_branch',
            '',
            '',
            '',
        ]
        input.return_value = ''
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'cleanup']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch'),
            call('remote prune origin'),
            call('branch -r --merged origin/master | grep -v master'
                 ' | grep -v release', pipe=True),
            call("branch --merged master | grep -v master | grep -v "
                 "'\\*' | xargs git branch -d"),
            call('branch --no-merged master')
        ])
        input_function.assert_called_with(
            'Do you want to delete those branches on the server? [y/N]')
        print_function.assert_has_calls([
            call('Deleting remote tracking branches whose tracked branches'
                 ' on server are gone...'),
            call('Searching all remote branches except release that are'
                 ' already merged into master...'),
            call('remote_merged_branch'),
            call('ok, will not delete anything.'),
            call('Deleting all local branches (except current) that are'
                 ' already merged into local master...'),
            call('Checking for unmerged local branches...')
        ])

    @unittest.mock.patch('os.system')
    @unittest.mock.patch('builtins.input')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_cleanup(self, git, input_function, os_system,
                     print_function):
        git.side_effect = [
            '',
            '',
            '',
            '',
            'remote_merged_branch',
            '',
            '',
            '',
        ]
        input_function.return_value = 'y'
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'cleanup']):
            git_devbliss_main()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('fetch'),
            call('remote prune origin'),
            call('branch -r --merged origin/master | grep -v master'
                 ' | grep -v release', pipe=True),
            call('remote prune origin'),
            call("branch --merged master | grep -v master | grep -v"
                 " '\\*' | xargs git branch -d"),
            call('branch --no-merged master')
        ])
        input_function.assert_called_with(
            'Do you want to delete those branches on the server? [y/N]')
        os_system.assert_called_with(
            "echo 'remote_merged_branch' | sed 's#origin/##' | xargs -I {}"
            " git push origin :{}")
        print_function.assert_has_calls([
            call('Deleting remote tracking branches whose tracked branches'
                 ' on server are gone...'),
            call('Searching all remote branches except release that are'
                 ' already merged into master...'),
            call('remote_merged_branch'),
            call('Deleting...'),
            call('Deleting all local branches (except current) that are'
                 ' already merged into local master...'),
            call('Checking for unmerged local branches...')
        ])
