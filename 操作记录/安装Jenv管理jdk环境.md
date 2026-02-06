## 安装

```bash
brew install jenv
```

## 配置zsh

以下这两段不需要执行，只是示意，配置已经在working路径下

```bash
echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(jenv init -)"' >> ~/.zshrc

# 如果JAVA_HOME没有设置，就需要执行下面这行
jenv enable-plugin export
```

将已有的jdk目录添加到 jenv

```bash
jenv add /Volumes/data/working/sdk/java/jdk1.8.0_361.jdk/Contents/Home/
jenv doctor
```

设置全局java版本

```bash
jenv global 1.8
```