   # 1. 看路由可达不（ICMP 层）                                                                                                                       
   ping -c 3 192.168.31.36                                                                                                                            
   # 2. 看 TCP 端口通不通（传输层）                                                                                                                   
   ssh -v -o ConnectTimeout=3 -o BatchMode=yes zhaoxin@192.168.31.36                                                                                  
   #     ↑ -v 会打印详细握手过程，-o BatchMode=yes 不进交互认证                                                                                       
   #     最后两行错误信息最关键  

❯  ssh -v -o ConnectTimeout=3 -o BatchMode=yes zhaoxin@192.168.31.36
OpenSSH_9.9p2, LibreSSL 3.3.6
debug1: Reading configuration data /Users/zhaoxin/.ssh/config
debug1: Reading configuration data /Users/zhaoxin/.orbstack/ssh/config
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: Reading configuration data /etc/ssh/ssh_config.d/100-macos.conf
debug1: /etc/ssh/ssh_config.d/100-macos.conf line 1: Applying options for *
debug1: Reading configuration data /etc/ssh/crypto.conf
debug1: Authenticator provider $SSH_SK_PROVIDER did not resolve; disabling
debug1: Connecting to 192.168.31.36 [192.168.31.36] port 22.
debug1: connect to address 192.168.31.36 port 22: Operation timed out
ssh: connect to host 192.168.31.36 port 22: Operation timed out
❯ ping -c 3 192.168.31.36
PING 192.168.31.36 (192.168.31.36): 56 data bytes
Request timeout for icmp_seq 0
ping: sendto: No route to host
Request timeout for icmp_seq 1

--- 192.168.31.36 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss