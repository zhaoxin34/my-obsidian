# Deep Dive into ast-grep's Pattern Syntax

> 原文: https://ast-grep.github.io/advanced/pattern-parse.html

ast-grep 的模式容易上手，但难以精通。虽然入门很简单，但掌握其细微之处可以大大增强你的代码搜索能力。

本文旨在帮助你深入理解 ast-grep 的模式是如何被解析、创建并有效用于代码匹配的。

## 创建模式的过程 (Steps to Create a Pattern)

在 ast-grep 中解析模式涉及以下关键步骤：

1. **预处理模式文本**，例如将 `$` 替换为 expando_char
2. **将预处理后的模式文本解析为 AST**
3. **根据内置启发式方法或用户提供的选择器提取有效的 AST 节点**
4. **检测带有通配符文本的 AST 并将其转换为元变量**

让我们深入了解每一个步骤。

## 模式基于 AST (Pattern is AST based)

首先，模式是基于 AST 的。

ast-grep 的模式代码将转换为抽象语法树 (AST) 格式，这是一种树结构，表示你要匹配的代码片段。

因此，模式不能是任意文本，而是带有元变量作为占位符的有效代码。如果模式无法被底层解析器 tree-sitter 解析，ast-grep 将无法找到有效的匹配。

创建模式时需要避免几个常见陷阱。

### 无效的模式代码 (Invalid Pattern Code)

ast-grep 模式必须是可解析的有效代码。虽然这看起来显而易见，但新手在创建带有元变量的模式时有时会犯错误。

元变量在大多数语言中通常被解析为标识符。

使用元变量时，请确保它们放在有效的上下文中，而不是用作关键字或运算符。例如，你可能想用 `$OP` 来匹配二元表达式 like `a + b`。下面的模式不会工作，因为解析器会将其视为三个用空格分隔的连续标识符。

```yaml
$LEFT $OP $RIGHT
```

你可以改用原子规则 kind: binary_expression 来匹配二元表达式。

同样，在 JavaScript 中，你可能想匹配对象访问器 like `{ get foo() {}, set bar() { } }`。下面的模式不会工作，因为元变量不会被解析为 get 和 set 关键字。

```javascript
obj = { $KODY foo() { } }
```

这种情况下，规则更适合：

```yaml
rule:
  kind: method_definition
  regex: '^get|set\s'
```

### 不完整的模式代码 (Incomplete Pattern Code)

在模式中编写不完整的代码片段是很常见的，甚至是一种尝试。然而，不完整的代码并不总是有效。

考虑以下 JSON 代码片段作为模式：

```json
"a": 123
```

虽然这里的意图显然是匹配键值对，但 tree-sitter 不会将其视为有效的 JSON 代码，因为它缺少外层的 `{}`。因此 ast-grep 无法解析它。

这里的解决方案是使用 pattern object 来提供完整的代码片段：

```yaml
pattern:
  context: '{ "a": 123 }'
  selector: pair
```

你可以使用 ast-grep playground 的 pattern tab 或 rule tab 来验证它。

**不完整的模式代码有时由于错误容忍可以正常工作**。

为了获得更好的用户体验，ast-grep 会尽可能宽松地解析模式代码。ast-grep 解析器会尝试恢复解析错误并忽略缺失的语言构造。

例如，Java 中的模式 `foo(bar)` 无法解析为有效代码。然而，ast-grep 恢复了解析错误，忽略了缺失的分号，并将其视为方法调用。所以这个模式仍然有效。

### 歧义模式代码 (Ambiguous Pattern Code)

正如编程语言有歧义的语法，ast-grep 模式也可能存在歧义。

让我们考虑以下 JavaScript 代码片段：

```javascript
a: 123
```

它可以被解释为对象键值对或标签语句。

没有其他提示，ast-grep 默认会将其解析为标签语句。要匹配对象键值对，我们需要通过使用 pattern object 来提供更多上下文：

```yaml
pattern:
  context: '{ a: 123 }'
  selector: pair
```

其他歧义模式的例子：
- 在 Golang 和 C 中匹配函数调用
- 在 JavaScript 中匹配类字段

## ast-grep 如何处理模式代码？ (How ast-grep Handles Pattern Code?)

ast-grep 竭尽全力解析模式代码，以获得最佳用户体验。

以下是 ast-grep 用于处理代码片段的一些策略：

1. **将 $ 替换为 expando_char**：某些语言使用 `$` 作为特殊字符，因此 ast-grep 会将其替换为 expando_char，以使模式代码可解析
2. **忽略缺失的节点**：ast-grep 会忽略模式中缺失的节点，如 Java/C/C++ 中的尾部逗号
3. **将根错误视为普通节点**：如果解析器错误没有兄弟节点，ast-grep 会将其视为普通节点

如果上述方法都失败，用户应该通过 pattern object 提供更多代码。

> ⚠️ **注意**: 模式错误恢复很有用，但不能保证
>
> ast-grep 的恢复机制严重依赖 tree-sitter 的行为。我们无法保证无效模式在不同版本之间解析的一致性。因此，使用无效模式可能会在升级 ast-grep 后导致意外结果。
>
> 如有疑问，请始终使用带有 pattern object 的有效代码片段。

## 提取模式的有效 AST (Extract Effective AST for Pattern)

解析模式代码后，ast-grep 需要提取 AST 节点来创建实际模式。

通常，由 tree-sitter 生成的代码片段将是一个完整的 AST 树。然而，整个树不太可能被用作模式。代码 `123` 会在许多语言中生成一个树，如 `program -> expression_statement -> number`。但我们想匹配代码中的数字字面量，而不是只包含一个数字的程序。

ast-grep 使用两种策略来提取将用于匹配代码的有效 AST 节点。

### 内置启发式方法 (Builtin Heuristic)

默认情况下，ast-grep 提取叶子节点或具有多个子节点的最内层节点。

这个启发式方法提取最具体的节点，同时保留模式中的所有结构信息。如果一个节点只有一个子节点，它是原子的，不能进一步分解。我们可以安全地假设该节点不包含用于匹配的结构信息。相反，具有多个子节点的节点包含我们想要搜索的结构。

**示例**：

- `123` 会被提取为 number，因为它是一个叶子节点
  ```yaml
  program
    expression_statement
      number              <--- 有效节点
  ```

- `foo(bar)` 会被提取为 call_expression，因为它是有多个子节点的最内层节点
  ```yaml
  program
    expression_statement
      call_expression       <--- 有效节点
        identifier
        arguments
          identifier
  ```

### 用户定义的选择器 (User Defined Selector)

有时内置启发式方法提取的有效节点可能不是你想要的。你可以使用规则配置中的 selector 字段显式指定要提取的节点。

例如，你可能想匹配 JavaScript 代码中的整个 `console.log` 语句。内置启发式方法提取的有效节点是 call_expression，但你想匹配整个 expression_statement。

直接使用 `console.log($$$)` 不会在模式中包含尾部分号。

```javascript
console.log("Hello")
console.log("World");
```

你可以使用 pattern object 显式指定有效节点为 expression_statement：

```yaml
pattern:
  context: console.log($$$)
  selector: expression_statement
```

当你也使用关系规则如 `follows` 和 `precedes` 时，使用 selector 特别有帮助。你想匹配语句而不是默认的内部表达式节点，并匹配周围的其他语句。

> 💡 **提示**: 如果有疑问，请首先尝试 pattern object。

## 元变量深度解析 (Meta Variable Deep Dive)

ast-grep 的元变量也是基于 AST 的，并在从模式代码提取的有效节点中检测。

### 模式中的元变量检测 (Meta Variable Detection in Pattern)

并非所有以 `$` 开头的字符串都会被检测为元变量。

只有匹配元变量语法的 AST 节点才会被检测到。如果元变量文本不是节点中的唯一文本，或者它跨越多个节点，它将不会被检测为元变量。

**有效的元变量示例**：

- `$A` 可以工作 - `$A` 是单个标识符
- `$A.$B` 可以工作 - `$A` 是 member_expression 中的标识符，`$B` 是 property_identifier
- `$A.method($B)` 可以工作 - `$A` 是 member_expression 中的标识符，`$B` 是 arguments 中的标识符

**无效的元变量示例**：

- `obj.on$EVENT` 不工作 - on$EVENT 是 property_identifier，但 $EVENT 不是唯一文本
- `"Hello $WORLD"` 不工作 - $WORLD 在 string_content 内，不是唯一文本
- `a $OP b` 不工作 - 整个模式无法解析
- `$jq` 不工作 - 元变量不接受小写字母

### 匹配未命名的节点 (Matching Unnamed Nodes)

默认情况下，元变量模式 `$META` 会捕获命名的节点。要捕获未命名的节点，可以使用双美元符号 `$$VAR`。

让我们回到二元表达式的例子。用一个单一的模式匹配任意二元表达式是不可能的。但我们可以结合 kind 和 has 来匹配二元表达式中的运算符。

注意，`$OP` 无法匹配运算符，因为运算符不是命名节点。我们需要改用 `$$OP`。

```yaml
rule:
  kind: binary_expression
  has:
    field: operator
    pattern: $$OP
    # pattern: $OP
```

参见上面的规则来匹配所有算术表达式。

## 多重元变量如何匹配代码 (How Multi Meta Variables Match Code)

像 `$$$ARGS` 这样的多重元变量具有特殊的匹配行为。它会在 AST 中匹配多个节点。

当元变量开始匹配时，`$$$ARGS` 会在源代码中匹配多个节点。它会尽可能多地匹配节点，直到模式中元变量之后的第一个 AST 节点被匹配。

这个行为类似于正则表达式中的非贪婪匹配和 TypeScript 中的模板字符串字面量推断。

## 使用 ast-grep playground 调试模式

ast-grep playground 是调试模式代码的好工具。pattern tab 和 pattern panel 可以帮助你可视化 AST 树、有效节点和元变量。

在下一篇文章中，我们将解释 ast-grep 的模式如何用于匹配代码，即模式匹配算法。

---

*最后更新: 2024-01*
