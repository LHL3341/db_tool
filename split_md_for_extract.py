import os
from pathlib import Path
import re
import json

# 匹配 Markdown 图片：![caption](path)
IMG_PATTERN = re.compile(r'!\[(.*?)\]\((.*?)\)')


def split_markdown(md_text, max_chars=3000):
    """
    将 Markdown 文件按标题或图片分块。
    """
    blocks = re.split(r'(?=^#{1,6} )|(?=!\[)', md_text, flags=re.MULTILINE)
    chunks, buf = [], ""
    for b in blocks:
        if len(buf) + len(b) > max_chars:
            chunks.append(buf.strip())
            buf = b
        else:
            buf += "\n" + b
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def replace_images(md_text):
    """
    将图片替换为 [caption]<imageX> 形式，
    并返回映射字典 {<imageX>: path}。
    """
    counter = 1
    mapping = {}

    def repl(match):
        nonlocal counter
        caption, path = match.groups()
        placeholder = f"<image{counter}>"
        mapping[placeholder] = path
        formatted = f"[{caption.strip() if caption else ''}]{placeholder}"
        counter += 1
        return formatted

    new_text = IMG_PATTERN.sub(repl, md_text)
    return new_text, mapping


def remove_image_placeholders(md_text):
    """
    去掉 <imageX> 占位符，保留 [caption]。
    """
    text = re.sub(r"\[(.*?)\]<image\d+>", r"[\1]", md_text)
    text = re.sub(r"<image\d+>", "", text)
    return text


def process_md_file(md_path: Path, output_dir: Path, start_global_id=1, max_chars=3000):
    """
    处理单个 Markdown 文件，生成有图和无图版本。
    start_global_id: 当前文档开始的全局 chunk id
    返回: (records_with_img, records_no_img, next_global_id)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    chunks = split_markdown(md_text, max_chars=max_chars)
    records_with_img, records_no_img = [], []
    global_id = start_global_id

    for i, chunk in enumerate(chunks, 1):
        # 有图版本
        md_with_img, mapping = replace_images(chunk)
        out_path_img = output_dir / f"chunk_{i:03d}_with_img.md"
        with open(out_path_img, "w", encoding="utf-8") as f:
            f.write(md_with_img)

        rec_with_img = {
            "id": global_id,
            "doc": output_dir.name,
            "chunk_id": i,
            "path": str(out_path_img),
            "text": md_with_img.strip(),
            "images": mapping
        }
        records_with_img.append(rec_with_img)

        # 无图版本
        md_no_img = remove_image_placeholders(md_with_img)
        out_path_no_img = output_dir / f"chunk_{i:03d}_no_img.md"
        with open(out_path_no_img, "w", encoding="utf-8") as f:
            f.write(md_no_img)

        rec_no_img = {
            "id": global_id,
            "doc": output_dir.name,
            "chunk_id": i,
            "path": str(out_path_no_img),
            "text": md_no_img.strip()
        }
        records_no_img.append(rec_no_img)

        global_id += 1

    print(f"✅ {md_path.name} -> {len(chunks)} chunks saved to {output_dir}")
    return records_with_img, records_no_img, global_id


def batch_process(root_dir: str, processed_root: str = "processed", max_chars=3000):
    root = Path(root_dir)
    all_with_img, all_no_img = [], []
    global_chunk_id = 1  # 全局 chunk id 起始值

    for sub in root.iterdir():
        if sub.is_dir():
            md_files = list(sub.glob("*.md"))
            if not md_files:
                continue
            md_path = md_files[0]
            output_dir = Path(processed_root) / sub.name
            rec_with_img, rec_no_img, global_chunk_id = process_md_file(
                md_path, output_dir, start_global_id=global_chunk_id, max_chars=max_chars
            )
            all_with_img.extend(rec_with_img)
            all_no_img.extend(rec_no_img)

    # 有图版本 JSONL
    jsonl_with_img = Path(processed_root) / "all_chunks_with_img.jsonl"
    with open(jsonl_with_img, "w", encoding="utf-8") as f:
        for rec in all_with_img:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 无图版本 JSONL
    jsonl_no_img = Path(processed_root) / "all_chunks_no_img.jsonl"
    with open(jsonl_no_img, "w", encoding="utf-8") as f:
        for rec in all_no_img:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\n📄 JSONL saved: {jsonl_with_img} ({len(all_with_img)} records)")
    print(f"📄 JSONL saved: {jsonl_no_img} ({len(all_no_img)} records)\n")




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch split Markdown files for VQA processing.")
    parser.add_argument("--root_dir", required=True, help="Root directory containing doc subfolders.")
    parser.add_argument("--processed_dir", default="processed", help="Output base directory.")
    parser.add_argument("--max_chars", type=int, default=50000, help="Max chars per chunk.")
    args = parser.parse_args()

    batch_process(args.root_dir, args.processed_dir, args.max_chars)
