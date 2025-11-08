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

*配置domains.lua*
```lua
  ssh_domains = {
    {
      name = 'w11',
      remote_address = 'w11',
      username = 'zhaoxin',
      multiplexing = 'None',
    }
  }
```

*此时执行connect会报错
```bash
wezterm connect w11
23:49:09.891  WARN   wezterm_ssh::pty > ssh: setenv COLORTERM=truecolor failed: RequestDenied: Channel request env failed. Check the AcceptEnv setting on the ssh server side. Additional errors with setting env vars in this session will be logged at debug log level.
```

*修改w11的sshd配置，让他支持现代终端特性，即wezterm特性*
```
```