## 创建新用户，赋予权限

```sql
create user 'xin'@'%' IDENTIFIED by 'abc123';
grant select on wolf.* to 'xin'@'%';
```
## 设置root密码

```sql
ALTER USER 'root'@'%' IDENTIFIED BY 'abc123';
```