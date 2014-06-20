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
        print_function.assert_has_calls([
        ])

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
        print_function.assert_has_calls([
        ])

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
