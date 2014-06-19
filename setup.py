import setuptools


setuptools.setup(
    name="git_devbliss",
    version="1.8.0",
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
    #  data_files=[
    #      ("share/man/man1", ["debian/git-devbliss.1"]),
    #  ],
)
