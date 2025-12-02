```bash
zkCli.sh -server 127.0.0.1:2181
setAcl /myNode ip:192.168.1.10:rw
```
- `r` = read
- `w` = write
- `c` = create
- `d` = delete
- `a` = admin

*示例1*
setAcl /myNode ip:192.168.1.10:rcdwa

*示例2*

