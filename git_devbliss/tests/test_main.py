import pkg_resources
import unittest
import unittest.mock
from unittest.mock import call
import subprocess
import sys

git_devbliss = pkg_resources.load_entry_point(
    "git_devbliss", "console_scripts", "git-devbliss")


@unittest.mock.patch("builtins.print")
class MainTest(unittest.TestCase):

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_main(self, git, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss']):
            with self.assertRaises(SystemExit):
                git_devbliss()
        git.assert_has_calls([
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_main_error(self, git, print_function):
        git.side_effect = subprocess.CalledProcessError('3', 'git')
        with self.assertRaises(SystemExit):
            git_devbliss()
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
            git_devbliss()
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
    def test_feature_finish(self, git, print_function):
        with unittest.mock.patch('sys.argv',
                                 ['git-devbliss', 'feature', 'finish']):
            git_devbliss()

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
            git_devbliss()
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
            git_devbliss()
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
            git_devbliss()
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
                git_devbliss()
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
            git_devbliss()
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
                git_devbliss()
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
            'some_branch',
            '0',
            'some_branch',
            ''
        ]
        with unittest.mock.patch(
                'sys.argv', ['git-devbliss', 'finish', 'annegret']):
            git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('status --short --untracked-files=no | wc -l', pipe=True),
            call('branch --contains annegret', pipe=True)
        ])
        call_hook.assert_has_calls([
            call('finish', 'DEVBLISS_BRANCH_TYPE=some_branch'),
            call('changelog', 'DEVBLISS_BRANCH_TYPE=some_branch'),
            call('version', 'DEVBLISS_BRANCH_TYPE=some_branch')
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
                git_devbliss()
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
                git_devbliss()
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
                git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
                git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
                git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
            git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
            git_devbliss()
        github.assert_has_calls([
            call(['status']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_issue(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'issue']):
            git_devbliss()
        github.assert_has_calls([
            call(['issue', None]),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_issue_with_title(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'issue',
                                 'title']):
            git_devbliss()
        github.assert_has_calls([
            call(['issue', 'title']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_review(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'review',
                                 'pull_id']):
            git_devbliss()
        github.assert_has_calls([
            call(['review', 'pull_id']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_merge_button(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'merge-button',
                                 'pull_id']):
            git_devbliss()
        github.assert_has_calls([
            call(['merge-button', 'pull_id']),
        ])
        self.assertEqual(print_function.call_count, 0)

    @unittest.mock.patch('git_devbliss.__main__.github_devbliss')
    @unittest.mock.patch('git_devbliss.__main__.git')
    def test_close_button(self, git, github, print_function):
        with unittest.mock.patch('sys.argv', ['git-devbliss', 'close-button',
                                 'pull_id']):
            git_devbliss()
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
                git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
            git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
            git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
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
            git_devbliss()
        git.assert_has_calls([

            call('rev-parse --abbrev-ref HEAD', pipe=True),
            call('remote -v | grep "^origin.*github.*:.*(fetch)$"', pipe=True),
        ])
        self.assertEqual(input_function.call_count, 0)
        print_function.assert_has_calls([
            call('To restore the remote branch, type'),
            call('    git push --set-upstream origin test-branch'),
            call('To delete your local branch, type'),
            call('    git checkout master && git branch -d test-branch')
        ])
