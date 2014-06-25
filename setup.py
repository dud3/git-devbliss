import setuptools
import sys

if sys.version_info < (3, 4):
    print('Python 3.4 or above is required for git-devbliss')
    sys.exit(1)

setuptools.setup(
    name="git_devbliss",
    version="2.0.0",
    packages=setuptools.find_packages(),
    test_suite="git_devbliss",
    install_requires=[
        "docopt >=0.6.1",
        "requests ==2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "git-devbliss = git_devbliss.__main__:main",
            "github-devbliss = git_devbliss.github.__main__:main",
        ],
    }
)
