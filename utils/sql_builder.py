def list_to_sql_like(values, field):
    """将列表转换为 SQL 条件：field IN (...) 或 LIKE"""
    if not values:
        return None
    if isinstance(values, str):
        values = [values]
    if len(values) == 1:
        return f"{field} LIKE '%{values[0]}%'"
    else:
        clauses = [f"{field} LIKE '%{v}%'" for v in values]
        return "(" + " OR ".join(clauses) + ")"

def build_metadata_query(category_keyword=None, file_type=None, subject=None, db_source=None, limit_count=1000):
    """构造元数据查询 SQL（支持多值参数）"""
    conditions = ["1=1"]
    for field, val in [("category", category_keyword),
                       ("file_type", file_type),
                       ("subject", subject),
                       ("db_source", db_source)]:
        sql_cond = list_to_sql_like(val, field)
        if sql_cond:
            conditions.append(sql_cond)
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT sha256, category, title, author, abstract
    FROM ads.ads_xinghe_library_acc
    WHERE {where_clause}
    LIMIT {limit_count}
    """
    return sql
