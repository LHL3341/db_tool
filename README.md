# db_tool 项目说明文档

## 目录结构

```
db_tool/
├── __init__.py
├── config.py               # 全局配置文件，定义数据库连接、输出路径、查询参数等
├── examples/               # 配置示例目录
│   └── *.py                # 不同示例配置文件，供快速参考
├── utils/                  # 工具模块
│   ├── md_utils.py         # Markdown 文件生成及处理工具
│   ├── db_utils.py         # 数据库通用操作工具（执行 SQL、获取结果）
│   └── sql_builder.py      # SQL 查询语句构建工具，根据配置生成标准 SQL
├── main.py                 # 主程序入口，用于生成 Markdown 文件
├── download_images.py      # 图像下载脚本（目前不可用）
└── split_md_for_extract.py # 分割 Markdown 文件脚本，生成 processed/ 目录和 JSONL 文件
```

---

## 文件功能说明

### 1. `config.py`

* 用于定义项目的全局配置，包括：

  * 数据库连接信息（host, port, user, password, db_name 等）
  * 查询配置（SQL 查询模板、过滤条件、字段映射）
  * Markdown 输出目录
  * 分块处理参数（如 `max_chars`）
* 使用方法：

  * 拷贝 `examples/` 中的示例配置文件到 `config.py` 或直接修改 `config.py` 中对应字段。
  * 可根据实际业务场景自定义查询条件、输出路径、分块大小等。

---

### 2. `examples/`

* 提供配置示例，方便快速上手。
* 示例内容：

  * 如何配置数据库查询条件
  * 如何指定输出 Markdown 文件路径
  * 分块处理参数示例
* 使用方法：

  * 可直接参考示例配置复制到 `config.py` 中进行修改
  * 避免直接修改示例文件，以便保留参考模板

---

### 3. `utils/` 工具模块

#### `md_utils.py`

* 功能：

  * 将查询结果生成 Markdown 文件
  * 分割 Markdown 文件为多个 chunk
  * 替换图片占位符 `<imageX>`，生成有图和无图版本
* 常用函数：

  * `split_markdown(md_text, max_chars)`：按标题或图片分块
  * `replace_images(md_text)`：生成有图版本占位符
  * `remove_image_placeholders(md_text)`：生成无图版本

#### `db_utils.py`

* 功能：

  * 数据库连接管理
  * SQL 执行与结果获取
  * 可复用查询操作，支持分页、批量处理
* 常用函数：

  * `execute_query(sql)`：执行 SQL 并返回结果
  * `fetch_all(sql)`：获取全部查询结果

#### `sql_builder.py`

* 功能：

  * 根据配置参数动态生成 SQL 查询语句
  * 支持多表联合、条件过滤、字段映射
* 优点：

  * 不需要手动拼写 SQL
  * 统一 SQL 风格，减少错误

---

### 4. `main.py`

* 项目主入口，生成 Markdown 文件流程：

  1. 加载 `config.py` 配置
  2. 使用 `sql_builder.py` 生成 SQL
  3. 使用 `db_utils.py` 执行 SQL 并获取结果
  4. 使用 `md_utils.py` 将结果写入 Markdown 文件
* 使用方法：

  ```bash
  python main.py
  ```

---

### 5. `split_md_for_extract.py`

* 功能：

  * 将生成的 Markdown 文件按标题或图片分块
  * 生成 **processed/** 目录
  * 生成待处理 JSONL 文件，包含：

    * 有图版本：`all_chunks_with_img.jsonl`
    * 无图版本：`all_chunks_no_img.jsonl`
* 参数说明：

  * `max_chars`：每个 chunk 最大字符数（可根据实际情况调整，越大每个 chunk 内容越多）
* 使用方法：

  ```bash
  python split_md_for_extract.py --root_dir=./markdown_source --processed_dir=./processed --max_chars=50000
  ```

---

### 6. `download_images.py`

* 功能：

  * 根据 JSONL 中图片路径批量下载图片
* 注意事项：

  * 目前不可用
  * 依赖 `sensesync` 工具，需要申请权限
  * 可等待权限或改用其他下载方式

---

明白了，你希望以具体命令为例，写一个详细的 **使用流程示例**，清楚展示从配置到生成 Markdown、分割、JSONL 的完整步骤。下面是整理后的版本：

---

## 使用流程示例

假设我们要处理的数据集名称为 `${DATA_NAME}`（如 `math_textbook`），操作流程如下：

---

### 1. 配置数据集

* 参考 `examples/${DATA_NAME}/config.yaml` 修改配置：

  * 数据库连接信息（host, port, user, password, db_name 等）
  * 查询参数、字段映射
  * Markdown 输出目录和文件名

---

### 2. 生成 Markdown 文件

使用 `main.py` 根据配置生成 Markdown 文件：

```bash
python -m main --config examples/${DATA_NAME}/config.yaml
```

* 输出目录：通常为 `outputs/${DATA_NAME}/`

---

### 3. 分割 Markdown 文件

使用 `split_md_for_extract.py` 将 Markdown 文件分块，并生成 JSONL 文件：

```bash
python split_md_for_extract.py \
    --root_dir outputs/${DATA_NAME} \
    --processed_dir processed/${DATA_NAME}
```

* 输出内容：

  ```
  processed/${DATA_NAME}/chunk_001_with_img.md
  processed/${DATA_NAME}/chunk_001_no_img.md
  ...
  processed/${DATA_NAME}/all_chunks_with_img.jsonl
  processed/${DATA_NAME}/all_chunks_no_img.jsonl
  ```
* 功能：

  * 每个 chunk 生成 **有图** 和 **无图** 两个版本 Markdown
  * JSONL 文件记录每个 chunk 的路径和文本内容
  * `max_chars` 参数控制每个 chunk 的字符数，可在 `split_md_for_extract.py` 中修改

---

### 4. 下载图片（可选）

> ⚠️ 注意：目前 `download_images.py` 依赖 `sensesync` 工具，需要权限，暂不可用

```bash
# 下载 outputs/${DATA_NAME} 中 Markdown 的图片
# python download_images.py --doc_root outputs/${DATA_NAME}
```

* 功能：

  * 批量下载 Markdown 中引用的图片
  * 下载后可更新 Markdown 或 JSONL 的图片路径

---

### 5. 文件说明

* Markdown 文件：

  * `*_with_img.md`：有图版本，占位符 `<imageX>` 保留
  * `*_no_img.md`：无图版本，仅保留 caption
* JSONL 文件：

  * 每条记录格式：

    ```json
    {
      "doc": "math_textbook",
      "chunk_id": 1,
      "path": "processed/math_textbook/chunk_001_with_img.md",
      "text": "..."
    }
    ```
  * 两个文件：`all_chunks_with_img.jsonl` / `all_chunks_no_img.jsonl`

---

### 🔹 流程总结

1. 配置数据集 → `config.yaml`
2. 生成 Markdown → `python -m main`
3. 分割 Markdown → `python split_md_for_extract.py`
4. 可选：下载图片 → `python download_images.py`

这样就得到**有图/无图 Markdown 文件**和**JSONL 文件**，可以直接用于后续 AI 模型处理或数据分析。

