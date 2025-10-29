import boto3
import os

# -------------------------
# AWS 认证（环境变量或默认配置）
# -------------------------
os.environ["AWS_ACCESS_KEY_ID"] = "B5850CF7238163559DEC"
os.environ["AWS_SECRET_ACCESS_KEY"] = "wZK35mmnwq99bl8DxKaJ1elL4RIAAAGaI4FjYMIs"

# -------------------------
# 配置 S3 文件和本地路径
# -------------------------
s3_url = "s3://lakehouse/hive-ha/produce.db/anna_mineru_v1/result=success/type=image/dt=2025-07-31/ht=02/5e1ad8107535bb2f9bda2203b1c14613284be3e2614f290fc18f596a105e7f2f.jpg"
local_dir = "/mnt/dhwfile/raise/user/linhonglin/data_process/db_tool/outputs/math_textbook/images"  # 本地存储目录
os.makedirs(local_dir, exist_ok=True)

# 从 S3 URL 提取 bucket 和 key
from urllib.parse import urlparse
parsed = urlparse(s3_url)
bucket = parsed.netloc
key = parsed.path.lstrip("/")
filename = os.path.basename(key)
local_path = os.path.join(local_dir, filename)

# -------------------------
# 下载 S3 文件
# -------------------------
s3 = boto3.client("s3")
try:
    s3.download_file(bucket, key, local_path)
    print(f"✅ 下载成功: {local_path}")
except Exception as e:
    print(f"❌ 下载失败: {e}")
