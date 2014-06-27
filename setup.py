import setuptools
import setuptools.command.install
import sys
import os


class GitDevblissInstallCommand(setuptools.command.install.install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        notify(bash_completion_notice)
        notify(python_path_notice)
        setuptools.command.install.install.run(self)


def notify(message):
    if not message:
        return
    print()
    print('*' * len(message))
    print(message)
    print('*' * len(message))
    print()


if sys.version_info < (3, 4):
    print('Python 3.4 or above is required for git-devbliss')
    sys.exit(1)

python_path_notice = ''
installed_man_notice = ''
bash_completion_notice = ''
data_files = []

if os.path.exists('/usr/share/man'):
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
    bash_completion_notice = (
        'Please copy "source /etc/bash_completion.d/git-devbliss"'
        'into your profile to enable bash completion')


python_path = '/opt/local/Library/Frameworks/Python.framework/Versions/3.4/bin'
if (sys.platform == 'darwin'
        and os.path.exists(python_path)
        and python_path not in os.environ.get('PATH')):
    python_path_notice = (
        'Please ensure you have set your PATH to include python3.4'
        ' packages: "export PATH=$PATH:{}"'.format(python_path))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    author="devbliss GmbH",
    author_email="python_maintainer@devbliss.com",
    url="http://www.devbliss.com",
    download_url="https://github.com/devbliss/git-devbliss",
    description="Tool supporting the devbliss Git/GitHub Workflow",
    license="Apache2",
    long_description=read('README'),
    name="git_devbliss",
    version="2.0.3",
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
    cmdclass={
        'install': GitDevblissInstallCommand,
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
