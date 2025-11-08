# 使用技巧

*命令行开启一个新窗口，并启动一个命令*
```bash
wezterm start -- nvim ~/.config
```

# 使用sshdomain连接我的w11

*首先创建免密登录
`ssh-keygen`
`ssh-copy-id`

*创建配置文件~/.ssh/config
`chomd 600 config`
```text
Host w11
  HostName 192.168.31.36
  User zhaoxin
  Port 2222
  IdentityFile ~/.ssh/id_ed25519
```

*如下命令可以登录到w11上
```bash
ssh w11
```
