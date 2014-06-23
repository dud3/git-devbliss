import unittest
import git_devbliss


class DistributionTest(unittest.TestCase):

    def test_version(self):
        self.assertRegex(git_devbliss.__version__, r'\d+\.\d+\.\d+')
