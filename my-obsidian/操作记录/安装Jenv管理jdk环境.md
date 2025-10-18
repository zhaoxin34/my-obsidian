## 安装

```bash
brew install jenv
```

## 配置zsh

以下这两段不需要执行，只是示意，配置已经在working路径下

```bash
echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(jenv init -)"' >> ~/.zshrc
```

验证jdk是由安装

```bash
jenv doctor
[ERROR]	Java binary in path is not in the jenv shims.
```