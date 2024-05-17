import os
import yaml

file_dir = os.path.dirname(os.path.abspath(__file__))

def load_config(file_name):
    """讀取 YAML 配置文件並返回配置字典"""
    config_file = os.path.join(file_dir, file_name)

    with open(config_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# 分別讀取模型和提示配置文件
models_config = load_config("models.yml")
rags_config = load_config("rags.yml")

# 合併兩個配置字典
config = {
    "models": models_config.get("models", {}),
    "rags": rags_config.get("knowledge_bases", {}),
}