import os
import json
import re
import subprocess
from urllib.parse import unquote
from pathlib import Path

# ✅ 设置 AWS 凭据和 endpoint
os.environ["AWS_ACCESS_KEY_ID"] = "B5850CF7238163559DEC"
os.environ["AWS_SECRET_ACCESS_KEY"] = "wZK35mmnwq99bl8DxKaJ1elL4RIAAAGaI4FjYMIs"
AWS_ENDPOINT = "http://d-ceph-ssd-inside.pjlab.org.cn"


def safe_filename(name: str) -> str:
    """替换非法字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', name.strip()) or "untitled"


def download_and_rewrite_jsonl(process_dir: Path):
    """
    读取 process_dir 下的 all_chunks_with_img.jsonl，
    下载 S3 图片并更新为本地路径，
    输出 all_chunks_with_local_img.jsonl。
    """
    input_jsonl = process_dir / "all_chunks_with_img.jsonl"
    output_jsonl = process_dir / "all_chunks_with_local_img.jsonl"
    img_dir = process_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    if not input_jsonl.exists():
        raise FileNotFoundError(f"❌ 未找到 {input_jsonl}")

    with open(input_jsonl, "r", encoding="utf-8") as fin, \
         open(output_jsonl, "w", encoding="utf-8") as fout:

        count_total, count_downloaded = 0, 0

        for line in fin:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            images = rec.get("images", {})
            new_images = {}

            for placeholder, url in images.items():
                count_total += 1
                filename = safe_filename(os.path.basename(unquote(url)))
                local_path = img_dir / filename

                if not local_path.exists():
                    # 下载图片
                    cmd = [
                        "aws", "s3", "cp",
                        url, str(local_path),
                        "--endpoint-url", AWS_ENDPOINT
                    ]
                    print(f"🔄 下载: {url} -> {local_path}")
                    try:
                        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        count_downloaded += 1
                    except subprocess.CalledProcessError:
                        print(f"❌ 下载失败: {url}")
                        continue

                new_images[placeholder] = str(local_path)

            # 更新记录
            rec["images"] = new_images
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")

        print(f"\n📦 共处理 {count_total} 张图片，下载 {count_downloaded} 张。")
        print(f"📄 已保存更新后的 JSONL 到: {output_jsonl}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="下载 JSONL 中的 S3 图片并替换为本地路径")
    parser.add_argument("--dir", required=True, help="包含 all_chunks_with_img.jsonl 的目录路径")
    args = parser.parse_args()

    process_dir = Path(args.dir).resolve()
    download_and_rewrite_jsonl(process_dir)
