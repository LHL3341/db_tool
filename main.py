import datetime
from config import init_config
from utils.sql_builder import build_metadata_query
from utils.db_utils import get_metadata, query_content_batches

def main():
    # 1️⃣ 初始化配置
    config = init_config()
    db = config["db"]
    query_cfg = config["query"]
    output_dir = config["output"]["output_dir"]

    print(f"🚀 开始生成 '{query_cfg['category_keyword']}' 文档")
    print("=" * 60)

    # 2️⃣ 构建 SQL
    sql = build_metadata_query(**query_cfg)
    print(f"🧩 SQL:\n{sql}")

    # 3️⃣ 查询元数据
    sha256_list, metadata_map = get_metadata(
        db["host"], db["port"], db["username"], db["password"], sql
    )
    print(f"✅ 获取到 {len(sha256_list)} 条元数据\n")
    print(sha256_list[0:2])

    # 4️⃣ 查询内容 + 生成 Markdown
    query_content_batches(
        db["host"], db["port"], db["username"], db["password"],
        sha256_list, metadata_map, output_dir
    )

    print("=" * 60)
    print(f"🎉 生成完成，输出路径：{output_dir}")


if __name__ == "__main__":
    print("start:", datetime.datetime.now())
    main()
    print("finish:", datetime.datetime.now())
