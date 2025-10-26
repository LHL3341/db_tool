import json
import pymysql
from utils.sql_builder import build_metadata_query
from utils.md_utils import write_markdown_document


def execute_query(host, port, username, password, sql):
    """执行 SQL 并返回结果"""
    try:
        conn = pymysql.connect(
            host=host, port=port, user=username, password=password,
            charset="utf8mb4", autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ SQL执行错误: {e}\nSQL: {sql}")
        return []


def get_metadata(host, port, username, password, sql):
    """执行元数据查询并返回 sha256 列表"""
    rows = execute_query(host, port, username, password, sql)
    sha256_list, metadata_map = [], {}
    for row in rows:
        sha256, category, title, author, abstract = row
        sha256_list.append(sha256)
        metadata_map[sha256] = {"title": title, "abstract": abstract}
    return sha256_list, metadata_map


def query_content_batches(host, port, username, password, sha256_list, metadata_map, root_dir, batch_size=500):
    """
    分批查询每个 sha256 对应的内容列表，并生成 Markdown
    统计：内容为空（解析失败）与内容缺失（未返回）的文档数量
    """
    if not sha256_list:
        print("❌ sha256列表为空，无法查询内容")
        return 0, 0, 0

    def chunk_list(items, size):
        for i in range(0, len(items), size):
            yield items[i:i + size]

    total_written, empty_count, missing_count = 0, 0, 0
    total = len(sha256_list)
    print(f"🔍 准备查询 {total} 条记录，批量大小 {batch_size}")

    for batch_no, batch in enumerate(chunk_list(sha256_list, batch_size), start=1):
        # 使用 build_metadata_query 生成批量 sha256 条件
        sql = f"""
        SELECT sha256, content_list
        FROM ads.ads_xinghe_library_content_list_acc_view
        WHERE sha256 IN ('{"', '".join(batch)}')
        """
        rows = execute_query(host, port, username, password, sql)

        found_sha = {r[0] for r in rows}
        batch_missing = set(batch) - found_sha
        missing_count += len(batch_missing)
        for sha in batch_missing:
            title = metadata_map.get(sha, {}).get("title")
            print(f"⚠️ 缺失内容: {sha} ({title or '无标题'})")

        for sha256, content_list in rows:
            title = metadata_map.get(sha256, {}).get("title")
            try:
                parsed = json.loads(content_list) if content_list else []
            except Exception:
                parsed = []

            if not parsed:
                empty_count += 1
                print(f"⚠️ 空内容跳过: {sha256} ({title or '无标题'})")
                continue

            # print(parsed)
            # 确保为列表并按 record_id 排序
            if not isinstance(parsed, list):
                parsed = [parsed]
            parsed.sort(key=lambda x: x.get("record_id", 0))

            # 写入 Markdown
            write_markdown_document(root_dir, sha256, title, parsed)
            total_written += 1

    print(f"\n📊 汇总：生成 {total_written} 篇，空内容 {empty_count} 篇，缺失 {missing_count} 篇")
    return total_written, empty_count, missing_count

