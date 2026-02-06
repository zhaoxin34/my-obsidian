```bash
zkCli.sh -server 127.0.0.1:2181
```
- `r` = read
- `w` = write
- `c` = create
- `d` = delete
- `a` = admin

*示例1*
```bash
setAcl /myNode ip:192.168.1.10:rcdwa
```

*示例2  同一个节点可以设置多个 ACL*
- 内网段 192.168.1.0/24 有读权限
- 管理机 10.0.0.5 有全部权限
```bash
setAcl /myNode ip:192.168.1.0/24:r,ip:10.0.0.5:rcdwa
```
