## 代码示例

```python
  from rich.console import Console
  from rich.table import Table
  from rich.progress import track

  console = Console()

  # 彩色打印
  console.print("[bold red]Error:[/bold red] Something went wrong")
  console.print("[green]Success![/green] Operation completed")

  # 表格
  table = Table(title="Employees")
  table.add_column("Name", style="cyan")
  table.add_column("Dept", style="magenta")
  table.add_column("Email", style="green")
  table.add_row("Alice", "Engineering", "alice@example.com")
  table.add_row("Bob", "Sales", "bob@example.com")
  console.print(table)

  # 进度条
  for i in track(range(10), description="Processing..."):
      pass

  # pretty print 任意对象
  from rich.pretty import pprint
  data = {"name": "test", "items": [1, 2, 3]}
  pprint(data)
```