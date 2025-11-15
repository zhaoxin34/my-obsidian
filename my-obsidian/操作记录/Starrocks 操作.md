## 创建新用户，赋予权限

```sql
create user 'xin'@'%' IDENTIFIED by 'abc123';

-- 只读权限 
grant select on wolf.* to 'xin'@'%';
-- 全部权限
grant all on wolf.* to 'xin'@'%';
```
## 设置root密码

```sql
ALTER USER 'root'@'%' IDENTIFIED BY 'abc123';
```