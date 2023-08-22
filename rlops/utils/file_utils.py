import os
import platform


def data_dir_default():
    """

    :return: default data directory depending on the platform and environment variables
    """
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA"), "mlopskit")
    else:
        return os.path.join(os.path.expanduser("~"), ".mlopskit")


def data_dir():
    """

    :return: data directory in the filesystem for storage, for example when downloading models
    """
    return os.getenv("MLOPSKIT_HOME", data_dir_default())


def make_containing_dirs(path):
    """
    Create the base directory for a given file path if it does not exist; also creates parent
    directories.
    """
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
