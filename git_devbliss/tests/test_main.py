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
