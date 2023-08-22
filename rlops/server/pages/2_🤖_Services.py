import streamlit as st
from rlops.utils.file_utils import models_table, get_dirs_inside_dir, show_dir_tree
import os


st.set_page_config(page_title="RL model services", page_icon="📈")

"# 📈 RL Model Services"

base_path = os.path.join(os.path.expanduser("~"), "mlopskit")
table = st.empty()
st.sidebar.subheader("当前模型环境")
env_list = ["开发", "预生产", "生产"]
selected_genre = st.sidebar.selectbox("选择环境", env_list)

if selected_genre == "开发":
    file_path = "dev"
elif selected_genre == "预生产":
    file_path = "preprod"
else:
    file_path = "prod"

models_abs_dir = os.path.join(base_path, "files", file_path)
_models_abs_dir = os.path.join(base_path, "files", file_path)
files_in_dir = os.listdir(models_abs_dir)
table.write(models_table(files_in_dir=files_in_dir, models_dir=models_abs_dir))


# files_to_show = get_dirs_inside_dir(models_abs_dir)
models_to_show = get_dirs_inside_dir(models_abs_dir)
model_level = 1
temp = st.selectbox(
    "Models' folder" + f": level {model_level}",
    options=models_to_show,
    key=models_abs_dir,
)

table = st.empty()
models_abs_dir = os.path.join(models_abs_dir, temp)

files_in_dir = os.listdir(models_abs_dir)

table.write(models_table(files_in_dir, models_dir=models_abs_dir))


model_version_level = 2
models_versions_to_show = get_dirs_inside_dir(models_abs_dir)
temp2 = st.selectbox(
    "Models version' folder" + f": level {model_version_level}",
    options=models_versions_to_show,
    key=models_abs_dir,
)

models_abs_dir_version = os.path.join(models_abs_dir, temp2)

try:
    show_dir_tree(models_abs_dir, temp2)
except FileNotFoundError:
    pass
