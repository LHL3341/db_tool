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


def replace_images_with_placeholders(md_text):
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


def process_md_file(md_path: Path, output_dir: Path, max_chars=3000):
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    chunks = split_markdown(md_text, max_chars=max_chars)
    json_records = []

    for i, chunk in enumerate(chunks, 1):
        new_text, mapping = replace_images_with_placeholders(chunk)

        # 保存修改后的文本块
        out_path = output_dir / f"chunk_{i:03d}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(new_text)

        record = {
            "doc": output_dir.name,
            "chunk_id": i,
            "path": str(out_path),
            "text": new_text.strip()
        }
        if mapping:
            record["images"] = mapping

        json_records.append(record)

    print(f"✅ {md_path.name} -> {len(chunks)} chunks saved to {output_dir}")
    return json_records


def batch_process(root_dir: str, processed_root: str = "processed", max_chars=3000):
    root = Path(root_dir)
    all_records = []

    for sub in root.iterdir():
        if sub.is_dir():
            md_files = list(sub.glob("*.md"))
            if not md_files:
                continue
            md_path = md_files[0]
            output_dir = Path(processed_root) / sub.name
            records = process_md_file(md_path, output_dir, max_chars=max_chars)
            all_records.extend(records)

    # 汇总 JSONL
    jsonl_path = Path(processed_root) / "all_chunks.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\n📄 All chunks written to {jsonl_path} ({len(all_records)} records total)\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch split Markdown files for VQA processing.")
    parser.add_argument("--root_dir", required=True, help="Root directory containing doc subfolders.")
    parser.add_argument("--processed_dir", default="processed", help="Output base directory.")
    parser.add_argument("--max_chars", type=int, default=50000, help="Max chars per chunk.")
    args = parser.parse_args()

    batch_process(args.root_dir, args.processed_dir, args.max_chars)
