## 合并分支

```bash
# 切换到你想要合并结果落地的分支
git checkout main

# 合并 feature 分支
git merge feature-branch
```

*git > 2.23后可以用如下方法*
```bash
git switch main
git merge feature-branch
```

## 强制删除一个远程分支

如下演示强制回退一个提交，注意*谨慎操作*

```bash
git reset --hard HEAD~1
# 这时，只要不执行下面这行，也只是修改本地提交, feature_reentry是分支名称
git push --force-with-lease origin feature_reentry
```

## git rm --cached

将文件从 git 跟踪中移除，但**不删除本地文件**。

*常用场景*
- 文件已被 git 跟踪，后来才加入 `.gitignore`
- 不想删除本地文件，但希望停止版本控制

```bash
# 移除单个文件
git rm --cached filename

# 递归移除目录
git rm -r --cached directory/

# 多个文件/目录
git rm -r --cached dir1/ dir2/file.txt
```

