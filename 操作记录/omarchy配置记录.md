## 打开sshd服务

```bash
systemctl enable sshd
systemctl start sshd
ss -ntpl | grep 22
sudo ufw allow from 192.168.0.151 to any port 22 proto tcp
```