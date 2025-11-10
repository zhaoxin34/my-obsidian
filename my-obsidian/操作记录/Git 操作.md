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