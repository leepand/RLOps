import streamlit as st
from rlops.utils.file_utils import models_table
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
files_in_dir = os.listdir(models_abs_dir)
table.write(models_table(files_in_dir=files_in_dir, models_dir=models_abs_dir))
