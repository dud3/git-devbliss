import setuptools
import sys
import os

if sys.version_info < (3, 4):
    print('Python 3.4 or above is required for git-devbliss')
    sys.exit(1)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    author="devbliss GmbH",
    email="python_maintainer@devbliss.com",
    url="http://www.devbliss.com",
    description="Tool supporting the devbliss Git/GitHub Workflow",
    long_description=read('README.md'),
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
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
    ],
)
