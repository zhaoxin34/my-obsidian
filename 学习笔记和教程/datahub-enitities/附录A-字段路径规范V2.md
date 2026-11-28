---
title: 字段路径规范（Version 2）
entity: field-path-spec-v2
order: A1
source: https://docs.datahub.com/docs/advanced/field-path-spec-v2
---

# SchemaFieldPath 规范（Version 2）

本文档概述了 [SchemaField](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/schema/SchemaField.pdl) 模型中 `fieldPath` 成员的正式规范。本规范（第 2 版）考虑了支持多种嵌套类型、union（联合类型）和可选字段的独特需求，相较于当前实现（第 1 版）有显著改进。

## 需求

目前，datahub 使用 `fieldPath` 字段不仅用于在 UI 中渲染 schema 字段，还将其作为字段在其他位置的主要标识符，例如
[EditableSchemaFieldInfo](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/schema/EditableSchemaFieldInfo.pdl#L12)、
用量统计（usage stats）和数据画像（data profiles）。因此，它必须满足以下要求。

- 在一个 schema 内的所有字段中必须是唯一的。
- 使 UI 中的 schema 导航更加直观。
- 允许识别字段所属的 schema 类型，例如 `key-schema` 或 `value-schema`。
- 允许未来演进（future-evolution）

## 现有约定（v1）

现有约定是：对简单字段，直接使用字段名称作为 `fieldPath`；对嵌套字段，则使用以 `dot` 分隔的名称。该方案无法满足上述[需求](#需求)。下面的示例说明了该方案在哪里不满足 `uniqueness`（唯一性）需求。

### 示例：有歧义的字段路径

考虑下面的 `Avro` schema，它是由两种记录类型 `A` 和 `B` 构成的 `union`，二者各有一个同名为 `f` 的简单字段，其类型均为 `string`。v1 命名方案无法区分 `fieldPath=f` 指的是记录类型 `A` 还是 `B`。

```
[
    {
        "type": "record",
        "name": "A",
        "fields": [{ "name": "f", "type": "string" } ]
    }, {
        "type": "record",
        "name": "B",
        "fields": [{ "name": "f", "type": "string" } ]
    }
]
```

## FieldPath 编码方案（v2）

`fieldPath` 的 V2 编码语法由下面的文法（grammar）给出。`FieldPathSpec` 本质上是该成员带类型标注的路径，路径上的每个 token 表示一层嵌套成员，从最外层的类型开始，一直延伸到该成员。对于具有 `one-of` 语义的 `unions`，对应字段将为 union 的每个 `member` 分别作为其 `type` 输出一次，同时还有一个对应 `union` 本身的路径。

### 正式规范：

```
<SchemaFieldPath> := <VersionToken>.<PartOfKeySchemaToken>.<FieldPathSpec>  // when part of a key-schema
                   | <VersionToken>.<FieldPathSpec> // when part of a value schema
<VersionToken> := [version=<VersionId>] // [version=2.0] for v2
<PartOfKeySchemaToken> := [key=True]  // when part of a key schema
<FieldPathSpec> := <FieldToken>+  // this is the type prefixed path field (nested if repeats).
<FieldToken> := <TypePrefixToken>.<name_of_the_field> // type prefixed path of a field.
<TypePrefixToken> := <NestedTypePrefixToken>.<SimpleTypeToken> | <SimpleTypeToken>
<NestedTypePrefixToken> := [type=<NestedType>]
<SimpleTypeToken> := [type=<SimpleType>]
<NestedType> := <name of a struct/record> | union | array | map
<SimpleType> := int | float | double | string | fixed | enum
```

对于[上面的示例](#示例：有歧义的字段路径)，这种编码将产生下面 2 条分别对应 `A.f` 和 `B.f` 字段的唯一路径。

```python
unique_v2_field_paths = [
 "[version=2.0].[type=union].[type=A].[type=string].f",
 "[version=2.0].[type=union].[type=B].[type=string].f"
]
```

注意：

- 这种编码始终保证在一个 schema 内的唯一性，因为通向字段的完整类型标注都被编码进了 fieldPath 本身。
- 处理一个 fieldPath（例如来自 UI）时，只需从左到右遍历路径上的每个 token 即可简化处理。
- 加入 PartOfKeySchemaToken 后，可以识别该字段是否属于 key-schema。
- 加入 VersionToken 后，允许未来演进。
- 要表示 `optional` 字段（在 `Avro` 等格式中它们有时被建模为 `unions`），不要将其当作 `union` 成员处理，而应将 `SchemaField` 的 `nullable` 成员设置为 `True`。

## 示例

### 基础类型

```python
avro_schema = """
{
  "type": "string"
}
"""
unique_v2_field_paths = [
  "[version=2.0].[type=string]"
]
```

### 记录（Records）

**简单记录**

```python
avro_schema = """
{
  "type": "record",
  "name": "some.event.E",
  "namespace": "some.event.N",
  "doc": "this is the event record E"
  "fields": [
    {
      "name": "a",
      "type": "string",
      "doc": "this is string field a of E"
    },
    {
      "name": "b",
      "type": "string",
      "doc": "this is string field b of E"
    }
  ]
}
"""

unique_v2_field_paths = [
    "[version=2.0].[type=E].[type=string].a",
    "[version=2.0].[type=E].[type=string].b",
]
```

**嵌套记录**

```python
avro_schema = """
{
    "type": "record",
    "name": "SimpleNested",
    "namespace": "com.linkedin",
    "fields": [{
        "name": "nestedRcd",
        "type": {
            "type": "record",
            "name": "InnerRcd",
            "fields": [{
                "name": "aStringField",
                 "type": "string"
            } ]
        }
    }]
}
"""

unique_v2_field_paths = [
  "[version=2.0].[key=True].[type=SimpleNested].[type=InnerRcd].nestedRcd",
  "[version=2.0].[key=True].[type=SimpleNested].[type=InnerRcd].nestedRcd.[type=string].aStringField",
]
```

**递归记录**

```python
avro_schema = """
{
    "type": "record",
    "name": "Recursive",
    "namespace": "com.linkedin",
    "fields": [{
        "name": "r",
        "type": {
            "type": "record",
            "name": "R",
            "fields": [
                { "name" : "anIntegerField", "type" : "int" },
                { "name": "aRecursiveField", "type": "com.linkedin.R"}
            ]
        }
    }]
}
"""

unique_v2_field_paths = [
  "[version=2.0].[type=Recursive].[type=R].r",
  "[version=2.0].[type=Recursive].[type=R].r.[type=int].anIntegerField",
  "[version=2.0].[type=Recursive].[type=R].r.[type=R].aRecursiveField"
]
```

```python
avro_schema ="""
{
    "type": "record",
    "name": "TreeNode",
    "fields": [
        {
            "name": "value",
            "type": "long"
        },
        {
            "name": "children",
            "type": { "type": "array", "items": "TreeNode" }
        }
    ]
}
"""
unique_v2_field_paths = [
 "[version=2.0].[type=TreeNode].[type=long].value",
 "[version=2.0].[type=TreeNode].[type=array].[type=TreeNode].children",
]
```

### Unions

```python
avro_schema = """
{
    "type": "record",
    "name": "ABUnion",
    "namespace": "com.linkedin",
    "fields": [{
        "name": "a",
        "type": [{
            "type": "record",
            "name": "A",
            "fields": [{ "name": "f", "type": "string" } ]
            }, {
            "type": "record",
            "name": "B",
            "fields": [{ "name": "f", "type": "string" } ]
            }
        ]
    }]
}
"""
unique_v2_field_paths: List[str] = [
    "[version=2.0].[key=True].[type=ABUnion].[type=union].a",
    "[version=2.0].[key=True].[type=ABUnion].[type=union].[type=A].a",
    "[version=2.0].[key=True].[type=ABUnion].[type=union].[type=A].a.[type=string].f",
    "[version=2.0].[key=True].[type=ABUnion].[type=union].[type=B].a",
    "[version=2.0].[key=True].[type=ABUnion].[type=union].[type=B].a.[type=string].f",
]
```

### Arrays

```python
avro_schema = """
{
    "type": "record",
    "name": "NestedArray",
    "namespace": "com.linkedin",
    "fields": [{
        "name": "ar",
        "type": {
            "type": "array",
            "items": {
                "type": "array",
                "items": [
                    "null",
                    {
                        "type": "record",
                        "name": "Foo",
                        "fields": [ {
                            "name": "a",
                            "type": "long"
                        } ]
                    }
                ]
            }
        }
    }]
}
"""
unique_v2_field_paths: List[str] = [
  "[version=2.0].[type=NestedArray].[type=array].[type=array].[type=Foo].ar",
  "[version=2.0].[type=NestedArray].[type=array].[type=array].[type=Foo].ar.[type=long].a",
]
```

### Maps

```python
avro_schema = """
{
  "type": "record",
  "name": "R",
  "namespace": "some.namespace",
  "fields": [
    {
      "name": "a_map_of_longs_field",
      "type": {
        "type": "map",
        "values": "long"
      }
    }
  ]
}
"""
unique_v2_field_paths = [
  "[version=2.0].[type=R].[type=map].[type=long].a_map_of_longs_field",
]


```

### 混合复杂类型示例

```python
# Combines arrays, unions and records.
avro_schema = """
{
    "type": "record",
    "name": "ABFooUnion",
    "namespace": "com.linkedin",
    "fields": [{
        "name": "a",
        "type": [ {
            "type": "record",
            "name": "A",
            "fields": [{ "name": "f", "type": "string" } ]
            }, {
            "type": "record",
            "name": "B",
            "fields": [{ "name": "f", "type": "string" } ]
            }, {
            "type": "array",
            "items": {
                "type": "array",
                "items": [
                    "null",
                    {
                        "type": "record",
                        "name": "Foo",
                        "fields": [{ "name": "f", "type": "long" }]
                    }
                ]
            }
    }]
    }]
}
"""

unique_v2_field_paths: List[str] = [
  "[version=2.0].[type=ABFooUnion].[type=union].a",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=A].a",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=A].a.[type=string].f",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=B].a",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=B].a.[type=string].f",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=array].[type=array].[type=Foo].a",
  "[version=2.0].[type=ABFooUnion].[type=union].[type=array].[type=array].[type=Foo].a.[type=long].f",
]
```

更多示例，请参见
[AvroToMceSchemaConverter 的单元测试](https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/tests/unit/test_schema_util.py)。

### 向后兼容性

虽然该格式与 v1 格式并不直接兼容，但只需去除所有由方括号包裹的 v2 token `[<new_in_v2>]`，即可轻松从 v2 编码构造出等价的 v1 编码。

> 本文为 DataHub 官方文档的中文翻译：[原文链接](https://docs.datahub.com/docs/advanced/field-path-spec-v2)。
