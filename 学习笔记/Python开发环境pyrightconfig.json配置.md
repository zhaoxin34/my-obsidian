假设有如下目录, 即解决.venv不在根目录的情况
```text
root
|- mcp
  |- .venv
|- pyrightconfig.json
```

`pyrightconfig.json` 可以像如下配置
```json
  {
    "venvPath": "./mcp",
    "venv": ".venv"
  }
```
