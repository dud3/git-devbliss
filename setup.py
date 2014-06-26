import setuptools
import sys
import os

if sys.version_info < (3, 4):
    print('Python 3.4 or above is required for git-devbliss')
    sys.exit(1)
data_files = []
if os.path.exists('/usr/share/man'):
    print('Installing man page to /usr/share/man')
    data_files = data_files + [(
        '/usr/share/man/man1',
        ['man1/git-devbliss.1']
    )]

if os.path.exists('/etc'):
    if not os.path.exists('/etc/bash_completion.d/'):
        os.mkdir('/etc/bash_completion.d/')
    data_files = data_files + [(
        '/etc/bash_completion.d/',
        ['bash_completion/git-devbliss']
    )]
    bash_completion_help = (
        'Please copy "source /etc/bash_completion.d/git-devbliss"'
        'in your profile to enable bash completion')
    print('*' * len(bash_completion_help))
    print(bash_completion_help)
    print('*' * len(bash_completion_help))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    author="devbliss GmbH",
    author_email="python_maintainer@devbliss.com",
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
    data_files=data_files,
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
