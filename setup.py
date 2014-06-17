import setuptools


setuptools.setup(
    name="git_devbliss",
    version="1.8.0",
    packages=setuptools.find_packages(),
    test_suite="git_devbliss",
    entry_points={
        "console_scripts": [
            "git-devbliss = git_devbliss.__main__:main",
        ],
    },
    #  data_files=[
    #      ("share/man/man1", ["debian/git-devbliss.1"]),
    #  ],
)
