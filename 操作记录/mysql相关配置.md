
# 安装Mysql

使用oracle登陆下载Mysql，[http://dev.mysql.com/get/Downloads/MySQL-5.6/mysql-5.6.26.tar.gz](http://dev.mysql.com/get/Downloads/MySQL-5.6/mysql-5.6.26.tar.gz)
下载解压mysql，进入mysql目录
```bash
# 创建mysql用户和组
groupadd mysql
sudo useradd -g mysql mysql

# 创建数据和配置目录
mkdir /home/mysql/conf
mkdir /home/mysql/data
mkdir /home/mysql/log

# 编译安装
# 安装cmake

cmake . -DCMAKE_INSTALL_PREFIX=/usr/local/mysql/ -DMYSQL_DATADIR=/home/mysql/data/ -DMYSQL_UNIX_ADDR=/home/mysql/data/mysqld.sock -DWITH_INNOBASE_STORAGE_ENGINE=1 -DENABLED_LOCAL_INFILE=1 -DMYSQL_TCP_PORT=3306 -DEXTRA_CHARSETS=all -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci -DMYSQL_USER=mysql -DWITH_DEBUG=0 -DSYSCONFDIR=/home/mysql/conf/

make
make install
```



# 初始化数据库

```bash
/usr/local/mysql/scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql/ --datadir=/home/mysql/data/

# 放入.bash_profile
export PATH=$PATH:$HOME/bin:/usr/local/mysql/bin:/usr/local/mysql/lib
```



修改 /etc/my.cnf
```config
[mysqld]_

log-bin=mysql-bin_

binlog-format=ROW_
server-id=1_
datadir=/home/mysql/data_
socket=/home/mysql/mysql.sock_
user=mysql_
# Disabling symbolic-links is recommended to prevent assorted security risks_
symbolic-links=0_
skip-external-locking_
key_buffer_size = 16M_
max_allowed_packet = 1M_
table_open_cache = 64_
sort_buffer_size = 512K_
net_buffer_length = 8K_
read_buffer_size = 256K_
read_rnd_buffer_size = 512K_
myisam_sort_buffer_size = 8M_
character_set_server=utf8_

# innodb_
innodb_buffer_pool_size = 2048m_
innodb_log_file_size = 256m_
innodb_log_files_in_group = 2_
innodb_log_buffer_size = 3m_
innodb_flush_log_at_trx_commit = 2_
innodb_file_per_table = 1_
transaction-isolation = read-committed_
innodb_flush_method = O_DIRECT_
innodb_thread_concurrency = 64_
innodb_open_files = 800_
innodb_max_dirty_pages_pct = 50_

# lower_case_table_names = 1_
[mysqld_safe]_
log-error=/home/mysql/log/mysqld.log_
pid-file=/home/mysql/mysqld.pid_
```

# 启动mysql

```bash
sudo cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysqld
sudo /etc/init.d/mysqld start
```

在/etc/init.d/rc.local 加入上命令可以自动拉起
修改/etc/init.d/mysqld
修改pid文件的地址为/home/mysql/mysql.pid

# 登陆

mysql -u root -h 127.0.0.1

## 权限设置

*外网可以访问，并设置密码*
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'youpassword' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

*创建只读用户和删除用户*

```sql
create user 'xin'@'%' IDENTIFIED WITH mysql_native_password by 'abc123';
grant select on confluence.* to 'xin'@'%';
DROP USER 'bilian'@'%';
```

*观察mysql log

```sql
SET GLOBAL general_log = 'ON';
```

*看一看log文件的位置

```sql
SHOW VARIABLES LIKE "general_log%";
```
+------------------+----------------------------+
| Variable_name     | Value                      |
+------------------+----------------------------+
| general_log           | OFF                        |
| general_log_file    | /var/run/mysqld/mysqld.log |
+------------------+----------------------------+
>然后tail这个文件

*查看用户权限*

```sql
SHOW GRANTS FOR root;
SHOW GRANTS FOR chaos;
select user, plugin from mysql.user; 
```

*本机如果用户名密码不能登录，反而用空密码可以登陆的时候，其原因是system.user的有一条用户名为空，执行如下语句*

```sql
delete from mysql.user  where user='';
FLUSH PRIVILEGES;
```

# 数据导出

*只导出数据，不倒出表结构，不含注释，没有锁表语句，craw是库 job是一个表

```bash
mysqldump -u root -p'xxxxx' -h 127.0.0.1  --skip-comments  --no-create-info  --skip-add-locks craw job
```

*导出所有库
```bash
mysqldump -u root -p -h datatist.cxdhk735quly.ap-northeast-1.rds.amazonaws.com --all-databases --skip-lock-tables
```

# 性能相关

Explain extend select xxxxxxxxxxx 用于查看执行计划
mysql使用B+Tree平衡二叉树做索引

 varchar和text blob的区别如下：

TEXT and BLOB is stored off the table with the table just having a pointer to the location of the actual storage.

VARCHAR is stored inline with the table. VARCHAR is faster when the size is reasonable, the tradeoff of which would be faster depends upon your data and your hardware, you'd want to benchmark a realworld scenario with your data.

*Binlog查看

```sql
show master status;
``` 

+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000007 |      120 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
```sql
        SHOW BINLOG EVENTS
            [IN 'log_name'] //要查询的binlog文件名
            [FROM pos] 
            [LIMIT [offset,] row_count]
```

*找到没有主键的表*

```sql
select tab.table_schema as database_name,
       tab.table_name
from information_schema.tables tab
left join information_schema.table_constraints tco
          on tab.table_schema = tco.table_schema
          and tab.table_name = tco.table_name
          and tco.constraint_type = 'PRIMARY KEY'
where tco.constraint_type is null
      and tab.table_schema not in('mysql', 'information_schema',
                                  'performance_schema', 'sys')
      and tab.table_type = 'BASE TABLE'
        and tab.table_schema = 'hive' -- put schema name here
order by tab.table_schema,
         tab.table_name;
```
