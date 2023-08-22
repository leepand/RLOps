import os
import platform
import datetime
import pandas as pd
from pathlib import Path
import streamlit as st
import shutil
import sys


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


# Helper functions

tee = "├── "
last = "└── "
branch = "│   "
space = "    "


def tree(dir_path: Path, prefix: str = ""):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    contents = [
        path
        for path in contents
        if path.name not in [".git", ".ipynb_checkpoints", "__pycache__", ".gitkeep"]
    ]  # Filter the directory list

    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


def get_dirs_inside_dir(folder):
    return [
        my_dir
        for my_dir in list(
            map(
                lambda x: os.path.basename(x),
                sorted(Path(folder).iterdir(), key=os.path.getmtime, reverse=True),
            )
        )
        if os.path.isdir(os.path.join(folder, my_dir))
        and my_dir != "__pycache__"
        and my_dir != ".ipynb_checkpoints"
        and my_dir != "API"
    ]


def list_folders_in_folder(folder):
    return [
        file for file in os.listdir(folder) if os.path.isdir(os.path.join(folder, file))
    ]


def show_dir_tree(base_path_str, folder):
    with st.expander(f"Show {os.path.basename(folder)} folder tree"):
        for line in tree(Path(base_path_str) / folder):
            st.write(line)


def delete_folder(folder, ask=True):
    if not ask:
        shutil.rmtree(folder)
    else:
        folder_basename = os.path.basename(folder)
        if len(os.listdir(folder)) > 0:
            st.warning(
                f"**{folder_basename} is not empty. Are you sure you want to delete it?**"
            )
            show_dir_tree(folder)
            if st.button("Yes"):
                try:
                    shutil.rmtree(folder)
                except:
                    st.error(f"Couldn't delete {folder_basename}:")
                    e = sys.exc_info()
                    st.error(e)
        else:
            st.write(f"**Are you sure you want to delete {folder_basename}?**")
            if st.button("Yes"):
                try:
                    shutil.rmtree(folder)
                except:
                    st.error(f"Couldn't delete {folder_basename}:")
                    e = sys.exc_info()
                    st.error(e)
