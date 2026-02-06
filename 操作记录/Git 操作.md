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