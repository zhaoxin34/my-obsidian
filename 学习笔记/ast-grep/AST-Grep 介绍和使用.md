# 什么是 ast-grep？

## 简介

ast-grep 是一个新的基于 AST（抽象语法树）的工具，用于大规模管理代码。

使用 ast-grep 非常简单，只需在终端中运行一个命令：

```bash
ast-grep --pattern 'var code = $PAT' --rewrite 'let code = $PAT' --lang js
```

上面的命令会将所有 JavaScript 文件中的 `var` 语句替换为 `let`。

---

ast-grep 是一个多功能的代码搜索、重写和 lint 工具：

- **搜索**：作为终端中的命令行工具，`ast-grep` 可以精确地基于 AST 搜索代码，在亚秒级时间内遍历数万个文件。
- **Lint**：你可以将 ast-grep 用作 linter。得益于灵活的规则系统，添加新的自定义规则非常直观简单，并且开箱即用提供漂亮的错误报告。
- **重写**：ast-grep 提供了遍历和操作语法树的 API。此外，你还可以使用运算符将简单模式组合成复杂的匹配规则。

> 将 ast-grep 视为 [grep](https://www.gnu.org/software/grep/manual/grep.html)、[eslint](https://eslint.org/) 和 [codemod](https://github.com/facebookincubator/fastmod) 的混合体。

想试试吗？查看[[技术工作/AST-Grep 快速入门]]！或者看看一些[[技术工作/AST-Grep 示例]]来了解 ast-grep 能做什么！我们还有一个 [在线 Playground](https://ast-grep.github.io/playground.html) 让你在线体验 ast-grep！

## 支持的语言

ast-grep 支持广泛的编程语言。以下是它支持的主要编程语言列表：

| 语言领域 | 支持的语言 |
|----------|------------|
| 系统编程 | `C`, `Cpp`, `Rust` |
| 服务端编程 | `Go`, `Java`, `Python`, `C-sharp` |
| Web 开发 | `JS(X)`, `TS(X)`, `HTML`, `CSS` |
| 移动应用开发 | `Kotlin`, `Swift` |
| 配置 | `Json`, `YAML`, `Hcl` |
| 脚本和协议等 | `Lua`, `Nix` |

感谢 [tree-sitter](https://tree-sitter.github.io/tree-sitter/)，这是一个流行的解析器生成库，ast-grep 开箱即用地支持[多种语言](https://ast-grep.github.io/reference/languages.html)！

## 动机

使用基于文本的工具搜索代码很快但不精确。我们通常更倾向于将代码解析为[抽象语法树](https://www.wikiwand.com/en/Abstract_syntax_tree)（AST）来进行精确匹配。

然而，使用 AST 开发是繁琐且令人沮丧的。考虑这个 "hello-world" 级别的任务：使用 Babel 在 JavaScript 中匹配 `console.log`。我们需要编写如下代码：

```javascript
path.parentPath.isMemberExpression() &&
path.parentPath.get('object').isIdentifier({ name: 'console' }) &&
path.parentPath.get('property').isIdentifier({ name: 'log' })
```

这段代码对于初学者来说需要详细解释。即使是经验丰富的开发者，编写这段代码也需要大量查阅文档。

这种痛苦并非特定于语言。[HackerOne 联合创始人 Jobert Abba](https://portswigger.net/daily-swig/semgrep-static-code-analysis-tool-helps-eliminate-entire-classes-of-vulnerabilities) 的一句话说明了跨语言的普遍痛点：

> 这些工具提供的内部 AST 查询接口通常文档不完善，且难以编写、理解和维护。

---

ast-grep 通过提供一个简单的核心机制来解决这个问题：使用代码来搜索相同模式的代码。可以把它看作是 基于 AST 而不是文本的 `grep`。

与 Babel 相比，我们可以用 ast-grep 轻松完成这个 hello-world 任务：

```bash
ast-grep -p "console.log"
```

查看 [在线 Playground](https://ast-grep.github.io/playground.html) 的实际效果！

基于这个简单的模式代码，我们可以构建一系列运算符来组合复杂的匹配规则，以应对各种场景。

尽管我们在介绍中使用了 JavaScript，但 ast-grep 并不特定于语言。它是一个由著名库 [tree-sitter](https://tree-sitter.github.io/) 支持的*多语言*工具。ast-grep 的理念可以应用于许多其他语言！

## 特性

还有很多其他看起来像 ast-grep 的工具，著名的前辈包括 [Semgrep](https://semgrep.dev/)、[comby](https://comby.dev/)、[shisho](https://github.com/flatt-security/shisho)、[gogocode](https://github.com/thx/gogocode)，以及新来者如 [gritQL](https://about.grit.io/)。

让 ast-grep 脱颖而出的是：

### 性能

ast-grep 由 Rust 编写，这是一种原生语言并利用多核优势。（在搜索简单模式时，它甚至可以击败 `ag`。）ast-grep 可以在几秒内处理数万个文件。

### 渐进性

你可以从在命令行中创建一行代码重写开始，最低限度地投入时间。后来如果你发现项目中反复出现一些代码异味，可以用几个模式组合在 YAML 中编写 lint 规则。最后，如果你是一个库作者或框架设计师，ast-grep 提供了编程接口来高效地重写或转译代码。

### 实用性

ast-grep 配备齐全。交互式代码修改功能可用。安装命令行工具后，linter 和语言服务器开箱即用。ast-grep 还为规则作者提供了测试框架。

## 查看 Discord 和 StackOverflow

还有问题？加入我们的 [Discord](https://discord.gg/4YZjf6htSQ) 与其他用户讨论！

你也可以在 [StackOverflow](https://stackoverflow.com/questions/ask/) 上的 [ast-grep](https://stackoverflow.com/questions/tagged/ast-grep) 标签下提问。
