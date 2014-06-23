import pkg_resources

try:
        __version__ = pkg_resources.get_distribution("git_devbliss").version
except pkg_resources.DistributionNotFound:  # pragma: no cover
        __version__ = 'undefined'
