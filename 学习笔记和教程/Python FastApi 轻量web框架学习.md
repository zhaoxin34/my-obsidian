# 示例

pip install "fastapi[standard]"

```python
from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

```bash
fastapi dev main.py  
╭────────── FastAPI CLI - Development mode ───────────╮  
│                                                     │  
│ Serving at: http://127.0.0.1:8000                   │  
│                                                     │  
│ API docs: http://127.0.0.1:8000/docs                │  
│                                                     │  
│ Running in development mode, for production use:    │  
│                                                     │  
│ fastapi run                                         │  
│                                                     │  
╰─────────────────────────────────────────────────────╯  
  
INFO: Will watch for changes in these directories: ['/home/user/code/awesomeapp']  
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)  
INFO: Started reloader process [2248755] using WatchFiles  
INFO: Started server process [2248757]  
INFO: Waiting for application startup.  
INFO: Application startup complete.
```