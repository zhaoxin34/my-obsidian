1. 1.
    
    安装Mysql
    

使用oracle登陆下载Mysql，[http://dev.mysql.com/get/Downloads/MySQL-5.6/mysql-5.6.26.tar.gz](http://dev.mysql.com/get/Downloads/MySQL-5.6/mysql-5.6.26.tar.gz)

下载解压mysql，进入mysql目录

创建mysql用户和组

groupadd mysql

sudo useradd -g mysql mysql

创建数据和配置目录

mkdir /home/mysql/conf

mkdir /home/mysql/data

mkdir /home/mysql/log

编译安装

安装cmake

cmake . -DCMAKE_INSTALL_PREFIX=/usr/local/mysql/ -DMYSQL_DATADIR=/home/mysql/data/ -DMYSQL_UNIX_ADDR=/home/mysql/data/mysqld.sock -DWITH_INNOBASE_STORAGE_ENGINE=1 -DENABLED_LOCAL_INFILE=1 -DMYSQL_TCP_PORT=3306 -DEXTRA_CHARSETS=all -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci -DMYSQL_USER=mysql -DWITH_DEBUG=0 -DSYSCONFDIR=/home/mysql/conf/

make

make install

初始化数据库

/usr/local/mysql/scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql/ --datadir=/home/mysql/data/

放入.bash_profile

export PATH=$PATH:$HOME/bin:/usr/local/mysql/bin:/usr/local/mysql/lib

修改 /etc/my.cnf

_[mysqld]_

_log-bin=mysql-bin_

_binlog-format=ROW_

_server-id=1_

_datadir=/home/mysql/data_

_socket=/home/mysql/mysql.sock_

_user=mysql_

_# Disabling symbolic-links is recommended to prevent assorted security risks_

_symbolic-links=0_

_skip-external-locking_

_key_buffer_size = 16M_

_max_allowed_packet = 1M_

_table_open_cache = 64_

_sort_buffer_size = 512K_

_net_buffer_length = 8K_

_read_buffer_size = 256K_

_read_rnd_buffer_size = 512K_

_myisam_sort_buffer_size = 8M_

_character_set_server=utf8_

_# innodb_

_innodb_buffer_pool_size = 2048m_

_innodb_log_file_size = 256m_

_innodb_log_files_in_group = 2_

_innodb_log_buffer_size = 3m_

_innodb_flush_log_at_trx_commit = 2_

_innodb_file_per_table = 1_

_transaction-isolation = read-committed_

_innodb_flush_method = O_DIRECT_

_innodb_thread_concurrency = 64_

_innodb_open_files = 800_

_innodb_max_dirty_pages_pct = 50_

_# lower_case_table_names = 1_

_[mysqld_safe]_

_log-error=/home/mysql/log/mysqld.log_

_pid-file=/home/mysql/mysqld.pid_

启动mysql

sudo cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysqld

sudo /etc/init.d/mysqld start

在/etc/init.d/rc.local 加入上命令可以自动拉起

修改/etc/init.d/mysqld

修改pid文件的地址为/home/mysql/mysql.pid

登陆

mysql -u root -h 127.0.0.1

权限设置

1. 外网可以访问，并设置密码

mysql>GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'youpassword' WITH GRANT OPTION;

FLUSH PRIVILEGES;

2. 创建只读用户和删除用户

mysql>create user 'xin'@'%' IDENTIFIED WITH mysql_native_password by 'abc123';

mysql>grant select on confluence.* to 'xin'@'%';

mysql>DROP USER 'bilian'@'%';

3. 观察mysql log

mysql>SET GLOBAL general_log = 'ON';

看一看log文件的位置

mysql>SHOW VARIABLES LIKE "general_log%";

+------------------+----------------------------+

| Variable_name    | Value                      |

+------------------+----------------------------+

| general_log      | OFF                        |

| general_log_file | /var/run/mysqld/mysqld.log |

+------------------+----------------------------+

然后tail这个文件

4.查看用户权限

SHOW GRANTS FOR root;

SHOW GRANTS FOR chaos;

mysql> select user, plugin from mysql.user; +------------------+-----------------------+ | user | plugin | +------------------+-----------------------+ | root | mysql_native_password | | xin | caching_sha2_password | | mysql.infoschema | caching_sha2_password | | mysql.session | caching_sha2_password | | mysql.sys | caching_sha2_password | | root | mysql_native_password | +------------------+-----------------------+

5. 本机如果用户名密码不能登录，反而用空密码可以登陆的时候，其原因是system.user的有一条用户名为空，执行如下语句

delete from mysql.user  where user='';

FLUSH PRIVILEGES;

数据导出

只导出数据，不倒出表结构，不含注释，没有锁表语句，craw是库 job是一个表

mysqldump -u root -p'xxxxx' -h 127.0.0.1  --skip-comments  --no-create-info  --skip-add-locks craw job

导出所有库

mysqldump -u root -p -h datatist.cxdhk735quly.ap-northeast-1.rds.amazonaws.com --all-databases --skip-lock-tables

性能相关

Explain extend select xxxxxxxxxxx 用于查看执行计划

mysql使用B+Tree平衡二叉树做索引

 varchar和text blob的区别如下：

TEXT and BLOB is stored off the table with the table just having a pointer to the location of the actual storage.

VARCHAR is stored inline with the table. VARCHAR is faster when the size is reasonable, the tradeoff of which would be faster depends upon your data and your hardware, you'd want to benchmark a realworld scenario with your data.

Binlog查看

mysql> show master status;

+------------------+----------+--------------+------------------+-------------------+

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |

+------------------+----------+--------------+------------------+-------------------+

| mysql-bin.000007 |      120 |              |                  |                   |

+------------------+----------+--------------+------------------+-------------------+

        SHOW BINLOG EVENTS

            [IN 'log_name'] //要查询的binlog文件名

            [FROM pos] 

            [LIMIT [offset,] row_count]

找到没有主键的表

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