import os
import yaml
import argparse

# ==============================================
# 默认配置（当未指定 YAML 文件时使用）
# ==============================================
DEFAULT_CONFIG = {
    "db": {
        "host": "10.140.84.159",
        "port": 9030,
        "username": "dataresearch",
        "password": "zu7XBANm!1I9",
    },
    "query": {
        "category_keyword": "数学",
        "file_type": "textbook",
        "subject": None,
        "db_source": None,
        "limit_count": 50,
    },
    "output": {
        "base_dir": "/mnt/dhwfile/raise/user/linhonglin/database/mvp/docs"
    }
}


# ==============================================
# 加载 YAML 配置文件
# ==============================================
def load_config_from_yaml(path: str = None):
    """从 YAML 文件加载配置，如果未提供路径则使用默认配置"""
    if path is None:
        print("⚙️ 未指定配置文件，使用默认配置")
        return DEFAULT_CONFIG

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ 配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)

    # 合并默认值（避免 YAML 未覆盖的字段缺失）
    config = DEFAULT_CONFIG.copy()
    for key in yaml_config:
        if key in config and isinstance(config[key], dict):
            config[key].update(yaml_config[key])
        else:
            config[key] = yaml_config[key]

    return config


# ==============================================
# 命令行参数解析
# ==============================================
def parse_args():
    parser = argparse.ArgumentParser(description="文档导出工具")
    parser.add_argument(
        "--config",
        type=str,
        help="YAML 配置文件路径，例如：configs/math_textbook.yaml",
    )
    return parser.parse_args()


# ==============================================
# 入口函数：初始化配置
# ==============================================
def init_config():
    args = parse_args()
    config = load_config_from_yaml(args.config)
    query = config["query"]
    # 动态生成输出目录
    output_dir = config["output"]["base_dir"]
    os.makedirs(output_dir, exist_ok=True)
    config["output"]["output_dir"] = output_dir

    return config
