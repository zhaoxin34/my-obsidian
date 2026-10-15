直接执行下面的命令，这会安装到systemd
```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama
```

安装embedding模型
```bash
ollama pull bge-m3
```