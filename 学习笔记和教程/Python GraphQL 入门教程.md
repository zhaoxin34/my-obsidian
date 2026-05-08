---
title: Python GraphQL 入门教程
description: 使用 Strawberry 构建你的第一个 GraphQL API
---

# Python GraphQL 入门教程

在本教程中，你将使用 Python 和 Strawberry 库构建一个完整的 GraphQL API。通过本教程，你将学会如何定义 GraphQL 类型、执行查询和变更，以及启动一个可交互的 GraphQL 服务。

<Note>
本教程需要约 20 分钟完成。
</Note>

## 什么是 GraphQL？

GraphQL 是一种 API 查询语言，它允许客户端精确地请求需要的数据，而不是像 REST 那样返回固定格式的资源。

## 你将构建什么

```mermaid
graph LR
    A[客户端] -->|GraphQL 查询| B[Strawberry API]
    B -->|数据| C[内存数据源]
```

一个 **书籍查询 API**，支持：
- 查询所有书籍
- 根据 ID 查询单本书籍
- 添加新书籍
- 删除书籍

## 前置条件

- Python 3.10 或更高版本
- 会使用终端执行命令

<Tip>
新接触 Python？建议先阅读 [[Python-async-await-完全指南]] 了解基础。
</Tip>

## Step 1: 创建项目

创建项目目录并进入：

```bash
mkdir graphql-tutorial && cd graphql-tutorial
```

创建虚拟环境并激活：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 用户使用 .venv\Scripts\activate
```

你应该在终端前面看到 `(.venv)` 前缀，表示虚拟环境已激活。

## Step 2: 安装依赖

安装 Strawberry 和 Uvicorn（ASGI 服务器）：

```bash
pip install strawberry[fastapi] uvicorn
```

你将看到类似输出：

```
Successfully installed strawberry-0.xxx.x
Successfully installed uvicorn-0.xx.x
```

## Step 3: 定义数据模型

创建 `main.py` 文件：

```python
import strawberry
from typing import List, Optional

# 定义 Book 类型
@strawberry.type
class Book:
    id: int
    title: str
    author: str
    year: int

# 内存数据存储
books_db = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="动物农场", author="George Orwell", year=1945),
    Book(id=3, title="美丽新世界", author="Aldous Huxley", year=1932),
]

# 定义查询类型
@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> List[Book]:
        """返回所有书籍"""
        return books_db

    @strawberry.field
    def book(self, id: int) -> Optional[Book]:
        """根据 ID 返回单本书籍"""
        for book in books_db:
            if book.id == id:
                return book
        return None

# 定义变更类型
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str, year: int) -> Book:
        """添加新书籍"""
        new_id = max(b.id for b in books_db) + 1
        new_book = Book(id=new_id, title=title, author=author, year=year)
        books_db.append(new_book)
        return new_book

    @strawberry.mutation
    def delete_book(self, id: int) -> bool:
        """删除书籍"""
        global books_db
        original_count = len(books_db)
        books_db = [b for b in books_db if b.id != id]
        return len(books_db) < original_count

# 创建 Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

保存文件后，你应该看到 `main.py` 已创建。

## Step 4: 创建 FastAPI 应用

在 `main.py` 末尾添加启动代码：

```python
# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

但 Strawberry 需要通过 ASGI 应用启动。修改代码：

```python {26-27}
# ... 以上代码保持不变 ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:schema", host="127.0.0.1", port=8000, reload=True)
```

<Note>
`strawberry.Schema` 对象可以直接作为 ASGI 应用使用。
</Note>

## Step 5: 启动服务器

运行以下命令启动服务：

```bash
python main.py
```

你应该看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Step 6: 使用 GraphQL Playground

打开浏览器访问 http://127.0.0.1:8000/graphql

你应该看到 GraphQL Playground 界面，这是一个交互式 GraphQL 查询工具。

## Step 7: 执行第一个查询

在 Playground 左侧输入：

```graphql
query {
  books {
    id
    title
    author
    year
  }
}
```

点击播放按钮（或按 Ctrl+Enter），你应该看到右侧返回：

```json
{
  "data": {
    "books": [
      {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "year": 1949
      },
      {
        "id": 2,
        "title": "动物农场",
        "author": "George Orwell",
        "year": 1945
      },
      {
        "id": 3,
        "title": "美丽新世界",
        "author": "Aldous Huxley",
        "year": 1932
      }
    ]
  }
}
```

<Success>
第一个 GraphQL 查询成功执行！你刚刚获取了所有书籍数据。
</Success>

## Step 8: 查询单本书籍

在 Playground 中输入：

```graphql
query {
  book(id: 2) {
    title
    author
  }
}
```

你应该看到：

```json
{
  "data": {
    "book": {
      "title": "动物农场",
      "author": "George Orwell"
    }
  }
}
```

## Step 9: 使用变更添加数据

GraphQL 不仅能查询，还能修改数据。输入：

```graphql
mutation {
  addBook(title: "百年孤独", author: "Gabriel García Márquez", year: 1967) {
    id
    title
  }
}
```

你应该看到：

```json
{
  "data": {
    "addBook": {
      "id": 4,
      "title": "百年孤独"
    }
  }
}
```

<Success>
新书籍已添加到数据库！
</Success>

## Step 10: 验证数据已保存

再次查询所有书籍：

```graphql
query {
  books {
    id
    title
  }
}
```

你应该看到新添加的《百年孤独》在列表中：

```json
{
  "data": {
    "books": [
      {"id": 1, "title": "1984"},
      {"id": 2, "title": "动物农场"},
      {"id": 3, "title": "美丽新世界"},
      {"id": 4, "title": "百年孤独"}
    ]
  }
}
```

## Step 11: 删除数据

删除 ID 为 2 的书籍：

```graphql
mutation {
  deleteBook(id: 2)
}
```

返回 `true` 表示删除成功。

---

按 Ctrl+C 停止服务器。

## 你学到了什么

通过本教程，你：

- ✅ 安装了 Strawberry（Python GraphQL 库）
- ✅ 定义了 GraphQL 类型（`@strawberry.type`）
- ✅ 创建了查询操作（Query）
- ✅ 创建了变更操作（Mutation）
- ✅ 启动了 GraphQL 服务
- ✅ 使用 GraphQL Playground 执行查询和变更

## 完整代码

`main.py` 的完整代码：

```python
import strawberry
from typing import List, Optional

@strawberry.type
class Book:
    id: int
    title: str
    author: str
    year: int

books_db = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="动物农场", author="George Orwell", year=1945),
    Book(id=3, title="美丽新世界", author="Aldous Huxley", year=1932),
]

@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> List[Book]:
        return books_db

    @strawberry.field
    def book(self, id: int) -> Optional[Book]:
        for book in books_db:
            if book.id == id:
                return book
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str, year: int) -> Book:
        new_id = max(b.id for b in books_db) + 1
        new_book = Book(id=new_id, title=title, author=author, year=year)
        books_db.append(new_book)
        return new_book

    @strawberry.mutation
    def delete_book(self, id: int) -> bool:
        global books_db
        original_count = len(books_db)
        books_db = [b for b in books_db if b.id != id]
        return len(books_db) < original_count

schema = strawberry.Schema(query=Query, mutation=Mutation)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:schema", host="127.0.0.1", port=8000, reload=True)
```

## 下一步

- **[Strawberry 官方文档](https://strawberry.rocks/)** - 深入学习更多高级特性
- **[[Python FastApi 轻量web框架学习]]** - 学习如何将 GraphQL 集成到 FastAPI
- **[[Python-async-await-完全指南]]** - 了解如何使用异步操作

---

> [!tip] 继续探索
> GraphQL 的强大之处在于你能精确获取需要的数据。尝试在查询中只请求部分字段，观察返回结果的变化。