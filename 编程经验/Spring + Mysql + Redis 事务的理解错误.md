## 会误以为 Spring + @Transactional 能做到

这是个坑。

例如：

@Transactional  
public void biz(){  
   mysql.insert(...);  
   redis.set(...);  
}

很多人以为：

“这不是跨 MySQL + Redis事务了吗？”

其实不是。

通常：

- MySQL 受数据库事务控制
- Redis只是被 thread-bound 顺带延迟 EXEC

不是原子双提交。

如果进程挂了：

MySQL committed  
Redis没写进去

还是可能发生。