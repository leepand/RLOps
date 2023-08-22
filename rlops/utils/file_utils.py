import os
import platform
import datetime
import pandas as pd


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


# Helper functions


def get_file_size(file_path):
    # 获取文件大小（以字节为单位）
    file_size = os.path.getsize(file_path)
    print("文件大小（字节）:", file_size)

    # 获取文件大小（以可读格式显示）
    file_size_readable = os.path.getsize(file_path)
    size_suffixes = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    while file_size_readable >= 1024 and index < len(size_suffixes) - 1:
        file_size_readable /= 1024
        index += 1
    file_size_readable = f"{file_size_readable:.2f} {size_suffixes[index]}"
    return file_size_readable


def models_table(files_in_dir=None, models_dir=None, use_models_dir=True):
    if use_models_dir is False:
        models_dir = os.getcwd()
    if files_in_dir is None:
        files_in_dir = os.listdir(models_dir)
        if ".gitignore" in files_in_dir:
            files_in_dir.remove(".gitignore")
    file_modified_time = [
        datetime.datetime.fromtimestamp(
            os.path.getmtime(os.path.join(str(models_dir), str(file)))
        ).isoformat()
        for file in files_in_dir
    ]
    file_sizes = [
        get_file_size(os.path.join(models_dir, file)) for file in files_in_dir
    ]
    files_with_time = pd.DataFrame(
        data=[files_in_dir, file_modified_time, file_sizes],
        index=["Model", "Last modified", "Size in MB"],
    ).T
    return files_with_time
