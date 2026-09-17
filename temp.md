   # 1. 看路由可达不（ICMP 层）                                                                                                                       
   ping -c 3 192.168.31.36                                                                                                                            
   # 2. 看 TCP 端口通不通（传输层）                                                                                                                   
   ssh -v -o ConnectTimeout=3 -o BatchMode=yes zhaoxin@192.168.31.36                                                                                  
   #     ↑ -v 会打印详细握手过程，-o BatchMode=yes 不进交互认证                                                                                       
   #     最后两行错误信息最关键  