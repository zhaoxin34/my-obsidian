## 用户操作

*创建用户*
`create user 'xin'@'%' IDENTIFIED WITH mysql_native_password by 'abc123';`

*只读权限*
`grant select on wolf.* to 'xin'@'%';`

-- 全部权限
```sql

-- 只读权限 
grant all on wolf.* to 'xin'@'%';
```

*修改表名*
`ALTER TABLE label_info RENAME  label_info2;`
## 设置root密码

```sql
ALTER USER 'root'@'%' IDENTIFIED BY 'abc123';
```