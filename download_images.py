import os
import re
import subprocess
from urllib.parse import urlparse

def safe_filename(name: str) -> str:
    import re
    return re.sub(r'[\\/*?:"<>|]', '_', name.strip()) or "untitled"

def collect_s3_paths(doc_root):
    """
    遍历文档目录，提取 S3 或 HTTP 图片路径
    返回 [(s3_url, local_path)]
    """
    s3_list = []
    for root, dirs, files in os.walk(doc_root):
        for file in files:
            if not file.endswith((".md", ".json")):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            urls = re.findall(r'(s3://[^\s)]+|https?://[^\s)]+)', content)
            for url in urls:
                img_filename = safe_filename(os.path.basename(url))
                images_dir = os.path.join(root, "images")
                os.makedirs(images_dir, exist_ok=True)
                local_path = os.path.join(images_dir, img_filename)
                if not os.path.exists(local_path):
                    s3_list.append((url, local_path))
    return s3_list

def sync_images_with_sensesync(s3_list):
    """
    使用 sensesync 批量同步图片
    """
    for src, tgt in s3_list:
        tgt_dir = os.path.dirname(tgt)
        os.makedirs(tgt_dir, exist_ok=True)
        cmd = ["srun", "-p", "raise", "/mnt/petrelfs/share/sensesync", "sync", src, tgt]
        print(f"🔄 同步: {src} -> {tgt}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ 同步失败: {src}, {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="使用 sensesync 同步文档图片")
    parser.add_argument("--doc_root", type=str, required=True, help="文档根目录")
    args = parser.parse_args()

    s3_list = collect_s3_paths(args.doc_root)
    print(f"共找到 {len(s3_list)} 张需要同步的图片")
    sync_images_with_sensesync(s3_list)
    print("🎉 图片同步完成！")
