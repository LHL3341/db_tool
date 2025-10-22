import os
import json
import re

def safe_filename(name, max_length=100):
    # 去掉非法字符
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # 截断长度
    if len(name) > max_length:
        name = name[:max_length] + "..."
    return name

def write_markdown_document(root_dir: str, sha256: str, title: str, content_list: list):
    """
    根据 content_list 四种类型生成 Markdown：
    - text: 根据 text_level 使用 #、##、### 等
    - image: ![](img_path) + caption/footnote
    - equation: 以 LaTeX 形式 $$...$$
    - table: 图片 + HTML 表格 + caption/footnote
    """
    title = title or sha256
    safe_title = safe_filename(title)
    doc_dir = os.path.join(root_dir, safe_title)
    os.makedirs(doc_dir, exist_ok=True)
    md_path = os.path.join(doc_dir, f"{safe_title}.md")

    lines = [f"# {title}\n\n"]

    for item in content_list:
        try:
            if isinstance(item, str):
                item = json.loads(item)
            if not isinstance(item, dict):
                continue

            type_ = item.get("type")

            # -------------------------
            # 文字
            # -------------------------
            if type_ == "text":
                text = item.get("text", "").strip()
                level = item.get("text_level", 0)  # 默认 0
                if text:
                    if level == 0:
                        lines.append(text + "\n\n")  # 普通段落
                    else:
                        header = "#" * level
                        lines.append(f"{header} {text}\n\n")

            # -------------------------
            # 图片
            # -------------------------
            elif type_ == "image":
                img_path = item.get("img_path", "").strip()
                if img_path:
                    lines.append(f"![]({img_path})\n")
                    caption = " ".join(item.get("image_caption", []))
                    footnote = " ".join(item.get("image_footnote", []))
                    if caption:
                        lines.append(f"> {caption}\n")
                    if footnote:
                        lines.append(f"> {footnote}\n")
                    lines.append("\n")

            # -------------------------
            # 方程
            # -------------------------
            elif type_ == "equation":
                latex = item.get("text", "").strip()
                img_path = item.get("img_path", "").strip()
                if latex:
                    lines.append(f"{latex}\n")
                if img_path:
                    lines.append(f"![]({img_path})\n\n")

            # -------------------------
            # 表格
            # -------------------------
            elif type_ == "table":
                img_path = item.get("img_path", "").strip()
                if img_path:
                    lines.append(f"![]({img_path})\n")
                # caption & footnote
                caption = " ".join(item.get("table_caption", []))
                footnote = " ".join(item.get("table_footnote", []))
                if caption:
                    lines.append(f"> {caption}\n")
                if footnote:
                    lines.append(f"> {footnote}\n")
                # table_body HTML 原样插入（可用 HTML 渲染）
                table_body = item.get("table_body", "").strip()
                if table_body:
                    lines.append(table_body + "\n")
                lines.append("\n")

        except Exception as e:
            print(f"⚠️ 内容解析错误: {e}")
            continue

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ 保存文档: {md_path} ({len(content_list)} 段)")
    return md_path