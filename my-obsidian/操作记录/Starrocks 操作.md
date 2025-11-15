## 创建新用户，赋予权限

```sql
create user 'xin'@'%' IDENTIFIED WITH mysql_native_password by 'abc123';
grant select on confluence.* to 'xin'@'%';
```
## 设置root密码

```sql
ALTER USER 'root'@'%' IDENTIFIED BY 'abc123';
```